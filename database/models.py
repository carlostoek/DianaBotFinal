from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
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
    telegram_id = Column(BigInteger, nullable=True, index=True)
    
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


class UserBalance(Base):
    """User balance model for besitos economy"""
    __tablename__ = "user_balances"

    user_id = Column(Integer, primary_key=True)
    besitos = Column(Integer, default=0, nullable=False)
    lifetime_besitos = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserBalance(user_id={self.user_id}, besitos={self.besitos})>"


class Transaction(Base):
    """Transaction model for besitos economy"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'earn', 'spend', 'gift'
    source = Column(String(100), nullable=False)  # 'mission', 'purchase', 'daily_reward', etc.
    description = Column(Text, nullable=True)
    transaction_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Transaction(user_id={self.user_id}, amount={self.amount}, type={self.transaction_type})>"


class Item(Base):
    """Item model for the inventory system"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String(50), nullable=False)  # 'narrative_key', 'collectible', 'power_up', 'consumable'
    rarity = Column(String(50), default='common')  # 'common', 'rare', 'epic', 'legendary'
    price_besitos = Column(Integer, default=0)
    item_metadata = Column(JSON, nullable=True)  # effects, requirements, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Item(item_key={self.item_key}, name={self.name}, type={self.item_type})>"

    def to_dict(self):
        """Convert item to dictionary for API responses"""
        return {
            "id": self.id,
            "item_key": self.item_key,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "rarity": self.rarity,
            "price_besitos": self.price_besitos,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class UserInventory(Base):
    """User inventory model for storing user items"""
    __tablename__ = "user_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    item_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Integer, default=1)
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserInventory(user_id={self.user_id}, item_id={self.item_id}, quantity={self.quantity})>"

    def to_dict(self):
        """Convert inventory entry to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "acquired_at": self.acquired_at.isoformat() if hasattr(self.acquired_at, 'isoformat') else None
        }


class NarrativeLevel(Base):
    """Narrative level model for story progression"""
    __tablename__ = "narrative_levels"

    id = Column(Integer, primary_key=True, index=True)
    level_key = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    unlock_conditions = Column(JSON, nullable=True)  # besitos, items, achievements requeridos
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<NarrativeLevel(level_key={self.level_key}, title={self.title})>"


class NarrativeFragment(Base):
    """Narrative fragment model for story content"""
    __tablename__ = "narrative_fragments"

    id = Column(Integer, primary_key=True, index=True)
    fragment_key = Column(String(100), unique=True, nullable=False, index=True)
    level_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    unlock_conditions = Column(JSON, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    is_starting_fragment = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    progress = relationship("UserNarrativeProgress", back_populates="fragment")

    def __repr__(self):
        return f"<NarrativeFragment(fragment_key={self.fragment_key}, title={self.title})>"


class UserNarrativeProgress(Base):
    """User narrative progress tracking"""
    __tablename__ = "user_narrative_progress"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    fragment_id = Column(Integer, ForeignKey("narrative_fragments.id"), primary_key=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    choices_made = Column(JSON, nullable=True)  # decisiones tomadas en este fragmento
    narrative_flags = Column(JSON, nullable=True)  # flags narrativos acumulados
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fragment = relationship("NarrativeFragment", back_populates="progress")

    def __repr__(self):
        return f"<UserNarrativeProgress(user_id={self.user_id}, fragment_id={self.fragment_id})>"


class Mission(Base):
    """Mission model for gamification system"""
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_key = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    mission_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'narrative', 'special'
    recurrence = Column(String(50), nullable=False)  # 'once', 'daily', 'weekly'
    requirements = Column(JSON, nullable=False)  # qué debe hacer el usuario
    rewards = Column(JSON, nullable=False)  # besitos, items, achievements
    expiry_date = Column(DateTime(timezone=True), nullable=True)  # para misiones temporales
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Mission(mission_key={self.mission_key}, title={self.title}, type={self.mission_type})>"

    def to_dict(self):
        """Convert mission to dictionary for API responses"""
        return {
            "id": self.id,
            "mission_key": self.mission_key,
            "title": self.title,
            "description": self.description,
            "mission_type": self.mission_type,
            "recurrence": self.recurrence,
            "requirements": self.requirements,
            "rewards": self.rewards,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class UserMission(Base):
    """User mission progress tracking"""
    __tablename__ = "user_missions"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), primary_key=True)
    status = Column(String(50), nullable=False)  # 'active', 'completed', 'expired'
    progress = Column(JSON, nullable=True)  # progreso actual hacia requisitos
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<UserMission(user_id={self.user_id}, mission_id={self.mission_id}, status={self.status})>"

    def to_dict(self):
        """Convert user mission to dictionary"""
        return {
            "user_id": self.user_id,
            "mission_id": self.mission_id,
            "status": self.status,
            "progress": self.progress,
            "assigned_at": self.assigned_at.isoformat() if hasattr(self.assigned_at, 'isoformat') else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Achievement(Base):
    """Achievement model for gamification system"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_emoji = Column(String(50), nullable=True)
    points = Column(Integer, default=0)
    reward_besitos = Column(Integer, default=0)
    reward_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    unlock_conditions = Column(JSON, nullable=False)  # criterios para desbloquear
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Achievement(achievement_key={self.achievement_key}, name={self.name})>"

    def to_dict(self):
        """Convert achievement to dictionary for API responses"""
        return {
            "id": self.id,
            "achievement_key": self.achievement_key,
            "name": self.name,
            "description": self.description,
            "icon_emoji": self.icon_emoji,
            "points": self.points,
            "reward_besitos": self.reward_besitos,
            "reward_item_id": self.reward_item_id,
            "unlock_conditions": self.unlock_conditions,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class UserAchievement(Base):
    """User achievement progress tracking"""
    __tablename__ = "user_achievements"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), primary_key=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(JSON, nullable=True)  # para logros progresivos

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"

    def to_dict(self):
        """Convert user achievement to dictionary"""
        return {
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "unlocked_at": self.unlocked_at.isoformat() if hasattr(self.unlocked_at, 'isoformat') else None,
            "progress": self.progress
        }