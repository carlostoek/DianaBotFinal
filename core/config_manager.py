"""
Configuration Manager - Centralized configuration management system

This module provides a unified interface for managing configurations across
all DianaBot modules. It handles validation, propagation, and versioning
of configuration changes.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from database.models import ConfigTemplate, ConfigInstance, ConfigVersion
from database.connection import get_db
from core.validators import validate_config_data
from core.config_propagator import propagate_config_changes

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Main configuration manager class"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or next(get_db())
    
    def create_config_instance(
        self, 
        template_key: str, 
        instance_data: Dict[str, Any], 
        created_by: Optional[int] = None,
        status: str = 'draft'
    ) -> Tuple[bool, Optional[ConfigInstance], List[str]]:
        """
        Create a new configuration instance from a template
        
        Args:
            template_key: Key of the template to use
            instance_data: Configuration data for this instance
            created_by: ID of the admin user creating this instance
            status: Initial status ('draft', 'active', 'archived')
            
        Returns:
            Tuple of (success, config_instance, validation_errors)
        """
        try:
            # Get the template
            template = self.db_session.query(ConfigTemplate).filter(
                and_(
                    ConfigTemplate.template_key == template_key,
                    ConfigTemplate.is_active == True
                )
            ).first()
            
            if not template:
                return False, None, [f"Template '{template_key}' not found or inactive"]
            
            # Validate the configuration data
            is_valid, errors = validate_config_data(template.template_schema, instance_data)
            if not is_valid:
                return False, None, errors
            
            # Create the config instance
            config_instance = ConfigInstance(
                template_id=template.id,
                instance_data=instance_data,
                created_by=created_by,
                status=status
            )
            
            self.db_session.add(config_instance)
            self.db_session.commit()
            
            # Create initial version
            self._create_version(config_instance, instance_data, created_by, "Initial version")
            
            logger.info(f"Created config instance {config_instance.id} from template {template_key}")
            return True, config_instance, []
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error creating config instance: {e}")
            return False, None, [str(e)]
    
    def update_config_instance(
        self,
        instance_id: int,
        updates: Dict[str, Any],
        changed_by: Optional[int] = None,
        change_reason: str = "",
        propagate: bool = False
    ) -> Tuple[bool, Optional[ConfigInstance], List[str]]:
        """
        Update an existing configuration instance
        
        Args:
            instance_id: ID of the config instance to update
            updates: Dictionary of updates to apply
            changed_by: ID of the admin user making changes
            change_reason: Reason for the change
            propagate: Whether to propagate changes to other systems
            
        Returns:
            Tuple of (success, updated_instance, validation_errors)
        """
        try:
            # Get the instance
            instance = self.db_session.query(ConfigInstance).filter(
                ConfigInstance.id == instance_id
            ).first()
            
            if not instance:
                return False, None, [f"Config instance {instance_id} not found"]
            
            # Get the template for validation
            template = self.db_session.query(ConfigTemplate).filter(
                ConfigTemplate.id == instance.template_id
            ).first()
            
            if not template:
                return False, None, [f"Template for instance {instance_id} not found"]
            
            # Create updated data by merging updates
            current_data = instance.instance_data
            updated_data = {**current_data, **updates}
            
            # Validate the updated data
            is_valid, errors = validate_config_data(template.template_schema, updated_data)
            if not is_valid:
                return False, None, errors
            
            # Calculate changes for versioning
            changes = self._calculate_changes(current_data, updated_data)
            
            # Update the instance
            instance.instance_data = updated_data
            
            # Create new version
            self._create_version(instance, changes, changed_by, change_reason)
            
            # Propagate changes if requested
            if propagate:
                propagation_success, propagation_errors = propagate_config_changes(
                    instance, changes, self.db_session
                )
                if not propagation_success:
                    logger.warning(f"Propagation failed for instance {instance_id}: {propagation_errors}")
                    # Continue anyway, but log the warning
            
            self.db_session.commit()
            
            logger.info(f"Updated config instance {instance_id}")
            return True, instance, []
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error updating config instance {instance_id}: {e}")
            return False, None, [str(e)]
    
    def get_config_instance(self, instance_id: int) -> Optional[ConfigInstance]:
        """Get a configuration instance by ID"""
        return self.db_session.query(ConfigInstance).filter(
            ConfigInstance.id == instance_id
        ).first()
    
    def get_config_instances_by_template(
        self, 
        template_key: str, 
        status: Optional[str] = None
    ) -> List[ConfigInstance]:
        """Get all config instances for a template, optionally filtered by status"""
        query = self.db_session.query(ConfigInstance).join(ConfigTemplate).filter(
            ConfigTemplate.template_key == template_key
        )
        
        if status:
            query = query.filter(ConfigInstance.status == status)
        
        return query.all()
    
    def activate_config_instance(self, instance_id: int) -> Tuple[bool, List[str]]:
        """Activate a configuration instance"""
        try:
            instance = self.get_config_instance(instance_id)
            if not instance:
                return False, [f"Config instance {instance_id} not found"]
            
            instance.status = 'active'
            
            # Propagate activation
            propagation_success, propagation_errors = propagate_config_changes(
                instance, {}, self.db_session, activation=True
            )
            
            if not propagation_success:
                return False, propagation_errors
            
            self.db_session.commit()
            logger.info(f"Activated config instance {instance_id}")
            return True, []
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error activating config instance {instance_id}: {e}")
            return False, [str(e)]
    
    def archive_config_instance(self, instance_id: int) -> Tuple[bool, List[str]]:
        """Archive a configuration instance"""
        try:
            instance = self.get_config_instance(instance_id)
            if not instance:
                return False, [f"Config instance {instance_id} not found"]
            
            instance.status = 'archived'
            
            # Propagate deactivation
            propagation_success, propagation_errors = propagate_config_changes(
                instance, {}, self.db_session, deactivation=True
            )
            
            if not propagation_success:
                return False, propagation_errors
            
            self.db_session.commit()
            logger.info(f"Archived config instance {instance_id}")
            return True, []
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error archiving config instance {instance_id}: {e}")
            return False, [str(e)]
    
    def get_config_version_history(self, instance_id: int) -> List[ConfigVersion]:
        """Get version history for a configuration instance"""
        return self.db_session.query(ConfigVersion).filter(
            ConfigVersion.config_instance_id == instance_id
        ).order_by(ConfigVersion.version_number.desc()).all()
    
    def rollback_config_instance(
        self, 
        instance_id: int, 
        version_number: int,
        changed_by: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """Rollback a configuration instance to a previous version"""
        try:
            # Get the target version
            version = self.db_session.query(ConfigVersion).filter(
                and_(
                    ConfigVersion.config_instance_id == instance_id,
                    ConfigVersion.version_number == version_number
                )
            ).first()
            
            if not version:
                return False, [f"Version {version_number} not found for instance {instance_id}"]
            
            if not version.can_rollback:
                return False, [f"Version {version_number} cannot be rolled back"]
            
            # Get current instance
            instance = self.get_config_instance(instance_id)
            if not instance:
                return False, [f"Config instance {instance_id} not found"]
            
            # Apply rollback changes
            current_data = instance.instance_data
            rollback_updates = self._apply_rollback_changes(current_data, version.changes)
            
            # Update the instance
            instance.instance_data = rollback_updates
            
            # Create rollback version
            self._create_version(
                instance, 
                {"rollback_to_version": version_number}, 
                changed_by, 
                f"Rollback to version {version_number}"
            )
            
            # Propagate rollback
            propagation_success, propagation_errors = propagate_config_changes(
                instance, rollback_updates, self.db_session
            )
            
            if not propagation_success:
                return False, propagation_errors
            
            self.db_session.commit()
            logger.info(f"Rolled back config instance {instance_id} to version {version_number}")
            return True, []
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error rolling back config instance {instance_id}: {e}")
            return False, [str(e)]
    
    def _create_version(
        self, 
        instance: ConfigInstance, 
        changes: Dict[str, Any], 
        changed_by: Optional[int], 
        change_reason: str
    ) -> ConfigVersion:
        """Create a new version record"""
        # Get the next version number
        last_version = self.db_session.query(ConfigVersion).filter(
            ConfigVersion.config_instance_id == instance.id
        ).order_by(ConfigVersion.version_number.desc()).first()
        
        next_version = (last_version.version_number + 1) if last_version else 1
        
        version = ConfigVersion(
            config_instance_id=instance.id,
            version_number=next_version,
            changed_by=changed_by,
            changes=changes,
            change_reason=change_reason
        )
        
        self.db_session.add(version)
        return version
    
    def _calculate_changes(
        self, 
        old_data: Dict[str, Any], 
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate the differences between two configuration datasets"""
        changes = {}
        
        # Find added/updated fields
        for key, new_value in new_data.items():
            if key not in old_data:
                changes[f"added_{key}"] = new_value
            elif old_data[key] != new_value:
                changes[f"updated_{key}"] = {
                    "old": old_data[key],
                    "new": new_value
                }
        
        # Find removed fields
        for key in old_data:
            if key not in new_data:
                changes[f"removed_{key}"] = old_data[key]
        
        return changes
    
    def _apply_rollback_changes(
        self, 
        current_data: Dict[str, Any], 
        version_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply rollback changes to current data"""
        rollback_data = current_data.copy()
        
        for change_key, change_value in version_changes.items():
            if change_key.startswith("added_"):
                # Remove added field
                field_name = change_key[6:]  # Remove "added_" prefix
                if field_name in rollback_data:
                    del rollback_data[field_name]
            elif change_key.startswith("updated_"):
                # Revert to old value
                field_name = change_key[8:]  # Remove "updated_" prefix
                if isinstance(change_value, dict) and "old" in change_value:
                    rollback_data[field_name] = change_value["old"]
            elif change_key.startswith("removed_"):
                # Add back removed field
                field_name = change_key[8:]  # Remove "removed_" prefix
                rollback_data[field_name] = change_value
        
        return rollback_data


# Global instance for easy access
config_manager = ConfigurationManager()