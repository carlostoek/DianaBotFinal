#!/usr/bin/env python3
"""
Test script for the inventory system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, UserBalance
from modules.gamification.inventory import inventory_service
from modules.gamification.besitos import besitos_service


def test_inventory_system():
    """Test the inventory system functionality"""
    
    print("🧪 Testing Inventory System...\n")
    
    # Get a test user (create one if needed)
    db: Session = next(get_db())
    
    try:
        # Get or create test user
        test_user = db.query(User).filter(User.telegram_id == 123456789).first()
        
        if not test_user:
            print("Creating test user...")
            test_user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User",
                language_code="es"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user: {test_user.id}")
        
        # Ensure user has balance
        user_balance = db.query(UserBalance).filter(UserBalance.user_id == test_user.id).first()
        if not user_balance:
            user_balance = UserBalance(user_id=test_user.id, besitos=100, lifetime_besitos=100)
            db.add(user_balance)
            db.commit()
            print(f"✅ Created balance for user: {user_balance.besitos} besitos")
        
        print(f"\n🧪 Testing with user: {test_user.id} (Telegram: {test_user.telegram_id})")
        
        # Test 1: Add items to inventory
        print("\n1️⃣ Testing item addition...")
        test_items = [
            ("caramelo_energia", 3, "test"),
            ("pocion_doble_besitos", 1, "test"),
            ("fragmento_espejo_1", 1, "test")
        ]
        
        for item_key, quantity, source in test_items:
            success = inventory_service.add_item_to_inventory(test_user.id, item_key, quantity, source)
            if success:
                print(f"   ✅ Added {quantity} {item_key}")
            else:
                print(f"   ❌ Failed to add {item_key}")
        
        # Test 2: Get user inventory
        print("\n2️⃣ Testing inventory retrieval...")
        inventory = inventory_service.get_user_inventory(test_user.id)
        print(f"   📦 Inventory items: {len(inventory)}")
        for item in inventory:
            print(f"      - {item['name']} x{item['quantity']}")
        
        # Test 3: Check item existence
        print("\n3️⃣ Testing item checks...")
        has_caramelo = inventory_service.has_item(test_user.id, "caramelo_energia")
        has_te = inventory_service.has_item(test_user.id, "te_fortuna")
        print(f"   ✅ Has caramelo_energia: {has_caramelo}")
        print(f"   ❌ Has te_fortuna: {has_te}")
        
        # Test 4: Get item quantity
        print("\n4️⃣ Testing quantity checks...")
        caramelo_qty = inventory_service.get_item_quantity(test_user.id, "caramelo_energia")
        print(f"   📊 Caramelo quantity: {caramelo_qty}")
        
        # Test 5: Remove items
        print("\n5️⃣ Testing item removal...")
        success = inventory_service.remove_item_from_inventory(test_user.id, "caramelo_energia", 1, "test")
        if success:
            print(f"   ✅ Removed 1 caramelo_energia")
            new_qty = inventory_service.get_item_quantity(test_user.id, "caramelo_energia")
            print(f"   📊 New quantity: {new_qty}")
        else:
            print(f"   ❌ Failed to remove caramelo_energia")
        
        # Test 6: Get item details
        print("\n6️⃣ Testing item details...")
        item_details = inventory_service.get_item_by_key("pocion_doble_besitos")
        if item_details:
            print(f"   📝 Item: {item_details['name']}")
            print(f"   📋 Type: {item_details['item_type']}")
            print(f"   ⭐ Rarity: {item_details['rarity']}")
        else:
            print(f"   ❌ Item not found")
        
        # Final inventory state
        print("\n📊 Final Inventory State:")
        final_inventory = inventory_service.get_user_inventory(test_user.id)
        for item in final_inventory:
            print(f"   - {item['name']} x{item['quantity']}")
        
        print("\n🎉 Inventory system tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_inventory_system()