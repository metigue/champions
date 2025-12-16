import requests
import csv
import io
import json
import re
from difflib import SequenceMatcher

def build_champion_database():
    """Build a comprehensive JSON database by combining data from both sheets"""
    
    # URLs for the spreadsheets
    champion_tier_list_url = "https://docs.google.com/spreadsheets/d/1-jx73TSUeauTe15taA5vNmCUCxjQvrf83aPPu56O3Jw/export?format=csv&gid=0"
    battlegrounds_tier_list_url = "https://docs.google.com/spreadsheets/d/154iFgpTI6lfBLgXariI3W1pLjS2wXSsiMademauXzLU/export?format=csv&gid=0"
    
    # Fetch and parse both sheets
    print("Fetching Champion Tier List sheet...")
    champion_tier_list_response = requests.get(champion_tier_list_url)
    champion_tier_list_response.raise_for_status()
    champion_tier_list_csv = list(csv.reader(io.StringIO(champion_tier_list_response.text)))
    
    print("Fetching Battlegrounds Tier List sheet...")
    battlegrounds_tier_list_response = requests.get(battlegrounds_tier_list_url)
    battlegrounds_tier_list_response.raise_for_status()
    battlegrounds_tier_list_csv = list(csv.reader(io.StringIO(battlegrounds_tier_list_response.text)))
    
    # Parse Battlegrounds data - create a lookup table
    battlegrounds_data = {}  # {champion_name: {rating: float, type: str, symbols: list}}

    # Process the battlegrounds_tier_list_csv
    current_role = None
    current_tier = None
    class_headers = {}
    if len(battlegrounds_tier_list_csv) > 0:
        for col_idx, cell_value in enumerate(battlegrounds_tier_list_csv[0]):
            if cell_value.strip().lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic']:
                class_headers[col_idx] = cell_value.strip()

    for row_idx, row in enumerate(battlegrounds_tier_list_csv):
        if not row:
            continue

        first_col_value = row[0].strip()

        if first_col_value in ["Dual Threat", "Attackers", "Defenders"]:
            current_role = first_col_value
            current_tier = None  # Reset tier when role changes
            continue

        if not current_role:
            continue

        if first_col_value in ["Tier Above All", "Scorching", "Super Hot", "Hot", "Mild", "Information"]:
            current_tier = first_col_value
            # Process this row the same as data rows (for immediate data)
            for col_idx in range(1, len(row)):
                if col_idx in class_headers:
                    category = class_headers[col_idx]
                    cell_value = row[col_idx].strip()

                    if not cell_value:
                        continue

                    parts = cell_value.split('-', 1)
                    if len(parts) >= 2:
                        name_part = parts[0].strip()
                        rating_part_str = parts[1].strip()

                        rating = None
                        if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
                            rating = 10
                        elif rating_part_str and rating_part_str[0].isdigit():
                            rating = int(rating_part_str[0])

                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(cell_value)

                        if name_part:
                            battlegrounds_data[name_part.lower()] = {
                                "rating": rating,
                                "type": current_role,
                                "symbols": symbols
                            }
                    else: # Handle cases where there's a name but no rating (e.g. just a champion name)
                        # Extract symbols from the original cell value
                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(cell_value)
                        clean_name = emoji_pattern.sub('', cell_value).strip()

                        if clean_name:
                            battlegrounds_data[clean_name.lower()] = {
                                "rating": None, # No explicit rating
                                "type": current_role,
                                "symbols": symbols
                            }
        elif current_tier and first_col_value == "":  # This is a data row without a tier header
            # Process rows that contain data but don't have the tier in the first column
            for col_idx in range(1, len(row)):
                if col_idx in class_headers:
                    category = class_headers[col_idx]
                    cell_value = row[col_idx].strip()

                    if not cell_value:
                        continue

                    parts = cell_value.split('-', 1)
                    if len(parts) >= 2:
                        name_part = parts[0].strip()
                        rating_part_str = parts[1].strip()

                        rating = None
                        if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
                            rating = 10
                        elif rating_part_str and rating_part_str[0].isdigit():
                            rating = int(rating_part_str[0])

                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(cell_value)

                        if name_part:
                            battlegrounds_data[name_part.lower()] = {
                                "rating": rating,
                                "type": current_role,
                                "symbols": symbols
                            }
                    else: # Handle cases where there's a name but no rating (e.g. just a champion name)
                        # Extract symbols from the original cell value
                        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
                        symbols = emoji_pattern.findall(cell_value)
                        clean_name = emoji_pattern.sub('', cell_value).strip()

                        if clean_name:
                            battlegrounds_data[clean_name.lower()] = {
                                "rating": None, # No explicit rating
                                "type": current_role,
                                "symbols": symbols
                            }
    
    # Parse Champion Tier list data to get class rankings and tiers
    champions_data = {}
    # Dictionary of known champions and their special properties
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
    
    # Assuming header rows are 0-7, and tier names are in row 6
    tier_names = [tier.strip() for tier in champion_tier_list_csv[6][1:] if tier.strip()]

    current_category = None
    for row_idx in range(8, len(champion_tier_list_csv)):
        row = champion_tier_list_csv[row_idx]
        if not row:
            continue

        first_col_cell = row[0].strip()
        if first_col_cell and first_col_cell.lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic']:
            current_category = first_col_cell
        elif not first_col_cell:
            # If first column is empty, continue using the current category if it's set
            # This handles rows like row 325 that contain champions but don't repeat the class name
            if not current_category:
                # Skip if there's no category established yet
                continue
        else:
            # If first column is not empty but not a class, it might be different data
            continue

        for col_idx in range(1, len(row)):
            cell_value = row[col_idx].strip()
            if not cell_value:
                continue

            if col_idx - 1 < len(tier_names):
                tier = tier_names[col_idx - 1]
            else:
                tier = "Information"

            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF]+')
            symbols = emoji_pattern.findall(cell_value)
            clean_name = emoji_pattern.sub('', cell_value).strip()

            if clean_name:
                name_key = clean_name.lower()
                symbol_overrides = known_champion_symbols.get(name_key, {})

                champions_data[name_key] = {
                    "name": clean_name,
                    "class": current_category,
                    "rank": None, # Rank is not explicitly given in this format, determined by order of parsing
                    "tier": tier,
                    "ranking_display": f"{current_category} ({tier})",
                    "ranking_depends_on_awakening": symbol_overrides.get('ranking_depends_on_awakening', '🌟' in symbols),
                    "ranking_depends_on_signature": symbol_overrides.get('ranking_depends_on_signature', '🚀' in symbols),
                    "top_candidate_for_ascension": symbol_overrides.get('top_candidate_for_ascension', '💎' in symbols),
                    "difficult_as_7star": symbol_overrides.get('difficult_as_7star', '🌹' in symbols),
                    "specific_relic_needed": symbol_overrides.get('specific_relic_needed', '💾' in symbols),
                    "early_prediction": symbol_overrides.get('early_prediction', '🎲' in symbols),
                    "other_symbols": [s for s in symbols if s not in ['🌟', '🚀', '💎', '🌹', '💾', '🎲']],
                    "battlegrounds_rating": None, # Will be filled by matching
                    "battlegrounds_type": None, # Will be filled by matching
                    "source": "champion_tier_list"
                }

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
        if best_match and best_ratio > 0.7: # Only apply if the match is reasonably good
            champions_data[best_match]["battlegrounds_rating"] = bg_data["rating"]
            champions_data[best_match]["battlegrounds_type"] = bg_data["type"]
            champions_data[best_match]["source"] = "combined"
            # Record that this main sheet entry has been matched to prevent double matching
            matched_main_champions.add(best_match)
            # Remove from battlegrounds_data since it's been matched
            del battlegrounds_data[bg_name]

    # Include champions that are only in battlegrounds sheet but not in ranking sheet
    for bg_name, bg_data in battlegrounds_data.items():
        # Only add if it wasn't matched to an existing champion
        if bg_name not in champions_data:
            # For champions only in battlegrounds, we default some values
            champions_data[bg_name] = {
                "name": bg_name.title(),
                "class": "Unknown", # Class cannot be determined from BG sheet alone without complex lookup
                "rank": None,
                "tier": "Information",
                "ranking_display": "Battlegrounds Only",
                "ranking_depends_on_awakening": False,
                "ranking_depends_on_signature": False,
                "top_candidate_for_ascension": False,
                "difficult_as_7star": False,
                "specific_relic_needed": False,
                "early_prediction": False,
                "other_symbols": bg_data["symbols"],
                "battlegrounds_rating": bg_data["rating"],
                "battlegrounds_type": bg_data["type"],
                "source": "battlegrounds_only"
            }

    # Filter out non-champion entries that were accidentally included
    non_champion_keywords = [
        'mcoce', 'illuminati', 'vega', 'cantona', 'grass', 'encyclopedia', 'encyclopdia', 
        'nagase', 'tjarvis', 'william', 'creator codes', 'socials', 'youtube', 'twitter', 
        'bluesky', 'instagram', 'discord', 'more helpful videos', 'how to fight', 'series',
        'guide', 'video', 'channel', 'page', 'link', 'url', 'website', 'stream', 'twitch',
        'legend', 'use as a guide', 'non 7 star champions will struggle in higher tiers of pvp & end-game content',
        'not all champions are good enough to be ranked', 'all champions ranked on this sheet have uses',
        'endgame & competitive list', 'the broken or super meta', 'phenomenal', 'great', 'pretty good',
        'goodish', '59th edition - november, 2025'
    ]
    
    filtered_champions_data = {}
    for name_key, champion_data in champions_data.items():
        name_lower = champion_data['name'].lower()
        
        is_non_champion = False
        for keyword in non_champion_keywords:
            if keyword in name_lower:
                is_non_champion = True
                break
        
        # Additional check for generic "information" tier champions that aren't specific
        if not is_non_champion and champion_data['tier'] == 'Information' and champion_data['source'] == 'champion_tier_list':
            # This is a bit of a heuristic: if a champion is just "information" tier from the main list,
            # and its name is very short or looks like a header, it's likely noise.
            if len(name_lower) < 5 or any(char.isdigit() for char in name_lower) or name_lower in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic']:
                 is_non_champion = True
        
        if not is_non_champion:
            filtered_champions_data[name_key] = champion_data

    # Save to JSON file
    with open('champions_database.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_champions_data, f, indent=2, ensure_ascii=False)
    
    print(f"Database built successfully! Contains {len(filtered_champions_data)} champions.")
    
    # Check if there are any champions with battlegrounds data
    print(f"\nSample entries from the database:")
    bg_count = 0
    no_bg_count = 0
    
    for champ_name, champ_data in filtered_champions_data.items():
        if bg_count < 3 and champ_data['battlegrounds_rating'] is not None:  # Print first 3 with BG data
            print(f"\n{champ_name.title()}:")
            print(f"  Name: {champ_data['name']}")
            print(f"  Class: {champ_data['class']}")
            print(f"  Tier: {champ_data['tier']}")
            print(f"  Ranking Display: {champ_data['ranking_display']}")
            print(f"  Battlegrounds Rating: {champ_data['battlegrounds_rating']}")
            print(f"  Battlegrounds Type: {champ_data['battlegrounds_type']}")
            bg_count += 1
        elif no_bg_count < 2 and champ_data['battlegrounds_rating'] is None and bg_count >= 3:  # Print 2 without BG data after we've shown some with it
            print(f"\n{champ_name.title()}:")
            print(f"  Name: {champ_data['name']}")
            print(f"  Class: {champ_data['class']}")
            print(f"  Tier: {champ_data['tier']}")
            print(f"  Ranking Display: {champ_data['ranking_display']}")
            print(f"  Battlegrounds Rating: {champ_data['battlegrounds_rating']}")
            no_bg_count += 1
        elif bg_count < 3 and no_bg_count >= 2:  # Continue looking for BG data
            continue
        elif bg_count >= 3 and no_bg_count >= 2:
            break
    
    # Check if any champions have battlegrounds data
    champs_with_bg = [name for name, data in filtered_champions_data.items() if data['battlegrounds_rating'] is not None]
    print(f"\nTotal champions with battlegrounds data: {len(champs_with_bg)}")
    
    if champs_with_bg:
        print("Some champions with BG data:", champs_with_bg[:5])  # First 5
    else:
        print("No champions found with battlegrounds data.")
    
    return filtered_champions_data

if __name__ == "__main__":
    build_champion_database()