"""
Core monitoring and performance tracking utilities.
"""

import time
import logging
import psutil
from contextlib import contextmanager
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

@contextmanager
def track_performance(operation_name: str):
    """
    Context manager to track performance of operations.
    
    Args:
        operation_name: Name of the operation being tracked
    """
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - start_time
        memory_delta = end_memory - start_memory
        
        # Log performance metrics
        logger.info(
            f"Performance: {operation_name} completed in {duration:.2f}s, "
            f"memory delta: {memory_delta:.2f}MB"
        )
        
        # Store metrics in cache for monitoring
        metrics_key = f"performance_{operation_name}_{int(time.time())}"
        cache.set(metrics_key, {
            'operation': operation_name,
            'duration': duration,
            'memory_delta': memory_delta,
            'timestamp': timezone.now().isoformat()
        }, 3600)  # Keep for 1 hour

def log_audit_event(event_type: str, user_id: Optional[int] = None, 
                   customer_id: Optional[int] = None, metadata: Dict[str, Any] = None):
    """
    Log audit events for compliance and monitoring.
    
    Args:
        event_type: Type of event being logged
        user_id: ID of the user performing the action (optional)
        customer_id: ID of the customer involved (optional)
        metadata: Additional event metadata
    """
    audit_data = {
        'event_type': event_type,
        'timestamp': timezone.now().isoformat(),
        'user_id': user_id,
        'customer_id': customer_id,
        'metadata': metadata or {}
    }
    
    # Log to structured logger
    logger.info(f"AUDIT: {event_type}", extra=audit_data)
    
    # Store in cache for recent events dashboard
    audit_key = f"audit_{int(time.time())}_{event_type}"
    cache.set(audit_key, audit_data, 86400)  # Keep for 24 hours

def get_system_health() -> Dict[str, Any]:
    """
    Get current system health metrics.
    
    Returns:
        Dict containing system health information
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / 1024 / 1024 / 1024  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free = disk.free / 1024 / 1024 / 1024  # GB
        
        # Load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = [0, 0, 0]  # Windows fallback
        
        health_status = 'healthy'
        
        # Determine health status
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            health_status = 'critical'
        elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
            health_status = 'warning'
        
        return {
            'status': health_status,
            'timestamp': timezone.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'load_avg': load_avg
            },
            'memory': {
                'percent': memory_percent,
                'available_gb': round(memory_available, 2)
            },
            'disk': {
                'percent': disk_percent,
                'free_gb': round(disk_free, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

