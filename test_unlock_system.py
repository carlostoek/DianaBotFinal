#!/usr/bin/env python3
"""
Test script for the unlock system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.narrative.unlocks import UnlockEngine


def test_unlock_engine():
    """Test the unlock engine with various conditions"""
    
    print("🧪 Testing Unlock Engine...")
    
    unlock_engine = UnlockEngine()
    
    # Test 1: Simple besitos requirement
    print("\n1. Testing besitos requirement:")
    conditions_1 = {"min_besitos": 50}
    result_1 = unlock_engine.evaluate_conditions(1, conditions_1)
    print(f"   Conditions: {conditions_1}")
    print(f"   Result: {result_1}")
    
    # Test 2: Fragment requirement
    print("\n2. Testing fragment requirement:")
    conditions_2 = {"required_fragments": ["intro_1"]}
    result_2 = unlock_engine.evaluate_conditions(1, conditions_2)
    print(f"   Conditions: {conditions_2}")
    print(f"   Result: {result_2}")
    
    # Test 3: Complex AND condition
    print("\n3. Testing complex AND condition:")
    conditions_3 = {
        "operator": "AND",
        "conditions": [
            {"min_besitos": 50},
            {"required_fragments": ["intro_1"]}
        ]
    }
    result_3 = unlock_engine.evaluate_conditions(1, conditions_3)
    print(f"   Conditions: {conditions_3}")
    print(f"   Result: {result_3}")
    
    # Test 4: Complex OR condition
    print("\n4. Testing complex OR condition:")
    conditions_4 = {
        "operator": "OR",
        "conditions": [
            {"min_besitos": 100},
            {"required_items": ["llave_especial"]}
        ]
    }
    result_4 = unlock_engine.evaluate_conditions(1, conditions_4)
    print(f"   Conditions: {conditions_4}")
    print(f"   Result: {result_4}")
    
    # Test 5: Missing requirements
    print("\n5. Testing missing requirements:")
    conditions_5 = {
        "min_besitos": 200,
        "required_fragments": ["fragmento_inexistente"]
    }
    missing = unlock_engine.get_missing_requirements(1, conditions_5)
    print(f"   Conditions: {conditions_5}")
    print(f"   Missing: {missing}")
    
    # Test 6: Fragment unlock status
    print("\n6. Testing fragment unlock status:")
    status = unlock_engine.check_unlock_status(1, "intro_1")
    print(f"   Fragment: intro_1")
    print(f"   Status: {status}")
    
    print("\n✅ Unlock Engine tests completed!")


if __name__ == "__main__":
    test_unlock_engine()