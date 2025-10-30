#!/usr/bin/env python3
"""
Continue command for the narrative system
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from modules.narrative.engine import NarrativeEngine

logger = logging.getLogger(__name__)


async def continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /continue command - continue current story or start new one"""
    
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
            # No current progress, show available levels
            await _show_available_levels(update, user)
            return
        
        # Show current fragment and next options
        await _show_current_fragment(update, current_progress)
        
    except Exception as e:
        logger.error(f"Error in continue command: {e}")
        await update.message.reply_text("❌ Ocurrió un error al continuar la historia.")
    finally:
        db.close()


async def _show_available_levels(update: Update, user: User):
    """Show available narrative levels to start"""
    
    db: Session = next(get_db())
    
    try:
        narrative_engine = NarrativeEngine()
        available_levels = narrative_engine.get_available_levels(user)
        
        if not available_levels:
            await update.message.reply_text(
                "📚 No tienes niveles narrativos disponibles en este momento.\n\n"
                "💡 Completa misiones diarias para ganar besitos y desbloquear nuevas historias."
            )
            return
        
        # Build response
        response = "📖 **¿Qué historia quieres comenzar?**\n\n"
        
        for i, level in enumerate(available_levels, 1):
            response += f"**{i}. {level.title}**\n"
            response += f"   {level.description}\n\n"
        
        response += "💡 Responde con el número de la historia que quieres comenzar."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing available levels: {e}")
        await update.message.reply_text("❌ Error al mostrar los niveles disponibles.")
    finally:
        db.close()


async def _show_current_fragment(update: Update, current_progress: dict):
    """Show current fragment and next options"""
    
    response = f"📖 **{current_progress['title']}**\n\n"
    
    # Add fragment content based on fragment key
    fragment_content = _get_fragment_content(current_progress['fragment_key'])
    response += fragment_content
    
    # Show next options
    next_fragments = current_progress['next_fragments']
    if next_fragments:
        response += "\n\n**¿Qué quieres hacer?**\n"
        for i, fragment in enumerate(next_fragments, 1):
            response += f"\n**{i}. {fragment['title']}**\n"
            response += f"   {fragment['description']}"
        
        response += "\n\n💡 Responde con el número de tu elección."
    else:
        response += "\n\n🏁 **¡Has completado esta parte de la historia!**\n"
        response += "Usa /story para ver qué más puedes explorar."
    
    await update.message.reply_text(response, parse_mode='Markdown')


def _get_fragment_content(fragment_key: str) -> str:
    """Get content for specific fragment"""
    
    content_map = {
        "fragment_1_1": (
            "Te despiertas en una habitación desconocida. La luz del amanecer se filtra por la ventana, "
            "iluminando polvo dorado que danza en el aire. Escuchas voces lejanas..."
        ),
        "fragment_1_2": (
            "Sigues las voces por el pasillo. Las paredes están cubiertas de retratos antiguos que "
            "parecen observarte. Una puerta al final del pasillo está entreabierta..."
        ),
        "fragment_1_3": (
            "Al entrar en la habitación, te encuentras con Diana. Su mirada es intensa pero amable. "
            "'Llevaba tiempo esperándote', dice con una sonrisa misteriosa..."
        ),
        "level_1_end": (
            "Has completado tu primera incursión en la Mansión Diana. Los misterios apenas comienzan, "
            "pero ya has demostrado tu valentía. Diana parece interesada en conocerte mejor..."
        ),
        "fragment_2_1": (
            "Te adentras en el bosque que rodea la mansión. Los árboles susurran secretos antiguos "
            "y el camino se bifurca frente a ti. ¿Qué camino tomarás?"
        ),
        "level_2_end": (
            "El bosque te ha revelado sus secretos. Ahora comprendes mejor la conexión entre Diana "
            "y este lugar mágico. Pero los mayores misterios aún están por descubrir..."
        ),
        "intro_3": (
            "Con la llave del ático en tu poder, te enfrentas a la puerta final. Lo que encuentres "
            "aquí podría cambiar todo lo que creías saber sobre Diana y la mansión..."
        )
    }
    
    return content_map.get(fragment_key, "Continuas tu aventura en la Mansión Diana...")