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
    
    def _normalize_name(self, name: str) -> str:
        """Normalize champion name for comparison"""
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def _levenshtein_distance(self, s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1,        # Deletion
                               dp[i][j - 1] + 1,        # Insertion
                               dp[i - 1][j - 1] + cost) # Substitution
        return dp[m][n]

    def _jaro_winkler_similarity(self, s1, s2, p=0.1):
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        len1 = len(s1)
        len2 = len(s2)

        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0

        s1_matches = [False] * len1
        s2_matches = [False] * len2

        matches = 0
        transpositions = 0
        
        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(len2, i + match_distance + 1)
            for j in range(start, end):
                if not s2_matches[j] and s1[i] == s2[j]:
                    s1_matches[i] = True
                    s2_matches[j] = True
                    matches += 1
                    break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len1):
            if s1_matches[i]:
                while not s2_matches[k]:
                    k += 1
                if s1[i] != s2[k]:
                    transpositions += 1
                k += 1
        
        transpositions //= 2

        jaro_similarity = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0

        prefix = 0
        for i in range(min(len1, len2, 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break
        
        return jaro_similarity + (prefix * p * (1 - jaro_similarity))

    def _ngram_similarity(self, s1, s2, n=2):
        def get_ngrams(s, n):
            return set(s[i:i+n] for i in range(len(s)-n+1))

        ngrams1 = get_ngrams(s1, n)
        ngrams2 = get_ngrams(s2, n)

        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0

        return len(ngrams1.intersection(ngrams2)) / len(ngrams1.union(ngrams2))

    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive) - returns only the closest match"""
        name_lower = self._normalize_name(name)

        # Special case for "Doom"
        if name_lower == "doom":
            return [self.champion_lookup["doctor doom"]]

        # Direct lookup first
        if name_lower in self.champion_lookup:
            return [self.champion_lookup[name_lower]]

        # Try fuzzy matching with close matches using multiple strategies
        best_match = None
        best_score = -1

        for key, champion in self.champion_lookup.items():
            normalized_key = self._normalize_name(key)

            # Calculate similarity scores
            lev_distance = self._levenshtein_distance(name_lower, normalized_key)
            lev_similarity = 1 - (lev_distance / max(len(name_lower), len(normalized_key)))
            jaro_winkler_score = self._jaro_winkler_similarity(name_lower, normalized_key)
            ngram_score = self._ngram_similarity(name_lower, normalized_key)

            # Weighted average
            score = (0.4 * jaro_winkler_score) + (0.4 * lev_similarity) + (0.2 * ngram_score)

            # Boost score for prefix matches
            if normalized_key.startswith(name_lower):
                score += 0.1

            if score > best_score:
                best_score = score
                best_match = champion

        if best_match and best_score > 0.6:
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