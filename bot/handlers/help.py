import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show available commands"""
    if not update.message:
        return
    
    help_text = (
        "🤖 *DianaBot - Comandos Disponibles*\n\n"
        "*/start* - Iniciar sesión y registrarse\n"
        "*/help* - Mostrar esta ayuda\n"
        "*/stats* - Ver tus estadísticas\n\n"
        "*Próximamente:*\n"
        "• Narrativas interactivas\n"
        "• Sistema de gamificación\n"
        "• Logros y recompensas\n\n"
        "¡Explora y diviértete! 🎮"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")