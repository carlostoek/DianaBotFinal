"""
Achievement Service for DianaBot
Handles achievement unlocking, progress tracking, and rewards
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Achievement, UserAchievement, User, UserBalance, Item, UserInventory
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievements and user achievement progress"""
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    def check_achievement_unlock(self, user_id: int, achievement_key: str) -> bool:
        """
        Check if a user can unlock an achievement
        
        Args:
            user_id: User ID
            achievement_key: Achievement identifier
            
        Returns:
            bool: True if achievement can be unlocked
        """
        try:
            # Get achievement
            achievement = self.db.query(Achievement).filter(
                Achievement.achievement_key == achievement_key
            ).first()
            
            if not achievement:
                logger.error(f"Achievement {achievement_key} not found")
                return False
            
            # Check if user already has this achievement
            existing = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            
            if existing:
                logger.info(f"User {user_id} already has achievement {achievement_key}")
                return False
            
            # Check unlock conditions
            user_progress = self._get_user_progress(user_id)
            can_unlock = self._check_conditions(achievement.unlock_conditions, user_progress)
            
            if can_unlock:
                return self.unlock_achievement(user_id, achievement_key)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check achievement unlock for user {user_id}: {e}")
            return False
    
    def unlock_achievement(self, user_id: int, achievement_key: str) -> bool:
        """
        Unlock an achievement for a user
        
        Args:
            user_id: User ID
            achievement_key: Achievement identifier
            
        Returns:
            bool: True if achievement was unlocked successfully
        """
        try:
            # Get achievement
            achievement = self.db.query(Achievement).filter(
                Achievement.achievement_key == achievement_key
            ).first()
            
            if not achievement:
                logger.error(f"Achievement {achievement_key} not found")
                return False
            
            # Check if user already has this achievement
            existing = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            
            if existing:
                logger.info(f"User {user_id} already has achievement {achievement_key}")
                return True
            
            # Create user achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id
            )
            
            self.db.add(user_achievement)
            
            # Award rewards
            self._award_rewards(user_id, achievement)
            
            self.db.commit()
            
            # Publish event
            event_bus.publish("gamification.achievement_unlocked", {
                "user_id": user_id,
                "achievement_id": achievement.id,
                "achievement_key": achievement_key,
                "achievement_name": achievement.name,
                "rewards": {
                    "besitos": achievement.reward_besitos,
                    "item_id": achievement.reward_item_id
                }
            })
            
            logger.info(f"Achievement {achievement_key} unlocked by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unlock achievement {achievement_key} for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get unlocked achievements for a user
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of unlocked achievements
        """
        try:
            user_achievements = self.db.query(UserAchievement, Achievement).join(
                Achievement, UserAchievement.achievement_id == Achievement.id
            ).filter(
                UserAchievement.user_id == user_id
            ).all()
            
            result = []
            for user_achievement, achievement in user_achievements:
                achievement_data = achievement.to_dict()
                achievement_data["unlocked_at"] = user_achievement.unlocked_at
                achievement_data["progress"] = user_achievement.progress or {}
                result.append(achievement_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get achievements for user {user_id}: {e}")
            return []
    
    def get_achievement_progress(self, user_id: int, achievement_key: str) -> Dict[str, Any]:
        """
        Get progress for a specific achievement
        
        Args:
            user_id: User ID
            achievement_key: Achievement identifier
            
        Returns:
            dict: Progress information
        """
        try:
            achievement = self.db.query(Achievement).filter(
                Achievement.achievement_key == achievement_key
            ).first()
            
            if not achievement:
                return {"error": "Achievement not found"}
            
            # Check if already unlocked
            user_achievement = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            
            if user_achievement:
                return {
                    "unlocked": True,
                    "unlocked_at": user_achievement.unlocked_at,
                    "progress": user_achievement.progress or {}
                }
            
            # Calculate current progress
            user_progress = self._get_user_progress(user_id)
            conditions = achievement.unlock_conditions
            
            progress_data = {}
            for condition_key, target_value in conditions.items():
                current_value = user_progress.get(condition_key, 0)
                progress_data[condition_key] = {
                    "current": current_value,
                    "target": target_value,
                    "percentage": min(100, int((current_value / target_value) * 100)) if target_value > 0 else 100
                }
            
            return {
                "unlocked": False,
                "progress": progress_data,
                "achievement": achievement.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get achievement progress for user {user_id}: {e}")
            return {"error": str(e)}
    
    def get_available_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get achievements available for a user (not yet unlocked)
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of available achievements
        """
        try:
            # Get unlocked achievement IDs
            unlocked_achievement_ids = [ua.achievement_id for ua in self.db.query(UserAchievement.achievement_id).filter(
                UserAchievement.user_id == user_id
            ).all()]
            
            # Get all achievements
            all_achievements = self.db.query(Achievement).all()
            
            # Filter out unlocked achievements
            available_achievements = [a for a in all_achievements if a.id not in unlocked_achievement_ids]
            
            return [achievement.to_dict() for achievement in available_achievements]
            
        except Exception as e:
            logger.error(f"Failed to get available achievements for user {user_id}: {e}")
            return []
    
    def check_all_achievements(self, user_id: int) -> List[str]:
        """
        Check all achievements for a user and unlock any that are ready
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of achievement keys that were unlocked
        """
        try:
            unlocked_achievements = []
            
            # Get all achievements
            all_achievements = self.db.query(Achievement).all()
            
            for achievement in all_achievements:
                if self.check_achievement_unlock(user_id, achievement.achievement_key):
                    unlocked_achievements.append(achievement.achievement_key)
            
            logger.info(f"Checked all achievements for user {user_id}, unlocked {len(unlocked_achievements)}")
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Failed to check all achievements for user {user_id}: {e}")
            return []
    
    def _get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user progress data for achievement checking"""
        progress = {}
        
        try:
            # Get user stats
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                progress["total_messages"] = user.total_messages or 0
                progress["total_commands"] = user.total_commands or 0
                progress["total_stories_started"] = user.total_stories_started or 0
            
            # Get besitos stats
            balance = self.db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
            if balance:
                progress["besitos"] = balance.besitos or 0
                progress["lifetime_besitos"] = balance.lifetime_besitos or 0
            
            # Get inventory stats
            inventory_count = self.db.query(UserInventory).filter(UserInventory.user_id == user_id).count()
            progress["items_owned"] = inventory_count
            
            # Get narrative progress
            from database.models import UserNarrativeProgress, NarrativeFragment
            completed_fragments = self.db.query(UserNarrativeProgress).filter(
                UserNarrativeProgress.user_id == user_id
            ).count()
            progress["fragments_completed"] = completed_fragments
            
            # Estimate narrative level based on completed fragments
            if completed_fragments >= 10:
                progress["narrative_level"] = 3
            elif completed_fragments >= 5:
                progress["narrative_level"] = 2
            elif completed_fragments >= 1:
                progress["narrative_level"] = 1
            else:
                progress["narrative_level"] = 0
            
            # Get mission stats
            from database.models import UserMission, Mission
            completed_missions = self.db.query(UserMission).filter(
                UserMission.user_id == user_id,
                UserMission.status == "completed"
            ).count()
            progress["missions_completed"] = completed_missions
            
            # Get daily missions completed
            daily_missions_completed = self.db.query(UserMission).join(
                Mission, UserMission.mission_id == Mission.id
            ).filter(
                UserMission.user_id == user_id,
                UserMission.status == "completed",
                Mission.mission_type == "daily"
            ).count()
            progress["daily_missions_completed"] = daily_missions_completed
            
        except Exception as e:
            logger.error(f"Error getting user progress for achievements: {e}")
        
        return progress
    
    def _check_conditions(self, conditions: Dict[str, Any], user_progress: Dict[str, Any]) -> bool:
        """Check if user progress meets achievement conditions"""
        for condition_key, target_value in conditions.items():
            current_value = user_progress.get(condition_key, 0)
            # Handle SQLAlchemy Column objects
            if hasattr(target_value, 'scalar'):
                target = target_value.scalar()
            else:
                target = target_value
            if current_value < target:
                return False
        return True
    
    def _award_rewards(self, user_id: int, achievement: Achievement) -> None:
        """Award rewards for unlocking an achievement"""
        try:
            # Award besitos
            if achievement.reward_besitos and achievement.reward_besitos > 0:
                self._award_besitos(user_id, achievement.reward_besitos)
            
            # Award item
            if achievement.reward_item_id:
                self._award_item(user_id, achievement.reward_item_id)
            
        except Exception as e:
            logger.error(f"Failed to award rewards for achievement {achievement.achievement_key}: {e}")
    
    def _award_besitos(self, user_id: int, amount: int) -> None:
        """Award besitos to user"""
        user_balance = self.db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        
        if user_balance:
            # Get current values and add amount
            current_besitos = user_balance.besitos or 0
            current_lifetime = user_balance.lifetime_besitos or 0
            user_balance.besitos = current_besitos + amount
            user_balance.lifetime_besitos = current_lifetime + amount
        else:
            user_balance = UserBalance(
                user_id=user_id,
                besitos=amount,
                lifetime_besitos=amount
            )
            self.db.add(user_balance)
    
    def _award_item(self, user_id: int, item_id: int) -> None:
        """Award item to user"""
        # Check if user already has this item
        existing_inventory = self.db.query(UserInventory).filter(
            UserInventory.user_id == user_id,
            UserInventory.item_id == item_id
        ).first()
        
        if existing_inventory:
            # Get current quantity and add 1
            current_quantity = existing_inventory.quantity or 0
            existing_inventory.quantity = current_quantity + 1
        else:
            inventory = UserInventory(
                user_id=user_id,
                item_id=item_id,
                quantity=1
            )
            self.db.add(inventory)


# Global achievement service instance
achievement_service = AchievementService()