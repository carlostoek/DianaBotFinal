import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from modules.gamification.besitos import besitos_service

logger = logging.getLogger(__name__)


async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command - show user's besitos balance"""
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
        
        # Get besitos balance
        current_balance = besitos_service.get_balance(db_user.id)
        lifetime_besitos = besitos_service.get_lifetime_besitos(db_user.id)
        
        if current_balance is None:
            current_balance = 0
        if lifetime_besitos is None:
            lifetime_besitos = 0
        
        # Format balance message
        balance_text = (
            f"💋 *Balance de Besitos de {user.first_name}*\n\n"
            f"💰 *Besitos actuales:* **{current_balance}** 💋\n"
            f"📊 *Besitos ganados en total:* **{lifetime_besitos}** 💋\n\n"
        )
        
        # Add tips based on balance
        if current_balance == 0:
            balance_text += "💡 *Consejo:* Usa `/daily` para obtener 10 besitos gratis cada día!"
        elif current_balance < 50:
            balance_text += "💡 *Consejo:* ¡Sigue acumulando! Pronto podrás desbloquear contenido especial."
        else:
            balance_text += "💡 *Consejo:* ¡Excelente progreso! Ya tienes suficientes besitos para recompensas especiales."
        
        await update.message.reply_text(balance_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in balance handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al obtener tu balance. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()