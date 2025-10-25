#!/usr/bin/env python3
"""
Test script to demonstrate the MCOC Champions Discord Bot data processing
"""
import requests
import csv
import io
import re
from typing import List

# Import the Champion class from our model
from champion_model import Champion


class SimpleDataManager:
    """Simplified version of DataManager for demonstration"""
    
    def get_vega_tier_by_position(self, position: int) -> str:
        """Convert position in category to Vega's tier system"""
        tier_order = ["Above All", "Scorching", "Super Hot", "Hot", "Mild"]
        
        if 0 <= position < len(tier_order):
            return tier_order[position]
        else:
            return "Information"  # Default for lower-ranked champions

    def _fetch_illuminati_sheet(self, url: str) -> List[Champion]:
        """Fetch data from MCoC Illuminati Tier List spreadsheet using CSV export"""
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert the response content to a CSV reader
        csv_content = io.StringIO(response.text)
        csv_reader = csv.reader(csv_content)
        
        champions = []
        
        # This is actually the Vega BGs sheet with numbers like 7, 9 for dual-threat, attack, defense
        # Column A: Champion name
        # Other columns: Various scores/ratings for different modes
        
        rows = list(csv_reader)
        
        for row_idx, row in enumerate(rows):
            # Skip the header row if it looks like a header
            if row_idx == 0 and row and row[0].lower() in ['champion', 'champions', 'name', 'dual threat', 'attack', 'defense']:
                continue
                
            try:
                # Get the champion name from column A (index 0)
                if len(row) > 0 and row[0].strip() and row[0].strip().lower() not in ['champion', 'champions', 'name', 'nan', '']:
                    name = row[0].strip()
                else:
                    continue
                
                # This sheet doesn't have explicit tiers, so we'll determine based on position
                # or if there are numerical values in other columns, we can use them as indicators
                # For now, default to Information tier
                tier = "Information"
                
                # Since this is the BGs sheet with different categories (dual threat, attack, defense)
                category = "Battlegrounds"
                
                # Extract any numerical scores (these might be in different columns)
                rating = None
                # Look for numerical values in other columns
                for i in range(1, len(row)):
                    if row[i].strip():
                        try:
                            score = float(row[i].strip())
                            if rating is None or score > rating:
                                rating = score  # Use the highest score found
                        except ValueError:
                            pass  # Not a numeric value
                
                # Extract symbols from the name and other columns
                symbols = []
                # Check all columns for emojis
                for i in range(len(row)):
                    if row[i].strip():
                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        found_emojis = emoji_pattern.findall(row[i])
                        symbols.extend(found_emojis)
                
                champion = Champion(
                    name=name,
                    tier=tier,
                    category=category,
                    rating=rating,
                    symbols=list(set(symbols)),  # Remove duplicates
                    source="vega"  # This is actually the vega sheet despite the function name
                )
                champions.append(champion)
            except Exception as e:
                continue  # Skip problematic rows
        
        return champions

    def _fetch_vega_sheet(self, url: str) -> List[Champion]:
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
                            tier = self.get_vega_tier_by_position(rank_counter - 1)
                            
                            champion = Champion(
                                name=clean_name,
                                tier=tier,
                                category=actual_category,
                                symbols=list(set(symbols)),  # Remove duplicates
                                source="illuminati"  # This is actually the illuminati-style ranking sheet
                            )
                            champions.append(champion)
                            
                            # Increment rank for next champion in this class
                            rank_counter += 1
                            
                    except (IndexError, TypeError):
                        continue  # Skip if cell doesn't exist
        
        return champions

    def get_champion_by_name(self, name: str, all_champions: List[Champion]) -> List[Champion]:
        """Get champion information by name (case-insensitive)"""
        results = []
        name_lower = name.lower().strip()
        
        for champion in all_champions:
            if name_lower in champion.name.lower():
                results.append(champion)
        
        return results


def main():
    print("MCOC Champions Discord Bot - Data Processing Demo")
    print("="*50)
    
    # Initialize data manager
    dm = SimpleDataManager()
    
    # URLs for the spreadsheets
    # Actually, the first one is the BGs sheet with numbers (Vega's)
    vega_bgs_url = "https://docs.google.com/spreadsheets/d/1KzfdzI_HxK7zk_eTwmdwI5G84k9HSIYPzAMSPgGYjUE/export?format=csv&gid=0"
    # The second one is the ranking sheet (Illuminati's)
    illuminati_ranking_url = "https://docs.google.com/spreadsheets/d/10OeQixQCrMKuw-pa3-LDUOQO70WGAFYROPu825Kr-eo/export?format=csv&gid=323504536"
    
    print("Fetching data from Vega's BGs sheet (with numbers)...")
    try:
        vega_champions = dm._fetch_illuminati_sheet(vega_bgs_url)  # This function now handles the numbers sheet
        print(f"Loaded {len(vega_champions)} champions from Vega's BGs sheet")
    except Exception as e:
        print(f"Error fetching Vega's BGs sheet: {e}")
        vega_champions = []
    
    print("Fetching data from Illuminati's ranking sheet (column ranking)...")
    try:
        illuminati_champions = dm._fetch_vega_sheet(illuminati_ranking_url)  # This function handles the ranking sheet
        print(f"Loaded {len(illuminati_champions)} champions from Illuminati's ranking sheet")
    except Exception as e:
        print(f"Error fetching Illuminati's ranking sheet: {e}")
        illuminati_champions = []
    
    # Combine all champions
    all_champions = vega_champions + illuminati_champions
    
    print(f"\nTotal champions loaded: {len(all_champions)}")
    
    # Demonstrate champion lookup for Baron Zemo, Venom, Katrina Dean, and Anti-Venom specifically
    test_champions = ["baron zemo", "venom", "katrina dean", "antivenom", "nico minoru", "tigra"]
    
    for test_name in test_champions:
        print(f"\nSearching for: {test_name}")
        matches = dm.get_champion_by_name(test_name, all_champions)
        
        if matches:
            for champion in matches:
                rating_str = f"Rating: {champion.rating}/10 | " if champion.rating else ""
                symbols_str = f" Symbols: {' '.join(champion.symbols)}" if champion.symbols else ""
                
                print(f"  - {champion.name}")
                print(f"    Source: {champion.source} | {rating_str}Tier: {champion.tier} | Category: {champion.category}{symbols_str}")
                
                # Show rank-up priority based on tier
                tier_order = {
                    "Above All": "TOP TIER - Definitely prioritize rank-up!",
                    "Scorching": "HIGH TIER - Strong recommendation for rank-up",
                    "Super Hot": "HIGH TIER - Good for rank-up when possible", 
                    "Hot": "MEDIUM TIER - Consider for rank-up",
                    "Mild": "LOWER TIER - Lower priority for rank-up",
                    "Information": "LOW TIER - Lowest priority for rank-up"
                }
                
                advice = tier_order.get(champion.tier, "Assess based on your team composition")
                print(f"    Rank-up Priority: {advice}")
        else:
            print(f"  No matches found for '{test_name}'")
    
    # Show top champions for general rank-up recommendations
    print("\n" + "="*50)
    print("SAMPLE GENERAL RANK-UP RECOMMENDATIONS:")
    print("Top champions by tier (from both sources):")
    
    # Define tier rankings (higher is better)
    tier_order = {
        "Above All": 10,
        "Scorching": 9,
        "Super Hot": 8,
        "Hot": 7,
        "Mild": 6,
        "Information": 5
    }
    
    # Sort champions by tier (with rating as secondary sort if available)
    def sort_key(champ):
        tier_rank = tier_order.get(champ.tier, 0)
        return (tier_rank, champ.rating or 0)
    
    sorted_champions = sorted(all_champions, key=sort_key, reverse=True)[:10]  # Top 10
    
    for i, champ in enumerate(sorted_champions, 1):
        rating_str = f" - Rating: {champ.rating}/10" if champ.rating else ""
        print(f"{i:2d}. {champ.name} - Tier: {champ.tier}{rating_str} (Source: {champ.source})")


if __name__ == "__main__":
    main()