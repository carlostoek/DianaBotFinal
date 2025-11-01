"""
Trivia command for DianaBot
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.handlers.trivias import trivia_start


async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trivia command"""
    await trivia_start(update, context)


async def trivia_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trivia <category> command"""
    if not context.args:
        await trivia_start(update, context)
        return
    
    category = " ".join(context.args).lower().replace(" ", "_")
    
    # For now, just start normal trivia
    # Category filtering will be handled in the trivia system
    await trivia_start(update, context)


# Handler registration
def register_trivia_commands(application):
    """Register trivia commands"""
    application.add_handler(CommandHandler("trivia", trivia_command))
    application.add_handler(CommandHandler("trivia_category", trivia_category_command))