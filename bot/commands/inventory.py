import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from modules.gamification.inventory import inventory_service

logger = logging.getLogger(__name__)


def format_rarity_emoji(rarity: str) -> str:
    """Get emoji for item rarity"""
    rarity_emojis = {
        "common": "⚪",
        "rare": "🔵", 
        "epic": "🟣",
        "legendary": "🟡"
    }
    return rarity_emojis.get(rarity, "⚪")


def format_item_type_emoji(item_type: str) -> str:
    """Get emoji for item type"""
    type_emojis = {
        "collectible": "🏆",
        "consumable": "🍯",
        "narrative_key": "🗝️",
        "power_up": "✨"
    }
    return type_emojis.get(item_type, "📦")


async def inventory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /inventory command - show user's inventory"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    
    # Get database session
    db: Session = next(get_db())
    
    try:
        # Get user from database
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ No estás registrado. Usa /start para registrarte."
            )
            return
        
        # Get user inventory
        inventory = inventory_service.get_user_inventory(db_user.id)
        
        if not inventory:
            await update.message.reply_text(
                "🎒 *Tu Mochila está Vacía*\n\n"
                "💡 *Consejos:*\n"
                "• Completa misiones para ganar items\n"
                "• Reclama tu recompensa diaria con `/daily`\n"
                "• Pronto podrás comprar items en la tienda",
                parse_mode="Markdown"
            )
            return
        
        # Group items by type
        items_by_type = {}
        for item in inventory:
            item_type = item["item_type"]
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)
        
        # Build inventory message
        message_parts = ["🎒 *Tu Mochila*\n\n"]
        
        for item_type, items in items_by_type.items():
            type_emoji = format_item_type_emoji(item_type)
            type_name = {
                "collectible": "Coleccionables",
                "consumable": "Consumibles", 
                "narrative_key": "Llaves Narrativas",
                "power_up": "Mejoras"
            }.get(item_type, item_type.title())
            
            message_parts.append(f"{type_emoji} *{type_name}*")
            
            for item in items:
                rarity_emoji = format_rarity_emoji(item["rarity"])
                quantity_text = f"x{item['quantity']}" if item["quantity"] > 1 else ""
                
                message_parts.append(
                    f"  {rarity_emoji} **{item['name']}** {quantity_text}"
                )
            
            message_parts.append("")
        
        # Add footer
        message_parts.extend([
            "💡 *Usa un item:* `/item <nombre>`",
            "💰 *Ver balance:* `/balance`",
            "📜 *Historial:* `/history`"
        ])
        
        await update.message.reply_text(
            "\n".join(message_parts),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in inventory handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al mostrar tu inventario. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()


async def item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /item command - show item details"""
    if not update.message or not update.effective_user:
        return
    
    user = update.effective_user
    
    # Check if item name was provided
    if not context.args:
        await update.message.reply_text(
            "❌ *Uso:* `/item <nombre_del_item>`\n\n"
            "💡 *Ejemplo:* `/item pocion_doble_besitos`\n"
            "💡 *Ver inventario:* `/inventory`",
            parse_mode="Markdown"
        )
        return
    
    item_key = context.args[0].lower()
    
    # Get database session
    db: Session = next(get_db())
    
    try:
        # Get user from database
        db_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ No estás registrado. Usa /start para registrarte."
            )
            return
        
        # Get item details
        item = inventory_service.get_item_by_key(item_key)
        
        if not item:
            await update.message.reply_text(
                f"❌ No se encontró el item: `{item_key}`\n\n"
                f"💡 *Consejo:* Usa `/inventory` para ver tus items.",
                parse_mode="Markdown"
            )
            return
        
        # Check if user has the item
        user_has_item = inventory_service.has_item(db_user.id, item_key)
        user_quantity = inventory_service.get_item_quantity(db_user.id, item_key)
        
        # Build item details message
        rarity_emoji = format_rarity_emoji(item["rarity"])
        type_emoji = format_item_type_emoji(item["item_type"])
        
        message_parts = [
            f"{type_emoji} *{item['name']}* {rarity_emoji}\n\n",
            f"📝 *Descripción:* {item['description']}\n",
            f"🏷️ *Tipo:* {item['item_type'].title()}\n",
            f"⭐ *Rareza:* {item['rarity'].title()}\n"
        ]
        
        if user_has_item:
            message_parts.append(f"📦 *En tu inventario:* {user_quantity}\n")
        else:
            message_parts.append("📦 *En tu inventario:* No tienes este item\n")
        
        if item["price_besitos"] > 0:
            message_parts.append(f"💰 *Precio:* {item['price_besitos']} 💋\n")
        
        # Add metadata info if available
        if item["item_metadata"]:
            metadata = item["item_metadata"]
            if "effect" in metadata:
                message_parts.append(f"✨ *Efecto:* {metadata['effect'].replace('_', ' ').title()}\n")
            if "duration" in metadata:
                minutes = metadata["duration"] // 60
                message_parts.append(f"⏰ *Duración:* {minutes} minutos\n")
            if "uses" in metadata:
                message_parts.append(f"🔢 *Usos:* {metadata['uses']}\n")
        
        message_parts.extend([
            "\n💡 *Consejos:*",
            "• Pronto podrás usar items en misiones",
            "• Los items narrativos desbloquearán historias",
            "• Los coleccionables completan sets especiales"
        ])
        
        await update.message.reply_text(
            "\n".join(message_parts),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in item handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Lo siento, hubo un error al mostrar el item. "
                "Por favor, intenta de nuevo más tarde."
            )
    finally:
        db.close()