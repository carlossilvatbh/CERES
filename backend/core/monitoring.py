"""
Health Check and Monitoring System for CERES
Provides comprehensive health checks and system monitoring
"""
import time
import logging
import psutil
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import asyncio

logger = logging.getLogger('ceres.monitoring')

class HealthCheckView(View):
    """
    Comprehensive health check endpoint for monitoring
    """
    
    def get(self, request):
        """Return system health status"""
        try:
            health_data = self.get_health_status()
            
            # Determine overall status
            overall_status = 'healthy'
            if any(check['status'] == 'critical' for check in health_data['checks'].values()):
                overall_status = 'critical'
            elif any(check['status'] == 'warning' for check in health_data['checks'].values()):
                overall_status = 'warning'
            
            health_data['overall_status'] = overall_status
            
            # Return appropriate HTTP status
            status_code = 200 if overall_status == 'healthy' else 503
            
            return JsonResponse(health_data, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JsonResponse({
                'overall_status': 'critical',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=503)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        checks = {}
        
        # Database health
        checks['database'] = self.check_database()
        
        # Cache health
        checks['cache'] = self.check_cache()
        
        # Redis health
        checks['redis'] = self.check_redis()
        
        # System resources
        checks['system'] = self.check_system_resources()
        
        # Application health
        checks['application'] = self.check_application()
        
        # External services
        checks['external_services'] = self.check_external_services()
        
        return {
            'service': 'CERES',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'uptime': self.get_uptime(),
            'checks': checks
        }
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            # Get connection info
            db_info = {
                'vendor': connection.vendor,
                'response_time_ms': round(response_time, 2),
                'queries_count': len(connection.queries),
            }
            
            # Determine status
            if response_time > 1000:  # > 1 second
                status = 'critical'
            elif response_time > 500:  # > 500ms
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'details': db_info,
                'message': f"Database responding in {response_time:.2f}ms"
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'details': {'error': str(e)},
                'message': 'Database connection failed'
            }
    
    def check_cache(self) -> Dict[str, Any]:
        """Check Django cache health"""
        try:
            start_time = time.time()
            
            # Test cache operations
            test_key = 'health_check_test'
            test_value = f'test_{int(time.time())}'
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if retrieved_value != test_value:
                raise Exception("Cache value mismatch")
            
            # Determine status
            if response_time > 100:  # > 100ms
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'details': {
                    'backend': cache.__class__.__name__,
                    'response_time_ms': round(response_time, 2)
                },
                'message': f"Cache responding in {response_time:.2f}ms"
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'details': {'error': str(e)},
                'message': 'Cache operation failed'
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
            redis_client = redis.from_url(redis_url, decode_responses=True)
            
            start_time = time.time()
            
            # Test Redis operations
            test_key = 'health_check_redis'
            test_value = f'test_{int(time.time())}'
            
            redis_client.set(test_key, test_value, ex=60)
            retrieved_value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if retrieved_value != test_value:
                raise Exception("Redis value mismatch")
            
            # Get Redis info
            redis_info = redis_client.info()
            
            # Determine status
            if response_time > 100:  # > 100ms
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'details': {
                    'response_time_ms': round(response_time, 2),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory_human': redis_info.get('used_memory_human', 'unknown'),
                    'version': redis_info.get('redis_version', 'unknown')
                },
                'message': f"Redis responding in {response_time:.2f}ms"
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'details': {'error': str(e)},
                'message': 'Redis connection failed'
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Load average (Unix only)
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                load_avg = None
            
            details = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 2),
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
            
            if load_avg:
                details['load_average'] = load_avg
            
            # Determine status
            if cpu_percent > 90 or memory.percent > 90:
                status = 'critical'
            elif cpu_percent > 70 or memory.percent > 70:
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'details': details,
                'message': f"CPU: {cpu_percent}%, Memory: {memory.percent}%"
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'details': {'error': str(e)},
                'message': 'Could not retrieve system resources'
            }
    
    def check_application(self) -> Dict[str, Any]:
        """Check application-specific health"""
        try:
            from core.cache_manager import cache_manager
            from core.alerts import alert_manager
            
            details = {
                'cache_manager_active': bool(cache_manager),
                'alert_manager_active': bool(alert_manager),
                'active_alerts': len(alert_manager.active_alerts) if alert_manager else 0,
                'settings_environment': getattr(settings, 'DJANGO_ENVIRONMENT', 'unknown')
            }
            
            # Check if critical services are running
            critical_issues = []
            
            if not cache_manager:
                critical_issues.append('Cache manager not initialized')
            
            if not alert_manager:
                critical_issues.append('Alert manager not initialized')
            
            if critical_issues:
                status = 'warning'
                message = f"Issues found: {', '.join(critical_issues)}"
            else:
                status = 'healthy'
                message = "All application services running"
            
            return {
                'status': status,
                'details': details,
                'message': message
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'details': {'error': str(e)},
                'message': 'Application health check failed'
            }
    
    def check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity"""
        try:
            import aiohttp
            import asyncio
            
            async def check_services():
                services = {
                    'ofac': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
                    'un': 'https://scsanctions.un.org/resources/xml/en/consolidated.json',
                    'eu': 'https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList/content',
                    'opensanctions': 'https://api.opensanctions.org'
                }
                
                results = {}
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    for service_name, url in services.items():
                        try:
                            start_time = time.time()
                            async with session.head(url) as response:
                                response_time = (time.time() - start_time) * 1000
                                
                                if response.status < 400:
                                    status = 'healthy'
                                elif response.status < 500:
                                    status = 'warning'
                                else:
                                    status = 'critical'
                                
                                results[service_name] = {
                                    'status': status,
                                    'response_time_ms': round(response_time, 2),
                                    'http_status': response.status
                                }
                        except Exception as e:
                            results[service_name] = {
                                'status': 'critical',
                                'error': str(e)
                            }
                
                return results
            
            # Run async check
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            service_results = loop.run_until_complete(check_services())
            loop.close()
            
            # Determine overall external services status
            if any(result['status'] == 'critical' for result in service_results.values()):
                overall_status = 'warning'  # External services down shouldn't be critical
            else:
                overall_status = 'healthy'
            
            return {
                'status': overall_status,
                'details': service_results,
                'message': f"Checked {len(service_results)} external services"
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'details': {'error': str(e)},
                'message': 'External services check failed'
            }
    
    def get_uptime(self) -> str:
        """Get application uptime"""
        try:
            # This is a simple implementation
            # In production, you might want to store start time in a file or database
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
            
        except Exception:
            return "unknown"

class MetricsView(View):
    """
    Prometheus-compatible metrics endpoint
    """
    
    def get(self, request):
        """Return Prometheus metrics"""
        try:
            metrics = self.generate_metrics()
            return JsonResponse(metrics, content_type='text/plain')
            
        except Exception as e:
            logger.error(f"Metrics generation failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_metrics(self) -> Dict[str, Any]:
        """Generate Prometheus-style metrics"""
        from core.performance import perf_monitor
        
        metrics = {}
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics.update({
            'ceres_cpu_usage_percent': cpu_percent,
            'ceres_memory_usage_percent': memory.percent,
            'ceres_memory_available_bytes': memory.available,
        })
        
        # Database metrics
        metrics['ceres_database_queries_total'] = len(connection.queries)
        
        # Performance metrics
        for metric_name in perf_monitor.metrics.keys():
            summary = perf_monitor.get_metrics_summary(metric_name)
            if summary['count'] > 0:
                metrics[f'ceres_{metric_name}_count'] = summary['count']
                metrics[f'ceres_{metric_name}_avg_seconds'] = summary['avg']
                metrics[f'ceres_{metric_name}_max_seconds'] = summary['max']
        
        # Cache metrics
        try:
            from core.cache_manager import cache_manager
            cache_info = cache_manager.get_cache_info()
            metrics['ceres_cache_total_keys'] = cache_info.get('total_keys', 0)
        except Exception:
            pass
        
        # Alert metrics
        try:
            from core.alerts import alert_manager
            metrics['ceres_active_alerts_total'] = len(alert_manager.active_alerts)
        except Exception:
            pass
        
        return metrics

# URL patterns for health and metrics
from django.urls import path

monitoring_urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
]

