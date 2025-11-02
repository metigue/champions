#!/usr/bin/env python3
"""
Test similarity ratios for champion names
"""

from difflib import SequenceMatcher

def test_similarity():
    """Test similarity between search terms and champion names"""
    search_term = "nico"
    
    # Test candidates
    candidates = ["nico minoru", "nimrod", "nico robin"]
    
    print(f"Searching for: '{search_term}'")
    print("\nSimilarity ratios:")
    
    for candidate in candidates:
        ratio = SequenceMatcher(None, search_term.lower(), candidate.lower()).ratio()
        print(f"  '{search_term}' vs '{candidate}': {ratio:.3f}")

if __name__ == "__main__":
    test_similarity()