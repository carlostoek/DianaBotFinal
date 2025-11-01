"""
Mission Service for DianaBot
Handles mission assignment, progress tracking, and completion
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Mission, UserMission, User, UserBalance, Item, UserInventory
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class MissionService:
    """Service for managing missions and user mission progress"""
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    def assign_mission(self, user_id: int, mission_key: str) -> bool:
        """
        Assign a mission to a user
        
        Args:
            user_id: User ID
            mission_key: Mission identifier
            
        Returns:
            bool: True if mission was assigned successfully
        """
        try:
            # Get mission
            mission = self.db.query(Mission).filter(
                Mission.mission_key == mission_key,
                Mission.is_active == True
            ).first()
            
            if not mission:
                logger.error(f"Mission {mission_key} not found or inactive")
                return False
            
            # Check if user already has this mission
            existing = self.db.query(UserMission).filter(
                UserMission.user_id == user_id,
                UserMission.mission_id == mission.id
            ).first()
            
            if existing:
                logger.info(f"User {user_id} already has mission {mission_key}")
                return True
            
            # Create user mission
            user_mission = UserMission(
                user_id=user_id,
                mission_id=mission.id,
                status="active",
                progress={}
            )
            
            self.db.add(user_mission)
            self.db.commit()
            
            # Publish event
            event_bus.publish("gamification.mission_assigned", {
                "user_id": user_id,
                "mission_id": mission.id,
                "mission_key": mission_key,
                "mission_title": mission.title
            })
            
            logger.info(f"Mission {mission_key} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign mission {mission_key} to user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def update_mission_progress(self, user_id: int, mission_id: int, progress_data: Dict[str, Any]) -> bool:
        """
        Update progress for a user mission
        
        Args:
            user_id: User ID
            mission_id: Mission ID
            progress_data: Progress data to update
            
        Returns:
            bool: True if progress was updated successfully
        """
        try:
            user_mission = self.db.query(UserMission).filter(
                UserMission.user_id == user_id,
                UserMission.mission_id == mission_id,
                UserMission.status == "active"
            ).first()
            
            if not user_mission:
                logger.error(f"Active mission {mission_id} not found for user {user_id}")
                return False
            
            # Update progress
            current_progress = user_mission.progress or {}
            current_progress.update(progress_data)
            user_mission.progress = current_progress
            
            # Check if mission is completed
            mission = self.db.query(Mission).filter(Mission.id == mission_id).first()
            if mission and self._is_mission_completed(mission.requirements, current_progress):
                return self.complete_mission(user_id, mission_id)
            
            self.db.commit()
            
            # Publish event
            event_bus.publish("gamification.mission_progress_updated", {
                "user_id": user_id,
                "mission_id": mission_id,
                "progress": current_progress
            })
            
            logger.info(f"Progress updated for mission {mission_id} - user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update progress for mission {mission_id} - user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def complete_mission(self, user_id: int, mission_id: int) -> bool:
        """
        Complete a mission and award rewards
        
        Args:
            user_id: User ID
            mission_id: Mission ID
            
        Returns:
            bool: True if mission was completed successfully
        """
        try:
            user_mission = self.db.query(UserMission).filter(
                UserMission.user_id == user_id,
                UserMission.mission_id == mission_id
            ).first()
            
            if not user_mission:
                logger.error(f"Mission {mission_id} not found for user {user_id}")
                return False
            
            mission = self.db.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                logger.error(f"Mission {mission_id} not found")
                return False
            
            # Update mission status
            user_mission.status = "completed"
            user_mission.completed_at = datetime.now()
            
            # Award rewards
            self._award_rewards(user_id, mission.rewards)
            
            self.db.commit()
            
            # Publish event
            event_bus.publish("gamification.mission_completed", {
                "user_id": user_id,
                "mission_id": mission_id,
                "mission_key": mission.mission_key,
                "mission_title": mission.title,
                "rewards": mission.rewards
            })
            
            logger.info(f"Mission {mission_id} completed by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete mission {mission_id} for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def get_active_missions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get active missions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of active missions with progress
        """
        try:
            user_missions = self.db.query(UserMission, Mission).join(
                Mission, UserMission.mission_id == Mission.id
            ).filter(
                UserMission.user_id == user_id,
                UserMission.status == "active"
            ).all()
            
            result = []
            for user_mission, mission in user_missions:
                mission_data = mission.to_dict()
                mission_data["progress"] = user_mission.progress or {}
                mission_data["assigned_at"] = user_mission.assigned_at
                result.append(mission_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get active missions for user {user_id}: {e}")
            return []
    
    def get_available_missions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get missions available for a user (not yet assigned)
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of available missions
        """
        try:
            # Get missions that are active and not assigned to user
            assigned_mission_ids = [um.mission_id for um in self.db.query(UserMission.mission_id).filter(
                UserMission.user_id == user_id
            ).all()]
            
            available_missions = self.db.query(Mission).filter(
                Mission.is_active == True
            ).all()
            
            # Filter out assigned missions
            available_missions = [m for m in available_missions if m.id not in assigned_mission_ids]
            
            return [mission.to_dict() for mission in available_missions]
            
        except Exception as e:
            logger.error(f"Failed to get available missions for user {user_id}: {e}")
            return []
    
    def assign_daily_missions(self, user_id: int) -> bool:
        """
        Assign daily missions to a user
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if missions were assigned successfully
        """
        try:
            daily_missions = self.db.query(Mission).filter(
                Mission.mission_type == "daily",
                Mission.is_active == True
            ).all()
            
            success_count = 0
            for mission in daily_missions:
                if self.assign_mission(user_id, mission.mission_key):
                    success_count += 1
            
            logger.info(f"Assigned {success_count} daily missions to user {user_id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to assign daily missions to user {user_id}: {e}")
            return False
    
    def _is_mission_completed(self, requirements: Dict[str, Any], progress: Dict[str, Any]) -> bool:
        """
        Check if mission requirements are met
        
        Args:
            requirements: Mission requirements
            progress: Current progress
            
        Returns:
            bool: True if mission is completed
        """
        for requirement_key, target_value in requirements.items():
            current_value = progress.get(requirement_key, 0)
            if current_value < target_value:
                return False
        return True
    
    def _award_rewards(self, user_id: int, rewards: Dict[str, Any]) -> None:
        """
        Award rewards to user
        
        Args:
            user_id: User ID
            rewards: Rewards to award
        """
        try:
            # Award besitos
            if "besitos" in rewards:
                amount = rewards["besitos"]
                self._award_besitos(user_id, amount)
            
            # Award items
            if "items" in rewards:
                for item_key in rewards["items"]:
                    self._award_item(user_id, item_key)
            
        except Exception as e:
            logger.error(f"Failed to award rewards to user {user_id}: {e}")
    
    def _award_besitos(self, user_id: int, amount: int) -> None:
        """Award besitos to user"""
        user_balance = self.db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        
        if user_balance:
            user_balance.besitos += amount
            user_balance.lifetime_besitos += amount
        else:
            user_balance = UserBalance(
                user_id=user_id,
                besitos=amount,
                lifetime_besitos=amount
            )
            self.db.add(user_balance)
    
    def _award_item(self, user_id: int, item_key: str) -> None:
        """Award item to user"""
        item = self.db.query(Item).filter(Item.item_key == item_key).first()
        
        if item:
            # Check if user already has this item
            existing_inventory = self.db.query(UserInventory).filter(
                UserInventory.user_id == user_id,
                UserInventory.item_id == item.id
            ).first()
            
            if existing_inventory:
                existing_inventory.quantity += 1
            else:
                inventory = UserInventory(
                    user_id=user_id,
                    item_id=item.id,
                    quantity=1
                )
                self.db.add(inventory)


# Global mission service instance
mission_service = MissionService()