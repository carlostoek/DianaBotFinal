"""
Rate limiting utility for DianaBot
"""

import time
from typing import Optional
from database.connection import get_redis


class RateLimiter:
    """Rate limiter for preventing farming and abuse"""
    
    def __init__(self):
        self.redis = get_redis()
    
    def can_perform_action(
        self, 
        user_id: int, 
        action_key: str, 
        max_attempts: int, 
        time_window: int
    ) -> bool:
        """
        Check if user can perform an action within rate limits
        
        Args:
            user_id: User ID
            action_key: Action identifier (e.g., 'trivia', 'daily_reward')
            max_attempts: Maximum attempts allowed in time window
            time_window: Time window in seconds
            
        Returns:
            bool: True if action is allowed, False if rate limited
        """
        key = f"rate_limit:{action_key}:{user_id}"
        
        # Get current count
        current_count = self.redis.get(key)
        
        if current_count is None:
            # First attempt in this window
            self.redis.setex(key, time_window, 1)
            return True
        
        current_count = int(current_count)
        
        if current_count >= max_attempts:
            return False
        
        # Increment count
        self.redis.incr(key)
        return True
    
    def get_remaining_attempts(
        self, 
        user_id: int, 
        action_key: str, 
        max_attempts: int
    ) -> int:
        """
        Get remaining attempts for an action
        
        Args:
            user_id: User ID
            action_key: Action identifier
            max_attempts: Maximum attempts allowed
            
        Returns:
            int: Remaining attempts
        """
        key = f"rate_limit:{action_key}:{user_id}"
        current_count = self.redis.get(key)
        
        if current_count is None:
            return max_attempts
        
        current_count = int(current_count)
        return max(0, max_attempts - current_count)
    
    def get_time_until_reset(
        self, 
        user_id: int, 
        action_key: str
    ) -> Optional[int]:
        """
        Get time until rate limit resets
        
        Args:
            user_id: User ID
            action_key: Action identifier
            
        Returns:
            Optional[int]: Seconds until reset, or None if not rate limited
        """
        key = f"rate_limit:{action_key}:{user_id}"
        ttl = self.redis.ttl(key)
        
        if ttl > 0:
            return ttl
        return None
    
    def reset_rate_limit(
        self, 
        user_id: int, 
        action_key: str
    ) -> bool:
        """
        Reset rate limit for a user and action
        
        Args:
            user_id: User ID
            action_key: Action identifier
            
        Returns:
            bool: True if reset successful
        """
        key = f"rate_limit:{action_key}:{user_id}"
        return bool(self.redis.delete(key))


# Global rate limiter instance
rate_limiter = RateLimiter()


# Predefined rate limits for different actions
RATE_LIMITS = {
    "trivia_free": {
        "max_attempts": 10,
        "time_window": 86400,  # 24 hours
        "description": "Free users: 10 trivias per day"
    },
    "trivia_vip": {
        "max_attempts": 50,
        "time_window": 86400,  # 24 hours
        "description": "VIP users: 50 trivias per day"
    },
    "daily_reward": {
        "max_attempts": 1,
        "time_window": 86400,  # 24 hours
        "description": "Daily reward: once per day"
    },
    "mission_claim": {
        "max_attempts": 10,
        "time_window": 3600,  # 1 hour
        "description": "Mission claims: 10 per hour"
    },
    "channel_reaction": {
        "max_attempts": 50,
        "time_window": 3600,  # 1 hour
        "description": "Channel reactions: 50 per hour"
    }
}