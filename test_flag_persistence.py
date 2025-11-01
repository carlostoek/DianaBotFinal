#!/usr/bin/env python3
"""
Test script to verify flag persistence issues
"""

from database.connection import get_db
from database.models import UserNarrativeProgress
from modules.narrative.flags import set_narrative_flag, get_narrative_flag, get_all_narrative_flags

def test_flag_persistence():
    """Test that multiple flags persist correctly"""
    user_id = 1
    
    print("=== Testing Flag Persistence ===")
    
    # Clear any existing flags first
    from modules.narrative.flags import reset_all_narrative_flags
    reset_all_narrative_flags(user_id)
    
    print("\n1. Setting multiple flags in sequence:")
    set_narrative_flag(user_id, 'flag_bool', True)
    set_narrative_flag(user_id, 'flag_int', 42)
    set_narrative_flag(user_id, 'flag_str', 'test_value')
    
    print("2. Reading flags immediately:")
    flags = get_all_narrative_flags(user_id)
    print(f"   All flags: {flags}")
    
    print("3. Setting more flags:")
    set_narrative_flag(user_id, 'flag_float', 3.14)
    set_narrative_flag(user_id, 'flag_list', [1, 2, 3])
    
    print("4. Reading flags again:")
    flags = get_all_narrative_flags(user_id)
    print(f"   All flags: {flags}")
    
    print("5. Testing individual flag retrieval:")
    print(f"   flag_bool: {get_narrative_flag(user_id, 'flag_bool')}")
    print(f"   flag_int: {get_narrative_flag(user_id, 'flag_int')}")
    print(f"   flag_str: {get_narrative_flag(user_id, 'flag_str')}")
    print(f"   flag_float: {get_narrative_flag(user_id, 'flag_float')}")
    print(f"   flag_list: {get_narrative_flag(user_id, 'flag_list')}")
    
    print("\n6. Testing database directly:")
    db = next(get_db())
    progress = db.query(UserNarrativeProgress).filter(
        UserNarrativeProgress.user_id == user_id
    ).first()
    if progress:
        print(f"   Database flags: {progress.narrative_flags}")
    else:
        print("   No progress entry found")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_flag_persistence()