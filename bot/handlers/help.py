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
        "*📋 Básicos:*\n"
        "*/start* - Iniciar sesión y registrarse\n"
        "*/help* - Mostrar esta ayuda\n"
        "*/stats* - Ver tus estadísticas\n\n"
        "*💰 Economía:*\n"
        "*/balance* - Ver tus besitos actuales\n"
        "*/history* - Ver historial de transacciones\n"
        "*/daily* - Reclamar recompensa diaria (10 💋)\n\n"
        "*🎒 Inventario:*\n"
        "*/inventory* - Ver tu mochila de items\n"
        "*/item <nombre>* - Ver detalles de un item\n\n"
        "*📖 Narrativa:*\n"
        "*/story* - Ver niveles narrativos disponibles\n"
        "*/continue* - Continuar o comenzar una historia\n"
        "*/choices* - Ver opciones disponibles\n\n"
        "*Próximamente:*\n"
        "• Logros y recompensas\n"
        "• Tienda virtual\n\n"
        "¡Explora y diviértete! 🎮"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")