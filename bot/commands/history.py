import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from modules.gamification.besitos import besitos_service

logger = logging.getLogger(__name__)


async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command - show user's transaction history"""
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
        
        # Get transaction history
        transactions = besitos_service.get_transaction_history(db_user.id, limit=10)
        
        if not transactions:
            await update.message.reply_text(
                "📝 *Historial de Transacciones*\n\n"
                "No tienes transacciones registradas aún.\n"
                "Usa `/daily` para obtener tus primeros besitos!",
                parse_mode="Markdown"
            )
            return
        
        # Format history message
        history_text = f"📝 *Últimas Transacciones de {user.first_name}*\n\n"
        
        for i, tx in enumerate(transactions, 1):
            emoji = "➕" if tx["type"] == "earn" else "➖"
            amount = f"+{tx['amount']}" if tx["type"] == "earn" else f"-{tx['amount']}"
            
            # Format date
            date_str = "Hoy"
            if tx["created_at"]:
                from datetime import datetime
                tx_date = datetime.fromisoformat(tx["created_at"])
                now = datetime.now()
                if tx_date.date() == now.date():
                    date_str = "Hoy"
                elif tx_date.date() == now.replace(day=now.day-1).date():
                    date_str = "Ayer"
                else:
                    date_str = tx_date.strftime("%d/%m")
            
            history_text += f"{emoji} **{amount}** 💋 - {tx['source']} ({date_str})\n"
            
            if tx["description"]:
                history_text += f"   📄 {tx['description']}\n"
            
            history_text += "\n"
        
        history_text += "💡 *Consejo:* Usa `/balance` para ver tu balance actual."
        
        await update.message.reply_text(history_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in history handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al obtener tu historial. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()