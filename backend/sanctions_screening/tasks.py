"""
Celery tasks for sanctions screening
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import asyncio
import logging

from .models import ScreeningSource, ScreeningResult, ScreeningBatch, ScreeningAlert
from .data_sources import DataSourceManager
from customer_enrollment.models import Customer

logger = logging.getLogger('ceres')

@shared_task(bind=True, max_retries=3)
def screen_customer(self, customer_id, source_codes=None, force_refresh=False):
    """
    Screen a single customer against sanctions lists
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        
        # Get customer name for screening
        if hasattr(customer, 'personal_data') and customer.personal_data:
            query_name = customer.personal_data.full_name
        else:
            logger.warning(f"No personal data found for customer {customer_id}")
            return {
                'success': False,
                'error': 'No personal data available for screening'
            }
        
        # Check if recent screening exists and force_refresh is False
        if not force_refresh:
            recent_cutoff = timezone.now() - timezone.timedelta(hours=24)
            recent_results = ScreeningResult.objects.filter(
                customer=customer,
                created_at__gte=recent_cutoff
            )
            if recent_results.exists():
                logger.info(f"Recent screening results exist for customer {customer_id}")
                return {
                    'success': True,
                    'message': 'Recent screening results already exist',
                    'results_count': recent_results.count()
                }
        
        # Get sources to screen
        if source_codes:
            sources = ScreeningSource.objects.filter(
                code__in=source_codes,
                is_active=True,
                is_available=True
            )
        else:
            sources = ScreeningSource.objects.filter(
                is_active=True,
                is_available=True
            )
        
        # Perform screening
        results = asyncio.run(perform_screening_async(customer, query_name, sources))
        
        # Process results and create alerts
        high_risk_matches = 0
        for result in results:
            if result.confidence_score >= 90:
                high_risk_matches += 1
                create_screening_alert.delay(result.id)
        
        logger.info(f"Screening completed for customer {customer_id}: {len(results)} results, {high_risk_matches} high-risk matches")
        
        return {
            'success': True,
            'customer_id': str(customer_id),
            'results_count': len(results),
            'high_risk_matches': high_risk_matches
        }
        
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return {
            'success': False,
            'error': f'Customer {customer_id} not found'
        }
    except Exception as e:
        logger.error(f"Screening failed for customer {customer_id}: {e}")
        # Retry the task
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

@shared_task
def batch_screen_customers(batch_id):
    """
    Process a batch screening operation
    """
    try:
        batch = ScreeningBatch.objects.get(id=batch_id)
        
        # Update batch status
        batch.status = 'processing'
        batch.started_at = timezone.now()
        batch.save()
        
        customers = batch.customers.all()
        sources = batch.sources.all()
        source_codes = [source.code for source in sources]
        
        batch.total_customers = customers.count()
        batch.save()
        
        # Process each customer
        for customer in customers:
            try:
                result = screen_customer.delay(
                    str(customer.id),
                    source_codes=source_codes,
                    force_refresh=True
                )
                
                # Update progress
                batch.processed_customers += 1
                batch.save()
                
            except Exception as e:
                logger.error(f"Failed to screen customer {customer.id} in batch {batch_id}: {e}")
        
        # Complete batch
        batch.status = 'completed'
        batch.completed_at = timezone.now()
        batch.save()
        
        logger.info(f"Batch screening {batch_id} completed: {batch.processed_customers}/{batch.total_customers} customers processed")
        
    except ScreeningBatch.DoesNotExist:
        logger.error(f"Screening batch {batch_id} not found")
    except Exception as e:
        logger.error(f"Batch screening {batch_id} failed: {e}")
        # Update batch status to failed
        try:
            batch = ScreeningBatch.objects.get(id=batch_id)
            batch.status = 'failed'
            batch.save()
        except:
            pass

@shared_task
def create_screening_alert(screening_result_id):
    """
    Create an alert for a high-risk screening match
    """
    try:
        result = ScreeningResult.objects.get(id=screening_result_id)
        
        # Determine alert severity based on confidence score
        if result.confidence_score >= 95:
            severity = 'critical'
        elif result.confidence_score >= 90:
            severity = 'high'
        elif result.confidence_score >= 80:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Create alert
        alert = ScreeningAlert.objects.create(
            alert_type='high_risk_match',
            severity=severity,
            customer=result.customer,
            screening_result=result,
            source=result.source,
            title=f"High-risk match found: {result.matched_name}",
            message=f"Customer {result.query_name} matched {result.matched_name} in {result.source.name} with {result.confidence_score}% confidence.",
            alert_data={
                'confidence_score': float(result.confidence_score),
                'match_type': result.match_type,
                'entity_type': result.entity_type,
                'categories': result.categories,
                'sanctions_programs': result.sanctions_programs
            },
            requires_action=severity in ['critical', 'high']
        )
        
        logger.info(f"Alert created for screening result {screening_result_id}: {alert.id}")
        
        return {
            'success': True,
            'alert_id': str(alert.id),
            'severity': severity
        }
        
    except ScreeningResult.DoesNotExist:
        logger.error(f"Screening result {screening_result_id} not found")
        return {
            'success': False,
            'error': 'Screening result not found'
        }
    except Exception as e:
        logger.error(f"Failed to create alert for screening result {screening_result_id}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def update_screening_sources():
    """
    Update screening sources data (periodic task)
    """
    try:
        sources = ScreeningSource.objects.filter(is_active=True)
        updated_count = 0
        
        for source in sources:
            try:
                # Check if source is available
                # This would typically involve pinging the API or checking data freshness
                source.is_available = True
                source.last_updated = timezone.now()
                source.save()
                updated_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to update source {source.code}: {e}")
                source.is_available = False
                source.save()
        
        logger.info(f"Updated {updated_count} screening sources")
        
        return {
            'success': True,
            'updated_count': updated_count,
            'total_sources': sources.count()
        }
        
    except Exception as e:
        logger.error(f"Failed to update screening sources: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def perform_screening_async(customer, query_name, sources):
    """
    Perform asynchronous screening across multiple sources
    """
    results = []
    
    async with DataSourceManager() as data_manager:
        # Get source codes
        source_codes = [source.code for source in sources]
        
        # Perform screening
        screening_results = await data_manager.search_all_sources(
            query_name,
            source_types=['sanctions', 'pep', 'corporate']
        )
        
        # Process results and save to database
        for source_code, source_result in screening_results.items():
            try:
                source = sources.filter(code=source_code).first()
                if not source:
                    continue
                
                if source_result.get('success') and source_result.get('matches'):
                    for match in source_result['matches']:
                        # Create screening result
                        result = ScreeningResult.objects.create(
                            customer=customer,
                            source=source,
                            query_name=query_name,
                            match_found=True,
                            match_type='fuzzy',  # This would be determined by the matching algorithm
                            confidence_score=match.get('confidence', 0),
                            matched_name=match.get('name', ''),
                            matched_entity_id=match.get('entity_id', ''),
                            entity_type=match.get('entity_type', ''),
                            categories=match.get('categories', []),
                            sanctions_programs=match.get('programs', []),
                            match_details=match,
                            raw_response=source_result,
                            processing_time=source_result.get('processing_time', 0)
                        )
                        results.append(result)
                else:
                    # Create negative result
                    result = ScreeningResult.objects.create(
                        customer=customer,
                        source=source,
                        query_name=query_name,
                        match_found=False,
                        confidence_score=0,
                        raw_response=source_result,
                        processing_time=source_result.get('processing_time', 0)
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Failed to process screening result for source {source_code}: {e}")
    
    return results

