# Core Directory - Central Components

## Purpose
This directory contains central components that are shared across multiple modules of DianaBot. These include database configuration, event bus, configuration manager, user state management, and other cross-cutting concerns.

## Structure
```
core/
├── __init__.py
├── event_bus.py               # Event system for inter-module communication
├── config_manager.py          # Unified configuration management
├── user_state_manager.py      # User state management across modules
├── models.py                  # Core database models
├── database.py                # Database connection and session management
├── cache.py                   # Redis cache integration
├── security.py                # Security utilities and validation
└── utils.py                   # General utility functions
```

## Required Models
- All models from `core.models` are used by other modules
- `modules.narrative.models` for narrative-specific models
- `modules.gamification.models` for gamification-specific models
- `modules.admin.models` for admin-specific models

## Connections
- `event_bus` connects to: `redis` for pub/sub messaging
- `database` connects to: `PostgreSQL` and `MongoDB` (through separate clients)
- `cache` connects to: `Redis` for caching and session storage
- `config_manager` connects to: `core.models.ConfigTemplate` and `core.models.ConfigInstance`
- `security` connects to: `config.settings` for security parameters

## Naming Conventions
- Service classes: `{Component}{Purpose}Service` (e.g., `EventBusService`)
- Manager classes: `{Component}Manager` (e.g., `UserStateManager`)
- Configuration classes: `{Component}Config` (e.g., `DatabaseConfig`)
- Utility functions: `get_{purpose}` or `format_{purpose}` (e.g., `get_db_session`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CACHE_TTL`)
- Configuration parameters: `snake_case` (e.g., `redis_host`)

## Key Requirements
- Database connection pooling with proper resource management
- Event system with guaranteed delivery and error handling
- Caching layer with proper TTL and invalidation strategies
- Security validation for all inputs and outputs
- Proper logging and monitoring capabilities
- Thread-safe implementations where applicable
- Configurable from environment variables
- Error handling with graceful degradation