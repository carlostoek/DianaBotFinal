"""
Narrative rewards system integration with besitos
"""

import logging
from typing import Dict, Any
from modules.gamification.besitos import BesitosService
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class NarrativeRewards:
    """Service for handling narrative rewards and besitos integration"""
    
    @staticmethod
    def handle_fragment_completion(event_data: Dict[str, Any]) -> None:
        """
        Handle narrative fragment completion and grant rewards
        
        Args:
            event_data: Event data from narrative.fragment_completed
        """
        try:
            user_id = event_data.get('user_id')
            fragment_key = event_data.get('fragment_key')
            
            if not user_id or not fragment_key:
                logger.error("Missing user_id or fragment_key in event data")
                return
            
            # Get fragment rewards configuration
            # TODO: Get from MongoDB narrative content
            rewards = NarrativeRewards._get_fragment_rewards(fragment_key)
            
            if not rewards:
                logger.debug(f"No rewards configured for fragment {fragment_key}")
                return
            
            # Grant besitos rewards
            besitos_amount = rewards.get('besitos', 0)
            if besitos_amount > 0:
                success = BesitosService.grant_besitos(
                    user_id=user_id,
                    amount=besitos_amount,
                    source='narrative_fragment',
                    description=f"Completaste el fragmento: {fragment_key}",
                    metadata={
                        'fragment_key': fragment_key,
                        'rewards': rewards
                    }
                )
                
                if success:
                    logger.info(f"Granted {besitos_amount} besitos to user {user_id} for fragment {fragment_key}")
                else:
                    logger.error(f"Failed to grant besitos to user {user_id} for fragment {fragment_key}")
            
            # Handle item rewards
            items = rewards.get('items', [])
            for item in items:
                # TODO: Integrate with inventory system
                logger.info(f"Would grant item {item} to user {user_id} for fragment {fragment_key}")
            
            # Handle achievement rewards
            achievements = rewards.get('achievements', [])
            for achievement in achievements:
                # TODO: Integrate with achievements system
                logger.info(f"Would grant achievement {achievement} to user {user_id} for fragment {fragment_key}")
            
        except Exception as e:
            logger.error(f"Failed to handle fragment completion rewards: {e}")
    
    @staticmethod
    def handle_decision_rewards(event_data: Dict[str, Any]) -> None:
        """
        Handle immediate rewards from narrative decisions
        
        Args:
            event_data: Event data from narrative.decision_made
        """
        try:
            user_id = event_data.get('user_id')
            fragment_key = event_data.get('fragment_key')
            decision_id = event_data.get('decision_id')
            
            if not user_id or not fragment_key or not decision_id:
                logger.error("Missing required data in decision event")
                return
            
            # Get decision rewards configuration
            # TODO: Get from MongoDB narrative content
            rewards = NarrativeRewards._get_decision_rewards(fragment_key, decision_id)
            
            if not rewards:
                logger.debug(f"No immediate rewards for decision {decision_id} in fragment {fragment_key}")
                return
            
            # Grant immediate besitos rewards
            besitos_amount = rewards.get('besitos', 0)
            if besitos_amount > 0:
                success = BesitosService.grant_besitos(
                    user_id=user_id,
                    amount=besitos_amount,
                    source='narrative_decision',
                    description=f"Decisión en {fragment_key}: {decision_id}",
                    metadata={
                        'fragment_key': fragment_key,
                        'decision_id': decision_id,
                        'rewards': rewards
                    }
                )
                
                if success:
                    logger.info(f"Granted {besitos_amount} besitos to user {user_id} for decision {decision_id}")
                else:
                    logger.error(f"Failed to grant besitos to user {user_id} for decision {decision_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle decision rewards: {e}")
    
    @staticmethod
    def _get_fragment_rewards(fragment_key: str) -> Dict[str, Any]:
        """
        Get rewards configuration for a fragment
        
        Args:
            fragment_key: Fragment identifier
            
        Returns:
            dict: Rewards configuration
        """
        # TODO: Get from MongoDB narrative content
        # For now, return static rewards based on fragment key
        
        rewards_map = {
            "fragment_1_1": {"besitos": 5},
            "fragment_1_2": {"besitos": 5},
            "fragment_1_3": {"besitos": 10},
            "level_1_end": {"besitos": 20},
            "fragment_2_1": {"besitos": 10},
            "level_2_end": {"besitos": 30},
            "intro_3": {"besitos": 15}
        }
        
        return rewards_map.get(fragment_key, {})
    
    @staticmethod
    def _get_decision_rewards(fragment_key: str, decision_id: str) -> Dict[str, Any]:
        """
        Get immediate rewards for a decision
        
        Args:
            fragment_key: Fragment identifier
            decision_id: Decision identifier
            
        Returns:
            dict: Immediate rewards
        """
        # TODO: Get from MongoDB narrative content
        # For now, return static rewards
        
        decision_rewards_map = {
            # Format: "fragment_key:decision_id"
            "fragment_1_1:continue": {"besitos": 2},
            "fragment_1_2:continue": {"besitos": 2},
            "fragment_1_3:complete": {"besitos": 5}
        }
        
        key = f"{fragment_key}:{decision_id}"
        return decision_rewards_map.get(key, {})


# Global instance
narrative_rewards = NarrativeRewards()


def setup_narrative_rewards_handlers():
    """Setup narrative rewards event handlers"""
    event_bus.subscribe("narrative.fragment_completed", narrative_rewards.handle_fragment_completion)
    event_bus.subscribe("narrative.decision_made", narrative_rewards.handle_decision_rewards)
    
    logger.info("Narrative rewards handlers setup completed")