# API Directory - REST API for Admin Dashboard

## Purpose
This directory contains the FastAPI application that serves the administrative dashboard and provides REST endpoints for configuration management, analytics, and administrative operations.

## Structure
```
api/
├── __init__.py
├── main.py                    # FastAPI application instance
├── routes/
│   ├── __init__.py
│   ├── config.py              # Configuration management endpoints
│   ├── analytics.py           # Analytics and metrics endpoints
│   ├── payments.py            # Payment-related endpoints
│   ├── admin.py               # Administrative endpoints
│   └── users.py               # User management endpoints
├── middleware/
│   ├── __init__.py
│   ├── auth.py                # Authentication middleware
│   └── rate_limit.py          # Rate limiting middleware
└── schemas/                   # Pydantic models for API validation
    ├── __init__.py
    ├── user.py                # User-related schemas
    ├── narrative.py           # Narrative-related schemas
    ├── gamification.py        # Gamification-related schemas
    └── admin.py               # Admin-related schemas
```

## Required Models
- `core.models.User` - User information for admin operations
- `core.models.ConfigTemplate` - Configuration templates
- `core.models.ConfigInstance` - Configuration instances
- `modules.narrative.models.NarrativeFragment` - Narrative content
- `modules.gamification.models.Item` - Item management
- `modules.gamification.models.Achievement` - Achievement management
- `modules.admin.models.Subscription` - Subscription management

## Connections
- Connects to: `core.database` for data access
- Connects to: `core.config_manager` for configuration operations
- Connects to: `modules.narrative.engine` for narrative operations
- Connects to: `modules.gamification.economy` for economy operations
- Connects to: `core.event_bus` for event publishing

## Naming Conventions
- Endpoint functions: `handle_{http_method}_{entity}` (e.g., `get_user_detail`)
- Router variables: `{entity}_router` (e.g., `config_router`)
- Schema classes: `{Entity}{Action}Schema` (e.g., `UserUpdateSchema`)
- Response models: `{Entity}Response` (e.g., `ConfigResponse`)
- Path parameters: `{entity}_id` (e.g., `user_id`, `fragment_key`)
- Query parameters: `{purpose}_{entity}` (e.g., `limit_users`, `offset_users`)

## Key Requirements
- JWT-based authentication for all endpoints
- Role-based access control for admin functions
- Input validation using Pydantic schemas
- Proper error handling with HTTP status codes
- Rate limiting to prevent abuse
- Comprehensive logging of admin actions
- Response caching where appropriate
- Pagination for list endpoints
- API documentation with OpenAPI/Swagger