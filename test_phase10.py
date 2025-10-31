#!/usr/bin/env python3
"""
Test script for Phase 10 features
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import User, UserNarrativeProgress
from modules.narrative.flags import set_narrative_flag, get_narrative_flag, get_all_narrative_flags
from modules.narrative.templating import interpolate_narrative_text


def test_phase10_features():
    """Test Phase 10 features"""
    
    db = SessionLocal()
    
    try:
        # Create a test user if it doesn't exist
        test_user = db.query(User).filter(User.telegram_id == 999999).first()
        if not test_user:
            test_user = User(
                telegram_id=999999,
                username="test_user",
                first_name="Test",
                last_name="User",
                language_code="es",
                current_state="start"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user with ID: {test_user.id}")
        
        # Test 1: Narrative Flags
        print("\n🧪 Test 1: Narrative Flags")
        print("Setting flag 'trusted_lucien' to True...")
        success = set_narrative_flag(test_user.id, "trusted_lucien", True)
        print(f"Flag set: {success}")
        
        print("Getting flag 'trusted_lucien'...")
        flag_value = get_narrative_flag(test_user.id, "trusted_lucien")
        print(f"Flag value: {flag_value}")
        
        print("Setting flag 'lucien_trust_level' to 7...")
        set_narrative_flag(test_user.id, "lucien_trust_level", 7)
        trust_level = get_narrative_flag(test_user.id, "lucien_trust_level")
        print(f"Trust level: {trust_level}")
        
        print("Getting all flags...")
        all_flags = get_all_narrative_flags(test_user.id)
        print(f"All flags: {all_flags}")
        
        # Test 2: Templating System
        print("\n🧪 Test 2: Templating System")
        
        templates = [
            "Hello {{flag:trusted_lucien ? 'friend' : 'stranger'}}",
            "Your trust level with Lucien: {{flag:lucien_trust_level}}",
            "{{flag:lucien_trust_level > 5 ? 'You are trusted' : 'You need to earn trust'}}",
            "{{flag:lucien_trust_level >= 7 ? 'Close ally' : 'Acquaintance'}}",
        ]
        
        for template in templates:
            result = interpolate_narrative_text(template, test_user.id)
            print(f"Template: {template}")
            print(f"Result: {result}")
            print("---")
        
        # Test 3: Branching Path Logic
        print("\n🧪 Test 3: Branching Path Logic")
        
        # Simulate different paths based on flags
        if get_narrative_flag(test_user.id, "trusted_lucien"):
            print("✅ Path: Trusted Lucien - Access to Lucien's storyline")
            set_narrative_flag(test_user.id, "lucien_path_unlocked", True)
        else:
            print("❌ Path: Distrusted Lucien - Access to Diana's storyline")
            set_narrative_flag(test_user.id, "diana_path_unlocked", True)
        
        if get_narrative_flag(test_user.id, "lucien_trust_level") >= 7:
            print("🌟 High trust level - Special dialogue options available")
        
        # Show final state
        print("\n📊 Final Narrative State:")
        final_flags = get_all_narrative_flags(test_user.id)
        for flag, value in final_flags.items():
            print(f"  {flag}: {value}")
        
        print("\n✅ Phase 10 tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_phase10_features()