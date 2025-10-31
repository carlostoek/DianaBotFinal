from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from database.connection import get_db
from database.models import ConfigInstance, AdminUser, EventLog
from ..middleware.auth import require_role, get_current_active_user

router = APIRouter(prefix="/config", tags=["configuration"])


class ConfigUpdateRequest(BaseModel):
    type: str
    settings: Dict[str, Any]


@router.get("/")
async def get_configurations(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get all configuration instances"""
    configs = db.query(ConfigInstance).all()
    return {
        "configurations": [
            {
                "id": config.id,
                "config_key": config.config_key,
                "name": config.name,
                "description": config.description,
                "status": config.status,
                "is_active": config.is_active,
                "created_at": config.created_at
            }
            for config in configs
        ]
    }


@router.get("/{config_key}")
async def get_configuration(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get specific configuration by key"""
    config = db.query(ConfigInstance).filter(
        ConfigInstance.config_key == config_key
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{config_key}' not found"
        )
    
    return {
        "id": config.id,
        "config_key": config.config_key,
        "name": config.name,
        "description": config.description,
        "instance_data": config.instance_data,
        "status": config.status,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }


@router.put("/{config_key}")
async def update_configuration(
    config_key: str,
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Update configuration data"""
    config = db.query(ConfigInstance).filter(
        ConfigInstance.config_key == config_key
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{config_key}' not found"
        )
    
    # Update configuration data
    config.instance_data = config_data
    db.commit()
    
    return {
        "message": f"Configuration '{config_key}' updated successfully",
        "config_key": config.config_key,
        "updated_data": config.instance_data
    }


@router.post("/{config_key}/activate")
async def activate_configuration(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Activate a configuration"""
    config = db.query(ConfigInstance).filter(
        ConfigInstance.config_key == config_key
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{config_key}' not found"
        )
    
    config.is_active = True
    config.status = "active"
    db.commit()
    
    return {
        "message": f"Configuration '{config_key}' activated successfully",
        "config_key": config.config_key,
        "status": config.status
    }


@router.post("/{config_key}/deactivate")
async def deactivate_configuration(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Deactivate a configuration"""
    config = db.query(ConfigInstance).filter(
        ConfigInstance.config_key == config_key
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{config_key}' not found"
        )

    config.is_active = False
    config.status = "inactive"
    db.commit()

    return {
        "message": f"Configuration '{config_key}' deactivated successfully",
        "config_key": config.config_key,
        "status": config.status
    }


@router.get("/")
async def get_dashboard_config(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get configuration settings for dashboard"""
    # Get or create default configurations
    config_keys = ['general', 'gamification', 'narrative', 'channels']
    config_data = {}

    for key in config_keys:
        config = db.query(ConfigInstance).filter(
            ConfigInstance.config_key == key,
            ConfigInstance.is_active == True
        ).first()

        if config and config.instance_data:
            config_data[key] = config.instance_data
        else:
            # Return default values if no config exists
            defaults = {
                'general': {
                    'botName': 'DianaBot',
                    'defaultLanguage': 'es',
                    'timezone': 'America/Bogota',
                    'debugMode': False
                },
                'gamification': {
                    'besitosPerMessage': 1,
                    'besitosPerTrivia': 5,
                    'besitosPerMission': 10,
                    'dailyBesitosLimit': 100,
                    'dailyReward': 10,
                    'vipMultiplier': 2.0
                },
                'narrative': {
                    'fragmentsPerDay': 3,
                    'timeBetweenFragments': 30,
                    'maxFragmentLength': 1000,
                    'autoContinue': True,
                    'requireUserChoice': False,
                    'narrationMode': 'branching'
                },
                'channels': {
                    'mainChannel': '',
                    'announcementsChannel': '',
                    'supportChannel': '',
                    'autoPublish': False,
                    'publishFrequency': 'daily',
                    'pushNotifications': True
                }
            }
            config_data[key] = defaults.get(key, {})

    return config_data


@router.post("/")
async def save_dashboard_config(
    config_update: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Save configuration settings from dashboard"""
    config_key = config_update.type
    settings = config_update.settings

    # Get or create configuration
    config = db.query(ConfigInstance).filter(
        ConfigInstance.config_key == config_key
    ).first()

    if not config:
        config = ConfigInstance(
            config_key=config_key,
            name=f"{config_key.title()} Configuration",
            description=f"Configuration for {config_key} settings",
            instance_data=settings,
            status="active",
            is_active=True
        )
        db.add(config)
    else:
        config.instance_data = settings
        config.updated_at = datetime.now()

    # Log the change
    event_log = EventLog(
        event_type="config_change",
        event_data={
            "config_type": config_key,
            "changes": settings,
            "user_id": current_user.id
        },
        user_id=current_user.id,
        timestamp=datetime.now()
    )
    db.add(event_log)

    db.commit()

    return {"success": True, "message": f"Configuration {config_key} saved successfully"}


@router.get("/history")
async def get_config_history(
    page: int = 1,
    limit: int = 10,
    config_type: str = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_role("admin"))
):
    """Get configuration change history"""
    query = db.query(EventLog).filter(EventLog.event_type == "config_change")

    if config_type:
        query = query.filter(EventLog.event_data['config_type'].astext == config_type)

    total = query.count()
    events = query.order_by(EventLog.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()

    history = []
    for event in events:
        data = event.event_data
        history.append({
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "type": data.get("config_type", "unknown"),
            "description": f"Updated {data.get('config_type', 'unknown')} configuration",
            "user": current_user.username if current_user else "System"
        })

    return {
        "history": history,
        "total": total,
        "page": page,
        "limit": limit
    }