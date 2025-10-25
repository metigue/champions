import requests
import csv
import io
import re
from typing import List, Dict
import logging
from champion_model import Champion

class DataManager:
    """Handles data retrieval and processing from public Google Sheets via web scraping"""
    
    def __init__(self):
        self.champions_data = {}
        
    def fetch_champions_from_spreadsheets(self) -> Dict[str, List[Champion]]:
        """Fetch and process champion data from both public spreadsheets"""
        
        # Spreadsheet URLs
        # Vega's BG sheet with numerical scores (dual threat, attack, defense numbers like 7, 9)
        vega_bgs_url = "https://docs.google.com/spreadsheets/d/1KzfdzI_HxK7zk_eTwmdwI5G84k9HSIYPzAMSPgGYjUE/export?format=csv&gid=0"
        
        # Illuminati's sheet with champions ranked in columns (Nico #1 mystic, Tigra #2 mystic, etc.)
        illuminati_ranking_url = "https://docs.google.com/spreadsheets/d/10OeQixQCrMKuw-pa3-LDUOQO70WGAFYROPu825Kr-eo/export?format=csv&gid=323504536"
        
        all_champions = {}
        
        # Process Vega's BGs spreadsheet (with numerical scores)
        try:
            vega_data = self._fetch_vega_sheet(vega_bgs_url)
            all_champions['vega'] = vega_data
            logging.info(f"Loaded {len(vega_data)} champions from Vega's BGs sheet")
        except Exception as e:
            logging.error(f"Error fetching Vega's BGs spreadsheet: {e}")
        
        # Process Illuminati's ranking spreadsheet (with column rankings)
        try:
            illuminati_data = self._fetch_illuminati_sheet(illuminati_ranking_url)
            all_champions['illuminati'] = illuminati_data
            logging.info(f"Loaded {len(illuminati_data)} champions from Illuminati's ranking sheet")
        except Exception as e:
            logging.error(f"Error fetching Illuminati's ranking spreadsheet: {e}")
        
        # Store combined champion data
        self.champions_data = all_champions
        return self.champions_data
    
    def _fetch_vega_sheet(self, url: str) -> List[Champion]:
        """Fetch data from the Vega BG sheet with numerical scores (dual threat, attack, defense)"""
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert the response content to a CSV reader
        csv_content = io.StringIO(response.text)
        csv_reader = csv.reader(csv_content)
        
        champions = []
        
        # Read all rows
        rows = list(csv_reader)
        
        # The structure is different than I initially thought
        # Row 0: Headers (Mystic, Science, etc.)
        # Row 1: "Dual Threat" 
        # Row 3: "Tier Above All" and then champion names with ratings "Nico Minoru - 10"
        # Row 4: More champions with ratings
        
        # Process each column (each class: Mystic, Science, etc.)
        for col_idx in range(1, len(rows[0])):  # Skip column 0 which is empty
            if col_idx >= len(rows[0]):
                continue
                
            category = rows[0][col_idx].strip() if col_idx < len(rows[0]) else f"Category_{col_idx}"
            if not category:
                continue
                
            # Process rows starting from row 3 where champions start
            for row_idx in range(3, len(rows)):
                if col_idx >= len(rows[row_idx]):
                    continue
                    
                cell_value = rows[row_idx][col_idx].strip()
                
                if not cell_value:
                    continue
                
                # Extract champion name and rating from format like "Nico Minoru - 10"
                # Find the part after the dash
                parts = cell_value.split('-', 1)
                if len(parts) >= 2:
                    name_part = parts[0].strip()
                    rating_part_str = parts[1].strip()
                    
                    # Extract rating: if starts with '1' followed by digit, it's 10, otherwise first digit
                    if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
                        rating_part = 10
                    elif rating_part_str and rating_part_str[0].isdigit():
                        rating_part = int(rating_part_str[0])
                    else:
                        continue  # Skip if no valid rating found
                    
                    # Extract symbols from the original cell value
                    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                    symbols = emoji_pattern.findall(cell_value)
                    
                    # Extract the tier from the row above (row 1 for Dual Threat, etc.)
                    tier = "Unknown"
                    if row_idx >= 1 and len(rows[1]) > col_idx:
                        tier = rows[1][col_idx].strip() or "Information"
                    
                    # If tier is empty, try to get from row 3 which has "Tier Above All"
                    if tier == "Unknown" or tier == "":
                        # Find the tier by checking the row headers
                        for check_row in range(min(3, len(rows))):
                            if check_row < len(rows) and col_idx < len(rows[check_row]):
                                cell = rows[check_row][col_idx].strip()
                                if cell and ("Above All" in cell or "Scorching" in cell or "Super Hot" in cell or 
                                           "Hot" in cell or "Mild" in cell or "Information" in cell):
                                    tier = cell.replace("Tier ", "").strip()
                                    break
                    
                    # Final fallback to get tier from row index context
                    if tier == "Unknown" or tier == "":
                        # Default to Information tier if we can't identify the specific tier
                        tier = "Information"
                    
                    champion = Champion(
                        name=name_part,
                        tier=tier,
                        category=category,
                        rating=rating_part,
                        symbols=list(set(symbols)),
                        source="vega"
                    )
                    champions.append(champion)
                else:
                    # If the format isn't "name - rating", try to extract rating differently
                    # Look for a number after the champion name
                    import re
                    # Pattern like "Name - 10" or "Name - 9 emoji"
                    # Find the part after the dash
                    parts = cell_value.split('-', 1)
                    if len(parts) >= 2:
                        name_part = parts[0].strip()
                        rating_part_str = parts[1].strip()
                        
                        # Extract rating: if starts with '1' followed by digit, it's 10, otherwise first digit
                        if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
                            rating_part = 10
                        elif rating_part_str and rating_part_str[0].isdigit():
                            rating_part = int(rating_part_str[0])
                        else:
                            continue  # Skip if no valid rating found
                        
                        # Extract symbols from the remaining part
                        remaining = alt_match.group(3)
                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(remaining)
                        
                        # Get tier from context
                        tier = "Information"  # Default fallback
                        
                        champion = Champion(
                            name=name_part,
                            tier=tier,
                            category=category,
                            rating=rating_part,
                            symbols=list(set(symbols)),
                            source="vega"
                        )
                        champions.append(champion)
        
        return champions

    def _get_tier_from_rating(self, rating):
        """Convert numerical rating to tier based on value"""
        if rating is None:
            return "Information"
        elif rating >= 9:
            return "Above All"
        elif rating >= 8:
            return "Scorching"
        elif rating >= 7:
            return "Super Hot"
        elif rating >= 6:
            return "Hot"
        elif rating >= 5:
            return "Mild"
        else:
            return "Information"

    def _get_vega_tier_by_position(self, position: int) -> str:
        """Convert position in category to Vega's tier system"""
        # Tier order from highest to lowest (Mild is the lowest tier, not Information)
        tier_order = ["Above All", "Scorching", "Super Hot", "Hot", "Mild"]
        
        if 0 <= position < len(tier_order):
            return tier_order[position]
        else:
            return "Information"  # Default for positions beyond the known tiers
    
    def _fetch_illuminati_sheet(self, url: str) -> List[Champion]:
        """Fetch data from the sheet with champions ranked in columns by tier (Illuminati-style)"""
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert the response content to a CSV reader
        csv_content = io.StringIO(response.text)
        csv_reader = csv.reader(csv_content)
        
        champions = []
        
        # Read all rows
        rows = list(csv_reader)
        
        if not rows or len(rows) < 2:
            return []
        
        # Find all class names in column A
        class_starts = []  # List of (row_index, class_name)
        
        for row_idx in range(len(rows)):
            if row_idx < len(rows) and len(rows[row_idx]) > 0:
                cell_a = rows[row_idx][0] if len(rows[row_idx]) > 0 else ""
                class_name = cell_a.strip().title() if cell_a.strip() else ""
                
                # Look for class names exactly as we know them from the debug output
                if class_name.lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic', 'guardian']:
                    class_starts.append((row_idx, class_name))
        
        # Process each class and its champion range
        for i, (start_row, class_name) in enumerate(class_starts):
            # Determine the end of this class range
            if i + 1 < len(class_starts):
                end_row = class_starts[i + 1][0]  # Start of next class
            else:
                end_row = len(rows)  # End of all data
            
            # For this class, assign rankings by going column by column, row by row in the class range
            rank_counter = 1  # Start ranking at 1 for each class
            
            # Process each column from B onward
            for col_idx in range(1, len(rows[0]) if len(rows) > 0 else 0):
                # Process each row in the class range for this column
                for row_idx in range(start_row, end_row):
                    try:
                        if col_idx >= len(rows[row_idx]):  # Column doesn't exist for this row
                            continue
                        
                        cell_value = rows[row_idx][col_idx].strip()
                        
                        # Skip empty cells
                        if not cell_value:
                            continue
                        
                        # Skip rows that appear to be headers or metadata
                        cell_lower = cell_value.lower()
                        if any(skip_text in cell_lower for skip_text in [
                            'champion', 'champions', 'name', 'tier', 'rating', 'category',
                            'above all', 'scorching', 'super hot', 'hot', 'mild', 'information',
                            'the truly o.p.', 'tier above all', 'omega days', 'glorious guardians',
                            'exclusive', 'go to file', 'to use tier list', 'filtering'
                        ]):
                            continue
                        
                        # Extract emoji symbols from the name
                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(cell_value)
                        
                        # Clean the champion name (remove emojis)
                        clean_name = emoji_pattern.sub('', cell_value).strip()
                        
                        if clean_name and len(clean_name) > 1:  # Valid champion name
                            actual_category = f"{class_name} #{rank_counter}"
                            
                            # Determine tier based on the rank
                            tier = self._get_vega_tier_by_position(rank_counter - 1)
                            
                            champion = Champion(
                                name=clean_name,
                                tier=tier,
                                category=actual_category,
                                symbols=list(set(symbols)),  # Remove duplicates
                                source="illuminati"
                            )
                            champions.append(champion)
                            
                            # Increment rank for next champion in this class
                            rank_counter += 1
                            
                    except (IndexError, TypeError):
                        continue  # Skip if cell doesn't exist
        
        return champions
    
    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive)"""
        results = []
        name_lower = name.lower().strip()
        
        for source, champions in self.champions_data.items():
            for champion in champions:
                if name_lower in champion.name.lower():
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
        """Refresh data from public Google Sheets"""
        logging.info("Refreshing data from public Google Sheets...")
        self.fetch_champions_from_spreadsheets()
        logging.info("Data refresh completed")