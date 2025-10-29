# Dashboard Directory - Administrative Dashboard

## Purpose
This directory contains the web-based administrative dashboard for DianaBot, allowing administrators to manage content, users, subscriptions, and configure the system through a visual interface.

## Structure
```
dashboard/
├── __init__.py
├── main.py                    # Dashboard Flask/FastAPI app
├── templates/
│   ├── base.html              # Base template with layout
│   ├── dashboard.html         # Main dashboard overview
│   ├── narrative_editor.html  # Narrative content editor
│   ├── user_management.html   # User management interface
│   ├── analytics.html         # Analytics dashboard
│   ├── configuration.html     # Unified configuration interface
│   └── login.html             # Authentication page
├── static/
│   ├── css/
│   │   ├── main.css           # Main stylesheet
│   │   └── admin.css          # Admin-specific styles
│   ├── js/
│   │   ├── main.js            # Main JavaScript
│   │   ├── narrative_editor.js # Narrative editor logic
│   │   └── analytics.js       # Analytics charting
│   └── images/                # Dashboard images and icons
└── views/
    ├── __init__.py
    ├── dashboard.py           # Dashboard overview view
    ├── narrative.py           # Narrative management views
    ├── users.py               # User management views
    ├── analytics.py           # Analytics views
    └── configuration.py       # Configuration views
```

## Required Models
- `api.schemas.user.UserSchema` - User data for display
- `api.schemas.narrative.NarrativeSchema` - Narrative data for editors
- `api.schemas.gamification.ItemSchema` - Item data for management
- `api.schemas.admin.ConfigSchema` - Configuration data for forms

## Connections
- Connects to: `api.main` for backend API calls
- Connects to: `api.routes.config` for configuration management
- Connects to: `api.routes.analytics` for metrics display
- Connects to: `api.routes.users` for user management
- Connects to: `api.routes.admin` for admin operations

## Naming Conventions
- Template files: `{feature}_{purpose}.html` (e.g., `user_management.html`)
- Static files: `{feature}.{extension}` (e.g., `narrative_editor.js`)
- View functions: `{feature}_{action}_view` (e.g., `narrative_edit_view`)
- CSS classes: `dash-{feature}-{element}` (e.g., `dash-narrative-editor`)
- JavaScript functions: `{feature}{Action}Handler` (e.g., `narrativeSaveHandler`)
- Form elements: `{feature}_{field_name}` (e.g., `narrative_title`)

## Key Requirements
- Responsive design for desktop and tablet access
- Secure authentication with session management
- Role-based access control for different admin levels
- Real-time updates where appropriate
- Form validation and error handling
- Loading states and user feedback
- Accessible design following WCAG guidelines
- Performance optimization for large datasets
- Consistent UI/UX across all dashboard sections