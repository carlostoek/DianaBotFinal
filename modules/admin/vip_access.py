#!/usr/bin/env python3
"""
VIP Access Control Middleware
Multi-layer verification for VIP content access
"""

import logging
from datetime import datetime
from typing import Tuple, Optional
from database.connection import get_redis
from modules.admin.subscriptions import get_active_subscription, is_vip

logger = logging.getLogger(__name__)


class VIPAccessControl:
    """VIP access control with multi-layer verification"""
    
    def __init__(self):
        self.redis_client = get_redis()
        # VIP channel ID (should be configured in settings)
        self.vip_channel_id = "@dianabot_vip"  # Placeholder - should be real channel ID
    
    def verify_vip_access(self, user_id: int, resource_type: str = None, resource_id: str = None) -> Tuple[bool, str]:
        """
        Multi-layer verification for VIP content access
        
        Args:
            user_id: User ID
            resource_type: Type of resource ('fragment', 'mission', 'channel')
            resource_id: Resource identifier
            
        Returns:
            Tuple of (access_granted, reason)
        """
        # Layer 1: Verify subscription in database
        subscription = get_active_subscription(user_id)
        if not subscription or subscription.status != 'active':
            return False, "No active VIP subscription"
        
        # Layer 2: Verify dates
        now = datetime.now()
        if not (subscription.start_date <= now <= subscription.end_date):
            return False, "Subscription expired"
        
        # Layer 3: Verify Telegram channel membership (with cache)
        cache_key = f'vip_member:{user_id}'
        is_member = self.redis_client.get(cache_key)
        
        if is_member is None:
            # Not in cache, verify with Telegram (placeholder - would need bot context)
            # For now, assume membership if subscription is active
            is_member = True
            self.redis_client.setex(cache_key, 3600, '1' if is_member else '0')
        else:
            is_member = is_member == b'1'
        
        if not is_member:
            return False, "Not member of VIP channel"
        
        # Layer 4: Verify specific resource permissions
        if resource_type == 'fragment':
            # Check if fragment is VIP-restricted
            # This would require checking fragment metadata
            # For now, assume all VIP fragments require verification
            pass
        
        return True, "Access granted"
    
    def check_telegram_membership(self, user_id: int, channel_id: str) -> bool:
        """
        Check if user is member of Telegram channel
        
        Note: This requires bot context and would be implemented
        with actual Telegram API calls in production
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if user is member, False otherwise
        """
        # Placeholder implementation
        # In production, this would use:
        # bot.get_chat_member(channel_id, user_id)
        
        logger.info(f"Checking Telegram membership for user {user_id} in channel {channel_id}")
        
        # For now, assume membership if user has active subscription
        return is_vip(user_id)
    
    def clear_membership_cache(self, user_id: int) -> bool:
        """
        Clear membership cache for user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = f'vip_member:{user_id}'
            self.redis_client.delete(cache_key)
            logger.info(f"Cleared membership cache for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear membership cache for user {user_id}: {e}")
            return False
    
    def get_vip_status(self, user_id: int) -> dict:
        """
        Get comprehensive VIP status for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with VIP status information
        """
        subscription = get_active_subscription(user_id)
        
        if not subscription:
            return {
                "is_vip": False,
                "reason": "No active subscription",
                "subscription": None
            }
        
        now = datetime.now()
        is_active = (subscription.status == 'active' and 
                    subscription.start_date <= now <= subscription.end_date)
        
        # Check membership cache
        cache_key = f'vip_member:{user_id}'
        is_member = self.redis_client.get(cache_key)
        if is_member is not None:
            is_member = is_member == b'1'
        else:
            is_member = self.check_telegram_membership(user_id, self.vip_channel_id)
        
        return {
            "is_vip": is_active and is_member,
            "subscription": {
                "type": subscription.subscription_type,
                "start_date": subscription.start_date.isoformat() if hasattr(subscription.start_date, 'isoformat') else str(subscription.start_date),
                "end_date": subscription.end_date.isoformat() if hasattr(subscription.end_date, 'isoformat') else str(subscription.end_date),
                "status": subscription.status,
                "auto_renew": subscription.auto_renew
            },
            "channel_membership": is_member,
            "days_remaining": (subscription.end_date - now).days if subscription.end_date > now else 0
        }


# Global instance
vip_access = VIPAccessControl()


# Convenience functions
def verify_vip_access(user_id: int, resource_type: str = None, resource_id: str = None) -> Tuple[bool, str]:
    """Verify VIP access for user"""
    return vip_access.verify_vip_access(user_id, resource_type, resource_id)

def get_vip_status(user_id: int) -> dict:
    """Get comprehensive VIP status for user"""
    return vip_access.get_vip_status(user_id)

def clear_membership_cache(user_id: int) -> bool:
    """Clear membership cache for user"""
    return vip_access.clear_membership_cache(user_id)