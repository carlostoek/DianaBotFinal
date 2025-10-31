"""
Reaction handler for Telegram channel reactions
Handles reaction events and gamified rewards
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Any

from modules.admin.reactions import reactions_service
from modules.gamification.missions import mission_service
from database.models import ChannelPost
from database.connection import get_db

logger = logging.getLogger(__name__)


async def handle_reaction_added(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle when a user adds a reaction to a channel post
    
    This handler processes reaction events and grants gamified rewards
    """
    try:
        # Extract reaction data from update
        reaction_data = _extract_reaction_data(update)
        if not reaction_data:
            return
        
        user_id = reaction_data["user_id"]
        post_id = reaction_data["post_id"]
        emoji = reaction_data["emoji"]
        
        # Process the reaction
        result = reactions_service.handle_reaction(user_id, post_id, emoji)
        
        if result.get("success") and result.get("rewards_granted"):
            # Update mission progress for reaction-based missions
            _update_reaction_missions(user_id, post_id, emoji)
            
            # Send reward notification if possible
            await _send_reward_notification(update, context, result)
            
            logger.info(f"Reaction processed successfully: user {user_id}, post {post_id}, emoji {emoji}")
        else:
            logger.info(f"Reaction processed without rewards: {result.get('reason', 'No rewards')}")
            
    except Exception as e:
        logger.error(f"Error handling reaction: {e}")


def _extract_reaction_data(update: Update) -> Dict[str, Any]:
    """Extract reaction data from Telegram update"""
    try:
        # This would need to be adapted based on how Telegram sends reaction updates
        # For now, we'll create a placeholder implementation
        
        # In a real implementation, this would extract:
        # - user_id from update.effective_user.id
        # - post_id from update.message.message_id or similar
        # - emoji from update.message.reaction
        
        # For testing/demo purposes, return mock data
        return {
            "user_id": update.effective_user.id if update.effective_user else 12345,
            "post_id": update.message.message_id if update.message else 67890,
            "emoji": "❤️"  # Default emoji for testing
        }
        
    except Exception as e:
        logger.error(f"Error extracting reaction data: {e}")
        return {}


def _update_reaction_missions(user_id: int, post_id: int, emoji: str) -> None:
    """Update mission progress for reaction-related missions"""
    try:
        db = next(get_db())
        
        # Get active missions for user
        active_missions = mission_service.get_active_missions(user_id)
        
        for mission in active_missions:
            mission_id = mission["id"]
            requirements = mission.get("requirements", {})
            
            # Check if this mission involves reactions
            if "react_to_posts" in requirements:
                # Update reaction count
                progress_data = {
                    "react_to_posts": mission.get("progress", {}).get("react_to_posts", 0) + 1,
                    "last_reaction_emoji": emoji,
                    "last_reaction_post": post_id
                }
                
                mission_service.update_mission_progress(user_id, mission_id, progress_data)
                
            # Check for specific emoji missions
            if f"react_{emoji}_count" in requirements:
                progress_data = {
                    f"react_{emoji}_count": mission.get("progress", {}).get(f"react_{emoji}_count", 0) + 1
                }
                
                mission_service.update_mission_progress(user_id, mission_id, progress_data)
                
    except Exception as e:
        logger.error(f"Error updating reaction missions: {e}")


async def _send_reward_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, result: Dict[str, Any]) -> None:
    """Send notification about rewards granted"""
    try:
        rewards = result.get("rewards", {})
        
        if not rewards:
            return
        
        message_parts = ["🎉 ¡Recompensa obtenida! 🎉\n\n"]
        
        # Add besitos reward
        if "besitos" in rewards:
            message_parts.append(f"💋 +{rewards['besitos']} besitos")
        
        # Add achievement trigger
        if "achievement_trigger" in rewards:
            message_parts.append("🏆 Progreso en logro desbloqueado")
        
        # Add unlock hint
        if "unlock_hint" in rewards:
            message_parts.append(f"💡 {rewards['unlock_hint']}")
        
        # Add trivia trigger
        if "trivia_trigger" in rewards:
            message_parts.append("❓ ¡Nueva trivia disponible!")
        
        if len(message_parts) > 1:  # More than just the header
            message = "\n".join(message_parts)
            
            # Try to send DM to user
            if update.effective_user:
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=message
                    )
                except Exception as e:
                    logger.warning(f"Could not send DM reward notification: {e}")
                    
    except Exception as e:
        logger.error(f"Error sending reward notification: {e}")


async def get_reaction_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get user reaction statistics"""
    try:
        user_id = update.effective_user.id
        
        stats = reactions_service.get_user_reaction_stats(user_id)
        
        if not stats:
            await update.message.reply_text("📊 No tienes estadísticas de reacciones aún.")
            return
        
        message = f"📊 **Estadísticas de Reacciones**\n\n"
        message += f"💖 **Total de reacciones:** {stats.get('total_reactions', 0)}\n"
        message += f"🎁 **Reacciones premiadas:** {stats.get('rewarded_reactions', 0)}\n\n"
        
        # Add emoji breakdown
        emoji_stats = stats.get('emoji_stats', {})
        if emoji_stats:
            message += "**Desglose por emoji:**\n"
            for emoji, data in emoji_stats.items():
                message += f"{emoji}: {data.get('total', 0)} total, {data.get('rewarded', 0)} premiadas\n"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error getting reaction stats: {e}")
        await update.message.reply_text("❌ Error al obtener estadísticas de reacciones.")


async def configure_post_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Configure reaction rewards for a post (admin command)"""
    try:
        # This would be an admin command to configure reaction rewards
        # For now, just a placeholder implementation
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Uso: /config_reactions <post_id> <config_json>\n"
                "Ejemplo: /config_reactions 123 '{\"❤️\": {\"besitos\": 2}}'"
            )
            return
        
        post_id = int(context.args[0])
        config_str = " ".join(context.args[1:])
        
        # Parse config (in real implementation, use json.loads)
        # For now, create a simple config
        reaction_config = {
            "❤️": {"besitos": 2, "limit_per_user": 1},
            "🔥": {"besitos": 3, "limit_per_user": 1}
        }
        
        success = reactions_service.configure_post_reactions(post_id, reaction_config)
        
        if success:
            await update.message.reply_text(f"✅ Configuración de reacciones aplicada al post {post_id}")
        else:
            await update.message.reply_text(f"❌ Error al configurar reacciones para el post {post_id}")
            
    except Exception as e:
        logger.error(f"Error configuring post reactions: {e}")
        await update.message.reply_text("❌ Error al configurar reacciones.")