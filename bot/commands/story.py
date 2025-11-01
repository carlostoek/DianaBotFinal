#!/usr/bin/env python3
"""
Story command for the narrative system
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, NarrativeLevel
from modules.narrative.engine import NarrativeEngine

logger = logging.getLogger(__name__)


async def story_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /story command - show available narrative levels"""
    
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Get available levels
        narrative_engine = NarrativeEngine()
        available_levels = narrative_engine.get_available_levels(user)
        
        if not available_levels:
            await update.message.reply_text(
                "📚 No tienes niveles narrativos disponibles en este momento.\n\n"
                "💡 Completa misiones diarias para ganar besitos y desbloquear nuevas historias."
            )
            return
        
        # Build response with interactive keyboard
        response = "📖 **Niveles Narrativos Disponibles**\n\n"
        
        for level in available_levels:
            response += f"**{level.title}**\n"
            response += f"   {level.description}\n"
            
            # Show unlock conditions if not yet unlocked
            if level.unlock_conditions:
                conditions = []
                if level.unlock_conditions.get('min_besitos', 0) > 0:
                    conditions.append(f"{level.unlock_conditions['min_besitos']} besitos")
                if level.unlock_conditions.get('required_items'):
                    conditions.append(f"items especiales")
                if level.unlock_conditions.get('required_fragments'):
                    conditions.append(f"completar niveles anteriores")
                
                if conditions:
                    response += f"   🔑 Requiere: {', '.join(conditions)}\n"
            
            response += "\n"
        
        response += "\n💡 Selecciona una historia para comenzar:"
        
        # Create interactive keyboard for level selection
        from bot.keyboards.narrative_keyboards import get_level_selection_keyboard
        keyboard = get_level_selection_keyboard(available_levels)
        
        await update.message.reply_text(response, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in story command: {e}")
        await update.message.reply_text("❌ Ocurrió un error al mostrar los niveles narrativos.")
    finally:
        db.close()