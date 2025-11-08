"""
Cache Manager for database query optimization
Provides intelligent caching with TTL, invalidation, and performance monitoring
"""
import json
import logging
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class CacheManager:
    """Intelligent cache manager for database query optimization"""
    
    def __init__(self):
        self.default_ttl = 300  # 5 minutes default
        self.cache_hits = 0
        self.cache_misses = 0
        self._cache = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key in self._cache:
                value, expiration_time = self._cache[key]
                if time.time() < expiration_time:
                    self.cache_hits += 1
                    return value
                else:
                    # Expired, delete it and fall through to miss
                    del self._cache[key]

            self.cache_misses += 1
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            expiration_time = time.time() + ttl
            self._cache[key] = (value, expiration_time)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._cache)
        }
    
    def clear_stats(self) -> None:
        """Clear cache statistics"""
        self.cache_hits = 0
        self.cache_misses = 0


def cached(ttl: int = 300, key_prefix: str = "cache", cache_instance: Optional[CacheManager] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache instance or default to global cache_manager
            cache = cache_instance or cache_manager
            
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + json.dumps(kwargs, sort_keys=True))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_invalidate(pattern: str, cache_instance: Optional[CacheManager] = None):
    """Decorator for invalidating cache patterns"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache instance or default to global cache_manager
            cache = cache_instance or cache_manager
            
            # Execute function first
            result = func(*args, **kwargs)
            
            # Invalidate cache pattern
            cache.invalidate_pattern(pattern)
            
            return result
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = CacheManager()