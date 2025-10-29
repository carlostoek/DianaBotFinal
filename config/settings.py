"""
DianaBot - Main Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "DianaBot"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Telegram
    telegram_bot_token: str
    telegram_webhook_url: Optional[str] = None
    
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "dianabot"
    postgres_user: str = "dianabot_user"
    postgres_password: str
    
    # MongoDB
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "dianabot_narrative"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = ""
    redis_db: int = 0
    
    # Payment Providers
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    telegram_payment_provider_token: Optional[str] = None
    
    # Security
    secret_key: str
    callback_secret: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Paths
    media_upload_path: str = "media_uploads"
    backup_path: str = "backups"
    
    # Limits
    daily_besitos_limit_free: int = 200
    daily_besitos_limit_vip: int = 500
    inventory_slots_free: int = 20
    inventory_slots_vip: int = 50
    
    # Cache timeouts (in seconds)
    user_cache_ttl: int = 3600  # 1 hour
    narrative_cache_ttl: int = 1800  # 30 minutes
    subscription_cache_ttl: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()