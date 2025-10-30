"""
Core user state management functions
"""
from sqlalchemy.orm import Session
from database.models import User


def get_user_state(db: Session, telegram_id: int) -> str:
    """Get current state of a user"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    return user.current_state if user else "start"


def set_user_state(db: Session, telegram_id: int, state: str) -> bool:
    """Set current state of a user"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.current_state = state
        db.commit()
        return True
    return False


def update_user_activity(db: Session, telegram_id: int) -> bool:
    """Update user's last active timestamp"""
    from sqlalchemy import func
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.last_active = func.now()
        db.commit()
        return True
    return False


def increment_user_messages(db: Session, telegram_id: int) -> bool:
    """Increment user's total message count"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.total_messages += 1
        db.commit()
        return True
    return False


def increment_user_commands(db: Session, telegram_id: int) -> bool:
    """Increment user's total command count"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.total_commands += 1
        db.commit()
        return True
    return False