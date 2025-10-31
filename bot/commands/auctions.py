"""
Auction commands for Telegram bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from modules.gamification.auctions import get_auction_service

logger = logging.getLogger(__name__)


async def create_auction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to create an auction (for testing)"""
    try:
        # Check if user is admin (basic check)
        user_id = update.effective_user.id
        
        # For now, allow only specific user IDs for testing
        # In production, this should check admin permissions
        allowed_admins = [123456789]  # Replace with actual admin IDs
        
        if user_id not in allowed_admins:
            await update.message.reply_text(
                "❌ Solo los administradores pueden crear subastas."
            )
            return
        
        if not context.args or len(context.args) < 3:
            await update.message.reply_text(
                "🏷️ *Crear Subasta*\n\n"
                "Uso: /crearsubasta <item_id> <precio_inicial> <duracion_minutos>\n\n"
                "Ejemplo: /crearsubasta 1 100 60\n"
                "Esto crea una subasta del item #1 con precio inicial 100 y duración 60 minutos",
                parse_mode="Markdown"
            )
            return
        
        item_id = int(context.args[0])
        start_price = int(context.args[1])
        duration_minutes = int(context.args[2])
        
        auction_service = get_auction_service()
        
        try:
            auction = auction_service.create_auction(
                item_id=item_id,
                start_price=start_price,
                duration_minutes=duration_minutes
            )
            
            await update.message.reply_text(
                f"✅ *Subasta creada exitosamente!*\n\n"
                f"🏷️ ID de subasta: {auction.auction_id}\n"
                f"💰 Precio inicial: {start_price} besitos\n"
                f"⏰ Duración: {duration_minutes} minutos\n"
                f"📅 Finaliza: {auction.end_time.strftime('%d/%m %H:%M')}\n\n"
                f"¡La subasta está activa! Los usuarios pueden pujar usando:\n"
                f"`/pujar {auction.auction_id} <cantidad>`",
                parse_mode="Markdown"
            )
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Error creating auction: {e}")
            await update.message.reply_text(
                "❌ Error al crear la subasta. Verifica los parámetros."
            )
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa: /crearsubasta <item_id> <precio_inicial> <duracion_minutos>"
        )
    except Exception as e:
        logger.error(f"Error in create auction command: {e}")
        await update.message.reply_text(
            "❌ Error al procesar el comando. Intenta más tarde."
        )


async def close_auction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to close an auction manually"""
    try:
        # Check if user is admin
        user_id = update.effective_user.id
        allowed_admins = [123456789]  # Replace with actual admin IDs
        
        if user_id not in allowed_admins:
            await update.message.reply_text(
                "❌ Solo los administradores pueden cerrar subastas."
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "🔚 *Cerrar Subasta*\n\n"
                "Uso: /cerrarsubasta <id_subasta>\n\n"
                "Ejemplo: /cerrarsubasta 1",
                parse_mode="Markdown"
            )
            return
        
        auction_id = int(context.args[0])
        auction_service = get_auction_service()
        
        result = auction_service.close_auction(auction_id)
        
        if result:
            if result["status"] == "won":
                await update.message.reply_text(
                    f"✅ *Subasta cerrada!*\n\n"
                    f"🏆 Ganador: Usuario #{result['winner_id']}\n"
                    f"💰 Puja ganadora: {result['winning_bid']} besitos\n"
                    f"🎁 Item: #{result['item_id']}\n\n"
                    f"¡El item ha sido transferido al ganador!",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"ℹ️ *Subasta cerrada sin ganador*\n\n"
                    f"No hubo pujas en esta subasta.\n"
                    f"El item #{result['item_id']} permanece disponible.",
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(
                f"❌ No se pudo cerrar la subasta #{auction_id}. "
                f"Puede que ya esté cerrada o no exista."
            )
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa: /cerrarsubasta <id_subasta>"
        )
    except Exception as e:
        logger.error(f"Error in close auction command: {e}")
        await update.message.reply_text(
            "❌ Error al cerrar la subasta. Intenta más tarde."
        )


def setup_auction_commands(application):
    """Setup auction commands"""
    application.add_handler(CommandHandler("crearsubasta", create_auction_command))
    application.add_handler(CommandHandler("cerrarsubasta", close_auction_command))