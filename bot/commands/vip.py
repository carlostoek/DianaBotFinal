#!/usr/bin/env python3
"""
VIP subscription commands for DianaBot
"""

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from modules.admin.subscriptions import SubscriptionService
from modules.admin.vip_access import VIPAccessControl


async def vip_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VIP subscription status and benefits"""
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Check VIP status
        subscription_service = SubscriptionService(db)
        subscription = subscription_service.get_active_subscription(user_id)
        vip_status = subscription_service.is_vip(user_id)
        
        if vip_status and subscription:
            message = "🎉 **ESTADO VIP ACTIVO** 🎉\n\n"
            message += f"📅 **Suscripción activa hasta:** {subscription.end_date.strftime('%d/%m/%Y')}\n"
            message += f"🔑 **Tipo:** {subscription.subscription_type.upper()}\n"
            message += "\n**🎁 Beneficios VIP:**\n"
            message += "• Acceso exclusivo al Nivel 4: El Santuario VIP\n"
            message += "• 5 fragmentos narrativos exclusivos\n"
            message += "• Recompensas de besitos duplicadas\n"
            message += "• Acceso prioritario a nuevas funciones\n"
            message += "• Soporte VIP personalizado\n"
            
            if subscription.auto_renew:
                message += "\n🔄 **Renovación automática:** ACTIVADA"
            else:
                message += "\n⚠️ **Renovación automática:** DESACTIVADA"
                
        else:
            message = "🔒 **ESTADO VIP INACTIVO**\n\n"
            message += "Actualmente no tienes una suscripción VIP activa.\n\n"
            message += "**💎 Beneficios de VIP:**\n"
            message += "• Contenido narrativo exclusivo\n"
            message += "• Recompensas duplicadas\n"
            message += "• Acceso prioritario\n"
            message += "• Soporte personalizado\n\n"
            message += "Usa /upgrade para obtener más información sobre cómo convertirte en VIP."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("❌ Error al verificar el estado VIP. Intenta más tarde.")
    finally:
        db.close()


async def vip_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VIP upgrade information"""
    message = "💎 **CONVIÉRTETE EN VIP** 💎\n\n"
    message += "Desbloquea contenido exclusivo y beneficios especiales:\n\n"
    
    message += "**🎁 Beneficios VIP:**\n"
    message += "• **Nivel 4 Exclusivo:** El Santuario VIP con 5 fragmentos narrativos únicos\n"
    message += "• **Recompensas Duplicadas:** Gana el doble de besitos en misiones\n"
    message += "• **Acceso Prioritario:** Nuevas funciones antes que nadie\n"
    message += "• **Soporte VIP:** Atención personalizada 24/7\n"
    message += "• **Sin Publicidad:** Experiencia limpia y sin interrupciones\n\n"
    
    message += "**💳 Planes Disponibles:**\n"
    message += "• **VIP Mensual:** $9.99/mes\n"
    message += "• **VIP Trimestral:** $24.99 (ahorra 17%)\n"
    message += "• **VIP Anual:** $89.99 (ahorra 25%)\n\n"
    
    message += "**📋 Cómo Suscribirse:**\n"
    message += "1. Contacta a @DianaBotAdmin\n"
    message += "2. Selecciona tu plan preferido\n"
    message += "3. Realiza el pago\n"
    message += "4. ¡Disfruta de tus beneficios VIP!\n\n"
    
    message += "Usa /vip para verificar tu estado actual."
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def vip_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available VIP content"""
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Check VIP access
        vip_access = VIPAccessControl()
        access_granted, reason = vip_access.verify_vip_access(user_id, "narrative_level", "level_4_vip_exclusive", db)
        
        if access_granted:
            message = "🎭 **CONTENIDO VIP DISPONIBLE** 🎭\n\n"
            message += "**Nivel 4: El Santuario VIP**\n"
            message += "Descubre los secretos más profundos de la mansión Diana:\n\n"
            
            message += "**📖 Fragmentos Exclusivos:**\n"
            message += "1. **La Invitación VIP** - Tu acceso al santuario\n"
            message += "2. **Secretos de la Cámara VIP** - Misterios ocultos\n"
            message += "3. **El Artefacto Ancestral VIP** - Poderes ancestrales\n"
            message += "4. **La Revelación Final VIP** - La verdad completa\n"
            message += "5. **Final Definitivo VIP** - El desenlace exclusivo\n\n"
            
            message += "Usa /story para comenzar tu aventura VIP."
        else:
            message = "🔒 **CONTENIDO VIP BLOQUEADO**\n\n"
            message += f"Para acceder al contenido VIP necesitas una suscripción activa.\n\n"
            message += f"Razón: {reason}\n\n"
            message += "Usa /upgrade para obtener más información sobre cómo convertirte en VIP."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("❌ Error al acceder al contenido VIP. Intenta más tarde.")
    finally:
        db.close()