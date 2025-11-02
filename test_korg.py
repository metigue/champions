#!/usr/bin/env python3
import re

def test_korg_parsing():
    # Test the parsing logic from build_database.py
    test_cell = "Korg - 7"
    
    # Extract champion name and rating from format like "Nico Minoru - 10"
    # Find the part after the dash
    parts = test_cell.split('-', 1)
    if len(parts) >= 2:
        name_part = parts[0].strip()
        rating_part_str = parts[1].strip()
        
        print(f"Cell value: {test_cell}")
        print(f"Name part: {name_part}")
        print(f"Rating part string: {rating_part_str}")
        
        # Extract rating: if starts with '1' followed by digit, it's 10, otherwise first digit
        if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
            rating_part = 10
        elif rating_part_str and rating_part_str[0].isdigit():
            rating_part = int(rating_part_str[0])
        else:
            print("No valid rating found")
            return
        
        print(f"Rating part: {rating_part}")
        
        # Extract symbols from the original cell value
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
        symbols = emoji_pattern.findall(test_cell)
        
        print(f"Found symbols: {symbols}")
        
        # Determine battleground type based on row position (assuming row 102)
        row_idx = 102
        bg_type = "Dual Threat"  # Default for early rows
        
        # Determine the battlegrounds type based on row position ONLY
        if 31 <= row_idx <= 90:
            # This is in the Attackers section
            bg_type = "Attacker"
        elif 91 <= row_idx:
            # This is in the Defenders section
            bg_type = "Defender"
        # Rows 3-30 default to Dual Threat
        
        print(f"Battleground type: {bg_type}")
        
        print(f"\nResult: {name_part.lower()} -> rating: {rating_part}, type: {bg_type}, symbols: {symbols}")
        
        # This should be added to the battlegrounds_data dictionary
        battlegrounds_data = {}
        battlegrounds_data[name_part.lower()] = {
            "rating": rating_part,
            "type": bg_type,
            "symbols": symbols
        }
        
        print(f"Added to battlegrounds_data: {battlegrounds_data}")

if __name__ == "__main__":
    test_korg_parsing()