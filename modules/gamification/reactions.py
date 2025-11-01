import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from database.connection import get_db
from core.event_bus import event_bus
from .besitos import besitos_service

logger = logging.getLogger(__name__)


class ReactionProcessor:
    """Processor for handling user reactions to content with rewards"""
    
    # Default reaction rewards configuration
    DEFAULT_REACTION_REWARDS = {
        '❤️': 10,  # love
        '🔥': 15,  # fire  
        '⭐': 20,  # star
        '👍': 5,   # like
    }
    
    @staticmethod
    def process_reaction(user_id: int, content_type: str, content_id: int, reaction_type: str) -> Dict[str, Any]:
        """
        Process user reaction to content with rewards and validation
        
        Args:
            user_id: User ID
            content_type: Type of content (narrative_fragment, channel_post, mission)
            content_id: ID of the content
            reaction_type: Type of reaction (❤️, 🔥, ⭐, 👍)
            
        Returns:
            Dict with processing results
        """
        db: Session = next(get_db())
        
        try:
            # Validate content exists
            if not ReactionProcessor._validate_content_exists(content_type, content_id, db):
                return {
                    'success': False, 
                    'reason': 'content_not_found',
                    'message': 'El contenido no existe'
                }
            
            # Check if user already reacted to this content
            if ReactionProcessor._has_user_reacted(user_id, content_type, content_id, reaction_type, db):
                return {
                    'success': False,
                    'reason': 'already_reacted',
                    'message': 'Ya has reaccionado a este contenido'
                }
            
            # Check daily limits
            if not ReactionProcessor._check_daily_limits(user_id, reaction_type, db):
                return {
                    'success': False,
                    'reason': 'daily_limit_reached',
                    'message': 'Has alcanzado el límite diario para esta reacción'
                }
            
            # Calculate besitos reward
            besitos_amount = ReactionProcessor._get_reaction_reward(reaction_type)
            
            # Register reaction
            reaction_id = ReactionProcessor._register_reaction(
                user_id, content_type, content_id, reaction_type, besitos_amount, db
            )
            
            # Grant besitos if applicable
            if besitos_amount > 0:
                besitos_service.grant_besitos(
                    user_id=user_id,
                    amount=besitos_amount,
                    source='reaction',
                    description=f"Reacción {reaction_type} en {content_type}"
                )
            
            # Emit event
            event_bus.publish("gamification.reaction_registered", {
                "user_id": user_id,
                "content_type": content_type,
                "content_id": content_id,
                "reaction_type": reaction_type,
                "besitos_earned": besitos_amount,
                "reaction_id": reaction_id
            })
            
            logger.info(f"User {user_id} reacted with {reaction_type} to {content_type} {content_id}")
            
            return {
                'success': True,
                'reaction_id': reaction_id,
                'besitos_earned': besitos_amount,
                'message': f"¡Reacción registrada! +{besitos_amount} besitos"
            }
            
        except Exception as e:
            logger.error(f"Failed to process reaction for user {user_id}: {e}")
            db.rollback()
            return {
                'success': False,
                'reason': 'processing_error',
                'message': 'Error al procesar la reacción'
            }
        finally:
            db.close()
    
    @staticmethod
    def _validate_content_exists(content_type: str, content_id: int, db: Session) -> bool:
        """Validate that the content exists in the system"""
        try:
            # This would need to be implemented based on actual content models
            # For now, we'll assume content exists
            return True
        except Exception as e:
            logger.error(f"Error validating content {content_type} {content_id}: {e}")
            return False
    
    @staticmethod
    def _has_user_reacted(user_id: int, content_type: str, content_id: int, reaction_type: str, db: Session) -> bool:
        """Check if user has already reacted to this content with same reaction"""
        try:
            # This would query the ContentReaction model once it's created
            # For now, we'll return False to allow reactions
            return False
        except Exception as e:
            logger.error(f"Error checking existing reaction: {e}")
            return True
    
    @staticmethod
    def _check_daily_limits(user_id: int, reaction_type: str, db: Session) -> bool:
        """Check if user has reached daily limits for this reaction type"""
        try:
            # This would query ContentReaction for today's count
            # For now, we'll return True (no limits)
            return True
        except Exception as e:
            logger.error(f"Error checking daily limits: {e}")
            return False
    
    @staticmethod
    def _get_reaction_reward(reaction_type: str) -> int:
        """Get besitos reward for reaction type"""
        return ReactionProcessor.DEFAULT_REACTION_REWARDS.get(reaction_type, 0)
    
    @staticmethod
    def _register_reaction(user_id: int, content_type: str, content_id: int, reaction_type: str, besitos_amount: int, db: Session) -> int:
        """Register reaction in database"""
        try:
            # This would create a ContentReaction record
            # For now, we'll return a mock ID
            return 1
        except Exception as e:
            logger.error(f"Error registering reaction: {e}")
            raise e
    
    @staticmethod
    def get_reaction_stats(content_type: str, content_id: int) -> Dict[str, int]:
        """Get reaction statistics for specific content"""
        try:
            # This would aggregate reactions from ContentReaction model
            # For now, return mock data
            return {
                '❤️': 5,
                '🔥': 3,
                '⭐': 2,
                '👍': 8
            }
        except Exception as e:
            logger.error(f"Error getting reaction stats: {e}")
            return {}
    
    @staticmethod
    def get_user_reactions(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's recent reactions"""
        try:
            # This would query ContentReaction for user
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting user reactions: {e}")
            return []


# Global service instance
reaction_processor = ReactionProcessor()