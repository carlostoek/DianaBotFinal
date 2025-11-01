#!/usr/bin/env python3
"""
Progress command for showing narrative map and unlock status
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from modules.narrative.engine import NarrativeEngine
from modules.narrative.flags import get_all_narrative_flags

logger = logging.getLogger(__name__)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command - show narrative progress map"""
    
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("❌ No se pudo encontrar tu información de usuario.")
            return
        
        # Get narrative engine
        narrative_engine = NarrativeEngine()
        
        # Get available levels
        available_levels = narrative_engine.get_available_levels(user)
        
        if not available_levels:
            await update.message.reply_text(
                "📚 No tienes niveles narrativos disponibles en este momento.\n\n"
                "💡 Completa misiones diarias para ganar besitos y desbloquear nuevas historias."
            )
            return
        
        # Get narrative flags to show branching decisions
        narrative_flags = get_all_narrative_flags(user.id)
        
        # Build progress response
        response = "🗺️ **Tu Progreso Narrativo**\n\n"
        
        # Show important decisions taken
        if narrative_flags:
            response += "🎭 **Decisiones Importantes:**\n"
            important_flags = [
                ("trusted_lucien", "Confiaste en Lucien"),
                ("distrusted_lucien", "Desconfiaste de Lucien"),
                ("accepted_lucien_offer", "Aceptaste la oferta de Lucien"),
                ("rejected_lucien_offer", "Rechazaste la oferta de Lucien"),
                ("lucien_path_complete", "Completaste el camino de Lucien"),
                ("diana_path_complete", "Completaste el camino de Diana"),
                ("neutral_path_complete", "Completaste el camino neutral"),
            ]
            
            for flag_key, flag_description in important_flags:
                if narrative_flags.get(flag_key):
                    response += f"   ✅ {flag_description}\n"
            
            response += "\n"
        
        for level in available_levels:
            response += f"📖 **{level.title}**\n"
            response += f"   {level.description}\n\n"
            
            # Get accessible fragments for this level
            accessible_fragments = narrative_engine.get_accessible_fragments(user.id, level.level_key)
            
            if accessible_fragments:
                for fragment in accessible_fragments:
                    status = fragment["access_status"]
                    
                    if status["completed"]:
                        response += f"   ✅ {fragment['title']}\n"
                    elif status["unlocked"]:
                        response += f"   🔓 {fragment['title']}\n"
                    else:
                        response += f"   🔒 {fragment['title']}\n"
                        
                        # Show missing requirements
                        missing = status.get("missing_requirements", [])
                        if missing:
                            response += f"      📋 Requiere: {', '.join(missing)}\n"
                
                response += "\n"
            else:
                response += "   📭 No hay fragmentos disponibles\n\n"
        
        # Add tips
        response += "\n💡 **Consejos:**\n"
        response += "• Usa `/story` para ver niveles disponibles\n"
        response += "• Usa `/continue` para avanzar en la historia\n"
        response += "• Gana besitos con `/daily` para desbloquear contenido\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in progress command: {e}")
        await update.message.reply_text("❌ Ocurrió un error al mostrar tu progreso.")
    finally:
        db.close()