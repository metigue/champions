#!/usr/bin/env python3
"""
Test script for the !pick command
"""

import sys
import os
import json

# Add the project directory to the path
sys.path.append('/home/david/champions')

from data_manager_json import DataManager
from cogs.command_handler import CommandHandler, MCOCCommands

def test_pick_functionality():
    """Test the pick champions functionality directly"""
    print("Testing pick champions functionality...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Initialize command handler
    command_handler = CommandHandler(data_manager)
    
    # Test the pick function directly
    test_champions = "nico, karolina, arnim zola, red skull, thor"
    print(f"\n=== Testing pick function with: {test_champions} ===")
    try:
        result = command_handler.pick_champions_for_battlegrounds(2, test_champions)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pick_functionality()