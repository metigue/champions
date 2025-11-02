#!/usr/bin/env python3
"""
Test how Legend displays
"""

import sys
import os
sys.path.append('/home/david/champions')

from data_manager_json import DataManager

def test_legend_display():
    """Test how Legend displays"""
    print("Testing Legend display...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Look up Legend
    champions = data_manager.get_champion_by_name("legend")
    if champions:
        for champ in champions:
            print(f"Found: {champ.name}")
            print(f"  Rating: {champ.rating}")
            print(f"  Tier: {champ.tier}")
            print(f"  Category: {champ.category}")
            print(f"  Battlegrounds Type: {champ.battlegrounds_type}")

if __name__ == "__main__":
    test_legend_display()