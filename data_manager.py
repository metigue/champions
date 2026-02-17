import requests
import csv
import io
import re
import logging
from typing import List, Dict
from champion_model import Champion, calculate_overall_tier, TIER_SCORES
try:
    from config import SHEET_URLS
except ImportError:
    SHEET_URLS = None

# Comprehensive alias mapping for champion name variations between sheets
# BG sheet uses abbreviations and different formats than PvE/PvP sheets
CHAMPION_ALIASES = {
    # Abbreviations in BG sheet
    'bpcw': 'blackpanthercivilwar',
    'cgr': 'cosmicghostrider',
    'dococ': 'dococtopus',
    'dococtopus': 'dococtopus',
    'doctoroctopus': 'dococtopus',
    'corvus': 'corvusglaive',
    'nefaria': 'countnefaria',
    'sinister': 'mistersinister',
    'voodoo': 'doctorvoodoo',
    'zola': 'arnimzola',
    'serpent': 'theserpent',
    'clairev': 'blackwidowclaire',
    'guillotine99': 'guillotine2099',
    'guillotine2099': 'guillotine2099',
    'deathlessguilly': 'guillotinedeathless',
    'guillotinedeathless': 'guillotinedeathless',
    'deathlesskg': 'kinggrootdeathless',
    'kinggrootdeathless': 'kinggrootdeathless',
    
    # Different word orders
    'futureantman': 'antmanfuture',
    'antmanfuture': 'antmanfuture',
    
    # Shortened names in BG
    'mrfantastic': 'misterfantastic',
    'misterfantastic': 'misterfantastic',
    'jackolantern': 'jackolantern',
    "jacko'lantern": 'jackolantern',
    'jackolantern': 'jackolantern',
    'cyclopsblue': 'cyclopsblueteam',
    'cyclopsblueteam': 'cyclopsblueteam',
    
    # Spelling variations
    'sabertooth': 'sabretooth',
    'sabretooth': 'sabretooth',
    
    # "The" prefix variations
    'theserpent': 'theserpent',
    
    # Spider-Man variations
    'spiderman': 'spidermanclassic',
    'spidermanclassic': 'spidermanclassic',
    'spidey2099': 'spiderman2099',
    'spiderman2099': 'spiderman2099',
    'spideysupreme': 'spidermansupreme',
    'spidermansupreme': 'spidermansupreme',
    'starkspidey': 'spidermanstark',
    'spidermanstark': 'spidermanstark',
    'stealthspidey': 'spidermanstealth',
    'spidermanstealth': 'spidermanstealth',
    
    # Captain America variations
    'capamericaiw': 'capamericainfinitywar',
    'capamericainfinitywar': 'capamericainfinitywar',
    'capsamwilson': 'capamericasamwilson',
    'capamericasamwilson': 'capamericasamwilson',
    
    # Iron Man variations
    'ironmaniw': 'ironmaninfinitywar',
    'ironmaninfinitywar': 'ironmaninfinitywar',
    'ogironman': 'ironman',
    'ironman': 'ironman', 'ironmanog': 'ironman',
    
    # Hulk variations
    'ihulk': 'hulkimmortal',
    'hulkimmortal': 'hulkimmortal',
    'oghulk': 'hulk',
    'hulk': 'hulk', 'hulkog': 'hulk',
    
    # Storm variations
    'stormog': 'stormog',
    'stormx': 'stormpyramidx',
    'stormpyramidx': 'stormpyramidx',
    
    # Other variations
    'iimirondoom': 'ironmaninfamous',
    'ironmaninfamous': 'ironmaninfamous',
    'jabari': 'jabaripanther',
    'jabaripanther': 'jabaripanther',
    'sigilwitch': 'scarletwitchsigil',
    'scarletwitchsigil': 'scarletwitchsigil',
    'symsupreme': 'symbiotesupreme',
    'symbiotesupreme': 'symbiotesupreme',
    'weaponx': 'wolverineweaponx',
    'wolverineweaponx': 'wolverineweaponx',
    'bwdo': 'blackwidowdeadlyorigin',
    'blackwidowdeadlyorigin': 'blackwidowdeadlyorigin',
    'blackwidowdeadlyorigins': 'blackwidowdeadlyorigin',  # plural form

    # Common search aliases
    'strange': 'doctorstrange',
    'ds': 'doctorstrange',
    'drstrange': 'doctorstrange',
    'karo': 'karolinadean',
    'nico': 'nicominoru',
    'magnetored': 'magnetored',  # Different from magneto
    'magnetowhite': 'magnetohouseofx',
    'magnetohouseofx': 'magnetohouseofx',
    'whitemagneto': 'magnetohouseofx',
    'milesmorales': 'spidermanmilesmorales',
    'spidermanmilesmorales': 'spidermanmilesmorales',
    'negasonic': 'negasonicteenagewarhead',
    'negasonicteenagewarhead': 'negasonicteenagewarhead',
    'spiderslayerjjj': 'spiderslayerjjameson',
    'spiderslayerjjameson': 'spiderslayerjjameson',
    'werewolfbynight': 'werewolf',
    'werewolf': 'werewolf',
}

class DataManager:
    """Handles data retrieval and processing from public Google Sheets via web scraping"""
    
    def __init__(self):
        self.champions_data = {}
        self.combined_champions = {}
    
    def fetch_champions_from_spreadsheets(self) -> Dict[str, List[Champion]]:
        """Fetch and process champion data from all three public spreadsheets"""
        # Use config URLs if available, otherwise fall back to hardcoded
        if SHEET_URLS:
            bgs_url = SHEET_URLS.get('battlegrounds')
            pve_url = SHEET_URLS.get('pve')
            pvp_url = SHEET_URLS.get('pvp')
        else:
            bgs_url = "https://docs.google.com/spreadsheets/d/111Xo45fxQxDzlWjjtvu1KqdNea0hHeRDdpbTrgIDS4A/export?format=csv&gid=0"
            pve_url = "https://docs.google.com/spreadsheets/d/1C-jcb0zED4VoSZ26lVTW7KKyE17u3Cj1kPZdqn8MAnU/export?format=csv&gid=0"
            pvp_url = "https://docs.google.com/spreadsheets/d/1fZ4nZeBZJjmPRSyWC1LY9XubfI3pPyJeYP2Aw9KVgJU/export?format=csv&gid=0"
        
        all_champions = {}
        
        try:
            bgs_data = self._fetch_bgs_sheet(bgs_url)
            all_champions['battlegrounds'] = bgs_data
            logging.info(f"Loaded {len(bgs_data)} champions from Battlegrounds sheet")
        except Exception as e:
            logging.error(f"Error fetching Battlegrounds spreadsheet: {e}")
            all_champions['battlegrounds'] = []
        
        try:
            pve_data = self._fetch_pve_pvp_sheet(pve_url, 'pve')
            all_champions['pve'] = pve_data
            logging.info(f"Loaded {len(pve_data)} champions from PvE sheet")
        except Exception as e:
            logging.error(f"Error fetching PvE spreadsheet: {e}")
            all_champions['pve'] = []
        
        try:
            pvp_data = self._fetch_pve_pvp_sheet(pvp_url, 'pvp')
            all_champions['pvp'] = pvp_data
            logging.info(f"Loaded {len(pvp_data)} champions from PvP sheet")
        except Exception as e:
            logging.error(f"Error fetching PvP spreadsheet: {e}")
            all_champions['pvp'] = []
        
        self.champions_data = all_champions
        self._build_combined_champions()
        
        return self.champions_data
    
    def _fix_encoding(self, text: str) -> str:
        """Fix encoding issues - convert mojibake back to proper UTF-8"""
        try:
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return text
    
    def _clean_champion_name(self, name: str) -> str:
        """Remove emojis and clean champion name"""
        name = self._fix_encoding(name)
        # Include variation selectors (U+FE00-U+FE0F) in the pattern
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\uFE00-\uFE0F]+')
        clean_name = emoji_pattern.sub('', name).strip()
        return clean_name
    
    def _extract_symbols(self, text: str) -> list:
        """Extract emoji symbols from text"""
        text = self._fix_encoding(text)
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u27BF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]+')
        return emoji_pattern.findall(text)
    
    def _normalize_tier_name(self, tier: str) -> str:
        """Normalize tier names - remove 'Tier ' prefix if present"""
        if not tier:
            return "Information"
        tier = tier.strip()
        if tier.lower().startswith("tier "):
            tier = tier[5:].strip()
        return tier
    
    def _fetch_bgs_sheet(self, url: str) -> List[Champion]:
        """Fetch data from the Battlegrounds sheet with numerical scores and BG types"""
        response = requests.get(url)
        response.raise_for_status()
        
        csv_content = io.StringIO(response.text)
        csv_reader = csv.reader(csv_content)
        champions = []
        rows = list(csv_reader)
        
        if not rows or len(rows) < 4:
            return []
        
        header_row = rows[0]
        
        # Find BG type labels (Attacker/Defender/Dual Threat) in column 0
        bg_type_rows = {}
        current_type = "Dual Threat"  # Default
        
        for row_idx in range(len(rows)):
            col0 = rows[row_idx][0].strip() if len(rows[row_idx]) > 0 else ""
            col0_lower = col0.lower()
            
            if col0_lower in ['dual threat', 'attackers', 'defenders', 'attacker', 'defender']:
                if col0_lower == 'attackers':
                    current_type = "Attacker"
                elif col0_lower == 'defenders':
                    current_type = "Defender"
                elif col0_lower == 'attacker':
                    current_type = "Attacker"
                elif col0_lower == 'defender':
                    current_type = "Defender"
                else:
                    current_type = "Dual Threat"
                bg_type_rows[row_idx] = current_type
        
        def get_bg_type_for_row(row_idx):
            """Get the BG type for a given row based on the nearest preceding label"""
            applicable_type = "Dual Threat"
            for label_row, bg_type in sorted(bg_type_rows.items()):
                if label_row <= row_idx:
                    applicable_type = bg_type
                else:
                    break
            return applicable_type
        
        for col_idx in range(1, len(header_row)):
            if col_idx >= len(header_row):
                continue
            
            category = header_row[col_idx].strip() if col_idx < len(header_row) else f"Category_{col_idx}"
            if not category:
                continue
            
            for row_idx in range(3, len(rows)):
                if col_idx >= len(rows[row_idx]):
                    continue
                
                cell_value = rows[row_idx][col_idx].strip()
                if not cell_value:
                    continue
                
                parts = cell_value.split('-', 1)
                if len(parts) >= 2:
                    name_part = self._clean_champion_name(parts[0].strip())
                    rating_part_str = parts[1].strip()
                    
                    if rating_part_str.startswith('1') and len(rating_part_str) > 1 and rating_part_str[1].isdigit():
                        rating_part = 10
                    elif rating_part_str and rating_part_str[0].isdigit():
                        rating_part = int(rating_part_str[0])
                    else:
                        continue
                    
                    symbols = self._extract_symbols(cell_value)
                    tier = self._get_tier_from_rating(rating_part)
                    bg_type = get_bg_type_for_row(row_idx)
                    
                    champion = Champion(
                        name=name_part,
                        tier=tier,
                        category=category,
                        rating=rating_part,
                        symbols=list(set(symbols)),
                        source="battlegrounds",
                        battlegrounds_type=bg_type
                    )
                    champions.append(champion)
        
        return champions
    
    def _fetch_pve_pvp_sheet(self, url: str, source: str) -> List[Champion]:
        """Fetch data from PvE or PvP sheet - tiers as columns, classes as rows
        Champions are ranked by position within each tier column"""
        response = requests.get(url)
        response.raise_for_status()
        
        csv_content = io.StringIO(response.text)
        csv_reader = csv.reader(csv_content)
        champions = []
        rows = list(csv_reader)
        
        if not rows or len(rows) < 8:
            return []
        
        # Get tier names from row 5 and normalize them
        tier_names = []
        if len(rows) > 5:
            for cell in rows[5][1:8]:
                normalized = self._normalize_tier_name(cell.strip())
                tier_names.append(normalized)
        
        # Class rows start at row 7
        class_row_indices = []
        for row_idx in range(7, len(rows)):
            if len(rows[row_idx]) > 0 and rows[row_idx][0].strip():
                cell = rows[row_idx][0].strip()
                if cell.lower() in ['mystic', 'science', 'skill', 'mutant', 'tech', 'cosmic']:
                    class_row_indices.append((row_idx, cell))
        
        # Process each class
        for i, (start_row, class_name) in enumerate(class_row_indices):
            if i + 1 < len(class_row_indices):
                end_row = class_row_indices[i + 1][0]
            else:
                end_row = len(rows)
            
            # Track overall rank within this class
            class_rank = 0
            
            # Process each tier column in order (Above All first, then Scorching, etc.)
            for col_idx, tier_name in enumerate(tier_names):
                if not tier_name or tier_name == 'Information':
                    continue
                
                actual_col = col_idx + 1
                
                # Process each row in this tier column for this class
                for row_idx in range(start_row, min(start_row + 15, end_row)):
                    if actual_col >= len(rows[row_idx]):
                        continue
                    
                    cell_value = rows[row_idx][actual_col].strip()
                    if not cell_value:
                        continue
                    
                    # Skip metadata rows
                    if any(skip in cell_value.lower() for skip in ['creator codes', 'legend', 'ranking', 'mcoc', 'benefits', 'caution']):
                        continue
                    
                    symbols = self._extract_symbols(cell_value)
                    clean_name = self._clean_champion_name(cell_value)
                    
                    if clean_name and len(clean_name) > 1:
                        class_rank += 1  # Increment rank for each champion found
                        
                        if source == 'pve':
                            champion = Champion(
                                name=clean_name,
                                tier=tier_name,
                                category=class_name,
                                symbols=list(set(symbols)),
                                source=source,
                                pve_tier=tier_name,
                                pve_rank=class_rank
                            )
                        else:
                            champion = Champion(
                                name=clean_name,
                                tier=tier_name,
                                category=class_name,
                                symbols=list(set(symbols)),
                                source=source,
                                pvp_tier=tier_name,
                                pvp_rank=class_rank
                            )
                        champions.append(champion)
        
        return champions
    
    def _build_combined_champions(self):
        """Build combined champion data with PvE, PvP, and overall rankings"""
        self.combined_champions = {}
        
        # Index champions by normalized name (using aliases)
        bgs_by_name = {}
        for champ in self.champions_data.get('battlegrounds', []):
            name_key = self._normalize_name(champ.name)
            if name_key not in bgs_by_name:
                bgs_by_name[name_key] = champ
        
        pve_by_name = {}
        for champ in self.champions_data.get('pve', []):
            name_key = self._normalize_name(champ.name)
            if name_key not in pve_by_name:
                pve_by_name[name_key] = champ
        
        pvp_by_name = {}
        for champ in self.champions_data.get('pvp', []):
            name_key = self._normalize_name(champ.name)
            if name_key not in pvp_by_name:
                pvp_by_name[name_key] = champ
        
        # Get all unique champion names (after alias resolution)
        all_names = set(bgs_by_name.keys()) | set(pve_by_name.keys()) | set(pvp_by_name.keys())
        
        # First pass: create combined champions with pve/pvp ranks
        temp_champions = {}
        for name_key in all_names:
            bgs_champ = bgs_by_name.get(name_key)
            pve_champ = pve_by_name.get(name_key)
            pvp_champ = pvp_by_name.get(name_key)
            
            # Use the cleanest name available
            name = bgs_champ.name if bgs_champ else (pve_champ.name if pve_champ else pvp_champ.name)
            
            # Get PvE and PvP tiers
            pve_tier = pve_champ.pve_tier if pve_champ else None
            pvp_tier = pvp_champ.pvp_tier if pvp_champ else None
            
            # Get PvE and PvP ranks
            pve_rank = pve_champ.pve_rank if pve_champ else None
            pvp_rank = pvp_champ.pvp_rank if pvp_champ else None
            
            # Calculate overall tier
            overall_tier = calculate_overall_tier(pve_tier, pvp_tier)
            
            # Get BGS rating and type if available
            rating = bgs_champ.rating if bgs_champ else None
            bg_type = bgs_champ.battlegrounds_type if bgs_champ else None
            category = bgs_champ.category if bgs_champ else (pve_champ.category if pve_champ else pvp_champ.category)
            
            # Combine symbols
            symbols = set()
            if bgs_champ and bgs_champ.symbols:
                symbols.update(bgs_champ.symbols)
            if pve_champ and pve_champ.symbols:
                symbols.update(pve_champ.symbols)
            if pvp_champ and pvp_champ.symbols:
                symbols.update(pvp_champ.symbols)
            
            temp_champions[name_key] = {
                'name': name,
                'pve_tier': pve_tier,
                'pvp_tier': pvp_tier,
                'overall_tier': overall_tier,
                'pve_rank': pve_rank,
                'pvp_rank': pvp_rank,
                'rating': rating,
                'battlegrounds_type': bg_type,
                'category': category,
                'symbols': list(symbols)
            }
        
        # Second pass: calculate overall rank by class with PvP priority
        # Group by class
        by_class = {}
        for name_key, data in temp_champions.items():
            cls = data['category']
            if cls not in by_class:
                by_class[cls] = []
            by_class[cls].append((name_key, data))
        
        # Rank within each class
        for cls, champions in by_class.items():
            # Sort by combined score (lower is better), PvP rank as tiebreaker
            def rank_score(item):
                name_key, data = item
                pve = data['pve_rank'] or 999
                pvp = data['pvp_rank'] or 999
                # Combined score: average of both ranks
                return (pve + pvp, pvp)  # PvP priority in ties
            
            sorted_champs = sorted(champions, key=rank_score)
            
            for overall_rank, (name_key, data) in enumerate(sorted_champs, 1):
                data['overall_rank'] = overall_rank
        
        # Final pass: create Champion objects
        for name_key, data in temp_champions.items():
            combined = Champion(
                name=data['name'],
                tier=data['overall_tier'],
                category=data['category'],
                rating=data['rating'],
                symbols=data['symbols'],
                source="combined",
                pve_tier=data['pve_tier'],
                pvp_tier=data['pvp_tier'],
                overall_tier=data['overall_tier'],
                pve_rank=data['pve_rank'],
                pvp_rank=data['pvp_rank'],
                overall_rank=data['overall_rank'],
                battlegrounds_type=data['battlegrounds_type']
            )
            
            self.combined_champions[name_key] = combined
    
    def _normalize_name(self, name: str) -> str:
        """Normalize champion name for matching - removes emojis, spaces, punctuation"""
        # First clean the name to remove emojis
        name = self._clean_champion_name(name)
        
        # Remove common prefixes
        name = name.strip()
        if name.lower().startswith('the '):
            name = name[4:]
        
        # Normalize: remove spaces, hyphens, parentheses, periods, apostrophes
        normalized = re.sub(r"[\s\-\(\)\.\']", '', name.lower().strip())
        
        # Look up in alias mapping
        return CHAMPION_ALIASES.get(normalized, normalized)
    
    def _get_tier_from_rating(self, rating) -> str:
        """Convert numerical rating to tier based on value"""
        if rating is None:
            return "Information"
        elif rating >= 10:
            return "Above All"
        elif rating >= 9:
            return "Scorching"
        elif rating >= 8:
            return "Super Hot"
        elif rating >= 7:
            return "Hot"
        elif rating >= 6:
            return "Mild"
        else:
            return "Information"
    
    def get_champion_by_name(self, name: str) -> List[Champion]:
        """Get champion information by name (case-insensitive, supports aliases)"""
        results = []
        
        # First, try to find by normalized name (with alias support)
        normalized_search = self._normalize_name(name)
        if normalized_search in self.combined_champions:
            return [self.combined_champions[normalized_search]]
        
        # Fall back to substring matching in champion names
        name_lower = name.lower().strip()
        for champ_key, champion in self.combined_champions.items():
            if name_lower in champion.name.lower():
                results.append(champion)
        
        return results
    
    def get_top_champions_by_tier(self, source: str = 'combined', limit: int = 10) -> List[Champion]:
        """Get top champions by tier from a specific source"""
        if source == 'combined':
            champions = list(self.combined_champions.values())
        elif source in self.champions_data:
            champions = self.champions_data[source]
        else:
            return []
        
        def sort_key(champ):
            tier_rank = TIER_SCORES.get(champ.tier, 0)
            rating = champ.rating if champ.rating else 0
            rank = champ.overall_rank if champ.overall_rank else 999
            return (tier_rank, -rank, rating)
        
        sorted_champions = sorted(champions, key=sort_key, reverse=True)
        return sorted_champions[:limit]
    
    def refresh_data(self):
        """Refresh data from public Google Sheets"""
        logging.info("Refreshing data from public Google Sheets...")
        self.fetch_champions_from_spreadsheets()
        logging.info("Data refresh completed")
