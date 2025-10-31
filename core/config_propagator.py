"""
Configuration propagator for the Configuration Manager

This module handles propagating configuration changes to various
modules and systems in DianaBot.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from sqlalchemy.orm import Session

from database.models import (
    ConfigInstance, NarrativeFragment, Mission, Item, Achievement, 
    ChannelPost, NarrativeLevel
)

logger = logging.getLogger(__name__)


def propagate_config_changes(
    config_instance: ConfigInstance,
    changes: Dict[str, Any],
    db_session: Session,
    activation: bool = False,
    deactivation: bool = False
) -> Tuple[bool, List[str]]:
    """
    Propagate configuration changes to relevant modules
    
    Args:
        config_instance: The configuration instance being changed
        changes: Dictionary of changes to propagate
        db_session: Database session
        activation: Whether this is an activation operation
        deactivation: Whether this is a deactivation operation
        
    Returns:
        Tuple of (success, error_messages)
    """
    errors = []
    
    try:
        template_type = config_instance.template.template_type
        instance_data = config_instance.instance_data
        
        if activation:
            # Handle activation of configuration
            success, activation_errors = _activate_configuration(
                template_type, instance_data, db_session
            )
            errors.extend(activation_errors)
            
        elif deactivation:
            # Handle deactivation of configuration
            success, deactivation_errors = _deactivate_configuration(
                template_type, instance_data, db_session
            )
            errors.extend(deactivation_errors)
            
        else:
            # Handle regular updates
            success, update_errors = _update_configuration(
                template_type, instance_data, changes, db_session
            )
            errors.extend(update_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error propagating configuration changes: {e}")
        return False, [f"Propagation error: {str(e)}"]


def _activate_configuration(
    template_type: str,
    instance_data: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Activate a configuration by creating necessary entities"""
    errors = []
    
    try:
        if template_type == 'experience':
            # Create narrative experience
            success, exp_errors = _create_narrative_experience(instance_data, db_session)
            errors.extend(exp_errors)
            
        elif template_type == 'mission':
            # Create mission
            success, mission_errors = _create_mission(instance_data, db_session)
            errors.extend(mission_errors)
            
        elif template_type == 'event':
            # Create event
            success, event_errors = _create_event(instance_data, db_session)
            errors.extend(event_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error activating configuration: {e}")
        return False, [f"Activation error: {str(e)}"]


def _deactivate_configuration(
    template_type: str,
    instance_data: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Deactivate a configuration by archiving entities"""
    errors = []
    
    try:
        if template_type == 'experience':
            # Archive narrative experience
            success, exp_errors = _archive_narrative_experience(instance_data, db_session)
            errors.extend(exp_errors)
            
        elif template_type == 'mission':
            # Archive mission
            success, mission_errors = _archive_mission(instance_data, db_session)
            errors.extend(mission_errors)
            
        elif template_type == 'event':
            # Archive event
            success, event_errors = _archive_event(instance_data, db_session)
            errors.extend(event_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error deactivating configuration: {e}")
        return False, [f"Deactivation error: {str(e)}"]


def _update_configuration(
    template_type: str,
    instance_data: Dict[str, Any],
    changes: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Update existing configuration entities"""
    errors = []
    
    try:
        if template_type == 'experience':
            # Update narrative experience
            success, exp_errors = _update_narrative_experience(instance_data, changes, db_session)
            errors.extend(exp_errors)
            
        elif template_type == 'mission':
            # Update mission
            success, mission_errors = _update_mission(instance_data, changes, db_session)
            errors.extend(mission_errors)
            
        elif template_type == 'event':
            # Update event
            success, event_errors = _update_event(instance_data, changes, db_session)
            errors.extend(event_errors)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return False, [f"Update error: {str(e)}"]


def _create_narrative_experience(
    data: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Create a narrative experience from configuration"""
    errors = []
    
    try:
        # Create or get narrative level
        level_number = data.get('level_number', 1)
        level = db_session.query(NarrativeLevel).filter(
            NarrativeLevel.level_key == f"level_{level_number}"
        ).first()
        
        if not level:
            level = NarrativeLevel(
                level_key=f"level_{level_number}",
                title=f"Level {level_number}",
                order_index=level_number,
                is_active=True
            )
            db_session.add(level)
            db_session.flush()
        
        # Create narrative fragments
        fragments = data.get('fragments', [])
        for fragment_data in fragments:
            fragment = NarrativeFragment(
                fragment_key=fragment_data.get('fragment_key'),
                level_id=level.id,
                title=fragment_data.get('title'),
                unlock_conditions=data.get('requirements', {}),
                order_index=fragment_data.get('order_index', 0),
                is_active=True
            )
            db_session.add(fragment)
        
        # Create items if specified
        items = data.get('rewards', {}).get('items', [])
        for item_key in items:
            # Check if item exists, create if not
            existing_item = db_session.query(Item).filter(
                Item.item_key == item_key
            ).first()
            
            if not existing_item:
                item = Item(
                    item_key=item_key,
                    name=item_key.replace('_', ' ').title(),
                    description=f"Item from narrative experience",
                    item_type='collectible',
                    rarity='common'
                )
                db_session.add(item)
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error creating narrative experience: {e}")
        return False, [f"Narrative experience creation error: {str(e)}"]


def _create_mission(data: Dict[str, Any], db_session: Session) -> Tuple[bool, List[str]]:
    """Create a mission from configuration"""
    errors = []
    
    try:
        mission = Mission(
            mission_key=data.get('mission_key'),
            title=data.get('title'),
            description=data.get('description'),
            mission_type=data.get('mission_type', 'daily'),
            recurrence=data.get('recurrence', 'once'),
            requirements=data.get('requirements', {}),
            rewards=data.get('rewards', {}),
            is_active=True
        )
        
        db_session.add(mission)
        return True, []
        
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        return False, [f"Mission creation error: {str(e)}"]


def _create_event(data: Dict[str, Any], db_session: Session) -> Tuple[bool, List[str]]:
    """Create an event from configuration"""
    errors = []
    
    try:
        # For events, we might create multiple entities
        # For now, just create a channel post announcing the event
        post = ChannelPost(
            channel_id=data.get('channel_id'),
            post_type='event',
            content={
                'title': data.get('name'),
                'description': data.get('description'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date')
            },
            status='scheduled',
            scheduled_for=data.get('start_date')
        )
        
        db_session.add(post)
        return True, []
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return False, [f"Event creation error: {str(e)}"]


def _archive_narrative_experience(
    data: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Archive a narrative experience"""
    errors = []
    
    try:
        # Archive all fragments in the experience
        fragments = data.get('fragments', [])
        for fragment_data in fragments:
            fragment_key = fragment_data.get('fragment_key')
            fragment = db_session.query(NarrativeFragment).filter(
                NarrativeFragment.fragment_key == fragment_key
            ).first()
            
            if fragment:
                fragment.is_active = False
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error archiving narrative experience: {e}")
        return False, [f"Narrative experience archiving error: {str(e)}"]


def _archive_mission(data: Dict[str, Any], db_session: Session) -> Tuple[bool, List[str]]:
    """Archive a mission"""
    errors = []
    
    try:
        mission_key = data.get('mission_key')
        mission = db_session.query(Mission).filter(
            Mission.mission_key == mission_key
        ).first()
        
        if mission:
            mission.is_active = False
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error archiving mission: {e}")
        return False, [f"Mission archiving error: {str(e)}"]


def _archive_event(data: Dict[str, Any], db_session: Session) -> Tuple[bool, List[str]]:
    """Archive an event"""
    errors = []
    
    try:
        # Archive event-related posts
        event_name = data.get('name')
        posts = db_session.query(ChannelPost).filter(
            ChannelPost.post_type == 'event'
        ).all()
        
        for post in posts:
            if post.content and post.content.get('title') == event_name:
                post.status = 'archived'
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error archiving event: {e}")
        return False, [f"Event archiving error: {str(e)}"]


def _update_narrative_experience(
    data: Dict[str, Any],
    changes: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Update a narrative experience"""
    errors = []
    
    try:
        # Update fragments based on changes
        for change_key, change_value in changes.items():
            if change_key.startswith('updated_fragments'):
                # Handle fragment updates
                for fragment_data in change_value.get('new', []):
                    fragment_key = fragment_data.get('fragment_key')
                    fragment = db_session.query(NarrativeFragment).filter(
                        NarrativeFragment.fragment_key == fragment_key
                    ).first()
                    
                    if fragment:
                        fragment.title = fragment_data.get('title', fragment.title)
                        # Update other fields as needed
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error updating narrative experience: {e}")
        return False, [f"Narrative experience update error: {str(e)}"]


def _update_mission(
    data: Dict[str, Any],
    changes: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Update a mission"""
    errors = []
    
    try:
        mission_key = data.get('mission_key')
        mission = db_session.query(Mission).filter(
            Mission.mission_key == mission_key
        ).first()
        
        if mission:
            # Update mission fields based on changes
            for change_key, change_value in changes.items():
                if change_key == 'updated_title':
                    mission.title = change_value.get('new')
                elif change_key == 'updated_description':
                    mission.description = change_value.get('new')
                elif change_key == 'updated_rewards':
                    mission.rewards = change_value.get('new')
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error updating mission: {e}")
        return False, [f"Mission update error: {str(e)}"]


def _update_event(
    data: Dict[str, Any],
    changes: Dict[str, Any],
    db_session: Session
) -> Tuple[bool, List[str]]:
    """Update an event"""
    errors = []
    
    try:
        event_name = data.get('name')
        posts = db_session.query(ChannelPost).filter(
            ChannelPost.post_type == 'event'
        ).all()
        
        for post in posts:
            if post.content and post.content.get('title') == event_name:
                # Update event post based on changes
                for change_key, change_value in changes.items():
                    if change_key == 'updated_description':
                        post.content['description'] = change_value.get('new')
                    elif change_key == 'updated_start_date':
                        post.scheduled_for = change_value.get('new')
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return False, [f"Event update error: {str(e)}"]