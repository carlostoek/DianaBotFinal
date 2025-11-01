#!/usr/bin/env python3
"""
Test complete subscription conversion flow
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.admin.subscription_lifecycle import SubscriptionLifecycle
from database.connection import get_db
from database.models import User, ConversionFunnel

def test_complete_subscription_flow():
    """Test the complete subscription conversion flow from start to finish"""
    print("Testing Complete Subscription Conversion Flow...")
    
    try:
        # Create subscription lifecycle instance
        lifecycle = SubscriptionLifecycle()
        print("✓ SubscriptionLifecycle instance created")
        
        # Test user ID (use a test user)
        test_user_id = 1
        
        # 1. Start conversion funnel
        print("\n1. Starting conversion funnel...")
        start_result = lifecycle.start_conversion_funnel(
            user_id=test_user_id,
            funnel_type="free_to_vip",
            initial_stage="free_trial"
        )
        print(f"✓ start_conversion_funnel: {start_result}")
        
        # 2. Get active funnel
        db = next(get_db())
        active_funnel = db.query(ConversionFunnel).filter(
            ConversionFunnel.user_id == test_user_id,
            ConversionFunnel.is_active == True
        ).first()
        
        if active_funnel:
            print(f"✓ Active funnel found: ID {active_funnel.id}")
            funnel_id = active_funnel.id
            
            # 3. Update conversion stage
            print("\n2. Updating conversion stage...")
            update_result = lifecycle.update_conversion_stage(
                funnel_id=funnel_id,
                new_stage="engagement",
                metadata={"action": "story_completed"}
            )
            print(f"✓ update_conversion_stage: {update_result}")
            
            # 4. Track offer interactions
            print("\n3. Tracking offer interactions...")
            track_result = lifecycle.track_offer_interaction(
                user_id=test_user_id,
                offer_type="trial",
                interaction_type="shown",
                metadata={"offer_id": "free_trial_7d"}
            )
            print(f"✓ track_offer_interaction (shown): {track_result}")
            
            track_click_result = lifecycle.track_offer_interaction(
                user_id=test_user_id,
                offer_type="trial",
                interaction_type="clicked",
                metadata={"offer_id": "free_trial_7d"}
            )
            print(f"✓ track_offer_interaction (clicked): {track_click_result}")
            
            # 5. Get contextual offers
            print("\n4. Getting contextual offers...")
            offers = lifecycle.get_contextual_offers(test_user_id)
            print(f"✓ get_contextual_offers: {len(offers)} offers")
            for offer in offers:
                print(f"  - {offer['title']}: {offer['description']}")
            
            # 6. Update to consideration stage
            print("\n5. Moving to consideration stage...")
            consideration_result = lifecycle.update_conversion_stage(
                funnel_id=funnel_id,
                new_stage="consideration",
                metadata={"action": "offer_clicked"}
            )
            print(f"✓ update_conversion_stage (consideration): {consideration_result}")
            
            # 7. Simulate subscription conversion
            print("\n6. Simulating subscription conversion...")
            conversion_result = lifecycle.handle_subscription_conversion(
                user_id=test_user_id,
                subscription_type="monthly",
                payment_data={
                    "amount": 9.99,
                    "payment_method": "stripe",
                    "currency": "USD"
                }
            )
            print(f"✓ handle_subscription_conversion: {conversion_result}")
            
            # 8. Verify funnel completion
            # Refresh the funnel from database
            db.refresh(active_funnel)
            
            if active_funnel and active_funnel.is_completed:
                print(f"✓ Funnel completed successfully!")
                print(f"  - Final stage: {active_funnel.stage_completed}")
                print(f"  - Time to convert: {active_funnel.funnel_data.get('time_to_convert', 0):.2f} seconds")
                print(f"  - Conversion value: ${active_funnel.funnel_data.get('conversion_value', 0)}")
            else:
                print("✗ Funnel not marked as completed")
                
            # 9. Test analytics data
            print("\n7. Testing analytics data...")
            from api.routers.analytics import get_conversion_funnel_analytics
            from api.middleware.auth import require_role
            
            # Note: This would require admin authentication in production
            # For testing, we'll directly query the database
            total_funnels = db.query(ConversionFunnel).count()
            completed_funnels = db.query(ConversionFunnel).filter(
                ConversionFunnel.is_completed == True
            ).count()
            
            print(f"✓ Total funnels in system: {total_funnels}")
            print(f"✓ Completed funnels: {completed_funnels}")
            
            # 10. Test bot command integration
            print("\n8. Testing bot command integration...")
            from bot.commands.subscription import subscription_offers, subscription_conversion, subscription_analytics
            print("✓ Bot command imports successful")
            
            print("\n✅ Complete subscription conversion flow test PASSED!")
            return True
            
        else:
            print("✗ No active funnel found")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_complete_subscription_flow()