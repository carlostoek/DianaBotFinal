# DianaBot Project Overview

## Purpose
DianaBot is an integrated system that combines three interconnected modules: Immersive Narrative, Gamification, and Channel Management. It provides an engaging, personalized, gamified experience in a narrative environment with emotional, psychological, and thematic elements.

## Project Structure
```
dianabot/
├── bot/                      # Core Telegram bot functionality
├── modules/                  # Main functional modules
│   ├── narrative/            # Narrative engine and content
│   ├── gamification/         # Besitos economy and game mechanics
│   └── admin/                # Channel and subscription management
├── core/                     # Central components and utilities
├── api/                      # REST API for admin dashboard
├── dashboard/                # Web-based admin dashboard
├── tasks/                    # Background and scheduled tasks
├── config/                   # Configuration management
├── utils/                    # Utility functions and helpers
├── tests/                    # Test files
├── docs/                     # Documentation
├── docker/                   # Docker configuration
├── migrations/               # Database migration files
├── scripts/                  # Utility scripts
└── requirements/             # Python requirements
```

## Main Dependencies
- `python-telegram-bot==20.7` - Telegram bot framework
- `fastapi==0.104.1` - Web framework for API
- `sqlalchemy==2.0.23` - ORM for PostgreSQL
- `pymongo==4.6.0` - MongoDB driver
- `redis==5.0.1` - Redis client for caching and events
- `celery==5.3.4` - Task queue for background jobs
- `pydantic==2.5.0` - Data validation

## Connection Patterns
- **Bot ↔ Modules**: Through event bus and direct service calls
- **Modules ↔ Core**: Through database models and event system
- **API ↔ Modules**: Through service layer calls
- **Dashboard ↔ API**: Through REST endpoints
- **Tasks ↔ All**: Through database and event bus

## Naming Conventions
- **Classes**: `PascalCase` (e.g., `NarrativeEngine`)
- **Functions**: `snake_case` (e.g., `process_decision`)
- **Variables**: `snake_case` (e.g., `user_balance`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_BESITOS`)
- **Files**: `snake_case.py` (e.g., `narrative_engine.py`)
- **Database Tables**: `snake_case` (e.g., `narrative_fragments`)

## Architecture Principles
1. **Modularity**: Each module should be as independent as possible
2. **Event-Driven**: Modules communicate primarily through events
3. **Configuration Centralization**: Use unified configuration system
4. **Security First**: Validate all inputs, secure all endpoints
5. **Scalability**: Design for horizontal scaling from the start
6. **Observability**: Comprehensive logging and monitoring

## Environment Variables
Required environment variables are documented in `.env.example`:
- `TELEGRAM_BOT_TOKEN` - Telegram bot authentication token
- Database credentials for PostgreSQL, MongoDB, Redis
- Payment provider tokens (Stripe, Telegram Stars)
- Security keys and secrets
- Application settings

## Development Guidelines
- All code must have proper type hints
- Implement comprehensive error handling
- Use dependency injection for service connections
- Follow single responsibility principle
- Write unit tests for all business logic
- Use async functions for I/O operations
- Implement proper logging throughout the application