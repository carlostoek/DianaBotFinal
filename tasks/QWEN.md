# Tasks Directory - Background and Scheduled Tasks

## Purpose
This directory contains background tasks and scheduled operations that run independently of user interactions, including subscription management, notification sending, content publishing, and system maintenance.

## Structure
```
tasks/
├── __init__.py
├── celery_app.py              # Celery application configuration
├── scheduled_tasks.py         # Daily/weekly recurring tasks
├── notification_tasks.py      # User notification tasks
├── cleanup_tasks.py           # Data cleanup and maintenance tasks
├── subscription_tasks.py      # Subscription management tasks
├── content_tasks.py           # Content publishing tasks
└── monitoring_tasks.py        # System monitoring tasks
```

## Required Models
- `core.models.User` - For user-related tasks
- `core.models.Subscription` - For subscription management
- `core.models.ChannelPost` - For content publishing
- `modules.gamification.models.Mission` - For mission-related tasks
- `core.models.Transaction` - For economy maintenance tasks

## Connections
- Connects to: `core.database` for data operations
- Connects to: `core.event_bus` for event publishing
- Connects to: `telegram.ext.Application` for bot interactions
- Connects to: `config.settings` for configuration
- Connects to: `core.cache` for temporary data storage

## Naming Conventions
- Task functions: `{module}_{action}_task` (e.g., `send_daily_mission_task`)
- Celery task names: `{app}.{module}.{action}` (e.g., `dianabot.notifications.send_reminder`)
- Scheduled task functions: `scheduled_{frequency}_{purpose}` (e.g., `scheduled_daily_cleanup`)
- Task parameters: `task_{parameter_name}` (e.g., `task_user_id`)
- Queue names: `{module}_queue` (e.g., `notifications_queue`)

## Key Requirements
- Proper error handling with retry mechanisms
- Idempotent task design (safe to run multiple times)
- Rate limiting to avoid API limits
- Proper logging for troubleshooting
- Resource management to avoid memory leaks
- Timeouts for long-running operations
- Task prioritization for critical operations
- Monitoring and alerting for task failures