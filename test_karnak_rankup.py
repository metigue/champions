#!/usr/bin/env python3
"""
Test how Karnak displays in the rankup command
"""

import sys
import os
sys.path.append('/home/david/champions')

from data_manager_json import DataManager

def test_karnak_rankup():
    """Test how Karnak displays in the rankup command"""
    print("Testing Karnak rankup display...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Look up Karnak
    champions = data_manager.get_champion_by_name("karnak")
    if champions:
        champion = champions[0]
        print(f"Found: {champion.name}")
        print(f"  Rating: {champion.rating}")
        print(f"  Tier: {champion.tier}")
        print(f"  Category: {champion.category}")
        print(f"  Battlegrounds Type: {champion.battlegrounds_type}")
        print(f"  Symbols: {champion.symbols}")
        
        # Mimic the rankup command format
        print("\n=== Rankup Command Format ===")
        info = f"**{champion.name}**\n"
        info += f"Tier: **{champion.tier}**\n"
        
        # Format category to show ranking if it's in the format "Class #N"  
        if champion.category and '#' in champion.category:
            info += f"Ranking: {champion.category}\n"
        else:
            info += f"Category: {champion.category}\n"
        
        # Show Battlegrounds scores from the vega source
        if champion.source == "vega" and champion.rating:
            battlegrounds_type = champion.battlegrounds_type or "Attacker"
            info += f"Battlegrounds: {battlegrounds_type} {champion.rating}/10\n"
        
        # Translate emoji symbols to their meanings
        if champion.symbols:
            symbols_meanings = {
                '🌟': 'Ranking depends on Awakening',
                '🚀': 'Ranking depends on high signature ability',
                '💎': 'Top candidate for Ascension',
                '🌹': 'Impossible/difficult to get as a 7 star',
                '💾': 'Specific Relic needed',
                '🎲': 'Early predictions/uncertain rankings',
                '👾': 'Saga Champion: Fantastic Force',
                '🥂': 'Big Caution, Ranking May Change A Lot',
                '⛰️': 'Great in Everest Content',
                '⚔️': 'Defense potential uses',
                '🤺': 'Offense potential uses',
                '💣': 'Effective in Recoil Metas',
                '🐣': 'Newness enhancing effectiveness',
                '7️⃣': '7 Star enhancing effectiveness',
                '6️⃣': '6 Star Lock Hurting Performance',
                '💬': 'Skilled use required',
                '🎙️': 'Referenced in videos',
                '🛡️': 'Defense potential',
                '🎯': 'Offense potential',
                '🔥': 'Hot pick'
            }
            
            translated_notes = []
            for symbol in champion.symbols:
                if symbol in symbols_meanings:
                    translated_notes.append(symbols_meanings[symbol])
                else:
                    # If symbol not in our known meanings, just show it
                    translated_notes.append(symbol)
            
            info += f"Special Notes: {', '.join(translated_notes)}\n"
        else:
            info += "Special Notes: None\n"
        
        # Provide rank-up advice based on tier/rating
        tier_order = {
            "Above All": "TOP TIER - Definitely prioritize rank-up!",
            "Scorching": "HIGH TIER - Strong recommendation for rank-up",
            "Super Hot": "HIGH TIER - Good for rank-up when possible",
            "Hot": "MEDIUM TIER - Consider for rank-up",
            "Mild": "LOWER TIER - Lower priority for rank-up",
            "Information": "LOW TIER - Lowest priority for rank-up"
        }
        
        advice = tier_order.get(champion.tier, "Assess based on your team composition")
        info += f"Rank-up Priority: {advice}"
        
        print(info)

if __name__ == "__main__":
    test_karnak_rankup()