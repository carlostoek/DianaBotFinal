# Config Directory - Configuration Management

## Purpose
This directory contains all configuration management for DianaBot, including settings, database configuration, and environment-specific configurations.

## Structure
```
config/
├── __init__.py
├── settings.py                # Main application settings with Pydantic
├── database.py                # Database connection configuration
├── redis.py                   # Redis configuration
├── telegram.py                # Telegram API configuration
├── security.py                # Security-related configuration
└── logging.py                 # Logging configuration
```

## Required Models
- `pydantic_settings.BaseSettings` - For settings validation
- Environment variables from `.env` file
- `core.models` - For database model configurations

## Connections
- Connects to: Environment variables via `.env` file
- Connects to: `core.database` for database configuration
- Connects to: `core.cache` for Redis configuration
- Connects to: `bot.core` for Telegram bot configuration

## Naming Conventions
- Settings classes: `{Component}Settings` (e.g., `DatabaseSettings`)
- Configuration attributes: `snake_case` (e.g., `telegram_bot_token`)
- Environment variable names: `UPPER_SNAKE_CASE` (e.g., `TELEGRAM_BOT_TOKEN`)
- Configuration files: `{component}_config.py` (e.g., `database_config.py`)
- Secret keys: `{purpose}_secret` (e.g., `callback_secret`)

## Key Requirements
- All sensitive data must be loaded from environment variables
- Settings validation using Pydantic
- Default values for optional settings
- Type hints for all configuration parameters
- Proper error handling for missing configuration
- Environment-specific configuration support
- Secure handling of sensitive information
- Configuration documentation in comments