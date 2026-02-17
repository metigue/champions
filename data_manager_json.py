import json
import re
from typing import List, Dict
import logging
from champion_model import Champion


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
            
        except FileNotFoundError:
            logging.error(f"Database file {self.db_file} not found. Run build_database.py first.")
            self.champions_data = {'vega': [], 'illuminati': []}
        except Exception as e:
            logging.error(f"Error loading database: {e}")
            self.champions_data = {'vega': [], 'illuminati': []}
    
    def fetch_champions_from_spreadsheets(self) -> Dict[str, List[Champion]]:
        """Fetch champion data (loads from JSON database instead)"""
        logging.info("Loading champions from JSON database...")
        return self.champions_data
    
    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive)"""
        name_lower = name.lower().strip()
        
        # Direct lookup first
        if name_lower in self.champion_lookup:
            return [self.champion_lookup[name_lower]]
        
        # Fuzzy matching
        results = []
        for key, champion in self.champion_lookup.items():
            if name_lower in key or name_lower in champion.name.lower():
                results.append(champion)
        
        return results
    
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