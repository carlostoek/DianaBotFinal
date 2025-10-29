"""
DianaBot - Main Bot Entry Point
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from utils.logger import get_logger
from config.settings import settings
from bot.handlers.start_handler import start_command
from bot.handlers.narrative_handler import handle_narrative_callback
from bot.handlers.gamification_handler import handle_gamification_callback
from bot.handlers.admin_handler import handle_admin_callback


logger = get_logger(__name__)


def create_application():
    """Create and configure the Telegram bot application"""
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("inventory", inventory_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(handle_narrative_callback, pattern=r'^narrative:'))
    application.add_handler(CallbackQueryHandler(handle_gamification_callback, pattern=r'^gamification:'))
    application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r'^admin:'))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    
    return application


async def help_command(update, context):
    """Handler for /help command"""
    help_text = """
🤖 *DianaBot - Ayuda*

Bienvenido a DianaBot, un mundo narrativo gamificado con personajes encantadores.

📚 *Comandos Disponibles:*
• /start - Iniciar tu aventura
• /balance - Ver tus besitos
• /inventory - Ver tu inventario
• /missions - Ver misiones activas
• /achievements - Ver tus logros
• /help - Este mensaje de ayuda

✨ *Narrativa Inmersiva*
Sigue la historia de Lucien y Diana a través de decisiones que alteran el rumbo de la narrativa.

🎮 *Gamificación*
Gana besitos, completa misiones, obtén logros y desbloquea contenido exclusivo.

💎 *Contenido VIP*
Suscríbete para acceder a niveles exclusivos y contenido premium.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def balance_command(update, context):
    """Handler for /balance command"""
    user_id = update.effective_user.id
    
    # Get user balance from database
    from core.database import get_db
    from core.models import UserBalance
    
    db = next(get_db())
    balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
    
    if balance:
        await update.message.reply_text(f"💰 Tienes {balance.besitos} besitos")
    else:
        await update.message.reply_text("💰 No tienes besitos aún. ¡Completa fragmentos para ganar!")


async def inventory_command(update, context):
    """Handler for /inventory command"""
    user_id = update.effective_user.id
    
    # Get user inventory from database
    from core.database import get_db
    from core.models import UserInventory, Item
    
    db = next(get_db())
    user_items = db.query(UserInventory, Item).join(Item).filter(UserInventory.user_id == user_id).all()
    
    if user_items:
        inventory_text = "🎒 *Tu Inventario:*\n\n"
        for inventory_item, item in user_items:
            inventory_text += f"• {item.name} x{inventory_item.quantity}\n"
    else:
        inventory_text = "🎒 Tu inventario está vacío. ¡Compra o gana items para llenarlo!"
    
    await update.message.reply_text(inventory_text, parse_mode='Markdown')


async def handle_user_message(update, context):
    """Generic message handler for user input"""
    message = update.message.text.lower()
    user_id = update.effective_user.id
    
    # Simple responses to common messages
    if 'hola' in message or 'hello' in message:
        await update.message.reply_text("¡Hola! Usa /start para comenzar tu aventura con Diana y Lucien.")
    elif 'ayuda' in message or 'help' in message:
        await help_command(update, context)
    else:
        await update.message.reply_text("No entiendo ese comando. Usa /help para ver comandos disponibles.")


def main():
    """Main function to run the bot"""
    logger.info("Starting DianaBot...")
    
    # Create application
    application = create_application()
    
    if settings.telegram_webhook_url:
        # Use webhook mode
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.port,
            url_path=settings.telegram_bot_token,
            webhook_url=f"{settings.telegram_webhook_url}/{settings.telegram_bot_token}"
        )
    else:
        # Use polling mode
        application.run_polling()


if __name__ == '__main__':
    main()