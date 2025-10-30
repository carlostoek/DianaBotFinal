"""
Narrative handlers with interactive keyboards
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from modules.narrative.engine import NarrativeEngine

logger = logging.getLogger(__name__)


async def narrative_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle narrative start callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    level_key = query.data.split(":")[-1]  # Extract level key from callback
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await query.edit_message_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Start the story
        narrative_engine = NarrativeEngine()
        result = narrative_engine.start_story(user, level_key)
        
        if not result:
            await query.edit_message_text("❌ No se pudo comenzar la historia.")
            return
        
        # Show first fragment
        await _show_fragment_with_decisions(query, result, user.id)
        
    except Exception as e:
        logger.error(f"Error in narrative start handler: {e}")
        await query.edit_message_text("❌ Ocurrió un error al comenzar la historia.")
    finally:
        db.close()


async def narrative_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle narrative decision callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    # Parse callback data: narrative:decision:<fragment_key>:<decision_id>
    parts = callback_data.split(":")
    if len(parts) != 4:
        await query.edit_message_text("❌ Datos de callback inválidos.")
        return
    
    fragment_key = parts[2]
    decision_id = parts[3]
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await query.edit_message_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Process decision
        narrative_engine = NarrativeEngine()
        result = narrative_engine.process_decision(user.id, fragment_key, decision_id)
        
        if not result:
            await query.edit_message_text("❌ No se pudo procesar tu decisión.")
            return
        
        # Show rewards if any
        rewards = result.get("rewards", {})
        if rewards:
            reward_text = _format_rewards(rewards)
            await query.edit_message_text(
                f"✨ **Recompensas obtenidas:**\n{reward_text}\n\nContinuando...",
                parse_mode='Markdown'
            )
        
        # Show next fragment
        next_fragment = result.get("next_fragment")
        if next_fragment:
            await _show_fragment_with_decisions(query, next_fragment, user.id)
        else:
            # End of current path
            await query.edit_message_text(
                "🏁 **Has llegado al final de esta parte de la historia.**\n\n"
                "Usa /story para explorar otras historias disponibles.",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Error in narrative decision handler: {e}")
        await query.edit_message_text("❌ Ocurrió un error al procesar tu decisión.")
    finally:
        db.close()


async def _show_fragment_with_decisions(query, fragment_data: dict, user_id: int):
    """Show fragment content with decision buttons"""
    narrative_engine = NarrativeEngine()
    
    # Get fragment content from MongoDB
    fragment_content = narrative_engine.get_fragment_content(fragment_data["fragment_key"])
    
    if not fragment_content:
        await query.edit_message_text("❌ No se pudo cargar el contenido de la historia.")
        return
    
    # Build message
    content = fragment_content.get("content", {})
    message = f"📖 **{fragment_data['title']}**\n\n"
    message += content.get("text", "Continuas tu aventura...")
    
    # Get available decisions
    decisions = narrative_engine.get_available_decisions(user_id, fragment_data["fragment_key"])
    
    if decisions:
        # Create inline keyboard with decisions
        keyboard = []
        for decision in decisions:
            callback_data = f"narrative:decision:{fragment_data['fragment_key']}:{decision['decision_id']}"
            keyboard.append([
                InlineKeyboardButton(decision["text"], callback_data=callback_data)
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # No decisions available (end of fragment)
        await query.edit_message_text(
            f"{message}\n\n🏁 **Fin del fragmento**\n"
            "Usa /continue para continuar tu aventura.",
            parse_mode='Markdown'
        )


def _format_rewards(rewards: dict) -> str:
    """Format rewards for display"""
    reward_text = ""
    
    if "besitos" in rewards:
        reward_text += f"💋 {rewards['besitos']} besitos\n"
    
    if "items" in rewards:
        for item in rewards["items"]:
            reward_text += f"🎁 {item['name']}\n"
    
    if "achievements" in rewards:
        for achievement in rewards["achievements"]:
            reward_text += f"🏆 {achievement['name']}\n"
    
    return reward_text.strip()


async def narrative_continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle narrative continue callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await query.edit_message_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Get current progress
        narrative_engine = NarrativeEngine()
        current_progress = narrative_engine.get_current_progress(user)
        
        if not current_progress:
            await query.edit_message_text("📚 No tienes una historia en progreso.")
            return
        
        # Show current fragment
        await _show_fragment_with_decisions(query, current_progress, user.id)
        
    except Exception as e:
        logger.error(f"Error in narrative continue handler: {e}")
        await query.edit_message_text("❌ Ocurrió un error al continuar la historia.")
    finally:
        db.close()


# Register handlers
def register_narrative_handlers(application):
    """Register narrative callback handlers"""
    application.add_handler(CallbackQueryHandler(
        narrative_start_handler, 
        pattern=r"^narrative:start:"
    ))
    application.add_handler(CallbackQueryHandler(
        narrative_decision_handler, 
        pattern=r"^narrative:decision:"
    ))
    application.add_handler(CallbackQueryHandler(
        narrative_continue_handler, 
        pattern=r"^narrative:continue$"
    ))