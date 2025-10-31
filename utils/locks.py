"""
Distributed locking system using Redis for preventing race conditions
"""
import time
import uuid
from typing import Optional
from functools import wraps
from database.connection import get_redis

class DistributedLock:
    """Distributed lock implementation using Redis"""
    
    def __init__(self):
        self.redis_client = get_redis()
    
    def acquire_lock(self, lock_name: str, timeout: int = 10, retry_delay: float = 0.1, max_retries: int = 10) -> Optional[str]:
        """
        Acquire a distributed lock
        
        Args:
            lock_name: Name of the lock
            timeout: Lock timeout in seconds
            retry_delay: Delay between retries in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Lock identifier if acquired, None if failed
        """
        lock_identifier = str(uuid.uuid4())
        
        for attempt in range(max_retries):
            # Try to acquire the lock
            acquired = self.redis_client.set(
                f"lock:{lock_name}",
                lock_identifier,
                nx=True,
                ex=timeout
            )
            
            if acquired:
                return lock_identifier
            
            # Wait before retrying
            time.sleep(retry_delay)
        
        return None
    
    def release_lock(self, lock_name: str, lock_identifier: str) -> bool:
        """
        Release a distributed lock
        
        Args:
            lock_name: Name of the lock
            lock_identifier: Lock identifier returned by acquire_lock
            
        Returns:
            True if lock was released, False otherwise
        """
        # Use Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis_client.eval(lua_script, 1, f"lock:{lock_name}", lock_identifier)
        return bool(result)
    
    def is_locked(self, lock_name: str) -> bool:
        """Check if a lock is currently held"""
        return bool(self.redis_client.exists(f"lock:{lock_name}"))


class AuctionLockManager:
    """Specialized lock manager for auction operations"""
    
    def __init__(self):
        self.lock = DistributedLock()
    
    def lock_auction_bid(self, auction_id: int, timeout: int = 5) -> Optional[str]:
        """Acquire lock for placing a bid on an auction"""
        return self.lock.acquire_lock(f"auction_bid:{auction_id}", timeout=timeout)
    
    def unlock_auction_bid(self, auction_id: int, lock_identifier: str) -> bool:
        """Release lock for auction bid"""
        return self.lock.release_lock(f"auction_bid:{auction_id}", lock_identifier)
    
    def lock_auction_close(self, auction_id: int, timeout: int = 10) -> Optional[str]:
        """Acquire lock for closing an auction"""
        return self.lock.acquire_lock(f"auction_close:{auction_id}", timeout=timeout)
    
    def unlock_auction_close(self, auction_id: int, lock_identifier: str) -> bool:
        """Release lock for auction close"""
        return self.lock.release_lock(f"auction_close:{auction_id}", lock_identifier)

def with_auction_lock(operation: str):
    """Decorator for acquiring auction locks during operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            lock_manager = get_lock_manager()
            
            # Determine auction_id from arguments
            auction_id = None
            if len(args) >= 2:
                auction_id = args[1]  # Second argument is typically auction_id
            elif len(args) == 1 and isinstance(args[0], int):
                auction_id = args[0]  # Single argument is auction_id
            elif 'auction_id' in kwargs:
                auction_id = kwargs['auction_id']
            
            if not auction_id:
                raise ValueError("Could not determine auction_id for lock")
            
            # Acquire appropriate lock
            if operation == "bid":
                lock_identifier = lock_manager.lock_auction_bid(auction_id)
            elif operation == "close":
                lock_identifier = lock_manager.lock_auction_close(auction_id)
            else:
                raise ValueError(f"Unknown lock operation: {operation}")
            
            if not lock_identifier:
                raise RuntimeError(f"Could not acquire {operation} lock for auction {auction_id}")
            
            try:
                return func(self, *args, **kwargs)
            finally:
                # Release lock
                if operation == "bid":
                    lock_manager.unlock_auction_bid(auction_id, lock_identifier)
                elif operation == "close":
                    lock_manager.unlock_auction_close(auction_id, lock_identifier)
        
        return wrapper
    return decorator


# Global lock manager instance
_lock_manager = None

def get_lock_manager() -> AuctionLockManager:
    """Get the global lock manager instance"""
    global _lock_manager
    
    if _lock_manager is None:
        _lock_manager = AuctionLockManager()
    
    return _lock_manager