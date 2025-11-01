#!/usr/bin/env python3
"""
Test complete narrative flow with flags and templating
"""

from modules.narrative.engine import NarrativeEngine
from modules.narrative.flags import set_narrative_flag, get_narrative_flag, get_all_narrative_flags
from modules.narrative.templating import interpolate_narrative_text
from database.connection import get_db
from database.models import User

def test_complete_narrative_flow():
    """Test the complete narrative flow with flags and templating"""
    user_id = 1
    
    print("=== Testing Complete Narrative Flow ===\n")
    
    # Get user and engine
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    engine = NarrativeEngine()
    
    print("1. Initial State:")
    print(f"   User ID: {user_id}")
    print(f"   Current progress: {engine.get_current_progress(user)}")
    print(f"   All narrative flags: {get_all_narrative_flags(user_id)}")
    
    print("\n2. Setting narrative flags:")
    set_narrative_flag(user_id, 'trusted_lucien', True)
    set_narrative_flag(user_id, 'lucien_trust_level', 7)
    set_narrative_flag(user_id, 'diana_alliance', False)
    print(f"   Flags set: trusted_lucien=True, lucien_trust_level=7, diana_alliance=False")
    
    print("\n3. Testing templating with flags:")
    test_texts = [
        'Lucien looks at you {{flag:trusted_lucien ? "with warmth" : "cautiously"}}.',
        'Your trust level with Lucien is {{flag:lucien_trust_level}}.',
        '{{flag:lucien_trust_level > 5 ? "Lucien trusts you completely" : "Lucien is still wary"}}.',
        '{{flag:diana_alliance ? "You have allied with Diana" : "You remain neutral with Diana"}}.'
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = interpolate_narrative_text(text, user_id)
        print(f"   {i}. {result}")
    
    print("\n4. Testing flag retrieval:")
    print(f"   trusted_lucien: {get_narrative_flag(user_id, 'trusted_lucien')}")
    print(f"   lucien_trust_level: {get_narrative_flag(user_id, 'lucien_trust_level')}")
    print(f"   diana_alliance: {get_narrative_flag(user_id, 'diana_alliance')}")
    
    print("\n5. Testing narrative engine integration:")
    
    # Test decision visibility with flags
    test_decision = {
        "text": "Trust Lucien",
        "next_fragment": "lucien_trusted_path",
        "visible_if": {
            "narrative_flags": ["trusted_lucien"]
        }
    }
    
    user_state = engine.get_user_narrative_state(user_id)
    is_visible = engine._check_decision_visibility(user_state, test_decision)
    print(f"   Decision 'Trust Lucien' visible: {is_visible}")
    
    # Test decision that should not be visible
    test_decision2 = {
        "text": "Betray Lucien",
        "next_fragment": "lucien_betrayal_path",
        "visible_if": {
            "narrative_flags": ["betrayed_lucien"]  # This flag doesn't exist
        }
    }
    
    is_visible2 = engine._check_decision_visibility(user_state, test_decision2)
    print(f"   Decision 'Betray Lucien' visible: {is_visible2}")
    
    print("\n6. Testing flag persistence across sessions:")
    # Simulate new session by creating new engine instance
    engine2 = NarrativeEngine()
    user_state2 = engine2.get_user_narrative_state(user_id)
    
    # Check if flags are still there
    print(f"   trusted_lucien (new session): {get_narrative_flag(user_id, 'trusted_lucien')}")
    print(f"   lucien_trust_level (new session): {get_narrative_flag(user_id, 'lucien_trust_level')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_complete_narrative_flow()