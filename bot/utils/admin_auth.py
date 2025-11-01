#!/usr/bin/env python3
"""
Admin authentication utilities for Telegram bot commands
"""

import os
from typing import List, Optional


def is_admin_user(user_id: int) -> bool:
    """
    Check if a user is an admin based on environment configuration
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin, False otherwise
    """
    # Get admin user IDs from environment variable
    admin_ids_str = os.getenv("TELEGRAM_ADMIN_IDS", "")
    
    if not admin_ids_str:
        # Fallback to hardcoded admin IDs for development
        admin_ids = [123456789]  # Replace with actual admin IDs
    else:
        # Parse comma-separated admin IDs from environment
        admin_ids = [int(id_str.strip()) for id_str in admin_ids_str.split(",") if id_str.strip()]
    
    return user_id in admin_ids


def get_admin_users() -> List[int]:
    """
    Get list of admin user IDs
    
    Returns:
        List of admin user IDs
    """
    admin_ids_str = os.getenv("TELEGRAM_ADMIN_IDS", "")
    
    if not admin_ids_str:
        return [123456789]  # Fallback for development
    
    return [int(id_str.strip()) for id_str in admin_ids_str.split(",") if id_str.strip()]