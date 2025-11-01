from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, JSON, ForeignKey, UniqueConstraint, Index, Date, Float, Numeric, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
from datetime import datetime


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

    # Relationships
    bids = relationship("Bid", back_populates="user")
    purchases = relationship("UserPurchase", back_populates="user")
    archetype_data = relationship("UserArchetype", back_populates="user", uselist=False)

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

    # Relationships
    auctions = relationship("Auction", back_populates="item")

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
    is_secret = Column(Boolean, default=False)  # Fragmento oculto que requiere descubrimiento
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


class ContentReaction(Base):
    """Content reaction model for tracking user reactions to various content types"""
    __tablename__ = "content_reactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_type = Column(String(50), nullable=False)  # narrative_fragment, channel_post, mission
    content_id = Column(Integer, nullable=False)
    reaction_type = Column(String(50), nullable=False)  # like, love, fire, star, custom
    
    # Recompensa
    besitos_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'content_type', 'content_id', 'reaction_type', 
                        name='unique_user_content_reaction'),
        Index('idx_content_reactions', 'content_type', 'content_id'),
    )

    def __repr__(self):
        return f"<ContentReaction(user_id={self.user_id}, content_type={self.content_type}, reaction_type={self.reaction_type})>"

    def to_dict(self):
        """Convert content reaction to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_type": self.content_type,
            "content_id": self.content_id,
            "reaction_type": self.reaction_type,
            "besitos_earned": self.besitos_earned,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class ReactionRewardConfig(Base):
    """Reaction reward configuration model"""
    __tablename__ = "reaction_reward_configs"
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False)
    reaction_type = Column(String(50), nullable=False)
    besitos_reward = Column(Integer, default=0)
    
    # Límites
    max_per_user_per_content = Column(Integer, default=1)
    max_per_user_per_day = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('content_type', 'reaction_type', name='unique_content_reaction_config'),
    )

    def __repr__(self):
        return f"<ReactionRewardConfig(content_type={self.content_type}, reaction_type={self.reaction_type}, reward={self.besitos_reward})>"

    def to_dict(self):
        """Convert reaction reward config to dictionary"""
        return {
            "id": self.id,
            "content_type": self.content_type,
            "reaction_type": self.reaction_type,
            "besitos_reward": self.besitos_reward,
            "max_per_user_per_content": self.max_per_user_per_content,
            "max_per_user_per_day": self.max_per_user_per_day,
            "is_active": self.is_active
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


class Auction(Base):
    """Auction model for real-time item auctions"""
    __tablename__ = "auctions"

    auction_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    auction_type = Column(String(50), nullable=False, default='standard')  # 'standard', 'dutch', 'silent'
    start_price = Column(Integer, nullable=False)
    current_bid = Column(Integer, nullable=False)
    current_bidder_id = Column(BigInteger, ForeignKey("users.id"))
    winner_id = Column(BigInteger, ForeignKey("users.id"))
    status = Column(String(50), nullable=False, default='active')  # 'active', 'closed', 'cancelled'
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False)
    extended_end_time = Column(DateTime(timezone=True))
    min_bid_increment = Column(Integer, nullable=False, default=10)
    bid_count = Column(Integer, nullable=False, default=0)
    auction_metadata = Column(JSON, nullable=True)  # Additional auction settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    item = relationship("Item", back_populates="auctions")
    current_bidder = relationship("User", foreign_keys=[current_bidder_id])
    winner = relationship("User", foreign_keys=[winner_id])
    bids = relationship("Bid", back_populates="auction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Auction(auction_id={self.auction_id}, item_id={self.item_id}, status={self.status})>"

    def to_dict(self):
        """Convert auction to dictionary"""
        return {
            "auction_id": self.auction_id,
            "item_id": self.item_id,
            "auction_type": self.auction_type,
            "start_price": self.start_price,
            "current_bid": self.current_bid,
            "current_bidder_id": self.current_bidder_id,
            "winner_id": self.winner_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "extended_end_time": self.extended_end_time,
            "min_bid_increment": self.min_bid_increment,
            "bid_count": self.bid_count,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Bid(Base):
    """Bid model for auction bids"""
    __tablename__ = "bids"

    bid_id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.auction_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    is_winning = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", back_populates="bids")

    def __repr__(self):
        return f"<Bid(bid_id={self.bid_id}, auction_id={self.auction_id}, user_id={self.user_id}, amount={self.amount})>"

    def to_dict(self):
        """Convert bid to dictionary"""
        return {
            "bid_id": self.bid_id,
            "auction_id": self.auction_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "is_winning": self.is_winning,
            "created_at": self.created_at
        }


class SecretCode(Base):
    """Secret code model for hidden fragment discovery"""
    __tablename__ = "secret_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    fragment_key = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SecretCode(code={self.code}, fragment_key={self.fragment_key})>"

    def to_dict(self):
        """Convert secret code to dictionary"""
        return {
            "id": self.id,
            "code": self.code,
            "fragment_key": self.fragment_key,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class UserSecretDiscovery(Base):
    """User secret discovery tracking"""
    __tablename__ = "user_secret_discoveries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    secret_code_id = Column(Integer, ForeignKey("secret_codes.id"), nullable=True, index=True)
    fragment_key = Column(String(100), nullable=False, index=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserSecretDiscovery(user_id={self.user_id}, fragment_key={self.fragment_key})>"

    def to_dict(self):
        """Convert user secret discovery to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "secret_code_id": self.secret_code_id,
            "fragment_key": self.fragment_key,
            "discovered_at": self.discovered_at.isoformat() if hasattr(self.discovered_at, 'isoformat') else None
        }


class AnalyticsEvent(Base):
    """Analytics event model for tracking user interactions and system events"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_metadata = Column(JSON, nullable=True)  # Additional event-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index('idx_analytics_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_analytics_type_timestamp', 'event_type', 'timestamp'),
    )

    def __repr__(self):
        return f"<AnalyticsEvent(event_type={self.event_type}, user_id={self.user_id}, timestamp={self.timestamp})>"

    def to_dict(self):
        """Convert analytics event to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, 'isoformat') else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class DailyMetrics(Base):
    """Daily aggregated metrics for analytics"""
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # User metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    
    # Engagement metrics
    total_messages = Column(Integer, default=0)
    total_reactions = Column(Integer, default=0)
    total_missions_completed = Column(Integer, default=0)
    total_achievements_unlocked = Column(Integer, default=0)
    
    # Economic metrics
    total_besitos_earned = Column(Integer, default=0)
    total_besitos_spent = Column(Integer, default=0)
    
    # Content metrics
    total_content_views = Column(Integer, default=0)
    total_trivia_answered = Column(Integer, default=0)
    total_auction_participations = Column(Integer, default=0)
    
    # Retention metrics
    retention_rate = Column(Float, default=0.0)  # Percentage of returning users
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('date', name='unique_daily_metrics_date'),
    )

    def __repr__(self):
        return f"<DailyMetrics(date={self.date}, active_users={self.active_users}, total_messages={self.total_messages})>"

    def to_dict(self):
        """Convert daily metrics to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if hasattr(self.date, 'isoformat') else None,
            "total_users": self.total_users,
            "active_users": self.active_users,
            "new_users": self.new_users,
            "total_messages": self.total_messages,
            "total_reactions": self.total_reactions,
            "total_missions_completed": self.total_missions_completed,
            "total_achievements_unlocked": self.total_achievements_unlocked,
            "total_besitos_earned": self.total_besitos_earned,
            "total_besitos_spent": self.total_besitos_spent,
            "total_content_views": self.total_content_views,
            "total_trivia_answered": self.total_trivia_answered,
            "total_auction_participations": self.total_auction_participations,
            "retention_rate": self.retention_rate,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else None
        }


class UserSessionMetrics(Base):
    """User session metrics for detailed user behavior analysis"""
    __tablename__ = "user_session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Session metrics
    session_duration = Column(Integer, default=0)  # in seconds
    messages_sent = Column(Integer, default=0)
    reactions_added = Column(Integer, default=0)
    missions_completed = Column(Integer, default=0)
    achievements_unlocked = Column(Integer, default=0)
    besitos_earned = Column(Integer, default=0)
    content_views = Column(Integer, default=0)
    trivia_answered = Column(Integer, default=0)
    
    # Platform info
    platform = Column(String(50), default='telegram')
    device_info = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index('idx_session_user_start', 'user_id', 'start_time'),
        Index('idx_session_duration', 'session_duration'),
    )

    def __repr__(self):
        return f"<UserSessionMetrics(user_id={self.user_id}, session_id={self.session_id}, duration={self.session_duration})>"

    def to_dict(self):
        """Convert user session metrics to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if hasattr(self.start_time, 'isoformat') else None,
            "end_time": self.end_time.isoformat() if hasattr(self.end_time, 'isoformat') else None,
            "session_duration": self.session_duration,
            "messages_sent": self.messages_sent,
            "reactions_added": self.reactions_added,
            "missions_completed": self.missions_completed,
            "achievements_unlocked": self.achievements_unlocked,
            "besitos_earned": self.besitos_earned,
            "content_views": self.content_views,
            "trivia_answered": self.trivia_answered,
            "platform": self.platform,
            "device_info": self.device_info,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None
        }


class ShopItem(Base):
    """Shop item model for commerce system"""
    __tablename__ = "shop_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # narrative_unlock, experience_unlock, vip_preview, power_up, cosmetic
    category = Column(String(50))  # content, subscription, boost, collectible
    
    # Pricing
    price_besitos = Column(Integer, nullable=True)
    price_real = Column(Numeric(10, 2), nullable=True)  # Precio en moneda real
    currency = Column(String(3), default='USD')
    
    # Disponibilidad
    is_available = Column(Boolean, default=True)
    stock = Column(Integer, nullable=True)  # NULL = stock ilimitado
    is_limited_time = Column(Boolean, default=False)
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    
    # Descuentos
    discount_percentage = Column(Integer, default=0)
    discount_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    rarity = Column(String(50))  # common, rare, epic, legendary
    image_url = Column(String(500), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Desbloqueos
    unlocks_content_type = Column(String(50), nullable=True)  # narrative, experience, mission, channel
    unlocks_content_id = Column(Integer, nullable=True)
    unlocks_data = Column(JSON, nullable=True)
    # Ejemplo:
    # {
    #     "narrative_fragments": [10, 11, 12],
    #     "experiences": [3],
    #     "vip_days": 30
    # }
    
    # Requisitos para comprar
    purchase_requirements = Column(JSON, nullable=True)
    # Ejemplo:
    # {
    #     "min_level": 10,
    #     "vip_required": false,
    #     "required_items": [1, 2]
    # }
    
    # Métricas
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    conversion_rate = Column(Numeric(5, 2), default=0.00)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    purchases = relationship("UserPurchase", back_populates="shop_item")
    game_item = relationship("Item", back_populates="shop_item", uselist=False)

    def __repr__(self):
        return f"<ShopItem(name={self.name}, type={self.type}, price_besitos={self.price_besitos})>"

    def to_dict(self):
        """Convert shop item to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "price_besitos": self.price_besitos,
            "price_real": float(self.price_real) if self.price_real else None,
            "currency": self.currency,
            "is_available": self.is_available,
            "stock": self.stock,
            "is_limited_time": self.is_limited_time,
            "available_from": self.available_from.isoformat() if self.available_from else None,
            "available_until": self.available_until.isoformat() if self.available_until else None,
            "discount_percentage": self.discount_percentage,
            "discount_expires_at": self.discount_expires_at.isoformat() if self.discount_expires_at else None,
            "rarity": self.rarity,
            "image_url": self.image_url,
            "tags": self.tags,
            "unlocks_content_type": self.unlocks_content_type,
            "unlocks_content_id": self.unlocks_content_id,
            "unlocks_data": self.unlocks_data,
            "purchase_requirements": self.purchase_requirements,
            "view_count": self.view_count,
            "purchase_count": self.purchase_count,
            "conversion_rate": float(self.conversion_rate) if self.conversion_rate else 0.0,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else None
        }


class UserPurchase(Base):
    """User purchase model for commerce system"""
    __tablename__ = "user_purchases"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shop_item_id = Column(Integer, ForeignKey('shop_items.id'), nullable=False)
    
    # Detalles de compra
    purchase_type = Column(String(50))  # besitos, real_money, reward, gift
    amount_paid = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    besitos_spent = Column(Integer, nullable=True)
    
    # Estado
    status = Column(String(50), default='pending')  # pending, completed, failed, refunded
    
    # Telegram Payment info
    telegram_payment_charge_id = Column(String(255), nullable=True)
    provider_payment_charge_id = Column(String(255), nullable=True)
    
    # Metadata
    unlocks_applied = Column(Boolean, default=False)
    unlocks_applied_at = Column(DateTime, nullable=True)
    
    purchase_date = Column(DateTime, default=datetime.utcnow)
    
    # Tracking
    purchase_context = Column(JSON, nullable=True)
    # Ejemplo:
    # {
    #     "source": "narrative_unlock_prompt",
    #     "fragment_id": 15,
    #     "offer_type": "contextual"
    # }
    
    # Relaciones
    user = relationship("User", back_populates="purchases")
    shop_item = relationship("ShopItem", back_populates="purchases")

    def __repr__(self):
        return f"<UserPurchase(user_id={self.user_id}, shop_item_id={self.shop_item_id}, status={self.status})>"

    def to_dict(self):
        """Convert user purchase to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "shop_item_id": self.shop_item_id,
            "purchase_type": self.purchase_type,
            "amount_paid": float(self.amount_paid) if self.amount_paid else None,
            "currency": self.currency,
            "besitos_spent": self.besitos_spent,
            "status": self.status,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
            "unlocks_applied": self.unlocks_applied,
            "unlocks_applied_at": self.unlocks_applied_at.isoformat() if self.unlocks_applied_at else None,
            "purchase_date": self.purchase_date.isoformat() if hasattr(self.purchase_date, 'isoformat') else None,
            "purchase_context": self.purchase_context
        }


class UserArchetype(Base):
    """User archetype model for personalization"""
    __tablename__ = "user_archetypes"
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    primary_archetype = Column(String(50), nullable=False)
    secondary_archetype = Column(String(50), nullable=True)
    confidence_score = Column(Numeric(3, 2), default=0.00)  # 0.00 - 1.00
    
    # Scores por arquetipo
    archetype_scores = Column(JSON)
    # Ejemplo:
    # {
    #     "NARRATIVE_LOVER": 0.85,
    #     "COLLECTOR": 0.62,
    #     "COMPETITIVE": 0.45,
    #     "SOCIAL": 0.38,
    #     "COMPLETIONIST": 0.71
    # }
    
    # Comportamiento detectado
    behavior_patterns = Column(JSON)
    # Ejemplo:
    # {
    #     "content_preference": "narrative",
    #     "spending_tendency": "high",
    #     "engagement_frequency": "daily",
    #     "social_activity": "moderate"
    # }
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="archetype_data")

    def __repr__(self):
        return f"<UserArchetype(user_id={self.user_id}, primary={self.primary_archetype}, confidence={self.confidence_score})>"

    def to_dict(self):
        """Convert user archetype to dictionary"""
        return {
            "user_id": self.user_id,
            "primary_archetype": self.primary_archetype,
            "secondary_archetype": self.secondary_archetype,
            "confidence_score": float(self.confidence_score) if self.confidence_score else 0.0,
            "archetype_scores": self.archetype_scores,
            "behavior_patterns": self.behavior_patterns,
            "last_updated": self.last_updated.isoformat() if hasattr(self.last_updated, 'isoformat') else None,
            "last_analyzed": self.last_analyzed.isoformat() if hasattr(self.last_analyzed, 'isoformat') else None
        }


class VIPSubscription(Base):
    """VIP subscription model for commerce system"""
    __tablename__ = "vip_subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscription_type = Column(String(50), nullable=False)  # monthly, annual, lifetime, trial
    
    # Fechas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL para lifetime
    
    # Estado
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    
    # Pago
    payment_method = Column(String(50))
    amount_paid = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    
    # Telegram Payment info
    telegram_payment_charge_id = Column(String(255), nullable=True)
    
    # Tracking
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="vip_subscriptions")

    def __repr__(self):
        return f"<VIPSubscription(user_id={self.user_id}, type={self.subscription_type}, is_active={self.is_active})>"

    def to_dict(self):
        """Convert VIP subscription to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_type": self.subscription_type,
            "start_date": self.start_date.isoformat() if hasattr(self.start_date, 'isoformat') else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "auto_renew": self.auto_renew,
            "payment_method": self.payment_method,
            "amount_paid": float(self.amount_paid) if self.amount_paid else None,
            "currency": self.currency,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else None
        }


class PersonalizedOffer(Base):
    """Personalized offer model for commerce system"""
    __tablename__ = "personalized_offers"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shop_item_id = Column(Integer, ForeignKey('shop_items.id'), nullable=False)
    
    # Personalización
    offer_type = Column(String(50))  # contextual, archetype_based, upsell, retention
    discount_percentage = Column(Integer, default=0)
    custom_message = Column(Text, nullable=True)
    
    # Contexto
    trigger_event = Column(String(100), nullable=True)
    trigger_context = Column(JSON, nullable=True)
    
    # Validez
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True)
    viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User")
    shop_item = relationship("ShopItem")

    def __repr__(self):
        return f"<PersonalizedOffer(user_id={self.user_id}, shop_item_id={self.shop_item_id}, discount={self.discount_percentage}%)>"

    def to_dict(self):
        """Convert personalized offer to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "shop_item_id": self.shop_item_id,
            "offer_type": self.offer_type,
            "discount_percentage": self.discount_percentage,
            "custom_message": self.custom_message,
            "trigger_event": self.trigger_event,
            "trigger_context": self.trigger_context,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else None,
            "expires_at": self.expires_at.isoformat() if hasattr(self.expires_at, 'isoformat') else None,
            "is_active": self.is_active,
            "viewed": self.viewed,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
            "accepted": self.accepted,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None
        }