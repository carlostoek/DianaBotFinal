"""
Channel handlers for Telegram channel events
Handles new member joins, channel posts, and membership verification
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from modules.admin.channels import channel_service
from modules.admin.subscriptions import subscription_service

logger = logging.getLogger(__name__)


async def handle_new_channel_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle new member joining a channel
    """
    try:
        if not update.message:
            return
            
        message = update.message
        
        if not hasattr(message, 'new_chat_members') or not message.new_chat_members:
            return
        
        chat = update.effective_chat
        new_members = message.new_chat_members
        
        # Get channel configuration
        channel_config = channel_service.get_channel_config(chat.id)
        if not channel_config:
            logger.warning(f"No configuration found for channel {chat.id}")
            return
        
        # Log the channel post
        channel_service.log_channel_post(
            channel_id=chat.id,
            post_id=message.message_id,
            post_type="welcome",
            content=f"New members joined: {', '.join([member.first_name for member in new_members])}",
            post_metadata={
                "new_members": [{
                    "id": member.id,
                    "first_name": member.first_name,
                    "username": member.username
                } for member in new_members]
            }
        )
        
        # Send welcome message for VIP channels
        if channel_config.channel_type == "vip":
            welcome_message = (
                f"🎉 ¡Bienvenido/a al canal VIP de DianaBot! 🎉\n\n"
                f"Gracias por unirte a nuestra comunidad exclusiva. \n"
                f"Aquí encontrarás:\n"
                f"• Contenido narrativo exclusivo\n"
                f"• Fragmentos de historia premium\n"
                f"• Beneficios especiales para suscriptores\n\n"
                f"¡Disfruta de la experiencia VIP! 🚀"
            )
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=welcome_message,
                reply_to_message_id=update.message.message_id
            )
            
            logger.info(f"Sent VIP welcome message in channel {chat.id}")
        
        elif channel_config.channel_type == "free":
            welcome_message = (
                f"👋 ¡Bienvenido/a al canal gratuito de DianaBot!\n\n"
                f"Aquí encontrarás contenido básico y actualizaciones. \n"
                f"Para acceder a contenido exclusivo, considera suscribirte al plan VIP.\n\n"
                f"Usa /vip para más información."
            )
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=welcome_message,
                reply_to_message_id=update.message.message_id
            )
            
            logger.info(f"Sent free welcome message in channel {chat.id}")
            
    except Exception as e:
        logger.error(f"Error handling new channel member: {e}")


async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle regular channel posts for tracking
    """
    try:
        if not update.channel_post:
            return
        
        chat = update.effective_chat
        message = update.channel_post
        
        # Get channel configuration
        channel_config = channel_service.get_channel_config(chat.id)
        if not channel_config:
            return
        
        # Determine post type based on content or channel type
        post_type = "content"
        if message.text and any(keyword in message.text.lower() for keyword in ["anuncio", "announcement", "importante"]):
            post_type = "announcement"
        elif message.text and any(keyword in message.text.lower() for keyword in ["recordatorio", "reminder", "no olvides"]):
            post_type = "reminder"
        
        # Log the channel post
        channel_service.log_channel_post(
            channel_id=chat.id,
            post_id=message.message_id,
            post_type=post_type,
            content=message.text,
            metadata={
                "message_type": message.content_type,
                "has_media": bool(message.photo or message.video or message.document),
                "date": message.date.isoformat() if message.date else None
            }
        )
        
        logger.debug(f"Logged channel post {message.message_id} in channel {chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling channel post: {e}")


async def handle_channel_invite_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle channel invite requests from users
    This would be triggered when a user requests to join a private channel
    """
    try:
        # This handler would be implemented when Telegram adds support for
        # handling channel join requests via bot API
        # Currently, this is a placeholder for future implementation
        
        logger.info("Channel invite request received (placeholder for future implementation)")
        
    except Exception as e:
        logger.error(f"Error handling channel invite request: {e}")


async def send_vip_invite(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """
    Send VIP channel invite to a user
    
    Args:
        update: Telegram update
        context: Context
        user_id: User ID to send invite to
    """
    try:
        # Check if user has active VIP subscription
        subscription = subscription_service.get_active_subscription(user_id)
        if not subscription:
            await update.message.reply_text(
                "❌ Necesitas una suscripción VIP activa para acceder al canal exclusivo.\n"
                "Usa /vip para más información sobre nuestros planes."
            )
            return
        
        # Generate VIP channel invite link
        invite_link = channel_service.generate_invite_link("vip", user_id)
        
        if not invite_link:
            await update.message.reply_text(
                "⚠️ Lo sentimos, el canal VIP no está disponible en este momento. "
                "Por favor, contacta con soporte."
            )
            return
        
        # Send invite message
        invite_message = (
            f"🎉 ¡Enhorabuena! Aquí tienes tu acceso al canal VIP 🎉\n\n"
            f"🔗 **Enlace de invitación:** {invite_link}\n\n"
            f"📋 **Instrucciones:**\n"
            f"1. Haz clic en el enlace de arriba\n"
            f"2. Únete al canal\n"
            f"3. ¡Disfruta del contenido exclusivo!\n\n"
            f"💎 **Beneficios del canal VIP:**\n"
            f"• Contenido narrativo premium\n"
            f"• Fragmentos de historia exclusivos\n"
            f"• Comunidad privada\n"
            f"• Soporte prioritario\n\n"
            f"¡Gracias por ser parte de nuestra comunidad VIP! 🚀"
        )
        
        await update.message.reply_text(invite_message)
        
        logger.info(f"Sent VIP channel invite to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending VIP invite to user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Error al generar el enlace de invitación. "
            "Por favor, intenta más tarde o contacta con soporte."
        )


async def send_free_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send free channel information to users
    """
    try:
        # Generate free channel invite link
        invite_link = channel_service.generate_invite_link("free", update.effective_user.id)
        
        if not invite_link:
            await update.message.reply_text(
                "⚠️ Lo sentimos, el canal gratuito no está disponible en este momento."
            )
            return
        
        # Send free channel info
        free_channel_message = (
            f"📢 **Canal Gratuito de DianaBot**\n\n"
            f"🔗 **Enlace:** {invite_link}\n\n"
            f"📋 **Qué encontrarás:**\n"
            f"• Contenido básico y actualizaciones\n"
            f"• Anuncios importantes\n"
            f"• Comunidad de usuarios\n\n"
            f"💎 **Para contenido exclusivo:**\n"
            f"Usa /vip para información sobre el plan premium\n\n"
            f"¡Te esperamos en el canal! 👋"
        )
        
        await update.message.reply_text(free_channel_message)
        
        logger.info(f"Sent free channel info to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending free channel info: {e}")
        await update.message.reply_text(
            "❌ Error al obtener información del canal. "
            "Por favor, intenta más tarde."
        )