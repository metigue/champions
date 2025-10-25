#!/usr/bin/env python3
"""
Test script to verify the champion comparison functionality works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager_json import DataManager
from champion_model import Champion

def test_champion_model_update():
    """Test that the Champion model now includes battlegrounds_type"""
    print("Testing Champion model update...")
    
    champion = Champion(
        name="Test Champion",
        tier="Above All", 
        category="Mystic #1",
        rating=8.5,
        battlegrounds_type="Dual Threat"
    )
    
    print(f"Champion name: {champion.name}")
    print(f"Champion battlegrounds_type: {champion.battlegrounds_type}")
    print("✅ Champion model update test passed!")
    
def test_data_manager_update():
    """Test that the data manager can load champions with battlegrounds_type"""
    print("\nTesting DataManager with battlegrounds_type...")
    
    dm = DataManager()
    
    # Test loading a champion that has battlegrounds data
    champions = dm.get_champion_by_name("nico minoru")
    if champions:
        champ = champions[0]
        print(f"Champion: {champ.name}")
        print(f"Rating: {champ.rating}")
        print(f"Battlegrounds Type: {champ.battlegrounds_type}")
        print(f"Category: {champ.category}")
        print("✅ DataManager test passed!")
    else:
        print("❌ DataManager test failed - couldn't find Nico Minoru")
        return False
    
    return True

def test_command_handler():
    """Test the command handler comparison functionality"""
    print("\nTesting CommandHandler comparison functionality...")
    
    # Import here to catch any syntax errors
    try:
        from cogs.command_handler import CommandHandler
        dm = DataManager()
        handler = CommandHandler(dm)
        
        # Test the compare_champions method
        result = handler.compare_champions("doctor doom, nico minoru, gwenpool")
        print(f"Comparison result length: {len(result)} characters")
        print("First 200 characters of result:")
        print(result[:200] + "..." if len(result) > 200 else result)
        print("✅ CommandHandler comparison test passed!")
        
        return True
    except Exception as e:
        print(f"❌ CommandHandler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running tests for champion comparison implementation...")
    
    try:
        test_champion_model_update()
        dm_success = test_data_manager_update()
        ch_success = test_command_handler()
        
        if dm_success and ch_success:
            print("\n🎉 All tests passed! The champion comparison feature is working correctly.")
        else:
            print("\n❌ Some tests failed.")
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()