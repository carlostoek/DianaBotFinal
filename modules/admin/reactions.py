"""
Gamified reactions service for Telegram channels
Handles reaction rewards, limits, and tracking
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import UserReaction, ChannelPost
from database.connection import get_db
from modules.gamification.besitos import BesitosService
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class ReactionsService:
    """Service for managing gamified reactions in channels"""
    
    def __init__(self):
        self.besitos_service = BesitosService()
    
    def configure_post_reactions(self, post_id: int, reaction_config: Dict[str, Any]) -> bool:
        """
        Configure reaction rewards for a post
        
        Args:
            post_id: Post ID to configure
            reaction_config: Reaction configuration
            
        Example config:
            {
                "❤️": {
                    "besitos": 2,
                    "limit_per_user": 1,
                    "achievement_trigger": {
                        "achievement_key": "romantic_soul",
                        "condition": "react_heart_50_times"
                    }
                },
                "🔥": {
                    "besitos": 3,
                    "limit_per_user": 1,
                    "unlock_hint": "You seem passionate. Check your DMs."
                }
            }
        """
        db: Session = next(get_db())
        try:
            post = db.query(ChannelPost).filter(ChannelPost.id == post_id).first()
            if not post:
                logger.error(f"Post {post_id} not found")
                return False
            
            post.reaction_rewards = reaction_config
            db.commit()
            
            logger.info(f"Configured reaction rewards for post {post_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error configuring reactions for post {post_id}: {e}")
            return False
        finally:
            db.close()
    
    def handle_reaction(self, user_id: int, post_id: int, emoji: str) -> Dict[str, Any]:
        """
        Handle a user reaction to a post
        
        Args:
            user_id: User ID who reacted
            post_id: Post ID that was reacted to
            emoji: Reaction emoji
            
        Returns:
            Dict with rewards granted and status
        """
        db: Session = next(get_db())
        try:
            # Get the post and its reaction configuration
            post = db.query(ChannelPost).filter(ChannelPost.id == post_id).first()
            if not post:
                return {"success": False, "error": "Post not found"}
            
            reaction_config = post.reaction_rewards or {}
            
            # Check if this emoji has rewards configured
            if emoji not in reaction_config:
                return {"success": True, "rewards_granted": False, "reason": "No rewards configured for this emoji"}
            
            emoji_config = reaction_config[emoji]
            
            # Check user limits
            if not self._can_user_react(db, user_id, post_id, emoji, emoji_config):
                return {"success": True, "rewards_granted": False, "reason": "User limit reached"}
            
            # Record the reaction
            reaction = UserReaction(
                user_id=user_id,
                post_id=post_id,
                emoji=emoji
            )
            db.add(reaction)
            
            # Grant rewards
            rewards = self._grant_rewards(user_id, emoji_config)
            
            # Mark as rewarded
            reaction.rewarded_at = datetime.now()
            
            db.commit()
            
            # Publish event
            event_bus.publish("admin.reaction_added", {
                "user_id": user_id,
                "post_id": post_id,
                "emoji": emoji,
                "rewards_granted": rewards,
                "reaction_id": reaction.id
            })
            
            logger.info(f"User {user_id} reacted with {emoji} to post {post_id}, rewards: {rewards}")
            
            return {
                "success": True,
                "rewards_granted": True,
                "rewards": rewards,
                "reaction_id": reaction.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error handling reaction for user {user_id} on post {post_id}: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def _can_user_react(self, db: Session, user_id: int, post_id: int, emoji: str, emoji_config: Dict[str, Any]) -> bool:
        """Check if user can react with this emoji to this post"""
        try:
            limit_per_user = emoji_config.get("limit_per_user")
            if not limit_per_user:
                return True
            
            # Count existing reactions by this user to this post with this emoji
            existing_count = db.query(UserReaction).filter(
                UserReaction.user_id == user_id,
                UserReaction.post_id == post_id,
                UserReaction.emoji == emoji
            ).count()
            
            return existing_count < limit_per_user
            
        except Exception as e:
            logger.error(f"Error checking reaction limits: {e}")
            return False
    
    def _grant_rewards(self, user_id: int, emoji_config: Dict[str, Any]) -> Dict[str, Any]:
        """Grant rewards based on reaction configuration"""
        rewards = {}
        
        try:
            # Grant besitos
            besitos_amount = emoji_config.get("besitos")
            if besitos_amount:
                self.besitos_service.grant_besitos(
                    user_id=user_id,
                    amount=besitos_amount,
                    source="reaction_reward",
                    description=f"Reaction reward: {besitos_amount} besitos"
                )
                rewards["besitos"] = besitos_amount
            
            # Handle achievement triggers
            achievement_trigger = emoji_config.get("achievement_trigger")
            if achievement_trigger:
                # In production, this would trigger achievement progress
                rewards["achievement_trigger"] = achievement_trigger
            
            # Handle unlock hints
            unlock_hint = emoji_config.get("unlock_hint")
            if unlock_hint:
                rewards["unlock_hint"] = unlock_hint
            
            # Handle trivia triggers
            trivia_trigger = emoji_config.get("trigger_trivia")
            if trivia_trigger:
                rewards["trivia_trigger"] = trivia_trigger
            
            return rewards
            
        except Exception as e:
            logger.error(f"Error granting rewards: {e}")
            return rewards
    
    def get_user_reaction_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user reaction statistics"""
        db: Session = next(get_db())
        try:
            total_reactions = db.query(UserReaction).filter(
                UserReaction.user_id == user_id
            ).count()
            
            rewarded_reactions = db.query(UserReaction).filter(
                UserReaction.user_id == user_id,
                UserReaction.rewarded_at.isnot(None)
            ).count()
            
            # Group by emoji
            emoji_stats = {}
            reactions_by_emoji = db.query(
                UserReaction.emoji,
                UserReaction.rewarded_at
            ).filter(
                UserReaction.user_id == user_id
            ).all()
            
            for emoji, rewarded_at in reactions_by_emoji:
                if emoji not in emoji_stats:
                    emoji_stats[emoji] = {"total": 0, "rewarded": 0}
                
                emoji_stats[emoji]["total"] += 1
                if rewarded_at:
                    emoji_stats[emoji]["rewarded"] += 1
            
            return {
                "total_reactions": total_reactions,
                "rewarded_reactions": rewarded_reactions,
                "emoji_stats": emoji_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting user reaction stats: {e}")
            return {}
        finally:
            db.close()
    
    def get_post_reaction_stats(self, post_id: int) -> Dict[str, Any]:
        """Get post reaction statistics"""
        db: Session = next(get_db())
        try:
            total_reactions = db.query(UserReaction).filter(
                UserReaction.post_id == post_id
            ).count()
            
            # Group by emoji
            emoji_stats = {}
            reactions_by_emoji = db.query(
                UserReaction.emoji,
                UserReaction.rewarded_at
            ).filter(
                UserReaction.post_id == post_id
            ).all()
            
            for emoji, rewarded_at in reactions_by_emoji:
                if emoji not in emoji_stats:
                    emoji_stats[emoji] = {"total": 0, "rewarded": 0}
                
                emoji_stats[emoji]["total"] += 1
                if rewarded_at:
                    emoji_stats[emoji]["rewarded"] += 1
            
            return {
                "post_id": post_id,
                "total_reactions": total_reactions,
                "emoji_stats": emoji_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting post reaction stats: {e}")
            return {}
        finally:
            db.close()
    
    def get_top_reactors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by reaction count"""
        db: Session = next(get_db())
        try:
            top_reactors = db.query(
                UserReaction.user_id,
                func.count(UserReaction.id).label('reaction_count')
            ).group_by(
                UserReaction.user_id
            ).order_by(
                func.count(UserReaction.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    "user_id": user_id,
                    "reaction_count": reaction_count
                }
                for user_id, reaction_count in top_reactors
            ]
            
        except Exception as e:
            logger.error(f"Error getting top reactors: {e}")
            return []
        finally:
            db.close()


# Global instance
reactions_service = ReactionsService()