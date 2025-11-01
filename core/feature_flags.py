"""
Feature Flags System

Manages feature flags for gradual rollout and A/B testing.
Supports percentage-based rollout, user segmentation, and beta testing.
"""

import hashlib
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.connection import get_db
from database.models import ConfigTemplate, ConfigInstance
from core.config_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Main feature flags manager class"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or next(get_db())
        self.config_manager = ConfigurationManager(self.db_session)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
        self._last_cache_update = datetime.min
    
    def is_enabled(self, feature_name: str, user_id: int, default: bool = False) -> bool:
        """
        Check if a feature is enabled for a specific user.
        
        Args:
            feature_name: Name of the feature to check
            user_id: User ID to check for
            default: Default value if feature flag not found
            
        Returns:
            True if feature is enabled for this user, False otherwise
        """
        try:
            # Get feature flag configuration
            feature_config = self._get_feature_config(feature_name)
            
            if not feature_config:
                return default
            
            # Check if feature is globally enabled
            if not feature_config.get('enabled', False):
                return False
            
            # Check beta testers
            if self._is_beta_tester(user_id, feature_config):
                return True
            
            # Check rollout percentage
            rollout_percentage = feature_config.get('rollout_percentage', 0)
            if rollout_percentage >= 100:
                return True
            
            # Calculate user hash for percentage-based rollout
            user_hash = self._get_user_hash(user_id, feature_name)
            return user_hash < rollout_percentage
            
        except Exception as e:
            logger.error(f"Error checking feature flag {feature_name} for user {user_id}: {e}")
            return default
    
    def get_rollout_percentage(self, feature_name: str) -> int:
        """Get the current rollout percentage for a feature"""
        feature_config = self._get_feature_config(feature_name)
        return feature_config.get('rollout_percentage', 0) if feature_config else 0
    
    def set_rollout_percentage(self, feature_name: str, percentage: int) -> bool:
        """Set the rollout percentage for a feature"""
        try:
            feature_config = self._get_feature_config(feature_name)
            if not feature_config:
                return False
            
            # Update the configuration
            updates = {'rollout_percentage': max(0, min(100, percentage))}
            success, _, errors = self.config_manager.update_config_instance(
                feature_config['instance_id'], updates, change_reason=f"Set rollout to {percentage}%"
            )
            
            if success:
                self._clear_cache()
                logger.info(f"Set rollout percentage for {feature_name} to {percentage}%")
            else:
                logger.error(f"Failed to set rollout percentage for {feature_name}: {errors}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting rollout percentage for {feature_name}: {e}")
            return False
    
    def enable_feature(self, feature_name: str) -> bool:
        """Enable a feature globally"""
        return self._update_feature_status(feature_name, True)
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a feature globally"""
        return self._update_feature_status(feature_name, False)
    
    def add_beta_tester(self, feature_name: str, user_id: int) -> bool:
        """Add a user as beta tester for a feature"""
        try:
            feature_config = self._get_feature_config(feature_name)
            if not feature_config:
                return False
            
            beta_testers = set(feature_config.get('beta_testers', []))
            beta_testers.add(user_id)
            
            updates = {'beta_testers': list(beta_testers)}
            success, _, errors = self.config_manager.update_config_instance(
                feature_config['instance_id'], updates, change_reason=f"Added beta tester {user_id}"
            )
            
            if success:
                self._clear_cache()
                logger.info(f"Added user {user_id} as beta tester for {feature_name}")
            else:
                logger.error(f"Failed to add beta tester for {feature_name}: {errors}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding beta tester for {feature_name}: {e}")
            return False
    
    def remove_beta_tester(self, feature_name: str, user_id: int) -> bool:
        """Remove a user from beta testers for a feature"""
        try:
            feature_config = self._get_feature_config(feature_name)
            if not feature_config:
                return False
            
            beta_testers = set(feature_config.get('beta_testers', []))
            if user_id in beta_testers:
                beta_testers.remove(user_id)
                
                updates = {'beta_testers': list(beta_testers)}
                success, _, errors = self.config_manager.update_config_instance(
                    feature_config['instance_id'], updates, change_reason=f"Removed beta tester {user_id}"
                )
                
                if success:
                    self._clear_cache()
                    logger.info(f"Removed user {user_id} from beta testers for {feature_name}")
                else:
                    logger.error(f"Failed to remove beta tester for {feature_name}: {errors}")
                
                return success
            
            return True  # User wasn't a beta tester, so no change needed
            
        except Exception as e:
            logger.error(f"Error removing beta tester for {feature_name}: {e}")
            return False
    
    def get_beta_testers(self, feature_name: str) -> List[int]:
        """Get list of beta testers for a feature"""
        feature_config = self._get_feature_config(feature_name)
        return feature_config.get('beta_testers', []) if feature_config else []
    
    def create_feature_flag(self, feature_name: str, description: str = "") -> bool:
        """Create a new feature flag"""
        try:
            # Check if feature flag template exists
            template = self.db_session.query(ConfigTemplate).filter(
                and_(
                    ConfigTemplate.template_key == 'feature_flag',
                    ConfigTemplate.is_active == True
                )
            ).first()
            
            if not template:
                logger.error("Feature flag template not found")
                return False
            
            # Create initial feature flag configuration
            initial_config = {
                'name': feature_name,
                'description': description,
                'enabled': False,
                'rollout_percentage': 0,
                'beta_testers': [],
                'created_at': datetime.now().isoformat()
            }
            
            success, _, errors = self.config_manager.create_config_instance(
                'feature_flag', initial_config, status='active'
            )
            
            if success:
                logger.info(f"Created feature flag: {feature_name}")
            else:
                logger.error(f"Failed to create feature flag {feature_name}: {errors}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating feature flag {feature_name}: {e}")
            return False
    
    def get_feature_stats(self, feature_name: str) -> Dict[str, Any]:
        """Get statistics for a feature flag"""
        feature_config = self._get_feature_config(feature_name)
        if not feature_config:
            return {}
        
        return {
            'name': feature_name,
            'enabled': feature_config.get('enabled', False),
            'rollout_percentage': feature_config.get('rollout_percentage', 0),
            'beta_testers_count': len(feature_config.get('beta_testers', [])),
            'created_at': feature_config.get('created_at'),
            'description': feature_config.get('description', '')
        }
    
    def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all feature flags with their stats"""
        try:
            instances = self.config_manager.get_config_instances_by_template('feature_flag', 'active')
            features = []
            
            for instance in instances:
                feature_data = instance.instance_data
                features.append({
                    'name': feature_data.get('name', 'Unknown'),
                    'enabled': feature_data.get('enabled', False),
                    'rollout_percentage': feature_data.get('rollout_percentage', 0),
                    'beta_testers_count': len(feature_data.get('beta_testers', [])),
                    'description': feature_data.get('description', ''),
                    'instance_id': instance.id
                })
            
            return features
            
        except Exception as e:
            logger.error(f"Error getting all features: {e}")
            return []
    
    def _get_feature_config(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get feature configuration from cache or database"""
        # Check cache first
        if self._should_refresh_cache():
            self._refresh_cache()
        
        if feature_name in self._cache:
            return self._cache[feature_name]
        
        # Load from database
        try:
            instances = self.config_manager.get_config_instances_by_template('feature_flag', 'active')
            
            for instance in instances:
                feature_data = instance.instance_data
                if feature_data.get('name') == feature_name:
                    config = {
                        'enabled': feature_data.get('enabled', False),
                        'rollout_percentage': feature_data.get('rollout_percentage', 0),
                        'beta_testers': feature_data.get('beta_testers', []),
                        'instance_id': instance.id
                    }
                    self._cache[feature_name] = config
                    return config
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting feature config for {feature_name}: {e}")
            return None
    
    def _is_beta_tester(self, user_id: int, feature_config: Dict[str, Any]) -> bool:
        """Check if user is a beta tester for this feature"""
        return user_id in feature_config.get('beta_testers', [])
    
    def _get_user_hash(self, user_id: int, feature_name: str) -> int:
        """Calculate consistent hash for user-feature combination"""
        hash_input = f"{user_id}:{feature_name}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        return int(hash_value[:8], 16) % 100
    
    def _update_feature_status(self, feature_name: str, enabled: bool) -> bool:
        """Update feature enabled status"""
        try:
            feature_config = self._get_feature_config(feature_name)
            if not feature_config:
                return False
            
            updates = {'enabled': enabled}
            success, _, errors = self.config_manager.update_config_instance(
                feature_config['instance_id'], updates, 
                change_reason=f"{'Enabled' if enabled else 'Disabled'} feature"
            )
            
            if success:
                self._clear_cache()
                logger.info(f"{'Enabled' if enabled else 'Disabled'} feature: {feature_name}")
            else:
                logger.error(f"Failed to update feature status for {feature_name}: {errors}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating feature status for {feature_name}: {e}")
            return False
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        return datetime.now() - self._last_cache_update > self._cache_ttl
    
    def _refresh_cache(self) -> None:
        """Refresh the feature flag cache"""
        try:
            instances = self.config_manager.get_config_instances_by_template('feature_flag', 'active')
            self._cache.clear()
            
            for instance in instances:
                feature_data = instance.instance_data
                feature_name = feature_data.get('name')
                if feature_name:
                    self._cache[feature_name] = {
                        'enabled': feature_data.get('enabled', False),
                        'rollout_percentage': feature_data.get('rollout_percentage', 0),
                        'beta_testers': feature_data.get('beta_testers', []),
                        'instance_id': instance.id
                    }
            
            self._last_cache_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error refreshing feature flag cache: {e}")
    
    def _clear_cache(self) -> None:
        """Clear the feature flag cache"""
        self._cache.clear()
        self._last_cache_update = datetime.min


# Global instance for easy access
feature_flags = FeatureFlags()