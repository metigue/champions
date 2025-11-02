#!/usr/bin/env python3
import json
import re
from difflib import get_close_matches
from typing import List

class Champion:
    def __init__(self, name, tier, category, rating, symbols, source, battlegrounds_type=None):
        self.name = name
        self.tier = tier
        self.category = category
        self.rating = rating
        self.symbols = symbols
        self.source = source
        self.battlegrounds_type = battlegrounds_type

class DataManager:
    """Handles data retrieval and processing from JSON database"""
    
    def __init__(self, db_file="champions_database.json"):
        self.champions_data = {}
        self.db_file = db_file
        self.champion_lookup = {}
        self.load_champions_from_json()
        
    def load_champions_from_json(self):
        """Load champion data from the JSON database"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Convert the raw data to Champion objects
            champions = []
            for name_key, champion_data in raw_data.items():
                # Determine source based on whether it has battlegrounds data
                if champion_data.get('battlegrounds_rating') is not None:
                    source = "vega"  # Has battlegrounds data
                else:
                    source = "illuminati"  # Doesn't have battlegrounds data, likely from ranking sheet
                
                # Build symbol list based on the boolean flags in the JSON
                symbols = []
                if champion_data.get('ranking_depends_on_awakening', False):
                    symbols.append('🌟')
                if champion_data.get('ranking_depends_on_signature', False):
                    symbols.append('🚀')
                if champion_data.get('top_candidate_for_ascension', False):
                    symbols.append('💎')
                if champion_data.get('difficult_as_7star', False):
                    symbols.append('🌹')
                if champion_data.get('specific_relic_needed', False):
                    symbols.append('💾')
                if champion_data.get('early_prediction', False):
                    symbols.append('🎲')
                # Add any other symbols from the 'other_symbols' list
                symbols.extend(champion_data.get('other_symbols', []))
                
                champion = Champion(
                    name=champion_data['name'],
                    tier=champion_data['tier'],
                    category=champion_data['ranking_display'],  # This includes the ranking like "Mystic #1"
                    rating=champion_data['battlegrounds_rating'],
                    symbols=symbols,
                    source=source,
                    battlegrounds_type=champion_data.get('battlegrounds_type')
                )
                
                champions.append(champion)
                # Add to lookup for fast searching
                self.champion_lookup[name_key.lower()] = champion
            
            # Group champions by source
            vega_champions = [c for c in champions if c.source == "vega"]
            illuminati_champions = [c for c in champions if c.source == "illuminati"]
            
            self.champions_data = {
                'vega': vega_champions,
                'illuminati': illuminati_champions
            }
            
            print(f"Loaded {len(champions)} champions from JSON database")
            print(f"Vega (BGs): {len(vega_champions)}, Illuminati (Ranking): {len(illuminati_champions)}")
            
        except FileNotFoundError:
            print(f"Database file {self.db_file} not found. Run build_database.py first.")
            self.champions_data = {'vega': [], 'illuminati': []}
        except Exception as e:
            print(f"Error loading database: {e}")
            self.champions_data = {'vega': [], 'illuminati': []}
    
    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive) - returns only the closest match"""
        name_lower = name.lower().strip()
        
        # Direct lookup first
        if name_lower in self.champion_lookup:
            return [self.champion_lookup[name_lower]]
        
        # Try fuzzy matching with close matches
        all_names = list(self.champion_lookup.keys())
        close_matches = get_close_matches(name_lower, all_names, n=1, cutoff=0.3)  # Only return closest match
        
        # If we have a close match, return that
        if close_matches:
            return [self.champion_lookup[close_matches[0]]]
        
        # If no close matches found via fuzzy search, try substring matching as fallback
        # But only return the best match based on length and position
        best_match = None
        best_score = -1
        for key, champion in self.champion_lookup.items():
            if name_lower in key or name_lower in champion.name.lower():
                # Score based on how much of the name matches (higher is better similarity)
                score = len(name_lower) / len(key) if key else 0
                if name_lower in champion.name.lower():
                    # Prefer matches in the actual champion name over key
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_match = champion
        
        if best_match:
            return [best_match]
        
        return []

class CommandHandler:
    """Handles all bot commands and their logic"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        # Only use the first (closest) match
        champion = champions[0]
        
        response = f"**{champion.name}**\n"
        response += f"Tier: **{champion.tier}**\n"
        
        # Format category to show ranking if it's in the format "Class #N"  
        if champion.category and '#' in champion.category:
            response += f"Ranking: {champion.category}\n"
        else:
            response += f"Category: {champion.category}\n"
        
        # Show Battlegrounds scores from the vega source
        if champion.source == "vega" and champion.rating:
            battlegrounds_type = champion.battlegrounds_type or "Attacker"
            response += f"Battlegrounds: {battlegrounds_type} {champion.rating}/10\n"
        
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
            
            response += f"Special Notes: {', '.join(translated_notes)}\n"
        else:
            response += "Special Notes: None\n"
        
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
        response += f"Rank-up Priority: {advice}"
        
        return response

def test_rankup_command():
    # Initialize data manager
    data_manager = DataManager()
    
    # Initialize command handler
    command_handler = CommandHandler(data_manager)
    
    # Test the rankup command with "mr negative"
    print("Testing: mr negative")
    result = command_handler.get_champion_rankup_info("mr negative")
    print(result)
    
    print("\nTesting: werewolf")
    result = command_handler.get_champion_rankup_info("werewolf")
    print(result)
    
    print("\nTesting: werewolf by night")
    result = command_handler.get_champion_rankup_info("werewolf by night")
    print(result)
    
    print("\nTesting: scarlet witch sigil")
    result = command_handler.get_champion_rankup_info("scarlet witch sigil")
    print(result)
    
    print("\nTesting: sigil witch")
    result = command_handler.get_champion_rankup_info("sigil witch")
    print(result)
    
    print("\nTesting: spider-man supreme")
    result = command_handler.get_champion_rankup_info("spider-man supreme")
    print(result)
    
    print("\nTesting: spidey supreme")
    result = command_handler.get_champion_rankup_info("spidey supreme")
    print(result)

if __name__ == "__main__":
    test_rankup_command()