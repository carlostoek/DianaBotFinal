import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from database.models import User
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show user statistics"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    
    # Get database session
    db: Session = next(get_db())
    
    try:
        # Get user from database
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ No estás registrado. Usa /start para registrarte."
            )
            return
        
        # Update last active and command count
        db_user.last_active = func.now()
        db_user.total_commands += 1
        db.commit()
        
        # Publish command executed event
        event_bus.publish("user.command_executed", {
            "telegram_id": user.id,
            "user_id": db_user.id,
            "command": "stats",
            "username": user.username
        })
        
        # Format stats message
        created_at_str = db_user.created_at.strftime('%d/%m/%Y') if hasattr(db_user.created_at, 'strftime') else 'N/A'
        last_active_str = db_user.last_active.strftime('%d/%m/%Y %H:%M') if hasattr(db_user.last_active, 'strftime') else 'N/A'
        
        stats_text = (
            f"📊 *Estadísticas de {user.first_name}*\n\n"
            f"👤 *Usuario:* {db_user.username or 'Sin username'}\n"
            f"📝 *Mensajes totales:* {db_user.total_messages}\n"
            f"⚡ *Comandos usados:* {db_user.total_commands}\n"
            f"📚 *Historias iniciadas:* {db_user.total_stories_started}\n"
            f"🔄 *Estado actual:* {db_user.current_state}\n"
            f"📅 *Registrado desde:* {created_at_str}\n"
            f"🕒 *Última actividad:* {last_active_str}\n\n"
            f"¡Sigue explorando! 🚀"
        )
        
        await update.message.reply_text(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al obtener tus estadísticas. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()