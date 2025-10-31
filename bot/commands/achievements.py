"""
Achievements command for DianaBot
Allows users to view their achievements and progress
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from modules.gamification.achievements import achievement_service

logger = logging.getLogger(__name__)


async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /achievements command
    Shows user's unlocked achievements and progress towards available ones
    """
    try:
        db: Session = next(get_db())
        
        # Get user from database
        user = db.query(User).filter(
            User.telegram_id == update.effective_user.id
        ).first()
        
        if not user:
            await update.message.reply_text(
                "❌ No se pudo encontrar tu información de usuario. "
                "Por favor, usa /start para registrarte."
            )
            return
        
        # Get user achievements
        unlocked_achievements = achievement_service.get_user_achievements(user.id)
        available_achievements = achievement_service.get_available_achievements(user.id)
        
        if not unlocked_achievements and not available_achievements:
            await update.message.reply_text(
                "🎯 *Logros*\n\n"
                "Aún no tienes logros desbloqueados. ¡Continúa explorando la narrativa "
                "y completando misiones para desbloquear logros!\n\n"
                "Los logros te otorgan besitos y recompensas especiales.",
                parse_mode='Markdown'
            )
            return
        
        # Build achievements message
        message_parts = ["🎯 *Tus Logros*\n\n"]
        
        # Show unlocked achievements
        if unlocked_achievements:
            message_parts.append("✨ *Logros Desbloqueados*\n")
            for achievement in unlocked_achievements:
                icon = achievement.get('icon_emoji', '🏆')
                name = achievement['name']
                description = achievement['description']
                points = achievement['points']
                
                message_parts.append(
                    f"{icon} *{name}* ({points} pts)\n"
                    f"_{description}_\n"
                )
            message_parts.append("\n")
        
        # Show available achievements with progress
        if available_achievements:
            message_parts.append("🎯 *Logros Disponibles*\n")
            for achievement in available_achievements:
                icon = achievement.get('icon_emoji', '🎯')
                name = achievement['name']
                description = achievement['description']
                points = achievement['points']
                
                # Get progress for this achievement
                progress_info = achievement_service.get_achievement_progress(
                    user.id, achievement['achievement_key']
                )
                
                if progress_info.get('unlocked'):
                    continue  # Skip if somehow unlocked but not in list
                
                progress_text = ""
                if 'progress' in progress_info:
                    progress_data = progress_info['progress']
                    for condition_key, condition_data in progress_data.items():
                        current = condition_data['current']
                        target = condition_data['target']
                        percentage = condition_data['percentage']
                        
                        # Map condition keys to readable names
                        condition_names = {
                            'fragments_completed': 'Fragmentos completados',
                            'items_owned': 'Items en inventario',
                            'lifetime_besitos': 'Besitos lifetime',
                            'daily_missions_completed': 'Misiones diarias completadas',
                            'narrative_level': 'Nivel narrativo'
                        }
                        
                        condition_name = condition_names.get(condition_key, condition_key)
                        progress_text = f"{current}/{target} {condition_name} ({percentage}%)"
                        break  # Show only first condition for simplicity
                
                message_parts.append(
                    f"{icon} *{name}* ({points} pts)\n"
                    f"_{description}_\n"
                    f"📊 Progreso: {progress_text}\n\n"
                )
        
        # Add total stats
        total_points = sum(achievement['points'] for achievement in unlocked_achievements)
        message_parts.append(
            f"\n📊 *Estadísticas*\n"
            f"• Logros desbloqueados: {len(unlocked_achievements)}/{len(unlocked_achievements) + len(available_achievements)}"
            f"\n• Puntos totales: {total_points}"
        )
        
        await update.message.reply_text(
            ''.join(message_parts),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in achievements command: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al cargar tus logros. Por favor, intenta más tarde."
        )


async def achievement_notification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, achievement_data: dict) -> None:
    """
    Handle achievement unlocked notifications
    This would be called from event handlers when achievements are unlocked
    """
    try:
        achievement_name = achievement_data.get('achievement_name', 'Logro')
        rewards = achievement_data.get('rewards', {})
        
        message = f"🎉 *¡Logro Desbloqueado!* 🎉\n\n"
        message += f"✨ *{achievement_name}* ✨\n\n"
        
        # Add rewards information
        if rewards.get('besitos'):
            message += f"💰 Recompensa: {rewards['besitos']} besitos\n"
        
        if rewards.get('item_id'):
            message += f"🎁 ¡Item especial desbloqueado!\n"
        
        message += "\n¡Felicidades! Continúa explorando para desbloquear más logros."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in achievement notification: {e}")