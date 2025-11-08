"""
Test script for Cache Manager functionality
"""
import time
from utils.cache_manager import CacheManager, cached, cache_invalidate


def test_basic_cache_operations():
    """Test basic cache operations"""
    print("Testing basic cache operations...")
    
    cache = CacheManager()
    
    # Test set and get
    cache.set("test_key", "test_value")
    result = cache.get("test_key")
    assert result == "test_value", f"Expected 'test_value', got {result}"
    print("✓ Basic set/get operations work")
    
    # Test cache miss
    result = cache.get("non_existent_key")
    assert result is None, f"Expected None for non-existent key, got {result}"
    print("✓ Cache miss handling works")
    
    # Test delete
    cache.delete("test_key")
    result = cache.get("test_key")
    assert result is None, f"Expected None after delete, got {result}"
    print("✓ Delete operation works")
    
    # Test pattern invalidation
    cache.set("user:123:profile", "profile_data")
    cache.set("user:123:settings", "settings_data")
    cache.set("user:456:profile", "other_profile")
    
    deleted_count = cache.invalidate_pattern("user:123:")
    assert deleted_count == 2, f"Expected 2 deletions, got {deleted_count}"
    assert cache.get("user:123:profile") is None
    assert cache.get("user:123:settings") is None
    assert cache.get("user:456:profile") == "other_profile"
    print("✓ Pattern invalidation works")
    
    print("All basic cache operations passed!")


def test_cache_stats():
    """Test cache statistics"""
    print("\nTesting cache statistics...")
    
    cache = CacheManager()
    
    # Generate some cache activity
    cache.get("miss1")  # miss
    cache.set("hit1", "value1")
    cache.get("hit1")  # hit
    cache.get("hit1")  # hit
    cache.get("miss2")  # miss
    
    stats = cache.get_stats()
    
    assert stats["cache_hits"] == 2, f"Expected 2 hits, got {stats['cache_hits']}"
    assert stats["cache_misses"] == 2, f"Expected 2 misses, got {stats['cache_misses']}"
    assert stats["total_requests"] == 4, f"Expected 4 total requests, got {stats['total_requests']}"
    assert stats["hit_rate_percent"] == 50.0, f"Expected 50% hit rate, got {stats['hit_rate_percent']}"
    
    print("✓ Cache statistics tracking works")
    
    # Test clearing stats
    cache.clear_stats()
    stats = cache.get_stats()
    assert stats["cache_hits"] == 0, f"Expected 0 hits after clear, got {stats['cache_hits']}"
    assert stats["cache_misses"] == 0, f"Expected 0 misses after clear, got {stats['cache_misses']}"
    print("✓ Stats clearing works")


def expensive_function(x):
    """Simulate an expensive function"""
    time.sleep(0.1)  # Simulate computation time
    return x * 2


def test_cached_decorator():
    """Test @cached decorator"""
    print("\nTesting @cached decorator...")
    
    # Create isolated cache instance for this test
    isolated_cache = CacheManager()
    
    @cached(ttl=60, cache_instance=isolated_cache)
    def cached_expensive_function(x):
        return expensive_function(x)
    
    # First call should be slow
    start_time = time.time()
    result1 = cached_expensive_function(5)
    first_call_time = time.time() - start_time
    
    # Second call should be fast (cached)
    start_time = time.time()
    result2 = cached_expensive_function(5)
    second_call_time = time.time() - start_time
    
    assert result1 == 10, f"Expected 10, got {result1}"
    assert result2 == 10, f"Expected 10, got {result2}"
    
    # Second call should be significantly faster
    assert second_call_time < first_call_time * 0.5, \
        f"Cached call not faster: {second_call_time:.3f}s vs {first_call_time:.3f}s"
    
    print("✓ @cached decorator works (performance improvement verified)")


def test_cache_invalidate_decorator():
    """Test @cache_invalidate decorator"""
    print("\nTesting @cache_invalidate decorator...")
    
    # Create isolated cache instance for this test
    isolated_cache = CacheManager()
    
    # Set up some cached data
    isolated_cache.set("user:123:profile", "old_profile")
    isolated_cache.set("user:123:settings", "old_settings")
    
    @cache_invalidate("user:123:", cache_instance=isolated_cache)
    def update_user_data():
        return "data_updated"
    
    # Call function that should invalidate cache
    result = update_user_data()
    assert result == "data_updated"
    
    # Verify cache was invalidated
    assert isolated_cache.get("user:123:profile") is None
    assert isolated_cache.get("user:123:settings") is None
    
    print("✓ @cache_invalidate decorator works")


def test_integration_with_database_patterns():
    """Test cache patterns that would be used with database queries"""
    print("\nTesting database query patterns...")
    
    cache = CacheManager()
    
    # Simulate database query patterns
    queries = [
        "user_profile:123",
        "user_balance:123", 
        "narrative_progress:123",
        "shop_items:all",
        "achievements:123"
    ]
    
    for query in queries:
        cache.set(query, f"result_for_{query}")
    
    # Test individual cache hits
    for query in queries:
        result = cache.get(query)
        assert result == f"result_for_{query}", f"Cache miss for {query}"
    
    # Test pattern invalidation for user data
    deleted = cache.invalidate_pattern("user_")
    assert deleted == 2, f"Expected 2 user-related entries deleted, got {deleted}"
    
    # Verify only user_ prefixed entries were deleted
    assert cache.get("user_profile:123") is None
    assert cache.get("user_balance:123") is None
    assert cache.get("narrative_progress:123") == "result_for_narrative_progress:123"
    assert cache.get("shop_items:all") == "result_for_shop_items:all"
    assert cache.get("achievements:123") == "result_for_achievements:123"
    
    print("✓ Database query patterns work correctly")


def main():
    """Run all cache manager tests"""
    print("="*50)
    print("CACHE MANAGER TEST SUITE")
    print("="*50)
    
    try:
        test_basic_cache_operations()
        test_cache_stats()
        test_cached_decorator()
        test_cache_invalidate_decorator()
        test_integration_with_database_patterns()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("Cache Manager is ready for production use")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise


if __name__ == "__main__":
    main()