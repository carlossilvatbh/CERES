"""
Health check views for monitoring and load balancer integration.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
import redis
import logging

from core.monitoring import get_system_health

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Comprehensive health check endpoint for load balancers and monitoring.
    
    Returns:
        JsonResponse with health status and system metrics
    """
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '2.0.0',
        'environment': 'production',
        'checks': {}
    }
    
    overall_status = 'healthy'
    
    # Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_data['checks']['database'] = {
            'status': 'healthy',
            'response_time_ms': 0  # Could measure actual response time
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # Redis connectivity check
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        if cache_result == 'ok':
            health_data['checks']['redis'] = {'status': 'healthy'}
        else:
            raise Exception("Cache test failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_data['checks']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # System resources check
    try:
        system_health = get_system_health()
        health_data['checks']['system'] = system_health
        
        if system_health['status'] in ['critical', 'error']:
            overall_status = 'unhealthy'
        elif system_health['status'] == 'warning' and overall_status == 'healthy':
            overall_status = 'degraded'
            
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        health_data['checks']['system'] = {
            'status': 'error',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # Celery worker check (if available)
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            health_data['checks']['celery'] = {
                'status': 'healthy',
                'active_workers': len(active_workers)
            }
        else:
            health_data['checks']['celery'] = {
                'status': 'warning',
                'message': 'No active workers found'
            }
            if overall_status == 'healthy':
                overall_status = 'degraded'
                
    except Exception as e:
        logger.warning(f"Celery health check failed: {e}")
        health_data['checks']['celery'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    health_data['status'] = overall_status
    
    # Return appropriate HTTP status code
    if overall_status == 'healthy':
        status_code = 200
    elif overall_status == 'degraded':
        status_code = 200  # Still operational
    else:
        status_code = 503  # Service unavailable
    
    return JsonResponse(health_data, status=status_code)

@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check for Kubernetes/container orchestration.
    
    Returns:
        JsonResponse indicating if the service is ready to accept traffic
    """
    try:
        # Check if database migrations are up to date
        from django.core.management import execute_from_command_line
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections
        
        executor = MigrationExecutor(connections['default'])
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            return JsonResponse({
                'status': 'not_ready',
                'reason': 'Pending database migrations',
                'timestamp': timezone.now().isoformat()
            }, status=503)
        
        # Check critical dependencies
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': timezone.now().isoformat()
        }, status=200)
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)

@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        JsonResponse indicating if the service is alive
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': timezone.now().isoformat()
    }, status=200)

