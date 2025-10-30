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


def narrative_fragment_completed_handler(event: Dict[str, Any]) -> None:
    """Handler for narrative fragment completion events"""
    try:
        event_data = event['data']
        user_id = event_data.get('user_id')
        fragment_key = event_data.get('fragment_key')
        
        logger.info(f"User {user_id} completed fragment {fragment_key}")
        
        # TODO: Add besitos rewards based on fragment configuration
        # This will be implemented in the narrative-besitos integration
        
    except Exception as e:
        logger.error(f"Failed to handle narrative fragment completion: {e}")


def narrative_decision_made_handler(event: Dict[str, Any]) -> None:
    """Handler for narrative decision events"""
    try:
        event_data = event['data']
        user_id = event_data.get('user_id')
        fragment_key = event_data.get('fragment_key')
        decision_id = event_data.get('decision_id')
        
        logger.info(f"User {user_id} made decision {decision_id} in fragment {fragment_key}")
        
    except Exception as e:
        logger.error(f"Failed to handle narrative decision: {e}")


def setup_event_handlers() -> None:
    """Setup all event handlers"""
    # Log all user events
    event_bus.subscribe("user.registered", log_event_handler)
    event_bus.subscribe("user.activity", log_event_handler)
    event_bus.subscribe("user.command_executed", log_event_handler)
    
    # Log gamification events
    event_bus.subscribe("gamification.besitos_earned", log_event_handler)
    event_bus.subscribe("gamification.besitos_spent", log_event_handler)
    event_bus.subscribe("gamification.item_acquired", log_event_handler)
    event_bus.subscribe("gamification.item_used", log_event_handler)
    
    # Narrative events
    event_bus.subscribe("narrative.fragment_started", log_event_handler)
    event_bus.subscribe("narrative.decision_made", log_event_handler)
    event_bus.subscribe("narrative.fragment_completed", log_event_handler)
    event_bus.subscribe("narrative.level_completed", log_event_handler)
    
    # Narrative event handlers
    event_bus.subscribe("narrative.fragment_completed", narrative_fragment_completed_handler)
    event_bus.subscribe("narrative.decision_made", narrative_decision_made_handler)
    
    # Update user activity for all user events
    event_bus.subscribe("user.registered", update_user_activity_handler)
    event_bus.subscribe("user.activity", update_user_activity_handler)
    event_bus.subscribe("user.command_executed", update_user_activity_handler)
    
    logger.info("Event handlers setup completed")