"""
Advanced Caching System for CERES
Implements distributed Redis caching with intelligent invalidation
"""
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import redis
from functools import wraps
import asyncio

logger = logging.getLogger('ceres.cache')

class CacheManager:
    """
    Advanced cache manager with intelligent invalidation and distributed support
    """
    
    # Cache key prefixes
    PREFIXES = {
        'screening_result': 'screening:result:',
        'screening_source': 'screening:source:',
        'customer_data': 'customer:data:',
        'document_ocr': 'document:ocr:',
        'risk_assessment': 'risk:assessment:',
        'api_response': 'api:response:',
        'user_session': 'user:session:',
        'statistics': 'stats:',
    }
    
    # Default TTL values (in seconds)
    DEFAULT_TTL = {
        'screening_result': 86400,      # 24 hours
        'screening_source': 3600,       # 1 hour
        'customer_data': 1800,          # 30 minutes
        'document_ocr': 7200,           # 2 hours
        'risk_assessment': 3600,        # 1 hour
        'api_response': 300,            # 5 minutes
        'user_session': 1800,           # 30 minutes
        'statistics': 600,              # 10 minutes
    }
    
    def __init__(self):
        self.redis_client = self._get_redis_client()
    
    def _get_redis_client(self) -> redis.Redis:
        """Get Redis client instance"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def _generate_cache_key(self, prefix: str, identifier: str, **kwargs) -> str:
        """Generate cache key with optional parameters"""
        key_parts = [self.PREFIXES.get(prefix, prefix), identifier]
        
        # Add additional parameters to key
        if kwargs:
            params_str = json.dumps(kwargs, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(params_hash)
        
        return ''.join(key_parts)
    
    def set(self, prefix: str, identifier: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Set cache value with intelligent TTL
        
        Args:
            prefix: Cache prefix type
            identifier: Unique identifier
            value: Value to cache
            ttl: Time to live in seconds (None for default)
            **kwargs: Additional parameters for key generation
            
        Returns:
            bool: Success status
        """
        try:
            cache_key = self._generate_cache_key(prefix, identifier, **kwargs)
            
            if ttl is None:
                ttl = self.DEFAULT_TTL.get(prefix, 3600)
            
            # Serialize value
            serialized_value = json.dumps({
                'data': value,
                'timestamp': datetime.now().isoformat(),
                'ttl': ttl
            })
            
            # Set in Django cache (primary)
            cache.set(cache_key, serialized_value, ttl)
            
            # Set in Redis (backup/distributed)
            if self.redis_client:
                self.redis_client.setex(cache_key, ttl, serialized_value)
            
            logger.debug(f"Cached {cache_key} with TTL {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache for {prefix}:{identifier}: {e}")
            return False
    
    def get(self, prefix: str, identifier: str, **kwargs) -> Optional[Any]:
        """
        Get cache value with fallback to Redis
        
        Args:
            prefix: Cache prefix type
            identifier: Unique identifier
            **kwargs: Additional parameters for key generation
            
        Returns:
            Cached value or None if not found
        """
        try:
            cache_key = self._generate_cache_key(prefix, identifier, **kwargs)
            
            # Try Django cache first
            cached_value = cache.get(cache_key)
            
            # Fallback to Redis
            if cached_value is None and self.redis_client:
                cached_value = self.redis_client.get(cache_key)
            
            if cached_value:
                # Deserialize value
                data = json.loads(cached_value)
                return data.get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cache for {prefix}:{identifier}: {e}")
            return None
    
    def delete(self, prefix: str, identifier: str, **kwargs) -> bool:
        """
        Delete cache entry
        
        Args:
            prefix: Cache prefix type
            identifier: Unique identifier
            **kwargs: Additional parameters for key generation
            
        Returns:
            bool: Success status
        """
        try:
            cache_key = self._generate_cache_key(prefix, identifier, **kwargs)
            
            # Delete from Django cache
            cache.delete(cache_key)
            
            # Delete from Redis
            if self.redis_client:
                self.redis_client.delete(cache_key)
            
            logger.debug(f"Deleted cache key: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete cache for {prefix}:{identifier}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Redis pattern (e.g., "screening:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            deleted_count = 0
            
            if self.redis_client:
                # Get matching keys
                keys = self.redis_client.keys(pattern)
                
                if keys:
                    # Delete from Redis
                    deleted_count = self.redis_client.delete(*keys)
                    
                    # Delete from Django cache
                    for key in keys:
                        cache.delete(key)
            
            logger.info(f"Invalidated {deleted_count} cache entries matching pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate pattern {pattern}: {e}")
            return 0
    
    def get_cache_info(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Get cache statistics and information
        
        Args:
            prefix: Optional prefix to filter by
            
        Returns:
            Cache information dictionary
        """
        try:
            info = {
                'redis_connected': bool(self.redis_client),
                'total_keys': 0,
                'keys_by_prefix': {},
                'memory_usage': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.redis_client:
                # Get Redis info
                redis_info = self.redis_client.info()
                info['memory_usage'] = redis_info.get('used_memory', 0)
                
                # Count keys by prefix
                pattern = f"{prefix}*" if prefix else "*"
                keys = self.redis_client.keys(pattern)
                info['total_keys'] = len(keys)
                
                # Group by prefix
                for key in keys:
                    key_prefix = key.split(':')[0] + ':'
                    info['keys_by_prefix'][key_prefix] = info['keys_by_prefix'].get(key_prefix, 0) + 1
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {'error': str(e)}

# Global cache manager instance
cache_manager = CacheManager()

def cache_result(prefix: str, ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """
    Decorator for caching function results
    
    Args:
        prefix: Cache prefix type
        ttl: Time to live in seconds
        key_func: Function to generate cache key from arguments
        
    Usage:
        @cache_result('screening_result', ttl=3600)
        def screen_customer(customer_id, source):
            # Function implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__] + [str(arg) for arg in args]
                if kwargs:
                    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(prefix, cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(prefix, cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator

def cache_async_result(prefix: str, ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """
    Decorator for caching async function results
    
    Args:
        prefix: Cache prefix type
        ttl: Time to live in seconds
        key_func: Function to generate cache key from arguments
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__] + [str(arg) for arg in args]
                if kwargs:
                    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(prefix, cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(prefix, cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator

class CacheInvalidationManager:
    """
    Manages intelligent cache invalidation based on data changes
    """
    
    # Invalidation rules: when X changes, invalidate Y patterns
    INVALIDATION_RULES = {
        'customer_updated': ['customer:data:*', 'risk:assessment:*'],
        'document_processed': ['document:ocr:*', 'customer:data:*'],
        'screening_completed': ['screening:result:*', 'risk:assessment:*'],
        'source_updated': ['screening:source:*', 'screening:result:*'],
        'user_logout': ['user:session:*'],
    }
    
    @classmethod
    def invalidate_on_event(cls, event: str, entity_id: Optional[str] = None):
        """
        Invalidate cache based on event
        
        Args:
            event: Event type
            entity_id: Optional entity ID for targeted invalidation
        """
        try:
            patterns = cls.INVALIDATION_RULES.get(event, [])
            
            for pattern in patterns:
                # Add entity ID to pattern if provided
                if entity_id and '*' in pattern:
                    targeted_pattern = pattern.replace('*', f"{entity_id}*")
                    cache_manager.invalidate_pattern(targeted_pattern)
                else:
                    cache_manager.invalidate_pattern(pattern)
            
            logger.info(f"Cache invalidated for event: {event}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache for event {event}: {e}")

# Example usage functions
def cache_screening_result(customer_id: str, source: str, result: Dict[str, Any], ttl: int = 86400):
    """Cache screening result"""
    return cache_manager.set('screening_result', f"{customer_id}:{source}", result, ttl)

def get_cached_screening_result(customer_id: str, source: str) -> Optional[Dict[str, Any]]:
    """Get cached screening result"""
    return cache_manager.get('screening_result', f"{customer_id}:{source}")

def cache_document_ocr(document_id: str, ocr_data: Dict[str, Any], ttl: int = 7200):
    """Cache OCR result"""
    return cache_manager.set('document_ocr', document_id, ocr_data, ttl)

def get_cached_document_ocr(document_id: str) -> Optional[Dict[str, Any]]:
    """Get cached OCR result"""
    return cache_manager.get('document_ocr', document_id)

