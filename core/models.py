"""
DianaBot - Core Database Models
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True)
    telegram_username = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True))
    user_state = Column(String(50), default='free')  # 'free', 'vip', 'banned'
    metadata_json = Column(JSON)  # Flexible additional user data


class UserBalance(Base):
    __tablename__ = "user_balances"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    besitos = Column(Integer, default=0, CheckConstraint("besitos >= 0"))
    lifetime_besitos = Column(Integer, default=0)  # For statistics
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), index=True)
    amount = Column(Integer, nullable=False)  # Can be positive or negative
    transaction_type = Column(String(50), nullable=False)  # 'earn', 'spend', 'gift'
    source = Column(String(100))  # 'mission', 'purchase', 'daily_reward', 'achievement', etc.
    description = Column(Text)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    item_key = Column(String(100), unique=True, nullable=False)  # Unique identifier
    name = Column(String(255), nullable=False)
    description = Column(Text)
    item_type = Column(String(50))  # 'narrative_key', 'collectible', 'power_up'
    rarity = Column(String(50))  # 'common', 'rare', 'epic', 'legendary'
    price_besitos = Column(Integer)
    metadata_json = Column(JSON)  # Effects, requirements, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserInventory(Base):
    __tablename__ = "user_inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True)
    quantity = Column(Integer, default=1)
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (CheckConstraint(quantity >= 1),)


class Achievement(Base):
    __tablename__ = "achievements"

    achievement_id = Column(Integer, primary_key=True, index=True)
    achievement_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon_emoji = Column(String(50))
    points = Column(Integer, default=0)
    reward_besitos = Column(Integer, default=0)
    reward_item_id = Column(Integer, ForeignKey("items.item_id"))
    unlock_conditions = Column(JSON)  # Criteria for unlocking
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievements.achievement_id"), primary_key=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(JSON)  # For progressive achievements


class NarrativeLevel(Base):
    __tablename__ = "narrative_levels"

    level_id = Column(Integer, primary_key=True, index=True)
    level_number = Column(Integer, unique=True, nullable=False)
    title = Column(String(255))
    is_vip = Column(Boolean, default=False)
    unlock_conditions = Column(JSON)  # besitos, items, achievements required
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NarrativeFragment(Base):
    __tablename__ = "narrative_fragments"

    fragment_id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("narrative_levels.level_id"), index=True)
    fragment_key = Column(String(100), unique=True, nullable=False)
    title = Column(String(255))
    content_type = Column(String(50))  # 'story', 'decision', 'mini_game'
    unlock_conditions = Column(JSON)
    rewards = Column(JSON)  # besitos, items, achievements granted
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserNarrativeProgress(Base):
    __tablename__ = "user_narrative_progress"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    fragment_id = Column(Integer, ForeignKey("narrative_fragments.fragment_id"), primary_key=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    choices_made = Column(JSON)  # Decisions made in this fragment


class Mission(Base):
    __tablename__ = "missions"

    mission_id = Column(Integer, primary_key=True, index=True)
    mission_key = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    mission_type = Column(String(50))  # 'daily', 'weekly', 'narrative', 'special'
    recurrence = Column(String(50))  # 'once', 'daily', 'weekly'
    requirements = Column(JSON)  # What user must do
    rewards = Column(JSON)  # besitos, items, achievements
    expiry_date = Column(DateTime(timezone=True))  # For temporary missions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserMission(Base):
    __tablename__ = "user_missions"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.mission_id"), primary_key=True, index=True)
    status = Column(String(50))  # 'active', 'completed', 'expired'
    progress = Column(JSON)  # Current progress toward requirements
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True)
    subscription_type = Column(String(50))  # 'monthly', 'yearly', etc.
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50))  # 'active', 'expired', 'cancelled'
    payment_reference = Column(String(255))  # External payment ID
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(BigInteger, primary_key=True)
    channel_type = Column(String(50))  # 'free', 'vip'
    channel_username = Column(String(255))
    settings = Column(JSON)  # Specific channel configurations
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChannelPost(Base):
    __tablename__ = "channel_posts"

    post_id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, ForeignKey("channels.channel_id"), index=True)
    post_type = Column(String(50))  # 'narrative', 'mission', 'trivia', 'announcement'
    content = Column(JSON)  # Text, media, buttons
    scheduled_for = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    is_protected = Column(Boolean, default=False)
    linked_mission_id = Column(Integer, ForeignKey("missions.mission_id"))
    linked_fragment_id = Column(Integer, ForeignKey("narrative_fragments.fragment_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConfigTemplate(Base):
    __tablename__ = "config_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    template_key = Column(String(100), unique=True, nullable=False)
    template_type = Column(String(50))  # 'experience', 'event', 'mission_chain'
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_schema = Column(JSON)  # Structure of the template
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConfigInstance(Base):
    __tablename__ = "config_instances"

    instance_id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("config_templates.template_id"), index=True)
    instance_data = Column(JSON)  # Specific configuration
    created_by = Column(Integer)  # Admin user ID
    status = Column(String(50))  # 'draft', 'active', 'archived'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())