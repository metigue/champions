from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Champion:
    """Data class to represent a champion with all relevant information"""
    name: str
    tier: str
    category: str
    rating: Optional[float] = None
    symbols: List[str] = None
    special_notes: str = ""
    source: str = ""
    battlegrounds_type: Optional[str] = None  # Added battlegrounds type (e.g., Attacker, Defender, Dual Threat)
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = []

@dataclass
class ChampionRecommendation:
    """Data class to represent a recommendation"""
    champion: Champion
    reason: str
    priority: int  # 1 = highest priority