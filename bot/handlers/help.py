import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show available commands"""
    if not update.message:
        return
    
    help_text = (
        "🤖 *DianaBot - Guía Completa de Comandos*\n\n"
        "*📋 COMANDOS BÁSICOS:*\n"
        "*/start* - Iniciar sesión y registrarse\n"
        "*/help* - Mostrar esta ayuda completa\n"
        "*/stats* - Ver tus estadísticas generales\n\n"
        "*💰 SISTEMA ECONÓMICO:*\n"
        "*/balance* - Ver tus besitos actuales 💋\n"
        "*/history* - Ver historial de transacciones\n"
        "*/daily* - Reclamar recompensa diaria (10 💋)\n\n"
        "*🎒 INVENTARIO Y OBJETOS:*\n"
        "*/inventory* - Ver tu mochila de items\n"
        "*/item <nombre>* - Ver detalles de un item específico\n\n"
        "*📖 SISTEMA NARRATIVO:*\n"
        "*/story* - Ver niveles narrativos disponibles\n"
        "*/continue* - Continuar o comenzar una historia\n"
        "*/choices* - Ver opciones disponibles en el fragmento actual\n"
        "*/progress* - Ver tu progreso narrativo\n\n"
        "*💎 SISTEMA DE SECRETOS:*\n"
        "*/secret <código>* - Ingresar código secreto para desbloquear fragmentos\n"
        "*/secrets* - Listar todos los secretos que has descubierto\n"
        "*/hint* - Obtener pistas sobre próximos secretos\n\n"
        "*🎮 GAMIFICACIÓN:*\n"
        "*/missions* - Ver misiones activas y recompensas\n"
        "*/achievements* - Ver logros desbloqueados y disponibles\n\n"
        "*🏷️ SISTEMA DE SUBASTAS:*\n"
        "*/subastas* - Ver subastas activas\n"
        "*/pujar <id> <cantidad>* - Pujar en una subasta\n"
        "*/estadosubasta <id>* - Ver estado detallado de una subasta\n"
        "*/mispujas* - Ver tu historial de pujas\n\n"
        "*❓ TRIVIAS Y DESAFÍOS:*\n"
        "*/trivia* - Iniciar una trivia aleatoria\n"
        "*/trivia_category <categoría>* - Trivia por categoría específica\n\n"
        "*👑 SISTEMA VIP:*\n"
        "*/vip* - Ver tu estado VIP y beneficios\n"
        "*/upgrade* - Mejorar a suscripción VIP\n"
        "*/vip_content* - Acceder a contenido exclusivo VIP\n"
        "*/vip_invite* - Obtener invitación al canal VIP\n\n"
        "*📢 CANALES Y COMUNIDAD:*\n"
        "*/free_channel* - Obtener información del canal gratuito\n\n"
        "*⚙️ COMANDOS DE ADMINISTRADOR:*\n"
        "*/crearsubasta <item> <precio> <tiempo>* - Crear nueva subasta\n"
        "*/cerrarsubasta <id>* - Cerrar subasta manualmente\n\n"
        "---\n"
        "*💡 Consejos:*\n"
        "• Usa `/daily` todos los días para ganar besitos\n"
        "• Explora combinaciones de objetos en tu inventario\n"
        "• Revisa los canales VIP para encontrar códigos secretos\n"
        "• Participa en subastas para obtener items raros\n"
        "• Completa misiones para recompensas especiales\n\n"
        "¡Diviértete explorando todas las funcionalidades! 🎮✨"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")