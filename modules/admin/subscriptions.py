#!/usr/bin/env python3
"""
Subscription Service for VIP System
Manages user subscriptions and VIP status
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database.models import Subscription, User
from bot.utils.user_validation import (
    validate_user_exists, 
    validate_user_not_banned, 
    validate_user_can_subscribe,
    UserValidationError
)

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing user subscriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subscription(self, user_id: int, subscription_type: str, duration_days: int, 
                          payment_reference: Optional[str] = None, auto_renew: bool = False) -> Optional[Subscription]:
        """
        Create a new subscription for a user
        
        Args:
            user_id: User ID
            subscription_type: Type of subscription ('monthly', 'yearly', 'lifetime')
            duration_days: Duration in days
            payment_reference: Payment reference (optional)
            auto_renew: Whether to auto-renew
            
        Returns:
            Subscription object if successful, None otherwise
        """
        try:
            # Validate user can subscribe
            validate_user_can_subscribe(self.db, user_id)
            
            # Calculate dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                start_date=start_date,
                end_date=end_date,
                status='active',
                payment_reference=payment_reference,
                auto_renew=auto_renew
            )
            
            self.db.add(subscription)
            self.db.commit()
            
            # Update user state
            self._update_user_state(user_id, 'vip')
            
            logger.info(f"Created {subscription_type} subscription for user {user_id}")
            return subscription
            
        except UserValidationError as e:
            logger.warning(f"User validation failed for subscription creation: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create subscription for user {user_id}: {e}")
            return None
    
    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Get active subscription for user
        
        Args:
            user_id: User ID
            
        Returns:
            Active subscription or None
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            ).first()
            
            if subscription and subscription.end_date:
                # Convert to naive datetime for comparison
                end_date = subscription.end_date.replace(tzinfo=None) if subscription.end_date.tzinfo else subscription.end_date
                now = datetime.now()
                
                if end_date >= now:
                    return subscription
                
                # If subscription exists but is expired, update status
                if end_date < now:
                    subscription.status = 'expired'
                    self.db.commit()
                    self._update_user_state(user_id, 'free')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active subscription for user {user_id}: {e}")
            return None
    
    def is_vip(self, user_id: int) -> bool:
        """
        Check if user has active VIP subscription
        
        Args:
            user_id: User ID
            
        Returns:
            True if user is VIP, False otherwise
        """
        try:
            # Validate user exists and is not banned
            validate_user_not_banned(self.db, user_id)
            subscription = self.get_active_subscription(user_id)
            return subscription is not None
        except UserValidationError:
            return False
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            subscription.status = 'cancelled'
            self.db.commit()
            
            # Update user state
            self._update_user_state(subscription.user_id, 'free')
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            return False
    
    def get_expiring_subscriptions(self, days_before: int = 7) -> List[Subscription]:
        """
        Get subscriptions expiring within specified days
        
        Args:
            days_before: Days before expiration
            
        Returns:
            List of expiring subscriptions
        """
        try:
            expiration_date = datetime.now() + timedelta(days=days_before)
            
            subscriptions = self.db.query(Subscription).filter(
                Subscription.status == 'active',
                Subscription.end_date <= expiration_date,
                Subscription.end_date >= datetime.now()
            ).all()
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Failed to get expiring subscriptions: {e}")
            return []
    
    def get_expired_subscriptions(self) -> List[Subscription]:
        """
        Get subscriptions that have expired but still marked as active
        
        Returns:
            List of expired subscriptions
        """
        try:
            subscriptions = self.db.query(Subscription).filter(
                Subscription.status == 'active',
                Subscription.end_date < datetime.now()
            ).all()
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Failed to get expired subscriptions: {e}")
            return []
    
    def renew_subscription(self, subscription_id: int, duration_days: int) -> Optional[Subscription]:
        """
        Renew an existing subscription
        
        Args:
            subscription_id: Subscription ID
            duration_days: Duration in days
            
        Returns:
            Updated subscription or None
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                logger.warning(f"Subscription {subscription_id} not found")
                return None
            
            # Extend end date
            current_end = max(subscription.end_date, datetime.now())
            new_end = current_end + timedelta(days=duration_days)
            
            subscription.end_date = new_end
            subscription.status = 'active'
            self.db.commit()
            
            # Update user state
            self._update_user_state(subscription.user_id, 'vip')
            
            logger.info(f"Renewed subscription {subscription_id} until {new_end}")
            return subscription
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to renew subscription {subscription_id}: {e}")
            return None
    
    def _update_user_state(self, user_id: int, state: str) -> bool:
        """
        Update user state
        
        Args:
            user_id: User ID
            state: New state ('free', 'vip', 'banned')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.user_state = state
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update user state for {user_id}: {e}")
            return False