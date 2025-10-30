import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import EventLog, User
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


def log_event_handler(event: Dict[str, Any]) -> None:
    """Handler to log events to database"""
    db: Session = next(get_db())
    
    try:
        event_log = EventLog(
            event_type=event['type'],
            event_data=event['data'],
            user_id=event['data'].get('user_id'),
            telegram_id=event['data'].get('telegram_id')
        )
        
        db.add(event_log)
        db.commit()
        
        logger.info(f"Event logged: {event['type']} - User: {event['data'].get('telegram_id')}")
        
    except Exception as e:
        logger.error(f"Failed to log event {event['type']}: {e}")
        db.rollback()
    finally:
        db.close()


def update_user_activity_handler(event: Dict[str, Any]) -> None:
    """Handler to update user last_active timestamp"""
    db: Session = next(get_db())
    
    try:
        user_id = event['data'].get('user_id')
        telegram_id = event['data'].get('telegram_id')
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        elif telegram_id:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
        else:
            return
            
        if user:
            from sqlalchemy import func
            user.last_active = func.now()
            db.commit()
            logger.debug(f"Updated last_active for user: {user.telegram_id}")
            
    except Exception as e:
        logger.error(f"Failed to update user activity: {e}")
        db.rollback()
    finally:
        db.close()


def setup_event_handlers() -> None:
    """Setup all event handlers"""
    # Log all user events
    event_bus.subscribe("user.registered", log_event_handler)
    event_bus.subscribe("user.activity", log_event_handler)
    event_bus.subscribe("user.command_executed", log_event_handler)
    
    # Update user activity for all user events
    event_bus.subscribe("user.registered", update_user_activity_handler)
    event_bus.subscribe("user.activity", update_user_activity_handler)
    event_bus.subscribe("user.command_executed", update_user_activity_handler)
    
    logger.info("Event handlers setup completed")