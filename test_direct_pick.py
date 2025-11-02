#!/usr/bin/env python3
"""
Direct test of the pick champions functionality without Discord imports
"""

import sys
import os
sys.path.append('/home/david/champions')

from data_manager_json import DataManager
from difflib import get_close_matches, SequenceMatcher

class SimpleCommandHandler:
    """Simplified command handler for testing"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    print("Testing pick champions functionality...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Initialize command handler
    command_handler = SimpleCommandHandler(data_manager)
    
    # Test cases
    test_cases = [
        # Test case 1: Your example
        {
            "count": 2,
            "champions": "nico, karolina, arnim zola, red skull, thor",
            "description": "!pick 2 nico, karolina, arnim zola, red skull, thor"
        },
        # Test case 2: 5 random champions
        {
            "count": 5,
            "champions": "spider-man, wolverine, hulk, thor, captain america",
            "description": "!pick 5 spider-man, wolverine, hulk, thor, captain america"
        },
        # Test case 3: Champions with specific ratings
        {
            "count": 3,
            "champions": "nico minoru, mr negative, spider-man supreme",
            "description": "!pick 3 nico minoru, mr negative, spider-man supreme"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i}: {test_case['description']} ===")
        try:
            result = command_handler.pick_champions_for_battlegrounds(
                test_case['count'], 
                test_case['champions']
            )
            print(result)
        except Exception as e:
            print(f"Error in test case {i}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_pick_functionality()