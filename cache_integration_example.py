"""
Cache Manager Integration Example
Shows how to integrate cache manager with database queries
"""
import time
from utils.cache_manager import cached, cache_invalidate, cache_manager


class DatabaseService:
    """Example database service showing cache integration patterns"""
    
    @cached(ttl=300, key_prefix="user_profile")  # Cache for 5 minutes
    def get_user_profile(self, user_id: int):
        """Get user profile with caching"""
        print(f"[DB] Fetching user profile for {user_id}")
        time.sleep(0.1)  # Simulate database query
        return {
            "user_id": user_id,
            "name": f"User {user_id}",
            "balance": 100,
            "level": 5
        }
    
    @cached(ttl=600, key_prefix="user_balance")  # Cache for 10 minutes
    def get_user_balance(self, user_id: int):
        """Get user balance with caching"""
        print(f"[DB] Fetching balance for {user_id}")
        time.sleep(0.05)  # Simulate database query
        return {
            "user_id": user_id,
            "balance": 150,
            "currency": "besitos"
        }
    
    @cache_invalidate("user_profile:")
    def update_user_profile(self, user_id: int, new_data: dict):
        """Update user profile and invalidate cache"""
        print(f"[DB] Updating user profile for {user_id}")
        time.sleep(0.1)  # Simulate database update
        # Invalidate all user_profile cache entries
        return {"status": "updated", "user_id": user_id}
    
    @cache_invalidate("user_balance:")
    def update_user_balance(self, user_id: int, amount: int):
        """Update user balance and invalidate cache"""
        print(f"[DB] Updating balance for {user_id}")
        time.sleep(0.05)  # Simulate database update
        # Invalidate all user_balance cache entries
        return {"status": "updated", "user_id": user_id, "new_balance": amount}


def demonstrate_cache_performance():
    """Demonstrate cache performance improvements"""
    print("="*50)
    print("CACHE PERFORMANCE DEMONSTRATION")
    print("="*50)
    
    service = DatabaseService()
    
    # First call - should hit database
    print("\n1. First call (database hit):")
    start_time = time.time()
    profile1 = service.get_user_profile(123)
    first_call_time = time.time() - start_time
    print(f"   Result: {profile1}")
    print(f"   Time: {first_call_time:.3f}s")
    
    # Second call - should hit cache
    print("\n2. Second call (cache hit):")
    start_time = time.time()
    profile2 = service.get_user_profile(123)
    second_call_time = time.time() - start_time
    print(f"   Result: {profile2}")
    print(f"   Time: {second_call_time:.3f}s")
    
    # Performance improvement
    improvement = (first_call_time - second_call_time) / first_call_time * 100
    print(f"\n   Performance improvement: {improvement:.1f}% faster")
    
    # Test cache invalidation
    print("\n3. Cache invalidation test:")
    print("   Updating user profile...")
    service.update_user_profile(123, {"name": "Updated User"})
    
    # This should hit database again due to invalidation
    print("\n4. Call after invalidation (database hit again):")
    start_time = time.time()
    profile3 = service.get_user_profile(123)
    third_call_time = time.time() - start_time
    print(f"   Result: {profile3}")
    print(f"   Time: {third_call_time:.3f}s")
    
    print("\n" + "="*50)
    print("Cache statistics:")
    stats = cache_manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*50)


def demonstrate_concurrent_patterns():
    """Demonstrate patterns for concurrent access"""
    print("\n" + "="*50)
    print("CONCURRENT ACCESS PATTERNS")
    print("="*50)
    
    service = DatabaseService()
    
    # Simulate multiple users accessing same data
    print("\nSimulating 5 users accessing same profile:")
    for i in range(5):
        profile = service.get_user_profile(456)
        print(f"  User {i+1}: Got profile for user {profile['user_id']}")
    
    # Show cache statistics
    stats = cache_manager.get_stats()
    print(f"\nCache hits: {stats['cache_hits']}")
    print(f"Cache misses: {stats['cache_misses']}")
    print(f"Hit rate: {stats['hit_rate_percent']}%")


def main():
    """Run cache integration demonstration"""
    print("DianaBot Cache Manager Integration Demo")
    print("This demonstrates how to integrate caching with database queries")
    
    demonstrate_cache_performance()
    demonstrate_concurrent_patterns()
    
    print("\n✅ Cache integration demonstration completed!")
    print("The cache manager is ready to be integrated into DianaBot services.")


if __name__ == "__main__":
    main()