"""
Performance optimization utilities for CERES
"""
import time
import logging
from functools import wraps
from typing import Dict, Any, Optional
from django.db import connection
from django.core.cache import cache
import psutil
import threading
from collections import defaultdict

logger = logging.getLogger('ceres.performance')

class PerformanceMonitor:
    """
    Performance monitoring and optimization utilities
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        with self.lock:
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': time.time(),
                'tags': tags or {}
            })
    
    def get_metrics_summary(self, metric_name: str, window_seconds: int = 300) -> Dict[str, Any]:
        """Get summary statistics for a metric within time window"""
        with self.lock:
            current_time = time.time()
            recent_values = [
                m['value'] for m in self.metrics[metric_name]
                if current_time - m['timestamp'] <= window_seconds
            ]
            
            if not recent_values:
                return {'count': 0}
            
            return {
                'count': len(recent_values),
                'avg': sum(recent_values) / len(recent_values),
                'min': min(recent_values),
                'max': max(recent_values),
                'total': sum(recent_values)
            }

# Global performance monitor
perf_monitor = PerformanceMonitor()

def measure_time(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Decorator to measure function execution time
    
    Usage:
        @measure_time('screening_time')
        def screen_customer(customer_id):
            # Function implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                perf_monitor.record_metric(metric_name, execution_time, tags)
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        return wrapper
    return decorator

def measure_async_time(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Decorator to measure async function execution time
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                perf_monitor.record_metric(metric_name, execution_time, tags)
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        return wrapper
    return decorator

class DatabaseOptimizer:
    """
    Database query optimization utilities
    """
    
    @staticmethod
    def log_queries(func):
        """Decorator to log database queries for a function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_queries = len(connection.queries)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            query_count = len(connection.queries) - initial_queries
            
            logger.info(f"{func.__name__}: {query_count} queries in {execution_time:.3f}s")
            
            # Log slow queries
            for query in connection.queries[initial_queries:]:
                query_time = float(query['time'])
                if query_time > 0.1:  # Log queries slower than 100ms
                    logger.warning(f"Slow query ({query_time:.3f}s): {query['sql'][:200]}...")
            
            return result
        return wrapper
    
    @staticmethod
    def get_query_stats() -> Dict[str, Any]:
        """Get database query statistics"""
        return {
            'total_queries': len(connection.queries),
            'recent_queries': connection.queries[-10:] if connection.queries else [],
            'slow_queries': [
                q for q in connection.queries 
                if float(q['time']) > 0.1
            ][-5:]  # Last 5 slow queries
        }

class MemoryOptimizer:
    """
    Memory usage optimization utilities
    """
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
            'total': psutil.virtual_memory().total
        }
    
    @staticmethod
    def monitor_memory(threshold_percent: float = 80.0):
        """Decorator to monitor memory usage"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                initial_memory = MemoryOptimizer.get_memory_usage()
                
                result = func(*args, **kwargs)
                
                final_memory = MemoryOptimizer.get_memory_usage()
                memory_increase = final_memory['rss'] - initial_memory['rss']
                
                if final_memory['percent'] > threshold_percent:
                    logger.warning(
                        f"High memory usage after {func.__name__}: "
                        f"{final_memory['percent']:.1f}% "
                        f"(+{memory_increase / 1024 / 1024:.1f}MB)"
                    )
                
                return result
            return wrapper
        return decorator

class CacheOptimizer:
    """
    Cache optimization utilities
    """
    
    @staticmethod
    def warm_cache(cache_key: str, data_func: callable, ttl: int = 3600):
        """Warm cache with data from function"""
        try:
            if not cache.get(cache_key):
                data = data_func()
                cache.set(cache_key, data, ttl)
                logger.info(f"Cache warmed for key: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to warm cache for {cache_key}: {e}")
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # This would depend on the cache backend
            # For Redis, we could get more detailed stats
            return {
                'backend': cache.__class__.__name__,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}

class BatchProcessor:
    """
    Batch processing optimization utilities
    """
    
    @staticmethod
    def process_in_batches(items: list, batch_size: int, process_func: callable):
        """Process items in batches to optimize memory and performance"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = process_func(batch)
            results.extend(batch_results)
            
            # Log progress
            processed = min(i + batch_size, len(items))
            logger.info(f"Processed {processed}/{len(items)} items")
        
        return results
    
    @staticmethod
    async def process_in_batches_async(items: list, batch_size: int, process_func: callable):
        """Process items in batches asynchronously"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await process_func(batch)
            results.extend(batch_results)
            
            # Log progress
            processed = min(i + batch_size, len(items))
            logger.info(f"Processed {processed}/{len(items)} items")
        
        return results

# Utility functions for common optimizations
def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """Optimize Django queryset with select_related and prefetch_related"""
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset

def bulk_create_optimized(model_class, objects, batch_size=1000):
    """Optimized bulk create with batching"""
    created_objects = []
    
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        created_batch = model_class.objects.bulk_create(batch, ignore_conflicts=True)
        created_objects.extend(created_batch)
    
    return created_objects

def get_system_performance() -> Dict[str, Any]:
    """Get overall system performance metrics"""
    return {
        'memory': MemoryOptimizer.get_memory_usage(),
        'database': DatabaseOptimizer.get_query_stats(),
        'cache': CacheOptimizer.get_cache_stats(),
        'performance_metrics': {
            name: perf_monitor.get_metrics_summary(name)
            for name in perf_monitor.metrics.keys()
        },
        'timestamp': time.time()
    }

