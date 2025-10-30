import logging
import sys
import os
import threading

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings

# Import handlers
from bot.handlers.start import start_handler
from bot.handlers.help import help_handler
from bot.handlers.stats import stats_handler

# Import besitos commands
from bot.commands.balance import balance_handler
from bot.commands.history import history_handler
from bot.commands.daily import daily_handler

# Import event handlers
from core.event_handlers import setup_event_handlers
from core.event_bus import event_bus

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the bot"""
    # Setup event handlers
    setup_event_handlers()
    
    # Start event bus listener in background thread
    event_thread = threading.Thread(target=event_bus.listen, daemon=True)
    event_thread.start()
    
    # Create the Application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    
    # Add besitos commands
    application.add_handler(CommandHandler("balance", balance_handler))
    application.add_handler(CommandHandler("history", history_handler))
    application.add_handler(CommandHandler("daily", daily_handler))

    # Start the Bot
    logger.info("Starting DianaBot with Event Bus...")
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()