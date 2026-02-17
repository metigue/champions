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
    battlegrounds_type: Optional[str] = None  # Battlegrounds type (e.g., Attacker, Defender, Dual Threat)
    # New fields for PvE/PvP rankings
    pve_tier: Optional[str] = None
    pvp_tier: Optional[str] = None
    overall_tier: Optional[str] = None
    pve_rank: Optional[int] = None  # Rank within class for PvE
    pvp_rank: Optional[int] = None  # Rank within class for PvP
    overall_rank: Optional[int] = None  # Combined rank

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = []

# Tier hierarchy for scoring (higher = better)
TIER_SCORES = {
    "Above All": 6,
    "Scorching": 5,
    "Super Hot": 4,
    "Hot": 3,
    "Mild": 2,
    "Not Endgame Relevant": 1,
    "Not Endgame Relevant ": 1,  # Handle trailing space
    "Information": 0
}

def calculate_overall_tier(pve_tier: Optional[str], pvp_tier: Optional[str]) -> str:
    """Calculate overall tier from PvE and PvP tiers"""
    if not pve_tier and not pvp_tier:
        return "Information"
    
    pve_score = TIER_SCORES.get(pve_tier, 0) if pve_tier else 0
    pvp_score = TIER_SCORES.get(pvp_tier, 0) if pvp_tier else 0
    
    # Average the scores
    if pve_tier and pvp_tier:
        avg_score = (pve_score + pvp_score) / 2
    elif pve_tier:
        avg_score = pve_score
    else:
        avg_score = pvp_score
    
    # Map back to tier
    if avg_score >= 5.5:
        return "Above All"
    elif avg_score >= 4.5:
        return "Scorching"
    elif avg_score >= 3.5:
        return "Super Hot"
    elif avg_score >= 2.5:
        return "Hot"
    elif avg_score >= 1.5:
        return "Mild"
    elif avg_score >= 0.5:
        return "Not Endgame Relevant"
    else:
        return "Information"

@dataclass
class ChampionRecommendation:
    """Data class to represent a recommendation"""
    champion: Champion
    reason: str
    priority: int  # 1 = highest priority
