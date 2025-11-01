#!/usr/bin/env python3
"""
Subscription lifecycle commands for DianaBot
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database.connection import get_db
from modules.admin.subscription_lifecycle import SubscriptionLifecycle
from modules.admin.subscriptions import get_active_subscription, is_vip


async def subscription_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show contextual subscription offers based on user's conversion stage"""
    if not update.message:
        return
        
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Check if user is already VIP
        if is_vip(db, user_id):
            message = "🎉 **YA ERES VIP** 🎉\n\n"
            message += "¡Ya disfrutas de todos los beneficios VIP!\n\n"
            message += "**💎 Tus Beneficios:**\n"
            message += "• Contenido narrativo exclusivo\n"
            message += "• Recompensas duplicadas\n"
            message += "• Acceso prioritario\n"
            message += "• Soporte personalizado\n\n"
            message += "Usa /vip_content para ver tu contenido exclusivo."
        else:
            # Get contextual offers
            lifecycle = SubscriptionLifecycle(db)
            offers = lifecycle.get_contextual_offers(user_id)
            
            if offers:
                message = "💎 **OFERTAS PERSONALIZADAS** 💎\n\n"
                message += "Basado en tu actividad, estas ofertas son perfectas para ti:\n\n"
                
                for i, offer in enumerate(offers, 1):
                    message += f"**{i}. {offer['title']}**\n"
                    message += f"   {offer['description']}\n"
                    message += f"   💰 **Valor:** {offer['value']}\n\n"
                
                message += "**📋 Cómo Suscribirse:**\n"
                message += "1. Contacta a @DianaBotAdmin\n"
                message += "2. Menciona la oferta que te interesa\n"
                message += "3. Realiza el pago\n"
                message += "4. ¡Disfruta de tus beneficios VIP!\n\n"
                message += "Usa /vip para verificar tu estado actual."
            else:
                message = "💎 **SUSCRIPCIÓN VIP** 💎\n\n"
                message += "Desbloquea contenido exclusivo y beneficios especiales:\n\n"
                message += "**🎁 Beneficios VIP:**\n"
                message += "• Contenido narrativo exclusivo\n"
                message += "• Recompensas duplicadas\n"
                message += "• Acceso prioritario\n"
                message += "• Soporte personalizado\n\n"
                message += "Usa /upgrade para obtener más información."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("❌ Error al obtener ofertas personalizadas. Intenta más tarde.")
    finally:
        db.close()


async def subscription_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription conversion tracking"""
    if not update.message:
        return
        
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    
    try:
        # Start conversion funnel for free users
        lifecycle = SubscriptionLifecycle(db)
        
        # Check if user is VIP
        is_user_vip = is_vip(db, user_id)
        
        if not is_user_vip:
            # Start free_to_vip conversion funnel
            lifecycle.start_conversion_funnel(
                user_id=user_id,
                funnel_type="free_to_vip",
                initial_stage="free_trial"
            )
            
            message = "🎯 **CONVERSIÓN VIP** 🎯\n\n"
            message += "¡Estás en el camino hacia VIP!\n\n"
            message += "**📈 Tu Progreso:**\n"
            message += "• Etapa actual: Prueba Gratuita\n"
            message += "• Próximos pasos: Ofertas personalizadas\n"
            message += "• Meta final: Suscripción VIP\n\n"
            message += "Usa /offers para ver ofertas personalizadas para ti."
        else:
            message = "🎉 **YA ERES VIP** 🎉\n\n"
            message += "¡Ya completaste tu conversión a VIP!\n\n"
            message += "Disfruta de todos los beneficios exclusivos.\n"
            message += "Usa /vip_content para acceder a tu contenido."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("❌ Error en el seguimiento de conversión. Intenta más tarde.")
    finally:
        db.close()


async def subscription_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription analytics for admin users"""
    if not update.message:
        return
        
    user_id = update.effective_user.id
    
    # TODO: Add admin check
    # For now, show basic analytics to all users
    
    db: Session = next(get_db())
    
    try:
        lifecycle = SubscriptionLifecycle(db)
        
        message = "📊 **ANALÍTICAS DE SUSCRIPCIÓN** 📊\n\n"
        message += "**Tu Progreso de Conversión:**\n"
        
        # Get user's active funnels
        from database.models import ConversionFunnel
        
        active_funnels = db.query(ConversionFunnel).filter(
            ConversionFunnel.user_id == user_id,
            ConversionFunnel.is_active == True
        ).all()
        
        if active_funnels:
            for funnel in active_funnels:
                message += f"• **{funnel.funnel_type.replace('_', ' ').title()}**\n"
                message += f"  Etapa actual: {funnel.stage_current}\n"
                message += f"  Puntos de contacto: {funnel.funnel_data.get('touchpoints', 0)}\n"
                message += f"  Ofertas mostradas: {funnel.funnel_data.get('offers_shown', 0)}\n\n"
        else:
            message += "• No tienes embudos de conversión activos\n\n"
        
        message += "Usa /conversion para comenzar tu camino hacia VIP."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("❌ Error al obtener analíticas. Intenta más tarde.")
    finally:
        db.close()