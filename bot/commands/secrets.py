"""
Secret commands for hidden fragment discovery
"""
from telegram import Update
from telegram.ext import ContextTypes

from database.connection import get_db
from modules.narrative.secrets import SecretService


async def secret_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /secret <code> command"""
    if not update.message:
        return
        
    if not context.args:
        await update.message.reply_text(
            "💎 *Sistema de Secretos*\n\n"
            "Usa: `/secret <código>`\n"
            "Ejemplo: `/secret LUCIEN123`\n\n"
            "Los códigos secretos se encuentran en pistas ocultas "
            "en los canales VIP y mensajes especiales.",
            parse_mode="Markdown"
        )
        return

    code = " ".join(context.args)
    user_id = update.effective_user.id

    db = next(get_db())
    try:
        secret_service = SecretService(db)
        result = secret_service.submit_secret_code(user_id, code)

        if not result:
            await update.message.reply_text(
                "❌ Código secreto inválido o ya utilizado.\n"
                "Verifica que el código sea correcto y que no lo hayas usado antes."
            )
            return

        if result["success"]:
            await update.message.reply_text(
                f"🎉 *¡Secreto Descubierto!*\n\n"
                f"{result['message']}\n\n"
                f"Fragmento: *{result['fragment_title']}*\n"
                f"Usa `/story` para continuar tu aventura.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"ℹ️ {result['message']}\n"
                f"Fragmento: *{result['fragment_title']}*",
                parse_mode="Markdown"
            )
    finally:
        db.close()


async def secrets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /secrets command to show discovered secrets"""
    if not update.message:
        return
        
    user_id = update.effective_user.id

    db = next(get_db())
    try:
        secret_service = SecretService(db)
        discovered_secrets = secret_service.get_discovered_secrets(user_id)

        if not discovered_secrets:
            await update.message.reply_text(
                "🔍 *Tus Secretos Descubiertos*\n\n"
                "Aún no has descubierto ningún secreto.\n\n"
                "💡 *Consejos para encontrar secretos:*\n"
                "• Revisa los canales VIP regularmente\n"
                "• Combina objetos especiales en tu inventario\n"
                "• Toma decisiones inusuales en la historia\n"
                "• Usa `/hint` para obtener una pista",
                parse_mode="Markdown"
            )
            return

        secrets_text = "🔍 *Tus Secretos Descubiertos*\n\n"
        
        for i, secret in enumerate(discovered_secrets, 1):
            secrets_text += (
                f"{i}. *{secret['fragment_title']}*\n"
                f"   Descubierto: {secret['discovered_at'].strftime('%d/%m/%Y')}\n"
            )
            if secret.get('code_used'):
                secrets_text += f"   Código: `{secret['code_used']}`\n"
            secrets_text += "\n"

        secrets_text += (
            f"📊 *Total: {len(discovered_secrets)} secretos descubiertos*\n\n"
            "💎 Continúa explorando para encontrar más secretos ocultos!"
        )

        await update.message.reply_text(secrets_text, parse_mode="Markdown")
    finally:
        db.close()


async def hint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hint command to get hints about next secrets"""
    if not update.message:
        return
        
    user_id = update.effective_user.id

    db = next(get_db())
    try:
        secret_service = SecretService(db)
        
        # Check for item combinations first
        unlocked_fragments = secret_service.check_item_combinations(user_id)
        
        if unlocked_fragments:
            hint_text = "🎁 *¡Nuevos Secretos Desbloqueados!*\n\n"
            for fragment in unlocked_fragments:
                hint_text += (
                    f"• *{fragment['description']}*\n"
                    f"  Has desbloqueado un fragmento secreto con la combinación de objetos.\n\n"
                )
            
            hint_text += "Usa `/story` para explorar los nuevos fragmentos."
            await update.message.reply_text(hint_text, parse_mode="Markdown")
            return

        # Get hint for next secret
        hint = secret_service.get_secret_hint(user_id)

        if not hint:
            await update.message.reply_text(
                "🎯 *Pista del Día*\n\n"
                "¡Felicidades! Parece que has descubierto todos los secretos disponibles por ahora.\n\n"
                "💎 Nuevos secretos aparecerán en futuras actualizaciones.\n"
                "Mantente atento a los canales VIP para más contenido oculto.",
                parse_mode="Markdown"
            )
            return

        await update.message.reply_text(
            f"💡 *Pista del Día*\n\n"
            f"{hint}\n\n"
            f"💎 *Consejos adicionales:*\n"
            f"• Revisa tu inventario con `/inventory`\n"
            f"• Explora combinaciones de objetos\n"
            f"• Lee cuidadosamente los mensajes en canales VIP",
            parse_mode="Markdown"
        )
    finally:
        db.close()