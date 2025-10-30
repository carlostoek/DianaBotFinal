import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from database.models import User
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - register user and send welcome message"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    
    # Get database session
    db: Session = next(get_db())
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if existing_user:
            # Update last active
            existing_user.last_active = func.now()
            existing_user.total_commands += 1
            db.commit()
            
            # Publish user activity event
            event_bus.publish("user.activity", {
                "telegram_id": user.id,
                "user_id": existing_user.id,
                "action": "start_command",
                "username": user.username
            })
            
            welcome_message = (
                f"¡Bienvenido de nuevo, {user.first_name}! 👋\n\n"
                f"Ya estás registrado en DianaBot.\n"
                f"Usa /help para ver los comandos disponibles."
            )
        else:
            # Create new user
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
                is_bot=user.is_bot,
                total_commands=1
            )
            db.add(new_user)
            db.commit()
            
            # Publish user registered event
            event_bus.publish("user.registered", {
                "telegram_id": user.id,
                "user_id": new_user.id,
                "username": user.username,
                "first_name": user.first_name,
                "language_code": user.language_code
            })
            
            welcome_message = (
                f"¡Bienvenido a DianaBot, {user.first_name}! 🎉\n\n"
                f"Te has registrado exitosamente.\n"
                f"Soy tu asistente para narrativas interactivas y gamificación.\n\n"
                f"Usa /help para ver los comandos disponibles."
            )
            
            logger.info(f"New user registered: {user.id} - {user.username}")
        
        await update.message.reply_text(welcome_message)
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al procesar tu solicitud. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()