import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from database.models import Item, UserInventory
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing user inventory with atomic operations"""
    
    @staticmethod
    def add_item_to_inventory(user_id: int, item_key: str, quantity: int = 1, source: str = "unknown") -> bool:
        """
        Add item to user inventory with atomic transaction
        
        Args:
            user_id: User ID
            item_key: Item key identifier
            quantity: Quantity to add
            source: Source of the item (e.g., 'purchase', 'reward', 'mission')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if quantity <= 0:
            logger.error(f"Cannot add non-positive quantity: {quantity}")
            return False
            
        db: Session = next(get_db())
        
        try:
            # Get item by key
            item = db.query(Item).filter(Item.item_key == item_key).first()
            if not item:
                logger.error(f"Item not found: {item_key}")
                return False
            
            # Get or create inventory entry
            inventory_entry = db.query(UserInventory).filter(
                UserInventory.user_id == user_id,
                UserInventory.item_id == item.id
            ).first()
            
            if inventory_entry:
                # Update existing entry
                inventory_entry.quantity += quantity
            else:
                # Create new entry
                inventory_entry = UserInventory(
                    user_id=user_id,
                    item_id=item.id,
                    quantity=quantity
                )
                db.add(inventory_entry)
            
            db.commit()
            
            # Publish event
            event_bus.publish("gamification.item_acquired", {
                "user_id": user_id,
                "item_key": item_key,
                "item_id": item.id,
                "item_name": item.name,
                "quantity": quantity,
                "source": source,
                "new_quantity": inventory_entry.quantity
            })
            
            logger.info(f"Added {quantity} {item_key} to user {user_id}'s inventory from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add item {item_key} to user {user_id}'s inventory: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def remove_item_from_inventory(user_id: int, item_key: str, quantity: int = 1, purpose: str = "unknown") -> bool:
        """
        Remove item from user inventory with atomic transaction
        
        Args:
            user_id: User ID
            item_key: Item key identifier
            quantity: Quantity to remove
            purpose: Purpose of removal (e.g., 'use', 'gift', 'sell')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if quantity <= 0:
            logger.error(f"Cannot remove non-positive quantity: {quantity}")
            return False
            
        db: Session = next(get_db())
        
        try:
            # Get item by key
            item = db.query(Item).filter(Item.item_key == item_key).first()
            if not item:
                logger.error(f"Item not found: {item_key}")
                return False
            
            # Get inventory entry
            inventory_entry = db.query(UserInventory).filter(
                UserInventory.user_id == user_id,
                UserInventory.item_id == item.id
            ).first()
            
            if not inventory_entry:
                logger.error(f"User {user_id} doesn't have item {item_key}")
                return False
            
            if inventory_entry.quantity < quantity:
                logger.error(f"Insufficient quantity: {inventory_entry.quantity} < {quantity}")
                return False
            
            # Update or remove entry
            if inventory_entry.quantity == quantity:
                # Remove entry completely
                db.delete(inventory_entry)
            else:
                # Reduce quantity
                inventory_entry.quantity -= quantity
            
            db.commit()
            
            # Publish event
            event_bus.publish("gamification.item_used", {
                "user_id": user_id,
                "item_key": item_key,
                "item_id": item.id,
                "item_name": item.name,
                "quantity": quantity,
                "purpose": purpose,
                "remaining_quantity": inventory_entry.quantity if inventory_entry.quantity > quantity else 0
            })
            
            logger.info(f"Removed {quantity} {item_key} from user {user_id}'s inventory for {purpose}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove item {item_key} from user {user_id}'s inventory: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_user_inventory(user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's complete inventory with item details
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of inventory items with details
        """
        db: Session = next(get_db())
        
        try:
            inventory = db.query(
                UserInventory,
                Item
            ).join(
                Item, UserInventory.item_id == Item.id
            ).filter(
                UserInventory.user_id == user_id
            ).order_by(
                Item.item_type,
                Item.rarity.desc(),
                Item.name
            ).all()
            
            result = []
            for inventory_entry, item in inventory:
                result.append({
                    "inventory_id": inventory_entry.id,
                    "item_id": item.id,
                    "item_key": item.item_key,
                    "name": item.name,
                    "description": item.description,
                    "item_type": item.item_type,
                    "rarity": item.rarity,
                    "quantity": inventory_entry.quantity,
                    "acquired_at": inventory_entry.acquired_at.isoformat() if hasattr(inventory_entry.acquired_at, 'isoformat') else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get inventory for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def has_item(user_id: int, item_key: str, min_quantity: int = 1) -> bool:
        """
        Check if user has item with minimum quantity
        
        Args:
            user_id: User ID
            item_key: Item key identifier
            min_quantity: Minimum required quantity
            
        Returns:
            bool: True if user has the item with sufficient quantity
        """
        db: Session = next(get_db())
        
        try:
            inventory_entry = db.query(UserInventory).join(
                Item, UserInventory.item_id == Item.id
            ).filter(
                UserInventory.user_id == user_id,
                Item.item_key == item_key
            ).first()
            
            if inventory_entry and inventory_entry.quantity >= min_quantity:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to check item {item_key} for user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_item_quantity(user_id: int, item_key: str) -> int:
        """
        Get quantity of specific item in user's inventory
        
        Args:
            user_id: User ID
            item_key: Item key identifier
            
        Returns:
            int: Quantity of the item, 0 if not found
        """
        db: Session = next(get_db())
        
        try:
            inventory_entry = db.query(UserInventory).join(
                Item, UserInventory.item_id == Item.id
            ).filter(
                UserInventory.user_id == user_id,
                Item.item_key == item_key
            ).first()
            
            return inventory_entry.quantity if inventory_entry else 0
            
        except Exception as e:
            logger.error(f"Failed to get quantity of {item_key} for user {user_id}: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def get_item_by_key(item_key: str) -> Optional[Dict[str, Any]]:
        """
        Get item details by key
        
        Args:
            item_key: Item key identifier
            
        Returns:
            dict: Item details, or None if not found
        """
        db: Session = next(get_db())
        
        try:
            item = db.query(Item).filter(Item.item_key == item_key).first()
            
            if item:
                return {
                    "id": item.id,
                    "item_key": item.item_key,
                    "name": item.name,
                    "description": item.description,
                    "item_type": item.item_type,
                    "rarity": item.rarity,
                    "price_besitos": item.price_besitos,
                    "item_metadata": item.item_metadata,
                    "created_at": item.created_at.isoformat() if hasattr(item.created_at, 'isoformat') else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get item {item_key}: {e}")
            return None
        finally:
            db.close()


# Global service instance
inventory_service = InventoryService()