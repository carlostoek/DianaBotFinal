#!/usr/bin/env python3
"""
Choices command for the narrative system
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from modules.narrative.engine import NarrativeEngine

logger = logging.getLogger(__name__)


async def choices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /choices command - show available choices for current story"""
    
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Get current progress
        narrative_engine = NarrativeEngine()
        current_progress = narrative_engine.get_current_progress(user)
        
        if not current_progress:
            await update.message.reply_text(
                "📚 No tienes una historia en progreso.\n\n"
                "💡 Usa /story para ver los niveles disponibles o /continue para comenzar una nueva aventura."
            )
            return
        
        # Show current choices
        next_fragments = current_progress['next_fragments']
        if not next_fragments:
            await update.message.reply_text(
                "🏁 **¡Has completado esta parte de la historia!**\n\n"
                "Usa /story para ver qué más puedes explorar."
            )
            return
        
        response = f"📖 **Opciones Disponibles**\n\n"
        response += f"**Historia actual:** {current_progress['title']}\n\n"
        
        response += "**¿Qué quieres hacer a continuación?**\n"
        for i, fragment in enumerate(next_fragments, 1):
            response += f"\n**{i}. {fragment['title']}**\n"
            response += f"   {fragment['description']}"
        
        response += "\n\n💡 Responde con el número de tu elección o usa /continue para continuar."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in choices command: {e}")
        await update.message.reply_text("❌ Ocurrió un error al mostrar las opciones.")
    finally:
        db.close()