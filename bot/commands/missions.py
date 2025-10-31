"""
Missions command for DianaBot
Handles /missions command to show user missions
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from modules.gamification.missions import mission_service

logger = logging.getLogger(__name__)


async def missions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /missions command to show user missions
    """
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    try:
        # Get active missions
        active_missions = mission_service.get_active_missions(user_id)
        
        # Get available missions
        available_missions = mission_service.get_available_missions(user_id)
        
        if not active_missions and not available_missions:
            await update.message.reply_text(
                "🎯 *Tus Misiones*\n\n"
                "No tienes misiones activas en este momento. ¡Vuelve más tarde para nuevas aventuras!"
            )
            return
        
        # Build response message
        message_parts = ["🎯 *Tus Misiones*\n"]
        
        # Active missions
        if active_missions:
            message_parts.append("\n📋 *Misiones Activas:*\n")
            for mission in active_missions:
                progress_text = _format_progress(mission)
                message_parts.append(
                    f"• *{mission['title']}*\n"
                    f"  {mission['description']}\n"
                    f"  {progress_text}\n"
                )
        
        # Available missions
        if available_missions:
            message_parts.append("\n🔓 *Misiones Disponibles:*\n")
            for mission in available_missions:
                rewards_text = _format_rewards(mission['rewards'])
                message_parts.append(
                    f"• *{mission['title']}*\n"
                    f"  {mission['description']}\n"
                    f"  🎁 Recompensa: {rewards_text}\n"
                )
        
        message_parts.append(
            "\n💡 *Consejo:* Completa misiones para ganar besitos y objetos especiales!"
        )
        
        await update.message.reply_text(
            "\n".join(message_parts),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in missions command for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al cargar tus misiones. Intenta de nuevo más tarde."
        )


def _format_progress(mission: dict) -> str:
    """Format mission progress for display"""
    requirements = mission.get('requirements', {})
    progress = mission.get('progress', {})
    
    if not requirements:
        return "Progreso: Completado ✅"
    
    progress_parts = []
    for req_key, target in requirements.items():
        current = progress.get(req_key, 0)
        
        # Map requirement keys to readable names
        req_names = {
            "fragments_completed": "Fragmentos",
            "daily_rewards_claimed": "Recompensas Diarias",
            "narrative_level": "Nivel Narrativo"
        }
        
        req_name = req_names.get(req_key, req_key)
        progress_parts.append(f"{req_name}: {current}/{target}")
    
    if len(progress_parts) == 1:
        return f"Progreso: {progress_parts[0]}"
    else:
        return "Progreso: " + ", ".join(progress_parts)


def _format_rewards(rewards: dict) -> str:
    """Format rewards for display"""
    reward_parts = []
    
    if "besitos" in rewards:
        reward_parts.append(f"💋 {rewards['besitos']} besitos")
    
    if "items" in rewards:
        items = rewards["items"]
        if isinstance(items, list):
            reward_parts.append(f"🎁 {len(items)} objeto(s)")
        else:
            reward_parts.append(f"🎁 {items} objeto(s)")
    
    return ", ".join(reward_parts) if reward_parts else "Ninguna"