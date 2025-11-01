import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.connection import get_db, get_redis
from database.models import User
from modules.gamification.besitos import besitos_service

logger = logging.getLogger(__name__)


class DailyRewardService:
    """Service for managing daily rewards with streak tracking and progressive rewards"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.base_reward = 10
        self.streak_bonuses = {
            3: 5,   # +5 bonus for 3-day streak
            7: 10,  # +10 bonus for 7-day streak
            14: 15, # +15 bonus for 14-day streak
            30: 25  # +25 bonus for 30-day streak
        }
    
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
    
    def get_streak_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's current streak information
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with streak count, next bonus, and streak status
        """
        streak_key = f"daily_reward:{user_id}:streak"
        last_claim_key = f"daily_reward:{user_id}:last_claim"
        
        try:
            streak_count = int(self.redis_client.get(streak_key) or 0)
            last_claim_str = self.redis_client.get(last_claim_key)
            
            if not last_claim_str:
                return {
                    'streak_count': 0,
                    'next_bonus': None,
                    'is_active': False
                }
            
            last_claim = datetime.fromisoformat(last_claim_str)
            now = datetime.now()
            
            # Check if streak is broken (more than 48 hours since last claim)
            is_active = (now - last_claim) < timedelta(hours=48)
            
            if not is_active:
                streak_count = 0
                self.redis_client.set(streak_key, 0)
            
            # Find next streak bonus
            next_bonus = None
            for streak_days in sorted(self.streak_bonuses.keys()):
                if streak_count < streak_days:
                    next_bonus = {
                        'days_needed': streak_days - streak_count,
                        'bonus_amount': self.streak_bonuses[streak_days]
                    }
                    break
            
            return {
                'streak_count': streak_count,
                'next_bonus': next_bonus,
                'is_active': is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting streak info for user {user_id}: {e}")
            return {
                'streak_count': 0,
                'next_bonus': None,
                'is_active': False
            }
    
    def claim_daily_reward(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Claim daily reward for user with streak bonuses
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with reward details or None if failed
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
            
            # Get current streak info
            streak_info = self.get_streak_info(user_id)
            current_streak = streak_info['streak_count']
            
            # Calculate total reward
            base_amount = self.base_reward
            streak_bonus = 0
            
            # Check for streak bonus
            new_streak = current_streak + 1
            if new_streak in self.streak_bonuses:
                streak_bonus = self.streak_bonuses[new_streak]
            
            total_amount = base_amount + streak_bonus
            
            # Grant reward
            success = besitos_service.grant_besitos(
                user_id=user_id,
                amount=total_amount,
                source="daily_reward",
                description=f"Recompensa diaria (racha: {new_streak} días)"
            )
            
            if success:
                # Update streak and last claim
                now = datetime.now()
                
                last_claim_key = f"daily_reward:{user_id}:last_claim"
                streak_key = f"daily_reward:{user_id}:streak"
                
                self.redis_client.set(
                    last_claim_key,
                    now.isoformat(),
                    ex=86400  # 24 hours expiration
                )
                
                self.redis_client.set(
                    streak_key,
                    new_streak,
                    ex=172800  # 48 hours expiration (streak breaks after 2 days)
                )
                
                logger.info(f"Daily reward claimed by user {user_id}: {total_amount} besitos (streak: {new_streak})")
                
                return {
                    'base_amount': base_amount,
                    'streak_bonus': streak_bonus,
                    'total_amount': total_amount,
                    'new_streak': new_streak,
                    'next_streak_bonus': self._get_next_streak_bonus(new_streak)
                }
            else:
                logger.error(f"Failed to grant daily reward to user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error claiming daily reward for user {user_id}: {e}")
            return None
        finally:
            db.close()
    
    def _get_next_streak_bonus(self, current_streak: int) -> Optional[Dict[str, Any]]:
        """Get information about the next streak bonus"""
        for streak_days in sorted(self.streak_bonuses.keys()):
            if current_streak < streak_days:
                return {
                    'days_needed': streak_days - current_streak,
                    'bonus_amount': self.streak_bonuses[streak_days]
                }
        return None
    
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