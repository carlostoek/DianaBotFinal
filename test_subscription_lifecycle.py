#!/usr/bin/env python3
"""
Test for Subscription Lifecycle Management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.admin.subscription_lifecycle import SubscriptionLifecycle
from database.connection import get_db

def test_subscription_lifecycle():
    """Test basic subscription lifecycle functionality"""
    print("Testing Subscription Lifecycle...")
    
    try:
        # Create instance with proper dependency injection
        db = next(get_db())
        lifecycle = SubscriptionLifecycle(db)
        print("✓ SubscriptionLifecycle instance created")
        
        # Test starting conversion funnel
        result = lifecycle.start_conversion_funnel(
            user_id=1, 
            funnel_type="free_to_vip", 
            initial_stage="free_trial"
        )
        print(f"✓ start_conversion_funnel: {result}")
        
        # Test getting contextual offers
        offers = lifecycle.get_contextual_offers(user_id=1)
        print(f"✓ get_contextual_offers: {len(offers)} offers")
        
        # Test tracking offer interaction
        track_result = lifecycle.track_offer_interaction(
            user_id=1,
            offer_type="trial",
            interaction_type="shown",
            metadata={"offer_id": "free_trial_7d"}
        )
        print(f"✓ track_offer_interaction: {track_result}")
        
        print("✓ All subscription lifecycle tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_subscription_lifecycle()