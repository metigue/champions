import json
import re
from typing import List, Dict
import logging
from champion_model import Champion
from difflib import get_close_matches, SequenceMatcher
import csv


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
            
            logging.info(f"Loaded {len(champions)} champions from JSON database")
            logging.info(f"Vega (BGs): {len(vega_champions)}, Illuminati (Ranking): {len(illuminati_champions)}")
            
            # Load additional champions from the list that aren't in the tier list
            self.load_additional_champions()
            
        except FileNotFoundError:
            logging.error(f"Database file {self.db_file} not found. Run build_database.py first.")
            self.champions_data = {'vega': [], 'illuminati': []}
        except Exception as e:
            logging.error(f"Error loading database: {e}")
            self.champions_data = {'vega': [], 'illuminati': []}

    def load_additional_champions(self):
        """Load additional champions from the list that aren't in the tier list"""
        try:
            champions_added = 0
            
            # Read the list of champions from the text file
            with open('/home/david/champions/list_of_champions.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # Skip header
                
                # Parse champion names from the TSV file
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Split by tabs
                    parts = line.split('\t')
                    
                    # Look for champion names - they're typically in columns with actual text
                    champion_name = None
                    for part in parts:
                        part = part.strip()
                        # Skip if it looks like a file path, date, or class
                        if (part and 
                            'File:' not in part and 
                            'Coming' not in part and
                            'January' not in part and 'February' not in part and 
                            'March' not in part and 'April' not in part and 
                            'May' not in part and 'June' not in part and 
                            'July' not in part and 'August' not in part and 
                            'September' not in part and 'October' not in part and 
                            'November' not in part and 'December' not in part and
                            'Cosmic' not in part and 'Tech' not in part and 
                            'Mutant' not in part and 'Skill' not in part and 
                            'Science' not in part and 'Mystic' not in part and
                            'Class' not in part and 'Release' not in part):
                            
                            # This might be a champion name
                            champion_name = part
                            break
                    
                    if champion_name and len(champion_name) > 2:  # Valid champion name
                        # Check if this champion already exists in our database
                        champion_key = champion_name.lower()
                        if champion_key in self.champion_lookup:
                            continue  # Already exists, skip
                        
                        # Create a placeholder champion with no battlegrounds rating
                        # These champions exist in the game but aren't on the tier list, 
                        # so they have no battlegrounds rating
                        placeholder_champion = Champion(
                            name=champion_name,
                            tier="Mild",  # Lowest official tier for champions not on tier list
                            category="Not good enough to be on the tier list",  # Indicates not good enough for ranking
                            rating=None,  # No battlegrounds rating
                            symbols=[],  # No special symbols
                            source="game",  # Source indicating these are from the game but not tiered
                            battlegrounds_type=None  # No battlegrounds type
                        )
                        
                        # Add to our data structures
                        self.champions_data['vega'].append(placeholder_champion)
                        self.champion_lookup[champion_key] = placeholder_champion
                        champions_added += 1
            
            logging.info(f"Loaded {champions_added} additional champions from game list")
            
        except FileNotFoundError:
            logging.warning("Additional champions list not found. Continuing with existing data.")
        except Exception as e:
            logging.error(f"Error loading additional champions: {e}")
    
    def fetch_champions_from_spreadsheets(self) -> Dict[str, List[Champion]]:
        """Fetch champion data (loads from JSON database instead)"""
        logging.info("Loading champions from JSON database...")
        return self.champions_data
    
    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive) - returns only the closest match"""
        name_lower = name.lower().strip()
        
        # Direct lookup first
        if name_lower in self.champion_lookup:
            return [self.champion_lookup[name_lower]]
        
        # Try fuzzy matching with close matches using multiple strategies
        all_names = list(self.champion_lookup.keys())
        
        # First try standard close matches
        close_matches = get_close_matches(name_lower, all_names, n=3, cutoff=0.3)
        
        # Special handling for cases where search term is at the beginning of a champion name
        # This handles cases like "nico" matching "nico minoru" even if similarity isn't highest
        prefix_matches = []
        for key in all_names:
            champion = self.champion_lookup[key]
            # Check if the search term is at the beginning of either the key or the champion name
            if (key.startswith(name_lower) or 
                champion.name.lower().startswith(name_lower)):
                prefix_matches.append((key, champion))
        
        # If we have prefix matches, prioritize those over standard close matches
        # But prioritize champions with higher ratings (tiered champions over placeholders)
        if prefix_matches:
            # Sort prefix matches by rating (descending) to prioritize tiered champions
            prefix_matches.sort(key=lambda x: (x[1].rating or 0), reverse=True)
            return [prefix_matches[0][1]]
        
        # If we have close matches, pick the best one based on similarity ratio
        if close_matches:
            best_match = None
            best_ratio = 0
            
            for match in close_matches:
                champion = self.champion_lookup[match]
                # Calculate similarity between search term and both the lookup key and actual name
                ratio1 = SequenceMatcher(None, name_lower, match).ratio()
                ratio2 = SequenceMatcher(None, name_lower, champion.name.lower()).ratio()
                # Use the higher of the two ratios
                max_ratio = max(ratio1, ratio2)
                
                if max_ratio > best_ratio:
                    best_ratio = max_ratio
                    best_match = champion
            
            if best_match:
                return [best_match]
        
        # If no close matches found via fuzzy search, calculate similarity for all entries
        best_match = None
        best_ratio = 0
        for key, champion in self.champion_lookup.items():
            # Calculate similarity between search term and both the lookup key and actual name
            ratio1 = SequenceMatcher(None, name_lower, key).ratio()
            ratio2 = SequenceMatcher(None, name_lower, champion.name.lower()).ratio()
            # Use the higher of the two ratios
            max_ratio = max(ratio1, ratio2)
            
            if max_ratio > best_ratio:
                best_ratio = max_ratio
                best_match = champion
        
        if best_match and best_ratio > 0.4:  # Only return if similarity is above threshold
            return [best_match]
        
        return []
    
    def get_top_champions_by_tier(self, source: str = 'vega', limit: int = 10) -> List[Champion]:
        """Get top champions by tier from a specific source"""
        if source not in self.champions_data:
            return []
        
        # Define tier rankings (higher is better)
        tier_order = {
            "Above All": 10,
            "Scorching": 9,
            "Super Hot": 8,
            "Hot": 7,
            "Mild": 6,
            "Information": 5
        }
        
        champions = self.champions_data[source]
        
        # Sort by tier order, with rating as secondary sort if available
        def sort_key(champ):
            tier_rank = tier_order.get(champ.tier, 0)
            return (tier_rank, champ.rating or 0)
        
        sorted_champions = sorted(champions, key=sort_key, reverse=True)
        
        return sorted_champions[:limit]
    
    def refresh_data(self):
        """Refresh data from JSON database"""
        logging.info("Refreshing data from JSON database...")
        self.load_champions_from_json()
        logging.info("Data refresh completed")