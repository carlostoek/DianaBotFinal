import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from database.models import UserBalance, Transaction
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class BesitosService:
    """Service for managing besitos economy with atomic transactions"""
    
    @staticmethod
    def grant_besitos(user_id: int, amount: int, source: str, description: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Grant besitos to a user with atomic transaction
        
        Args:
            user_id: User ID
            amount: Amount of besitos to grant
            source: Source of besitos (e.g., 'daily_reward', 'mission', 'trivia')
            description: Optional description
            metadata: Optional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if amount <= 0:
            logger.error(f"Cannot grant non-positive amount: {amount}")
            return False
            
        db: Session = next(get_db())
        
        try:
            # Get or create user balance with lock
            balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).with_for_update().first()
            
            if not balance:
                balance = UserBalance(user_id=user_id, besitos=0, lifetime_besitos=0)
                db.add(balance)
            
            # Update balance
            balance.besitos += amount
            balance.lifetime_besitos += amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                transaction_type='earn',
                source=source,
                description=description,
                transaction_metadata=metadata
            )
            db.add(transaction)
            
            db.commit()
            
            # Publish event
            event_bus.publish("gamification.besitos_earned", {
                "user_id": user_id,
                "amount": amount,
                "source": source,
                "new_balance": balance.besitos,
                "description": description
            })
            
            logger.info(f"Granted {amount} besitos to user {user_id} from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant besitos to user {user_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def spend_besitos(user_id: int, amount: int, purpose: str, description: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Spend besitos from a user with atomic transaction
        
        Args:
            user_id: User ID
            amount: Amount of besitos to spend
            purpose: Purpose of spending (e.g., 'purchase', 'auction', 'gift')
            description: Optional description
            metadata: Optional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if amount <= 0:
            logger.error(f"Cannot spend non-positive amount: {amount}")
            return False
            
        db: Session = next(get_db())
        
        try:
            # Get user balance with lock
            balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).with_for_update().first()
            
            if not balance:
                logger.error(f"User {user_id} has no balance record")
                return False
            
            if balance.besitos < amount:
                logger.warning(f"Insufficient besitos for user {user_id}: {balance.besitos} < {amount}")
                return False
            
            # Update balance
            balance.besitos -= amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                transaction_type='spend',
                source=purpose,
                description=description,
                transaction_metadata=metadata
            )
            db.add(transaction)
            
            db.commit()
            
            # Publish event
            event_bus.publish("gamification.besitos_spent", {
                "user_id": user_id,
                "amount": amount,
                "purpose": purpose,
                "new_balance": balance.besitos,
                "description": description
            })
            
            logger.info(f"Spent {amount} besitos from user {user_id} for {purpose}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to spend besitos from user {user_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_balance(user_id: int) -> Optional[int]:
        """
        Get current besitos balance for a user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Current besitos balance, or None if user not found
        """
        db: Session = next(get_db())
        
        try:
            balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
            return balance.besitos if balance else 0
        except Exception as e:
            logger.error(f"Failed to get balance for user {user_id}: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_transaction_history(user_id: int, limit: int = 10) -> list:
        """
        Get transaction history for a user
        
        Args:
            user_id: User ID
            limit: Number of transactions to return
            
        Returns:
            list: List of transaction dictionaries
        """
        db: Session = next(get_db())
        
        try:
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(
                Transaction.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "type": t.transaction_type,
                    "source": t.source,
                    "description": t.description,
                    "created_at": t.created_at.isoformat() if hasattr(t.created_at, 'isoformat') else None
                }
                for t in transactions
            ]
        except Exception as e:
            logger.error(f"Failed to get transaction history for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_lifetime_besitos(user_id: int) -> Optional[int]:
        """
        Get lifetime besitos earned by a user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Lifetime besitos, or None if user not found
        """
        db: Session = next(get_db())
        
        try:
            balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
            return balance.lifetime_besitos if balance else 0
        except Exception as e:
            logger.error(f"Failed to get lifetime besitos for user {user_id}: {e}")
            return None
        finally:
            db.close()


# Global service instance
besitos_service = BesitosService()