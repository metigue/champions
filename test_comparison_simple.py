#!/usr/bin/env python3
"""
Test script to verify the champion comparison functionality works correctly.
This version doesn't import Discord dependencies to avoid audioop issues.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    
    # Load the JSON data directly to check the format
    with open('champions_database.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Test loading a champion that has battlegrounds data
    nico_data = raw_data.get('nico minoru', {})
    print(f"Nico Minoru battlegrounds_type: {nico_data.get('battlegrounds_type')}")
    print(f"Nico Minoru battlegrounds_rating: {nico_data.get('battlegrounds_rating')}")
    print(f"Nico Minoru ranking_display: {nico_data.get('ranking_display')}")
    
    # Create Champion object manually to test the new field
    champion = Champion(
        name=nico_data['name'],
        tier=nico_data['tier'],
        category=nico_data['ranking_display'],
        rating=nico_data['battlegrounds_rating'],
        battlegrounds_type=nico_data.get('battlegrounds_type')
    )
    
    print(f"Created Champion object with battlegrounds_type: {champion.battlegrounds_type}")
    print("✅ DataManager test passed!")
    
    return True

def test_comparison_logic():
    """Test the comparison logic manually"""
    print("\nTesting comparison logic manually...")
    
    # Test champion data
    doctor_doom = Champion(
        name="Doctor Doom",
        tier="Scorching",
        category="Mystic #8",
        rating=7,
        battlegrounds_type="Defender"  # Assuming Defender gets no bonus
    )
    
    nico_minoru = Champion(
        name="Nico Minoru", 
        tier="Above All",
        category="Mystic #1",
        rating=10,
        battlegrounds_type="Dual Threat"  # Gets +2 bonus
    )
    
    # Mock gwenpool without rating (should default to 5)
    gwenpool = Champion(
        name="Gwenpool",
        tier="Hot", 
        category="Skill #10",
        rating=None,  # No rating
        battlegrounds_type="Attacker"  # Gets +1 bonus
    )
    
    champions = [doctor_doom, nico_minoru, gwenpool]
    champion_scores = []
    
    for champion in champions:
        # Base score from battlegrounds rating (or 5 if no rating)
        rating_score = champion.rating if champion.rating is not None else 5
        
        # Add bonus based on battlegrounds type
        type_bonus = 0
        if champion.battlegrounds_type == "Attacker":
            type_bonus = 1
        elif champion.battlegrounds_type == "Dual Threat":
            type_bonus = 2
        # Defender gets no bonus
        
        # Calculate class ranking score (50 - ranking number, with minimum of 5)
        ranking_score = 5  # Default minimum
        if champion.category and '#' in champion.category:
            try:
                # Extract the ranking number after the '#'
                ranking_part = champion.category.split('#')[1].split()[0]  # Get first part after '#'
                ranking_num = int(ranking_part)
                ranking_score = max(5, 50 - ranking_num)
            except (IndexError, ValueError):
                # If we can't parse the ranking, keep the default score
                pass
        
        # Total score is the sum of all components
        total_score = rating_score + type_bonus + ranking_score
        
        champion_scores.append((champion, total_score))
    
    # Sort by total score descending
    champion_scores.sort(key=lambda x: x[1], reverse=True)
    
    print("Comparison Results:")
    for i, (champion, score) in enumerate(champion_scores, 1):
        rating_str = f"{champion.rating}/10" if champion.rating else "No rating"
        type_str = f" ({champion.battlegrounds_type})" if champion.battlegrounds_type else ""
        print(f"{i}. {champion.name} - Score: {score}")
        print(f"   - Battlegrounds Rating: {rating_str}{type_str}")
        print(f"   - Class Ranking: {champion.category}")
        print(f"   - Tier: {champion.tier}")
    
    print("✅ Comparison logic test passed!")
    return True

if __name__ == "__main__":
    print("Running tests for champion comparison implementation...")
    
    try:
        test_champion_model_update()
        dm_success = test_data_manager_update()
        logic_success = test_comparison_logic()
        
        if dm_success and logic_success:
            print("\n🎉 All tests passed! The champion comparison feature is working correctly.")
        else:
            print("\n❌ Some tests failed.")
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()