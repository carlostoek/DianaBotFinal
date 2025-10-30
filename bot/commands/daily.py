import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from modules.gamification.daily_rewards import daily_reward_service

logger = logging.getLogger(__name__)


async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command - claim daily reward"""
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
        
        # Claim daily reward
        amount = daily_reward_service.claim_daily_reward(db_user.id)
        
        if amount is not None:
            # Success message
            success_text = (
                f"🎉 *¡Recompensa Diaria Reclamada!*\n\n"
                f"💋 Has recibido **{amount} besitos**\n\n"
                f"💰 *Nuevo balance:* **{daily_reward_service.besitos_service.get_balance(db_user.id)}** 💋\n\n"
                f"⏰ *Próxima recompensa:* Mañana a esta misma hora\n\n"
                f"💡 *Consejo:* Vuelve cada día para acumular más besitos!"
            )
            
            await update.message.reply_text(success_text, parse_mode="Markdown")
            
        else:
            # Already claimed today
            next_claim = daily_reward_service.get_next_claim_time(db_user.id)
            
            if next_claim:
                from datetime import datetime
                now = datetime.now()
                time_left = next_claim - now
                hours_left = int(time_left.total_seconds() // 3600)
                minutes_left = int((time_left.total_seconds() % 3600) // 60)
                
                if hours_left > 0:
                    time_str = f"{hours_left}h {minutes_left}m"
                else:
                    time_str = f"{minutes_left}m"
                
                wait_text = (
                    f"⏰ *Ya reclamaste tu recompensa diaria*\n\n"
                    f"💋 Vuelve en **{time_str}** para obtener tus próximos 10 besitos.\n\n"
                    f"💡 *Consejo:* Usa `/balance` para ver tu balance actual."
                )
            else:
                wait_text = (
                    "❌ No puedes reclamar tu recompensa diaria en este momento. "
                    "Intenta de nuevo más tarde."
                )
            
            await update.message.reply_text(wait_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in daily handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al procesar tu recompensa diaria. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()