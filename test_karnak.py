#!/usr/bin/env python3
"""
Test how Karnak displays
"""

import sys
import os
sys.path.append('/home/david/champions')

from data_manager_json import DataManager

def test_karnak_display():
    """Test how Karnak displays"""
    print("Testing Karnak display...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Look up Karnak
    champions = data_manager.get_champion_by_name("karnak")
    if champions:
        for champ in champions:
            print(f"Found: {champ.name}")
            print(f"  Rating: {champ.rating}")
            print(f"  Tier: {champ.tier}")
            print(f"  Category: {champ.category}")
            print(f"  Battlegrounds Type: {champ.battlegrounds_type}")
            print(f"  Source: {champ.source}")

if __name__ == "__main__":
    test_karnak_display()