# Bot Directory - Telegram Bot Core

## Purpose
This directory contains the core Telegram bot functionality that handles all user interactions with DianaBot. It processes commands, callbacks, and messages from Telegram users.

## Structure
```
bot/
├── core/
│   ├── __init__.py
│   ├── bot.py                 # Main bot instance and initialization
│   ├── handlers/              # Update handlers for different update types
│   │   ├── __init__.py
│   │   ├── start_handler.py   # Handler for /start command
│   │   ├── narrative_handler.py # Handler for narrative callbacks
│   │   ├── gamification_handler.py # Handler for gamification callbacks
│   │   └── admin_handler.py   # Handler for admin callbacks
│   └── filters.py             # Custom filters for update processing
├── commands/
│   ├── __init__.py
│   ├── start.py               # Start command implementation
│   ├── help.py                # Help command implementation
│   ├── narrative.py           # Narrative-related commands
│   ├── shop.py                # Shop/economy commands
│   └── admin.py               # Admin commands
└── keyboards/
    ├── __init__.py
    ├── narrative_keyboard.py  # Inline keyboards for narrative
    ├── shop_keyboard.py       # Inline keyboards for shop
    └── admin_keyboard.py      # Inline keyboards for admin functions
```

## Required Models
- `core.models.User` - User information and state
- `modules.narrative.models.NarrativeFragment` - Current narrative state
- `modules.gamification.models.UserBalance` - Besitos balance
- `modules.gamification.models.UserInventory` - User's items

## Connections
- Connects to: `core.event_bus` for event publishing
- Connects to: `core.database` for data persistence
- Connects to: `modules.narrative.engine` for narrative processing
- Connects to: `modules.gamification.economy` for besitos operations

## Naming Conventions
- Handler functions: `handle_{module}_{action}` (e.g., `handle_narrative_decision`)
- Command functions: `{action}_command` (e.g., `balance_command`)
- Keyboard functions: `create_{module}_{purpose}_keyboard` (e.g., `create_narrative_decision_keyboard`)
- Callback pattern: `^{module}:(.*)` (e.g., `^narrative:`)

## Key Requirements
- All handlers must be asynchronous
- Error handling with graceful fallbacks
- Rate limiting implementation
- Input validation before processing
- Proper logging of all user interactions
- Security validation of callback data