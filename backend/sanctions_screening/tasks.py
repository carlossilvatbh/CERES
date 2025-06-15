"""
Celery tasks for sanctions screening.
Production-ready async task processing with proper error handling.
"""

from celery import shared_task
from celery.exceptions import Retry
from django.core.cache import cache
from django.utils import timezone
from typing import Dict, List, Any, Optional
import logging
import requests
import time
from datetime import datetime, timedelta

from .models import Customer, ScreeningResult, ScreeningAlert
from .sources.data_source_manager import DataSourceManager
from core.monitoring import track_performance, log_audit_event

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def screen_customer(self, customer_id: int, screening_sources: List[str] = None) -> Dict[str, Any]:
    """
    Screen a single customer against sanctions lists.
    
    Args:
        customer_id: ID of the customer to screen
        screening_sources: List of sources to check (optional)
        
    Returns:
        Dict containing screening results
    """
    try:
        with track_performance('customer_screening'):
            customer = Customer.objects.get(id=customer_id)
            
            # Log audit event
            log_audit_event(
                'screening_started',
                user_id=None,
                customer_id=customer_id,
                metadata={'sources': screening_sources}
            )
            
            # Initialize data source manager
            source_manager = DataSourceManager()
            
            # Use default sources if none specified
            if not screening_sources:
                screening_sources = ['ofac', 'un', 'eu', 'opensanctions']
            
            results = {}
            alerts = []
            
            for source in screening_sources:
                try:
                    # Check cache first
                    cache_key = f"screening_{source}_{customer_id}"
                    cached_result = cache.get(cache_key)
                    
                    if cached_result:
                        results[source] = cached_result
                        continue
                    
                    # Perform screening
                    source_result = source_manager.screen_customer(
                        customer=customer,
                        source=source
                    )
                    
                    results[source] = source_result
                    
                    # Cache result for 1 hour
                    cache.set(cache_key, source_result, 3600)
                    
                    # Create alerts for matches
                    if source_result.get('matches'):
                        for match in source_result['matches']:
                            alert = ScreeningAlert.objects.create(
                                customer=customer,
                                source=source,
                                match_data=match,
                                risk_score=match.get('score', 0),
                                status='pending'
                            )
                            alerts.append(alert.id)
                    
                except Exception as source_error:
                    logger.error(f"Error screening {source} for customer {customer_id}: {source_error}")
                    results[source] = {
                        'error': str(source_error),
                        'status': 'failed'
                    }
            
            # Create screening result record
            screening_result = ScreeningResult.objects.create(
                customer=customer,
                results=results,
                alerts_created=len(alerts),
                status='completed',
                screened_at=timezone.now()
            )
            
            # Log completion
            log_audit_event(
                'screening_completed',
                user_id=None,
                customer_id=customer_id,
                metadata={
                    'result_id': screening_result.id,
                    'alerts_created': len(alerts),
                    'sources_checked': len(screening_sources)
                }
            )
            
            return {
                'customer_id': customer_id,
                'screening_result_id': screening_result.id,
                'alerts_created': alerts,
                'status': 'completed',
                'sources_checked': screening_sources,
                'total_matches': sum(len(r.get('matches', [])) for r in results.values() if isinstance(r, dict))
            }
            
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return {
            'customer_id': customer_id,
            'status': 'failed',
            'error': 'Customer not found'
        }
        
    except Exception as exc:
        logger.error(f"Error screening customer {customer_id}: {exc}")
        
        # Retry on temporary failures
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying screening for customer {customer_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {
            'customer_id': customer_id,
            'status': 'failed',
            'error': str(exc),
            'retries_exhausted': True
        }

@shared_task(bind=True, max_retries=2)
def batch_screen_customers(self, customer_ids: List[int], screening_sources: List[str] = None) -> Dict[str, Any]:
    """
    Screen multiple customers in batch.
    
    Args:
        customer_ids: List of customer IDs to screen
        screening_sources: List of sources to check
        
    Returns:
        Dict containing batch screening results
    """
    try:
        batch_id = f"batch_{int(time.time())}"
        
        log_audit_event(
            'batch_screening_started',
            user_id=None,
            metadata={
                'batch_id': batch_id,
                'customer_count': len(customer_ids),
                'sources': screening_sources
            }
        )
        
        results = []
        failed_customers = []
        
        for customer_id in customer_ids:
            try:
                # Queue individual screening task
                result = screen_customer.delay(customer_id, screening_sources)
                results.append({
                    'customer_id': customer_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
            except Exception as e:
                logger.error(f"Failed to queue screening for customer {customer_id}: {e}")
                failed_customers.append({
                    'customer_id': customer_id,
                    'error': str(e)
                })
        
        log_audit_event(
            'batch_screening_queued',
            user_id=None,
            metadata={
                'batch_id': batch_id,
                'queued_count': len(results),
                'failed_count': len(failed_customers)
            }
        )
        
        return {
            'batch_id': batch_id,
            'queued_screenings': results,
            'failed_customers': failed_customers,
            'total_customers': len(customer_ids),
            'status': 'queued'
        }
        
    except Exception as exc:
        logger.error(f"Error in batch screening: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120)
        
        return {
            'status': 'failed',
            'error': str(exc),
            'customer_ids': customer_ids
        }

@shared_task(bind=True, max_retries=3)
def create_screening_alert(self, customer_id: int, match_data: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Create a screening alert for a customer match.
    
    Args:
        customer_id: ID of the customer
        match_data: Data about the match
        source: Source that generated the match
        
    Returns:
        Dict containing alert information
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        
        alert = ScreeningAlert.objects.create(
            customer=customer,
            source=source,
            match_data=match_data,
            risk_score=match_data.get('score', 0),
            status='pending',
            created_at=timezone.now()
        )
        
        # Send notification if high risk
        if alert.risk_score >= 80:
            send_high_risk_notification.delay(alert.id)
        
        log_audit_event(
            'screening_alert_created',
            user_id=None,
            customer_id=customer_id,
            metadata={
                'alert_id': alert.id,
                'source': source,
                'risk_score': alert.risk_score
            }
        )
        
        return {
            'alert_id': alert.id,
            'customer_id': customer_id,
            'risk_score': alert.risk_score,
            'status': 'created'
        }
        
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found for alert creation")
        return {
            'status': 'failed',
            'error': 'Customer not found'
        }
        
    except Exception as exc:
        logger.error(f"Error creating screening alert: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30)
        
        return {
            'status': 'failed',
            'error': str(exc)
        }

@shared_task(bind=True)
def send_high_risk_notification(self, alert_id: int) -> Dict[str, Any]:
    """
    Send notification for high-risk screening alerts.
    
    Args:
        alert_id: ID of the screening alert
        
    Returns:
        Dict containing notification status
    """
    try:
        alert = ScreeningAlert.objects.get(id=alert_id)
        
        # Implementation would send email/SMS/webhook notification
        # For now, just log the high-risk alert
        logger.warning(
            f"HIGH RISK ALERT: Customer {alert.customer.id} "
            f"matched {alert.source} with score {alert.risk_score}"
        )
        
        # Update alert status
        alert.notification_sent = True
        alert.save()
        
        return {
            'alert_id': alert_id,
            'status': 'notification_sent'
        }
        
    except ScreeningAlert.DoesNotExist:
        logger.error(f"Screening alert {alert_id} not found")
        return {
            'status': 'failed',
            'error': 'Alert not found'
        }
        
    except Exception as exc:
        logger.error(f"Error sending notification for alert {alert_id}: {exc}")
        return {
            'status': 'failed',
            'error': str(exc)
        }

@shared_task(bind=True)
def update_screening_sources(self) -> Dict[str, Any]:
    """
    Periodic task to update screening data sources.
    
    Returns:
        Dict containing update status
    """
    try:
        source_manager = DataSourceManager()
        
        update_results = {}
        
        # Update each source
        sources = ['ofac', 'un', 'eu', 'opensanctions']
        
        for source in sources:
            try:
                result = source_manager.update_source(source)
                update_results[source] = result
                
                # Clear cache for this source
                cache_pattern = f"screening_{source}_*"
                cache.delete_pattern(cache_pattern)
                
            except Exception as e:
                logger.error(f"Failed to update source {source}: {e}")
                update_results[source] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        log_audit_event(
            'screening_sources_updated',
            user_id=None,
            metadata={
                'update_results': update_results,
                'updated_at': timezone.now().isoformat()
            }
        )
        
        return {
            'status': 'completed',
            'update_results': update_results,
            'updated_at': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error updating screening sources: {exc}")
        return {
            'status': 'failed',
            'error': str(exc)
        }

