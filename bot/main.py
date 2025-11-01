import logging
import sys
import os
import threading
from datetime import datetime, time as dt_time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings
from database.connection import get_db
from database.models import User
from modules.gamification.missions import mission_service

# Import handlers
from bot.handlers.start import start_handler
from bot.handlers.help import help_handler
from bot.handlers.stats import stats_handler

# Import besitos commands
from bot.commands.balance import balance_handler
from bot.commands.history import history_handler
from bot.commands.daily import daily_handler

# Import inventory commands
from bot.commands.inventory import inventory_handler, item_handler

# Import narrative commands
from bot.commands.story import story_command
from bot.commands.continue_story import continue_command
from bot.commands.choices import choices_command
from bot.commands.progress import progress_command

# Import missions command
from bot.commands.missions import missions_command

# Import achievements command
from bot.commands.achievements import achievements_command

# Import trivia commands
from bot.commands.trivia import register_trivia_commands

# Import VIP commands
from bot.commands.vip import vip_status, vip_upgrade, vip_content

# Import secret commands
from bot.commands.secrets import secret_command, secrets_command, hint_command

# Import channel handlers
from bot.handlers.channels import handle_new_channel_member, handle_channel_post, send_vip_invite, send_free_channel_info

# Import narrative handlers
from bot.handlers.narrative import register_narrative_handlers

# Import auction handlers
from bot.handlers.auctions import setup_auction_handlers

# Import auction commands
from bot.commands.auctions import setup_auction_commands

# Import event handlers
from core.event_handlers import setup_event_handlers
from core.event_bus import event_bus

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def assign_daily_missions_to_all_users(context):
    """Assign daily missions to all active users"""
    try:
        db = next(get_db())
        
        # Get all active users
        users = db.query(User).all()
        
        assigned_count = 0
        for user in users:
            # TODO: Fix type issue with user.id
            # if mission_service.assign_daily_missions(user.id):
            #     assigned_count += 1
            pass
        
        logger.info(f"Assigned daily missions to {assigned_count} users")
        
    except Exception as e:
        logger.error(f"Error assigning daily missions: {e}")


def main():
    """Main function to run the bot"""
    # Setup event handlers
    setup_event_handlers()
    
    # Start event bus listener in background thread
    event_thread = threading.Thread(target=event_bus.listen, daemon=True)
    event_thread.start()
    
    # Create the Application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Setup daily mission assignment job (runs every day at 00:00)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(
            assign_daily_missions_to_all_users,
            time=dt_time(hour=0, minute=0),
            name="daily_missions_assignment"
        )
        logger.info("Daily mission assignment job scheduled")

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    
    # Add besitos commands
    application.add_handler(CommandHandler("balance", balance_handler))
    application.add_handler(CommandHandler("history", history_handler))
    application.add_handler(CommandHandler("daily", daily_handler))
    
    # Add inventory commands
    application.add_handler(CommandHandler("inventory", inventory_handler))
    application.add_handler(CommandHandler("item", item_handler))
    
    # Add narrative commands
    application.add_handler(CommandHandler("story", story_command))
    application.add_handler(CommandHandler("continue", continue_command))
    application.add_handler(CommandHandler("choices", choices_command))
    application.add_handler(CommandHandler("progress", progress_command))

    # Add missions command
    application.add_handler(CommandHandler("missions", missions_command))

    # Add achievements command
    application.add_handler(CommandHandler("achievements", achievements_command))

    # Add trivia commands
    register_trivia_commands(application)

    # Add VIP commands
    application.add_handler(CommandHandler("vip", vip_status))
    application.add_handler(CommandHandler("upgrade", vip_upgrade))
    application.add_handler(CommandHandler("vip_content", vip_content))

    # Add channel commands
    application.add_handler(CommandHandler("free_channel", send_free_channel_info))
    application.add_handler(CommandHandler("vip_invite", send_vip_invite))

    # Add secret commands
    application.add_handler(CommandHandler("secret", secret_command))
    application.add_handler(CommandHandler("secrets", secrets_command))
    application.add_handler(CommandHandler("hint", hint_command))

    # Add channel event handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_channel_member))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))

    # Register narrative callback handlers
    register_narrative_handlers(application)

    # Register auction handlers
    setup_auction_handlers(application)
    setup_auction_commands(application)

    # Start the Bot
    logger.info("Starting DianaBot with Event Bus...")
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()