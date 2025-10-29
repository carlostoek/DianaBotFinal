# Modules Directory - Functional Modules

## Purpose
This directory contains the main functional modules of DianaBot: narrative, gamification, and administration. Each module is self-contained with its own models, services, and business logic.

## Structure
```
modules/
├── narrative/
│   ├── __init__.py
│   ├── engine.py              # Narrative engine and processing logic
│   ├── models.py              # Narrative-related database models
│   ├── fragment_manager.py    # Fragment loading and management
│   ├── unlock_system.py       # Content unlocking logic
│   └── templates/             # Narrative content templates
├── gamification/
│   ├── __init__.py
│   ├── economy.py             # Besitos system and transactions
│   ├── missions.py            # Mission management
│   ├── achievements.py        # Achievement system
│   ├── auction.py             # Auction system
│   ├── inventory.py           # Inventory management
│   ├── trivia.py              # Trivia system
│   ├── models.py              # Gamification DB models
│   └── rewards.py             # Reward calculation logic
└── admin/
    ├── __init__.py
    ├── subscription_manager.py # VIP subscription handling
    ├── channel_manager.py      # Channel access management
    ├── content_publisher.py    # Content scheduling and publishing
    ├── models.py               # Admin DB models
    └── moderation.py           # User moderation tools
```

## Required Models per Module

### Narrative Module
- `core.models.User` - User information
- `core.models.NarrativeLevel` - Narrative level information
- `core.models.NarrativeFragment` - Fragment metadata
- `core.models.UserNarrativeProgress` - User's narrative progress

### Gamification Module
- `core.models.User` - User information
- `core.models.UserBalance` - Besitos balance
- `core.models.Transaction` - Transaction history
- `core.models.Item` - Item definitions
- `core.models.UserInventory` - User's items
- `core.models.Achievement` - Achievement definitions
- `core.models.UserAchievement` - User's achievements
- `core.models.Mission` - Mission definitions
- `core.models.UserMission` - User's missions

### Admin Module
- `core.models.User` - User information
- `core.models.Subscription` - Subscription information
- `core.models.Channel` - Channel information
- `core.models.ChannelPost` - Scheduled posts

## Connections
- All modules connect to: `core.database` for data persistence
- All modules connect to: `core.event_bus` for event publishing/subscribing
- Narrative connects to: `modules.gamification.economy` for rewards
- Gamification connects to: `modules.narrative.engine` for narrative-based rewards
- Admin connects to: `telegram.ext.Application` for channel management

## Naming Conventions
- Service classes: `{Module}{Service}Service` (e.g., `NarrativeEngineService`)
- Manager classes: `{Module}{Entity}Manager` (e.g., `SubscriptionManager`)
- Processing functions: `process_{action}` (e.g., `process_decision`)
- Validation functions: `validate_{entity}` (e.g., `validate_fragment_access`)
- Event handlers: `handle_{event_type}` (e.g., `handle_achievement_unlocked`)

## Key Requirements
- Each module must be loosely coupled from others
- Use dependency injection for cross-module communication
- Implement proper error handling and logging
- Maintain clear separation of concerns
- Follow single responsibility principle
- Use consistent data validation across modules
- Implement proper transaction management for data consistency