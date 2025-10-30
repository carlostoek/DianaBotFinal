import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database.connection import get_db, get_redis
from database.models import User
from modules.gamification.besitos import besitos_service

logger = logging.getLogger(__name__)


class DailyRewardService:
    """Service for managing daily rewards using Redis for tracking"""
    
    def __init__(self):
        self.redis_client = get_redis()
    
    def can_claim_daily_reward(self, user_id: int) -> bool:
        """
        Check if user can claim daily reward
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if user can claim, False otherwise
        """
        last_claim_key = f"daily_reward:{user_id}:last_claim"
        
        try:
            last_claim_str = self.redis_client.get(last_claim_key)
            
            if not last_claim_str:
                return True
            
            last_claim = datetime.fromisoformat(last_claim_str)
            now = datetime.now()
            
            # Check if 24 hours have passed
            return (now - last_claim) >= timedelta(hours=24)
            
        except Exception as e:
            logger.error(f"Error checking daily reward eligibility for user {user_id}: {e}")
            return True  # Allow claim on error
    
    def claim_daily_reward(self, user_id: int) -> Optional[int]:
        """
        Claim daily reward for user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Amount of besitos granted, or None if failed
        """
        if not self.can_claim_daily_reward(user_id):
            return None
        
        db: Session = next(get_db())
        
        try:
            # Get user to verify existence
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found for daily reward")
                return None
            
            # Grant daily reward
            amount = 10  # Base daily reward
            success = besitos_service.grant_besitos(
                user_id=user_id,
                amount=amount,
                source="daily_reward",
                description="Recompensa diaria"
            )
            
            if success:
                # Record claim in Redis
                last_claim_key = f"daily_reward:{user_id}:last_claim"
                self.redis_client.set(
                    last_claim_key,
                    datetime.now().isoformat(),
                    ex=86400  # 24 hours expiration
                )
                
                logger.info(f"Daily reward claimed by user {user_id}: {amount} besitos")
                return amount
            else:
                logger.error(f"Failed to grant daily reward to user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error claiming daily reward for user {user_id}: {e}")
            return None
        finally:
            db.close()
    
    def get_next_claim_time(self, user_id: int) -> Optional[datetime]:
        """
        Get next available claim time for user
        
        Args:
            user_id: User ID
            
        Returns:
            datetime: Next claim time, or None if can claim now
        """
        last_claim_key = f"daily_reward:{user_id}:last_claim"
        
        try:
            last_claim_str = self.redis_client.get(last_claim_key)
            
            if not last_claim_str:
                return None
            
            last_claim = datetime.fromisoformat(last_claim_str)
            next_claim = last_claim + timedelta(hours=24)
            
            return next_claim
            
        except Exception as e:
            logger.error(f"Error getting next claim time for user {user_id}: {e}")
            return None


# Global service instance
daily_reward_service = DailyRewardService()