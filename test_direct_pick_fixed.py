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
    
    def pick_champions_for_battlegrounds(self, count: int, champion_names: str) -> str:
        """Pick the best N champions for battlegrounds - streamlined for quick decisions"""
        # Split the champion names by commas
        names = [name.strip() for name in champion_names.split(',')]
        
        champions = []
        
        # Find each champion using the same fuzzy matching as the real implementation
        for name in names:
            found_champs = self.data_manager.get_champion_by_name(name)
            if found_champs:
                # If multiple matches are found, use the first one
                champions.append(found_champs[0])
            # Note: We intentionally skip champions not found rather than creating defaults
        
        # Calculate battlegrounds-focused scores for each champion
        champion_scores = []
        for champion in champions:
            # Focus on battlegrounds rating as the primary factor
            if champion.rating is not None:
                # Champions with battlegrounds ratings get priority
                bg_score = champion.rating
                
                # Boost Dual Threat champions by 1 point as requested
                if champion.battlegrounds_type == "Dual Threat":
                    bg_score += 1
                
                # Add a small bonus based on ranking for tie-breaking
                ranking_bonus = 0
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        # Higher ranked champions get a small bonus (1st gets more than 10th, etc.)
                        ranking_bonus = max(0, (50 - ranking_num) / 10)  # Scale down the bonus
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, no bonus
                        ranking_bonus = 0
                
                # Total score prioritizes battlegrounds rating first, then ranking
                total_score = bg_score + ranking_bonus
                champion_scores.append((champion, total_score, True))  # True = has BG rating
            else:
                # Champions without battlegrounds ratings get a very low base score
                # For these, we'll use ranking as the primary factor with a penalty
                ranking_score = 0
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        # Higher ranked champions get higher scores (1st = 50, 10th = 40, etc.)
                        ranking_score = max(1, 50 - ranking_num)
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, give a minimal score
                        ranking_score = 1
                
                # Apply a significant penalty for not having a battlegrounds rating
                total_score = ranking_score / 10  # Much lower than champions with ratings
                champion_scores.append((champion, total_score, False))  # False = no BG rating
        
        # Sort by total score descending, but prioritize champions with battlegrounds ratings
        # Primary sort: has battlegrounds rating (True > False)
        # Secondary sort: total score descending
        champion_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)
        
        # Select the top N champions
        selected_champions = champion_scores[:count] if count > 0 else champion_scores
        
        # Format the results - streamlined for battlegrounds context
        if not selected_champions:
            return "No champions found to pick from."
        
        response = f"**Top {count} Battlegrounds Picks:**\n"
        
        for i, (champion, score, has_bg_rating) in enumerate(selected_champions, 1):
            # Show champion name and battlegrounds rating/type
            if champion.rating is not None:
                response += f"{i}. **{champion.name}** - {champion.rating}/10 {champion.battlegrounds_type or 'Attacker'}\n"
            else:
                response += f"{i}. **{champion.name}** - Not recommended for BGs\n"
        
        return response

def test_pick_functionality():
    """Test the pick champions functionality directly"""
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