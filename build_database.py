import requests
import csv
import io
import json
import re
from difflib import SequenceMatcher

def build_champion_database():
    """Build a comprehensive JSON database by combining data from both sheets"""
    
    # URLs for the spreadsheets - updated to new general class rankings
    vega_bgs_url = "https://docs.google.com/spreadsheets/d/1KzfdzI_HxK7zk_eTwmdwI5G84k9HSIYPzAMSPgGYjUE/export?format=csv&gid=0"
    # New general class rankings sheet
    general_rankings_url = "https://docs.google.com/spreadsheets/d/1cUr2KoqGtZhx6zIAQw-LkUR9xFwS2xR6HNVKed3qSvQ/export?format=csv&gid=0"
    
    # Fetch and parse both sheets
    print("Fetching Battlegrounds sheet...")
    bg_response = requests.get(vega_bgs_url)
    bg_response.raise_for_status()
    bg_csv = list(csv.reader(io.StringIO(bg_response.text)))
    
    print("Fetching Ranking sheet (old sheet)...")  # Keep for reference, but will use new sheet below
    # rank_response = requests.get(illuminati_ranking_url)
    # rank_response.raise_for_status()
    # rank_csv = list(csv.reader(io.StringIO(rank_response.text)))
    
    # Instead of using the old ranking sheet, we'll use the new general rankings sheet
    print("Fetching New General Rankings sheet...")
    rank_response = requests.get(general_rankings_url)
    rank_response.raise_for_status()
    rank_csv = list(csv.reader(io.StringIO(rank_response.text)))
    
    # Parse Battlegrounds data - create a lookup table
    battlegrounds_data = {}  # {champion_name: {rating: float, type: str, symbols: list}}
    
    # Process each column (Mystic, Science, etc.) in the BGs sheet
    for col_idx in range(1, len(bg_csv[0])):  # Skip column 0
        if col_idx >= len(bg_csv[0]):
            continue
            
        category = bg_csv[0][col_idx].strip() if col_idx < len(bg_csv[0]) else ""
        if not category:
            continue
            
        # Process rows starting from row 3 where champions start
        for row_idx in range(3, len(bg_csv)):
            if col_idx >= len(bg_csv[row_idx]):
                continue
                
            cell_value = bg_csv[row_idx][col_idx].strip()
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
                
                # Determine battleground type based purely on row position
                # The Battlegrounds type is determined by the row position:
                # - Rows 3-30: Dual Threat section (Nico Minoru, Tigra, etc.)
                # - Rows 31-90: Attackers section (Spider-Man at Row 78, etc.)
                # - Rows 91+: Defenders section (Enchantress, Doctor Doom, etc.)
                bg_type = "Dual Threat"  # Default for early rows
                
                # Determine the battlegrounds type based on row position ONLY
                if 31 <= row_idx <= 90:
                    # This is in the Attackers section
                    bg_type = "Attacker"
                elif 91 <= row_idx:
                    # This is in the Defenders section
                    bg_type = "Defender"
                # Rows 3-30 default to Dual Threat
                

                
                battlegrounds_data[name_part.lower()] = {
                    "rating": rating_part,
                    "type": bg_type,
                    "symbols": symbols
                }
    
    # Parse Ranking sheet to get class rankings and tiers
    champions_data = {}
    # Dictionary of known champions and their special properties
    # This compensates for emoji symbols that may be lost in CSV export
    known_champion_symbols = {
        "mr. negative": {
            "ranking_depends_on_awakening": True,  # 🌟 Awakening needed for this ranking
            "difficult_as_7star": True,  # 🌹 Not available as a 7 star (or very rare)
            "early_prediction": False,  # Not marked with 🎲
            "specific_relic_needed": False,  # Not marked with 💾
            "ranking_depends_on_signature": False,  # Not marked with 🚀
            "top_candidate_for_ascension": False  # Not marked with 💎
        },
        "mister negative": {
            "ranking_depends_on_awakening": True,  # 🌟 Awakening needed for this ranking
            "difficult_as_7star": True,  # 🌹 Not available as a 7 star (or very rare)
            "early_prediction": False,
            "specific_relic_needed": False,
            "ranking_depends_on_signature": False,
            "top_candidate_for_ascension": False
        },
        "spider-man (supreme)": {
            "ranking_depends_on_awakening": False,
            "difficult_as_7star": False,
            "early_prediction": False,
            "specific_relic_needed": True,  # 💾 Correct relic is important
            "ranking_depends_on_signature": True,  # 🚀 High or Max Sig needed for this ranking
            "top_candidate_for_ascension": False
        }
        # Add more champions as needed
    }
    
    # Find all class names in column A of ranking sheet
    class_starts = []
    for row_idx in range(len(rank_csv)):
        if row_idx < len(rank_csv) and len(rank_csv[row_idx]) > 0:
            cell_a = rank_csv[row_idx][0] if len(rank_csv[row_idx]) > 0 else ""
            class_name = cell_a.strip().title() if cell_a.strip() else ""
            
            if class_name.lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic', 'guardian']:
                class_starts.append((row_idx, class_name))
    

    
    # Process each class and its champion range
    for i, (start_row, class_name) in enumerate(class_starts):
        # Determine the end of this class range
        if i + 1 < len(class_starts):
            end_row = class_starts[i + 1][0]  # Start of next class
        else:
            end_row = len(rank_csv)  # End of all data
        

        
        # For this class, assign rankings by going column by column, row by row in the class range
        rank_counter = 1  # Start ranking at 1 for each class
        
        # Process each column from B onward
        for col_idx in range(1, len(rank_csv[0]) if len(rank_csv) > 0 else 0):
            # Process each row in the class range for this column
            for row_idx in range(start_row, end_row):

                
                try:
                    if col_idx >= len(rank_csv[row_idx]):  # Column doesn't exist for this row
                        continue
                    
                    cell_value = rank_csv[row_idx][col_idx].strip()
                    
                    # Skip empty cells
                    if not cell_value:
                        continue
                    
                    # Skip rows that appear to be headers or metadata
                    cell_lower = cell_value.lower()
                    filtered_out = False
                    header_keywords = [
                        'champion', 'champions', 'name', 'tier', 'rating', 'category',
                        'above all', 'scorching', 'super hot', 'hot', 'mild', 'information',
                        'the truly o.p.', 'tier above all', 'omega days', 'glorious guardians',
                        'exclusive', 'go to file', 'to use tier list', 'filtering'
                    ]
                    
                    # Only filter if the cell is exactly or very close to a header keyword
                    # We don't want to filter champion names that happen to contain parts of these words
                    cell_stripped = cell_lower.strip()
                    for skip_text in header_keywords:
                        # Filter if it's an exact match or very close (allowing for small differences)
                        if skip_text == cell_stripped:
                            filtered_out = True
                            break
                        # Or if it's a very short string that matches closely
                        elif len(cell_stripped) <= len(skip_text) + 3 and skip_text in cell_stripped:
                            # But only if the lengths are close (to avoid filtering champion names like "photon")
                            if abs(len(cell_stripped) - len(skip_text)) <= 3:
                                filtered_out = True
                                break
                    

                    
                    if filtered_out:
                        continue
                    
                    # Extract emoji symbols from the name using pure Python
                    # Find the first non a-z, A-Z, 0-9, hyphen, space, parentheses character  
                    name_part = ""
                    i = 0
                    while i < len(cell_value):
                        char = cell_value[i]
                        # Check if character is a-z, A-Z, 0-9, hyphen, space, or parentheses
                        char_code = ord(char)
                        if (65 <= char_code <= 90) or (97 <= char_code <= 122) or (48 <= char_code <= 57) or char in ' -()':
                            name_part += char
                            i += 1
                        else:
                            # Found first non-allowed character (likely emoji start)
                            break
                    
                    # The rest is emojis and symbols
                    emoji_part = cell_value[i:].strip()
                    
                    # Clean the name part
                    clean_name = name_part.strip()
                    
                    # Extract symbols from the emoji part
                    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                    symbols = emoji_pattern.findall(emoji_part)
                    
                    if clean_name and len(clean_name) > 1:  # Valid champion name

                        
                        # Find the tier by looking up in row context
                        tier = "Information"  # Default
                        # We can determine tier based on the position of the champion in the class
                        # Higher positions (earlier rows, earlier columns) are higher tiers
                        
                        # Look upward from this row to find the tier classification
                        for check_row in range(row_idx, -1, -1):
                            if check_row < len(rank_csv) and len(rank_csv[check_row]) > col_idx:
                                row_header = rank_csv[check_row][col_idx].strip() if len(rank_csv[check_row]) > col_idx else ""
                                if "Above All" in row_header:
                                    tier = "Above All"
                                    break
                                elif "Scorching" in row_header:
                                    tier = "Scorching"
                                    break
                                elif "Super Hot" in row_header:
                                    tier = "Super Hot"
                                    break
                                elif "Hot" in row_header:
                                    tier = "Hot"
                                    break
                                elif "Mild" in row_header:
                                    tier = "Mild"
                                    break
                                elif "Information" in row_header:
                                    tier = "Information"
                                    break
                        
                        # Also check row 1 and 2 for tier info
                        if tier == "Information" and row_idx >= 1:
                            row1_header = rank_csv[1][col_idx].strip() if len(rank_csv[1]) > col_idx else ""
                            if "Above All" in row1_header:
                                tier = "Above All"
                            elif "Scorching" in row1_header:
                                tier = "Scorching"
                            elif "Super Hot" in row1_header:
                                tier = "Super Hot"
                            elif "Hot" in row1_header:
                                tier = "Hot"
                            elif "Mild" in row1_header:
                                tier = "Mild"
                            elif "Information" in row1_header:
                                tier = "Information"
                        
                        # Get battlegrounds data - try both clean name and original name with emojis
                        bg_data = battlegrounds_data.get(clean_name.lower(), {})
                        if not bg_data:  # If no data found for clean name, try original with emojis
                            bg_data = battlegrounds_data.get(cell_value.lower(), {})
                        

                        
                        # Override with known symbols if available
                        name_key = clean_name.lower()
                        symbol_overrides = known_champion_symbols.get(name_key, {})
                        
                        champions_data[clean_name.lower()] = {
                            "name": clean_name,
                            "class": class_name,
                            "rank": rank_counter,
                            "tier": tier,
                            "ranking_display": f"{class_name} #{rank_counter}",
                            "ranking_depends_on_awakening": symbol_overrides.get('ranking_depends_on_awakening', '🌟' in symbols),
                            "ranking_depends_on_signature": symbol_overrides.get('ranking_depends_on_signature', '🚀' in symbols),
                            "top_candidate_for_ascension": symbol_overrides.get('top_candidate_for_ascension', '💎' in symbols),
                            "difficult_as_7star": symbol_overrides.get('difficult_as_7star', '🌹' in symbols),
                            "specific_relic_needed": symbol_overrides.get('specific_relic_needed', '💾' in symbols),
                            "early_prediction": symbol_overrides.get('early_prediction', '🎲' in symbols),
                            "other_symbols": [s for s in symbols if s not in ['🌟', '🚀', '💎', '🌹', '💾', '🎲']],
                            "battlegrounds_rating": bg_data.get("rating"),
                            "battlegrounds_type": bg_data.get("type"),
                            "source": "combined"
                        }
                        
                        # Increment rank for next champion in this tier/class
                        rank_counter += 1
                        
                except (IndexError, TypeError):
                    continue  # Skip if cell doesn't exist
    
    # Now match battlegrounds data to champions in the main sheet
    # Track which main sheet champions have already been matched to prevent double-matching
    matched_main_champions = set()
    
    # First, match exact names
    for bg_name, bg_data in list(battlegrounds_data.items()):
        if bg_name in champions_data:
            # Exact match found, update with battlegrounds data
            champions_data[bg_name]["battlegrounds_rating"] = bg_data["rating"]
            champions_data[bg_name]["battlegrounds_type"] = bg_data["type"]
            champions_data[bg_name]["source"] = "combined"
            # Record that this main sheet entry has been matched
            matched_main_champions.add(bg_name)
            # Remove from battlegrounds_data since it's been matched
            del battlegrounds_data[bg_name]
    
    # Then, for remaining battlegrounds data, use fuzzy matching to find closest names
    remaining_bg_data = dict(battlegrounds_data)  # Copy remaining items
    for bg_name, bg_data in remaining_bg_data.items():
        best_match = None
        best_ratio = 0
        
        # Look for the best match among the remaining champions (excluding those already matched)
        for existing_name in champions_data.keys():
            # Skip if this main sheet champion has already been matched
            if existing_name in matched_main_champions:
                continue
                
            # Calculate similarity between battlegrounds name and existing champion name
            ratio = SequenceMatcher(None, bg_name.lower(), existing_name.lower()).ratio()
            
            # Also check if one name contains the other (for cases like "Werewolf" vs "Werewolf by Night")
            if bg_name.lower() in existing_name.lower() or existing_name.lower() in bg_name.lower():
                # Boost similarity if one name contains the other
                ratio = max(ratio, 0.85)
            
            # Special handling for known champion name variations to improve matching accuracy
            # Handle specific cases where we know the correct mappings
            known_variations = {
                'mr. negative': 'mister negative',
                'mr negative': 'mister negative',
                'mister negative': 'mr. negative',
                'spidey supreme': 'spider-man (supreme)',
                'spider-man (supreme)': 'spidey supreme',
                'sigil witch': 'scarlet witch (sigil)',
                'scarlet witch (sigil)': 'sigil witch'
            }
            
            bg_normalized = bg_name.lower().strip()
            existing_normalized = existing_name.lower().strip()
            
            # Check for exact known variations
            if bg_normalized in known_variations and known_variations[bg_normalized] == existing_normalized:
                # Very high match for known variations
                ratio = 0.95
            elif existing_normalized in known_variations and known_variations[existing_normalized] == bg_normalized:
                # Very high match for known variations (reverse)
                ratio = 0.95
            
            # Special handling for names with common prefixes like "Mr." vs "Dr." that might interfere
            # Process the names to remove common prefixes for additional similarity checking
            bg_no_prefix = bg_name.lower().replace('mr.', '').replace('dr.', '').replace('captain ', '').strip()
            existing_no_prefix = existing_name.lower().replace('mr.', '').replace('dr.', '').replace('captain ', '').strip()
            
            # Calculate ratio without prefixes to avoid prefix-based mismatches
            prefix_removed_ratio = SequenceMatcher(None, bg_no_prefix, existing_no_prefix).ratio()
            
            # Use the higher of the two ratios
            ratio = max(ratio, prefix_removed_ratio)
            
            # Look for shared special terms that would indicate a strong match
            bg_lower = bg_name.lower()
            existing_lower = existing_name.lower()
            
            # Common special terms found in champion names
            terms = ['sigil', 'supreme', 'future', 'movie', 'deathless', 'stark']
            shared_terms = [term for term in terms if term in bg_lower and term in existing_lower]
            if shared_terms:
                # Boost similarity for names sharing special terms
                ratio += 0.1  # Small boost for each shared term pattern
            
            if ratio > best_ratio:  # Take the closest match
                best_ratio = ratio
                best_match = existing_name
        
        # If we found a good match, update that champion with battlegrounds data
        if best_match:
            champions_data[best_match]["battlegrounds_rating"] = bg_data["rating"]
            champions_data[best_match]["battlegrounds_type"] = bg_data["type"]
            champions_data[best_match]["source"] = "combined"
            # Record that this main sheet entry has been matched to prevent double matching
            matched_main_champions.add(best_match)
            # Remove from battlegrounds_data since it's been matched
            del battlegrounds_data[bg_name]

    # Include champions that are only in battlegrounds sheet but not in ranking sheet
    # Need to map the column position to the class for proper categorization
    # First get class names from column headers in the battlegrounds sheet
    bg_class_mapping = {}
    for col_idx, header in enumerate(bg_csv[0]):  # Row 0 contains headers
        if col_idx > 0:  # Skip the first column
            class_name = header.strip()
            if class_name.lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic', 'guardian']:
                bg_class_mapping[col_idx] = class_name
    
    # For any remaining battlegrounds-only champions, add them to the database
    for bg_name, bg_data in battlegrounds_data.items():
        # Try to find the class for this champion by looking through the sheet data
        found_class = None
        
        for col_idx, header in enumerate(bg_csv[0]):  # Check each column
            if col_idx in bg_class_mapping:  # Only check valid class columns
                class_name = bg_class_mapping[col_idx]
                # Look through the rows in this column to find our champion
                for row_idx in range(3, len(bg_csv)):  # Start from row 3 where champions start
                    if col_idx < len(bg_csv[row_idx]):
                        cell_value = bg_csv[row_idx][col_idx].strip()
                        # Extract name from format like "Korg - 7"
                        parts = cell_value.split('-', 1)
                        if len(parts) >= 2:
                            name_part = parts[0].strip().lower()
                            if name_part == bg_name:
                                found_class = class_name
                                break
                if found_class:
                    break
        
        # If we couldn't determine the class, default to 'Unknown'
        if not found_class:
            found_class = 'Unknown'
            rank = 999  # High number to indicate lower priority
            tier = 'Information'  # Default for unknown ranking
        else:
            # For champions in ranking sheet, we'd have their rank and tier
            # But since they're battlegrounds-only, we'll default to Information tier
            rank = 999
            tier = 'Information'
        
        champions_data[bg_name] = {
            "name": bg_name.title(),
            "class": found_class,
            "rank": rank,
            "tier": tier,
            "ranking_display": f"{found_class} #{rank}",
            "ranking_depends_on_awakening": False,
            "ranking_depends_on_signature": False,
            "top_candidate_for_ascension": False,
            "difficult_as_7star": False,
            "specific_relic_needed": False,
            "early_prediction": False,
            "other_symbols": [],
            "battlegrounds_rating": bg_data["rating"],
            "battlegrounds_type": bg_data["type"],
            "source": "vega"  # From battlegrounds sheet
        }

    # Filter out non-champion entries that were accidentally included 
    # (like contributor names, social media links, etc. from the Information column)
    non_champion_keywords = [
        'mcoce', 'illuminati', 'vega', 'cantona', 'grass', 'encyclopedia', 'encyclopdia', 
        'nagase', 'tjarvis', 'william', 'creator codes', 'socials', 'youtube', 'twitter', 
        'bluesky', 'instagram', 'discord', 'more helpful videos', 'how to fight', 'series',
        'guide', 'video', 'channel', 'page', 'link', 'url', 'website', 'stream', 'twitch'
    ]
    
    # Create a new dictionary with only legitimate champions
    filtered_champions_data = {}
    for name_key, champion_data in champions_data.items():
        name_lower = champion_data['name'].lower()
        
        # Check if the name contains any non-champion keywords
        is_non_champion = False
        for keyword in non_champion_keywords:
            if keyword in name_lower:
                is_non_champion = True
                break
        
        # Also check if the tier is 'Information' but the name suggests it's not a real champion
        if not is_non_champion and champion_data['tier'] == 'Information':
            # If it's from the information tier but doesn't have obvious non-champion keywords,
            # we might still want to check if it's a real champion based on other factors
            # For now, we'll keep it unless we're sure it's a non-champion
            pass
        
        if not is_non_champion:
            filtered_champions_data[name_key] = champion_data

    # Save to JSON file
    with open('champions_database.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_champions_data, f, indent=2, ensure_ascii=False)
    
    print(f"Database built successfully! Contains {len(champions_data)} champions.")
    
    # Check if there are any champions with battlegrounds data
    print(f"\nSample entries from the database:")
    bg_count = 0
    no_bg_count = 0
    
    for champ_name, champ_data in champions_data.items():
        if bg_count < 3 and champ_data['battlegrounds_rating'] is not None:  # Print first 3 with BG data
            print(f"\n{champ_name.title()}:")
            print(f"  Name: {champ_data['name']}")
            print(f"  Class: {champ_data['class']}")
            print(f"  Rank: {champ_data['rank']}")
            print(f"  Tier: {champ_data['tier']}")
            print(f"  Ranking Display: {champ_data['ranking_display']}")
            print(f"  Battlegrounds Rating: {champ_data['battlegrounds_rating']}")
            print(f"  Battlegrounds Type: {champ_data['battlegrounds_type']}")
            print(f"  Has Relic Needed: {champ_data['specific_relic_needed']}")
            print(f"  Early Prediction: {champ_data['early_prediction']}")
            bg_count += 1
        elif no_bg_count < 2 and champ_data['battlegrounds_rating'] is None and bg_count >= 3:  # Print 2 without BG data after we've shown some with it
            print(f"\n{champ_name.title()}:")
            print(f"  Name: {champ_data['name']}")
            print(f"  Class: {champ_data['class']}")
            print(f"  Rank: {champ_data['rank']}")
            print(f"  Tier: {champ_data['tier']}")
            print(f"  Ranking Display: {champ_data['ranking_display']}")
            print(f"  Battlegrounds Rating: {champ_data['battlegrounds_rating']}")
            print(f"  Has Relic Needed: {champ_data['specific_relic_needed']}")
            print(f"  Early Prediction: {champ_data['early_prediction']}")
            no_bg_count += 1
        elif bg_count < 3 and no_bg_count >= 2:  # Continue looking for BG data
            continue
        elif bg_count >= 3 and no_bg_count >= 2:
            break
    
    # Check if any champions have battlegrounds data
    champs_with_bg = [name for name, data in champions_data.items() if data['battlegrounds_rating'] is not None]
    print(f"\nTotal champions with battlegrounds data: {len(champs_with_bg)}")
    
    if champs_with_bg:
        print("Some champions with BG data:", champs_with_bg[:5])  # First 5
    else:
        print("No champions found with battlegrounds data. Checking battlegrounds lookup table...")
        print("First few entries in battlegrounds lookup:", list(battlegrounds_data.items())[:5])
    
    return champions_data

if __name__ == "__main__":
    build_champion_database()