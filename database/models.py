from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_premium = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    
    # User state and progress
    current_state = Column(String(50), default="start")
    current_story = Column(String(50), nullable=True)
    current_chapter = Column(String(50), nullable=True)
    
    # Stats
    total_messages = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    total_stories_started = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "is_premium": self.is_premium,
            "current_state": self.current_state,
            "total_messages": self.total_messages,
            "total_commands": self.total_commands,
            "total_stories_started": self.total_stories_started,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None,
            "last_active": self.last_active.isoformat() if hasattr(self.last_active, 'isoformat') else None
        }


class EventLog(Base):
    """Event log model for storing system events"""
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    telegram_id = Column(Integer, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EventLog(event_type={self.event_type}, user_id={self.user_id})>"

    def to_dict(self):
        """Convert event log to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "user_id": self.user_id,
            "telegram_id": self.telegram_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }