#!/usr/bin/env python3
"""
User validation utilities for subscription operations
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import User, Subscription

logger = logging.getLogger(__name__)


class UserValidationError(Exception):
    """Custom exception for user validation errors"""
    pass


def validate_user_exists(db: Session, user_id: int) -> User:
    """
    Validate that a user exists in the database
    
    Args:
        db: Database session
        user_id: User ID to validate
        
    Returns:
        User object if found
        
    Raises:
        UserValidationError: If user doesn't exist
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UserValidationError(f"User with ID {user_id} not found")
    return user


def validate_user_not_banned(db: Session, user_id: int) -> User:
    """
    Validate that user is not banned
    
    Args:
        db: Database session
        user_id: User ID to validate
        
    Returns:
        User object if valid
        
    Raises:
        UserValidationError: If user is banned
    """
    user = validate_user_exists(db, user_id)
    
    # Check if user has banned state
    if hasattr(user, 'user_state') and user.user_state == 'banned':
        raise UserValidationError(f"User {user_id} is banned")
    
    return user


def validate_user_can_subscribe(db: Session, user_id: int) -> User:
    """
    Validate that user can subscribe (not already VIP, not banned, exists)
    
    Args:
        db: Database session
        user_id: User ID to validate
        
    Returns:
        User object if valid
        
    Raises:
        UserValidationError: If user cannot subscribe
    """
    user = validate_user_not_banned(db, user_id)
    
    # Check if user already has active subscription
    active_sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == 'active'
    ).first()
    
    if active_sub is not None and active_sub.end_date:
        # Check if subscription is still active
        now = datetime.now()
        # Convert to naive datetime for comparison
        end_date = active_sub.end_date.replace(tzinfo=None) if active_sub.end_date.tzinfo else active_sub.end_date
        if end_date >= now:
            raise UserValidationError(f"User {user_id} already has active subscription")
    
    return user


def validate_user_can_access_vip_content(db: Session, user_id: int) -> bool:
    """
    Validate that user can access VIP content
    
    Args:
        db: Database session
        user_id: User ID to validate
        
    Returns:
        True if user can access VIP content
    """
    try:
        user = validate_user_not_banned(db, user_id)
        
        # Check for active VIP subscription
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active'
        ).first()
        
        if active_sub and active_sub.end_date:
            # Convert to naive datetime for comparison
            end_date = active_sub.end_date.replace(tzinfo=None) if active_sub.end_date.tzinfo else active_sub.end_date
            now = datetime.now()
            if end_date >= now:
                return True
        
        return False
        
    except UserValidationError:
        return False


def get_user_state(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive user state for validation
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with user state information
    """
    try:
        user = validate_user_exists(db, user_id)
        
        # Get subscription status
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active'
        ).first()
        
        is_vip = False
        subscription_type = None
        days_remaining = 0
        
        if active_sub and active_sub.end_date:
            now = datetime.now()
            # Convert to naive datetime for comparison
            end_date = active_sub.end_date.replace(tzinfo=None) if active_sub.end_date.tzinfo else active_sub.end_date
            if end_date >= now:
                is_vip = True
                subscription_type = active_sub.subscription_type
                days_remaining = (end_date - now).days
        
        return {
            "user_id": user_id,
            "exists": True,
            "is_banned": hasattr(user, 'user_state') and user.user_state == 'banned',
            "is_vip": is_vip,
            "subscription_type": subscription_type,
            "days_remaining": days_remaining,
            "can_subscribe": not is_vip and not (hasattr(user, 'user_state') and user.user_state == 'banned'),
            "can_access_vip": is_vip
        }
        
    except UserValidationError:
        return {
            "user_id": user_id,
            "exists": False,
            "is_banned": False,
            "is_vip": False,
            "subscription_type": None,
            "days_remaining": 0,
            "can_subscribe": False,
            "can_access_vip": False
        }