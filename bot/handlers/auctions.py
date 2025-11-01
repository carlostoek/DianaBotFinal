"""
Auction handlers for Telegram bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from sqlalchemy.orm import Session

from database.connection import get_db
from modules.gamification.auctions import get_auction_service
from modules.gamification.besitos import besitos_service
from database.models import Auction, Bid, User

logger = logging.getLogger(__name__)


async def auctions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active auctions"""
    try:
        auction_service = get_auction_service()
        active_auctions = auction_service.get_active_auctions()
        
        if not active_auctions:
            await update.message.reply_text(
                "🏷️ *Subastas Activas*\n\n"
                "No hay subastas activas en este momento.\n"
                "¡Vuelve más tarde para ver nuevas subastas!",
                parse_mode="Markdown"
            )
            return
        
        message = "🏷️ *Subastas Activas*\n\n"
        
        for auction in active_auctions:
            time_remaining = max(0, (auction.end_time - auction_service.db.query(Auction).filter(Auction.auction_id == auction.auction_id).first().start_time).total_seconds())
            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)
            
            message += (
                f"*{auction.item.name if auction.item else 'Item'}*\n"
                f"💰 Puja actual: {auction.current_bid} besitos\n"
                f"⏰ Tiempo restante: {hours}h {minutes}m\n"
                f"👤 Pujador actual: {auction.current_bidder.username if auction.current_bidder else 'Nadie'}\n"
                f"🔢 Pujas totales: {auction.bid_count}\n"
                f"\nUsa /pujar {auction.auction_id} <cantidad> para pujar\n"
                "---\n\n"
            )
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing auctions: {e}")
        await update.message.reply_text(
            "❌ Error al cargar las subastas. Intenta más tarde."
        )


async def bid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Place a bid on an auction"""
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "💎 *Realizar Puja*\n\n"
                "Uso: /pujar <id_subasta> <cantidad>\n\n"
                "Ejemplo: /pujar 1 150\n"
                "Esto pujará 150 besitos en la subasta #1",
                parse_mode="Markdown"
            )
            return
        
        auction_id = int(context.args[0])
        amount = int(context.args[1])
        user_id = update.effective_user.id
        
        auction_service = get_auction_service()
        
        try:
            bid = auction_service.place_bid(user_id, auction_id, amount)
            
            # Get updated auction status
            auction_status = auction_service.get_auction_status(auction_id)
            
            if auction_status:
                auction = auction_status["auction"]
                time_remaining = auction_status["time_remaining"]
                hours = int(time_remaining // 3600)
                minutes = int((time_remaining % 3600) // 60)
                
                await update.message.reply_text(
                    f"✅ *¡Puja realizada!*\n\n"
                    f"💰 Has pujado *{amount}* besitos\n"
                    f"🏷️ Subasta: {auction['item_id']}\n"
                    f"⏰ Tiempo restante: {hours}h {minutes}m\n\n"
                    f"¡Buena suerte! 🍀",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"✅ Puja de {amount} besitos realizada en la subasta #{auction_id}"
                )
                
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            await update.message.reply_text(
                "❌ Error al realizar la puja. Intenta más tarde."
            )
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa: /pujar <id_subasta> <cantidad>"
        )
    except Exception as e:
        logger.error(f"Error in bid command: {e}")
        await update.message.reply_text(
            "❌ Error al procesar la puja. Intenta más tarde."
        )


async def auction_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed auction status"""
    try:
        if not context.args:
            await update.message.reply_text(
                "📊 *Estado de Subasta*\n\n"
                "Uso: /estadosubasta <id_subasta>\n\n"
                "Ejemplo: /estadosubasta 1",
                parse_mode="Markdown"
            )
            return
        
        auction_id = int(context.args[0])
        auction_service = get_auction_service()
        auction_status = auction_service.get_auction_status(auction_id)
        
        if not auction_status:
            await update.message.reply_text(
                f"❌ No se encontró la subasta #{auction_id}"
            )
            return
        
        auction = auction_status["auction"]
        item = auction_status["item"]
        top_bids = auction_status["top_bids"]
        time_remaining = auction_status["time_remaining"]
        
        hours = int(time_remaining // 3600)
        minutes = int((time_remaining % 3600) // 60)
        
        message = (
            f"📊 *Estado de Subasta #{auction_id}*\n\n"
            f"*{item['name'] if item else 'Item'}*\n"
            f"💰 Puja actual: *{auction['current_bid']}* besitos\n"
            f"⏰ Tiempo restante: *{hours}h {minutes}m*\n"
            f"👤 Pujador actual: {auction['current_bidder_id'] or 'Nadie'}\n"
            f"🔢 Pujas totales: {auction['bid_count']}\n"
            f"📈 Incremento mínimo: {auction['min_bid_increment']} besitos\n\n"
        )
        
        if top_bids:
            message += "*🏆 Top Pujas:*\n"
            for i, bid in enumerate(top_bids[:3], 1):
                message += f"{i}. {bid['amount']} besitos\n"
        
        keyboard = [
            [InlineKeyboardButton("💎 Pujar ahora", callback_data=f"bid_{auction_id}")],
            [InlineKeyboardButton("📋 Ver todas las subastas", callback_data="auctions_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Formato incorrecto. Usa: /estadosubasta <id_subasta>"
        )
    except Exception as e:
        logger.error(f"Error showing auction status: {e}")
        await update.message.reply_text(
            "❌ Error al cargar el estado de la subasta. Intenta más tarde."
        )


async def my_bids_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's bid history"""
    try:
        user_id = update.effective_user.id
        auction_service = get_auction_service()
        
        bid_history = auction_service.get_user_bid_history(user_id, limit=10)
        
        if not bid_history:
            await update.message.reply_text(
                "📋 *Mis Pujas*\n\n"
                "No has realizado ninguna puja todavía.\n"
                "¡Participa en las subastas activas usando /subastas!",
                parse_mode="Markdown"
            )
            return
        
        message = "📋 *Mis Últimas Pujas*\n\n"
        
        for bid in bid_history:
            auction = auction_service.db.query(Auction).filter(Auction.auction_id == bid.auction_id).first()
            item_name = auction.item.name if auction and auction.item else "Item"
            
            status = "🏆 Ganando" if bid.is_winning else "💔 Perdiendo"
            
            message += (
                f"*{item_name}*\n"
                f"💰 {bid.amount} besitos - {status}\n"
                f"⏰ {bid.created_at.strftime('%d/%m %H:%M')}\n"
                "---\n"
            )
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing bid history: {e}")
        await update.message.reply_text(
            "❌ Error al cargar tu historial de pujas. Intenta más tarde."
        )


async def bid_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bid button callbacks"""
    query = update.callback_query
    await query.answer()
    
    try:
        data = query.data
        
        if data.startswith("bid_"):
            auction_id = int(data.split("_")[1])
            
            # Show bid instructions
            await query.edit_message_text(
                f"💎 *Pujar en Subasta #{auction_id}*\n\n"
                f"Para pujar, usa el comando:\n"
                f"`/pujar {auction_id} <cantidad>`\n\n"
                f"Ejemplo: `/pujar {auction_id} 150`\n\n"
                f"¡Buena suerte! 🍀",
                parse_mode="Markdown"
            )
        elif data == "auctions_list":
            # Show active auctions
            auction_service = get_auction_service()
            active_auctions = auction_service.get_active_auctions()
            
            if not active_auctions:
                await query.edit_message_text(
                    "🏷️ *Subastas Activas*\n\n"
                    "No hay subastas activas en este momento.",
                    parse_mode="Markdown"
                )
                return
            
            message = "🏷️ *Subastas Activas*\n\n"
            
            for auction in active_auctions:
                time_remaining = max(0, (auction.end_time - auction_service.db.query(Auction).filter(Auction.auction_id == auction.auction_id).first().start_time).total_seconds())
                hours = int(time_remaining // 3600)
                minutes = int((time_remaining % 3600) // 60)
                
                message += (
                    f"*{auction.item.name if auction.item else 'Item'}*\n"
                    f"💰 {auction.current_bid} besitos\n"
                    f"⏰ {hours}h {minutes}m\n"
                    f"👤 {auction.current_bidder.username if auction.current_bidder else 'Nadie'}\n"
                    "---\n"
                )
            
            await query.edit_message_text(message, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error in bid callback: {e}")
        await query.edit_message_text(
            "❌ Error al procesar la acción. Intenta más tarde."
        )


def setup_auction_handlers(application):
    """Setup auction handlers"""
    application.add_handler(CommandHandler("subastas", auctions_command))
    application.add_handler(CommandHandler("pujar", bid_command))
    application.add_handler(CommandHandler("estadosubasta", auction_status_command))
    application.add_handler(CommandHandler("mispujas", my_bids_command))
    application.add_handler(CallbackQueryHandler(bid_callback_handler, pattern="^(bid_|auctions_list)"))