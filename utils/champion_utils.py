def normalize_champion_name(name: str) -> str:
    """
    Normalize champion names for consistent matching
    - Remove extra spaces
    - Convert to lowercase
    - Handle common variations
    """
    # Remove extra whitespace and convert to lowercase
    normalized = ' '.join(name.lower().split())
    
    # Handle common name variations/abbreviations
    name_variations = {
        'dr. strange': 'doctor strange',
        'dr strange': 'doctor strange',
        'doctor strange': 'doctor strange',
        'ms. marvel': 'ms marvel',
        'captain marvel': 'captain marvel',
        'iron man': 'iron man',
        'hawkeye': 'hawk eye',
        'black panther': 'black panther',
        'spider-man': 'spider man',
        'spider man': 'spider man',
        'wolverine': 'wolverine',
        'deadpool': 'deadpool',
        'thor': 'thor',
        'hulk': 'hulk',
        'captain america': 'captain america',
        'black widow': 'black widow',
        'scarlet witch': 'scarlet witch',
        'vision': 'vision',
        'warmachine': 'war machine',
        'war machine': 'war machine',
    }
    
    return name_variations.get(normalized, normalized)


def fuzzy_match_champion(name: str, champion_list: list) -> str:
    """
    Perform fuzzy matching to find the closest champion name
    """
    name = normalize_champion_name(name)
    
    # Direct match first
    for champion in champion_list:
        if normalize_champion_name(champion.name) == name:
            return champion
    
    # Partial match
    for champion in champion_list:
        if name in normalize_champion_name(champion.name) or normalize_champion_name(champion.name) in name:
            return champion
    
    # Check for substrings in either direction
    for champion in champion_list:
        champion_normalized = normalize_champion_name(champion.name)
        if name in champion_normalized or champion_normalized in name:
            return champion
    
    return None