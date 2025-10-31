"""
Narrative Flags System

Manages narrative flags that track important decisions and story state.
Flags are stored in user_narrative_progress.narrative_flags as JSON.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import UserNarrativeProgress


def set_narrative_flag(user_id: int, flag_name: str, value: Any) -> bool:
    """
    Set a narrative flag for a user.
    
    Args:
        user_id: User ID
        flag_name: Name of the flag to set
        value: Value to set (can be bool, int, str, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    db: Session = next(get_db())
    try:
        # Get all user progress entries
        progress_entries = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).all()
        
        if not progress_entries:
            # Create a new progress entry if none exists
            progress = UserNarrativeProgress(
                user_id=user_id,
                fragment_id=1,  # Default fragment
                narrative_flags={flag_name: value}
            )
            db.add(progress)
        else:
            # Update flags in all progress entries (flags are user-wide)
            for progress in progress_entries:
                current_flags = progress.narrative_flags or {}
                # Create a completely new dictionary to force SQLAlchemy change detection
                new_flags = {**current_flags, flag_name: value}
                progress.narrative_flags = new_flags
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error setting narrative flag: {e}")
        return False
    finally:
        db.close()


def get_narrative_flag(user_id: int, flag_name: str, default: Any = None) -> Any:
    """
    Get the value of a narrative flag for a user.
    
    Args:
        user_id: User ID
        flag_name: Name of the flag to get
        default: Default value if flag doesn't exist
        
    Returns:
        Flag value or default
    """
    db: Session = next(get_db())
    try:
        # Get any progress entry for this user
        progress = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).first()
        
        if progress and progress.narrative_flags:
            return progress.narrative_flags.get(flag_name, default)
        
        return default
        
    except Exception as e:
        print(f"Error getting narrative flag: {e}")
        return default
    finally:
        db.close()


def has_narrative_flags(user_id: int, flags_list: List[str]) -> bool:
    """
    Check if user has all specified narrative flags set to True.
    
    Args:
        user_id: User ID
        flags_list: List of flag names to check
        
    Returns:
        True if all flags are True, False otherwise
    """
    db: Session = next(get_db())
    try:
        # Get any progress entry for this user
        progress = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).first()
        
        if not progress or not progress.narrative_flags:
            return False
        
        # Check if all flags in the list are True
        for flag_name in flags_list:
            if not progress.narrative_flags.get(flag_name, False):
                return False
        
        return True
        
    except Exception as e:
        print(f"Error checking narrative flags: {e}")
        return False
    finally:
        db.close()


def get_all_narrative_flags(user_id: int) -> Dict[str, Any]:
    """
    Get all narrative flags for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary of all narrative flags
    """
    db: Session = next(get_db())
    try:
        # Get any progress entry for this user
        progress = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).first()
        
        if progress and progress.narrative_flags:
            return progress.narrative_flags.copy()
        
        return {}
        
    except Exception as e:
        print(f"Error getting all narrative flags: {e}")
        return {}
    finally:
        db.close()


def clear_narrative_flag(user_id: int, flag_name: str) -> bool:
    """
    Clear a specific narrative flag for a user.
    
    Args:
        user_id: User ID
        flag_name: Name of the flag to clear
        
    Returns:
        True if successful, False otherwise
    """
    db: Session = next(get_db())
    try:
        # Get all progress entries for this user
        progress_entries = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).all()
        
        if progress_entries:
            for progress in progress_entries:
                current_flags = progress.narrative_flags or {}
                if flag_name in current_flags:
                    del current_flags[flag_name]
                    progress.narrative_flags = current_flags
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error clearing narrative flag: {e}")
        return False
    finally:
        db.close()


def reset_all_narrative_flags(user_id: int) -> bool:
    """
    Reset all narrative flags for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        True if successful, False otherwise
    """
    db: Session = next(get_db())
    try:
        # Get all progress entries for this user
        progress_entries = db.query(UserNarrativeProgress).filter(
            UserNarrativeProgress.user_id == user_id
        ).all()
        
        if progress_entries:
            for progress in progress_entries:
                progress.narrative_flags = {}
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error resetting narrative flags: {e}")
        return False
    finally:
        db.close()