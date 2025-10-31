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
            "expiry_date": self.expiry_date,
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
            "completed_at": self.completed_at,
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


class Subscription(Base):
    """Subscription model for VIP users"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    subscription_type = Column(String(50), nullable=False)  # 'monthly', 'yearly', 'lifetime'
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False)  # 'active', 'expired', 'cancelled'
    payment_reference = Column(String(255), nullable=True)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, type={self.subscription_type}, status={self.status})>"

    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_type": self.subscription_type,
            "start_date": self.start_date.isoformat() if hasattr(self.start_date, 'isoformat') else None,
            "end_date": self.end_date.isoformat() if hasattr(self.end_date, 'isoformat') else None,
            "status": self.status,
            "payment_reference": self.payment_reference,
            "auto_renew": self.auto_renew,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class Channel(Base):
    """Channel model for Telegram channels management"""
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, unique=True, nullable=False, index=True)
    channel_type = Column(String(50), nullable=False)  # 'free', 'vip', 'announcements'
    channel_username = Column(String(255), nullable=True)
    channel_title = Column(String(255), nullable=False)
    settings = Column(JSON, nullable=True)  # welcome_message, rules, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Channel(channel_id={self.channel_id}, type={self.channel_type}, title={self.channel_title})>"

    def to_dict(self):
        """Convert channel to dictionary"""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "channel_type": self.channel_type,
            "channel_username": self.channel_username,
            "channel_title": self.channel_title,
            "settings": self.settings,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class UserReaction(Base):
    """User reaction tracking for gamified reactions"""
    __tablename__ = "user_reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    post_id = Column(Integer, nullable=False, index=True)
    emoji = Column(String(50), nullable=False)  # The reaction emoji
    rewarded_at = Column(DateTime(timezone=True), nullable=True)  # When reward was given
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserReaction(user_id={self.user_id}, post_id={self.post_id}, emoji={self.emoji})>"

    def to_dict(self):
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "post_id": self.post_id,
            "post_type": self.post_type,
            "content": self.content,
            "post_metadata": self.post_metadata,
            "reaction_rewards": self.reaction_rewards,
            "scheduled_for": self.scheduled_for,
            "published_at": self.published_at,
            "status": self.status,
            "recurrence": self.recurrence,
            "is_protected": self.is_protected,
            "linked_mission_id": self.linked_mission_id,
            "linked_fragment_id": self.linked_fragment_id,
            "created_at": self.created_at
        }


class ConfigTemplate(Base):
    """Configuration template model for unified configuration management"""
    __tablename__ = "config_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_key = Column(String(100), unique=True, nullable=False, index=True)
    template_type = Column(String(50), nullable=False)  # 'experience', 'event', 'mission_chain', 'trivia_set'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_schema = Column(JSON, nullable=False)  # JSON schema for validation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instances = relationship("ConfigInstance", back_populates="template")

    def __repr__(self):
        return f"<ConfigTemplate(template_key={self.template_key}, name={self.name}, type={self.template_type})>"

    def to_dict(self):
        """Convert config template to dictionary"""
        return {
            "id": self.id,
            "template_key": self.template_key,
            "template_type": self.template_type,
            "name": self.name,
            "description": self.description,
            "template_schema": self.template_schema,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ConfigInstance(Base):
    """Configuration instance model for specific configurations"""
    __tablename__ = "config_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("config_templates.id"), nullable=False)
    instance_data = Column(JSON, nullable=False)  # configuration specific data
    created_by = Column(Integer, nullable=True)  # admin user id
    status = Column(String(50), default='draft')  # 'draft', 'active', 'archived', 'testing'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    template = relationship("ConfigTemplate", back_populates="instances")
    versions = relationship("ConfigVersion", back_populates="instance")

    def __repr__(self):
        return f"<ConfigInstance(id={self.id}, template_id={self.template_id}, status={self.status})>"

    def to_dict(self):
        """Convert config instance to dictionary"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "instance_data": self.instance_data,
            "created_by": self.created_by,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ConfigVersion(Base):
    """Configuration version model for tracking changes"""
    __tablename__ = "config_versions"

    id = Column(Integer, primary_key=True, index=True)
    config_instance_id = Column(Integer, ForeignKey("config_instances.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    changed_by = Column(Integer, nullable=True)  # admin user id
    changes = Column(JSON, nullable=False)  # diff of changes
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    can_rollback = Column(Boolean, default=True)

    # Relationships
    instance = relationship("ConfigInstance", back_populates="versions")

    def __repr__(self):
        return f"<ConfigVersion(instance_id={self.config_instance_id}, version={self.version_number})>"

    def to_dict(self):
        """Convert config version to dictionary"""
        return {
            "id": self.id,
            "config_instance_id": self.config_instance_id,
            "version_number": self.version_number,
            "changed_by": self.changed_by,
            "changes": self.changes,
            "change_reason": self.change_reason,
            "created_at": self.created_at,
            "can_rollback": self.can_rollback
        }


class ChannelPost(Base):
    """Channel post model for tracking posts in channels"""
    __tablename__ = "channel_posts"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    post_id = Column(BigInteger, nullable=True, index=True)  # Nullable for scheduled posts
    post_type = Column(String(50), nullable=False)  # 'narrative', 'mission', 'announcement', 'trivia', 'event'
    content = Column(Text, nullable=True)
    post_metadata = Column(JSON, nullable=True)  # reactions, views, etc.
    reaction_rewards = Column(JSON, nullable=True)  # emoji -> reward configuration
    scheduled_for = Column(DateTime(timezone=True), nullable=True)  # When to publish
    published_at = Column(DateTime(timezone=True), nullable=True)  # When actually published
    status = Column(String(50), default='draft')  # 'draft', 'scheduled', 'published', 'cancelled'
    recurrence = Column(String(50), nullable=True)  # 'daily', 'weekly', 'monthly', None
    is_protected = Column(Boolean, default=False)  # Protect content from forwarding
    linked_mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    linked_fragment_id = Column(Integer, ForeignKey("narrative_fragments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChannelPost(channel_id={self.channel_id}, post_id={self.post_id}, type={self.post_type})>"

    def to_dict(self):
        """Convert channel post to dictionary"""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "post_id": self.post_id,
            "post_type": self.post_type,
            "content": self.content,
            "post_metadata": self.post_metadata,
            "reaction_rewards": self.reaction_rewards,
            "scheduled_for": self.scheduled_for,
            "published_at": self.published_at,
            "status": self.status,
            "recurrence": self.recurrence,
            "is_protected": self.is_protected,
            "linked_mission_id": self.linked_mission_id,
            "linked_fragment_id": self.linked_fragment_id,
            "created_at": self.created_at
        }


class AdminUser(Base):
    """Admin user model for API authentication"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='admin')  # 'owner', 'admin', 'moderator', 'content_creator'
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, nullable=True)  # Additional permissions beyond role
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AdminUser(username={self.username}, role={self.role})>"

    def to_dict(self):
        """Convert admin user to dictionary (without sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "permissions": self.permissions,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }