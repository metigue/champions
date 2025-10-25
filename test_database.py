import json

# Load the database
with open('champions_database.json', 'r', encoding='utf-8') as f:
    champions_data = json.load(f)

print("Champions Database Analysis:")
print(f"Total champions in database: {len(champions_data)}")

# Look for specific champions
test_champions = ['nico minoru', 'venom', 'baron zemo', 'tigra', 'spider-man', 'enchantress', 'doctor doom']

for test_name in test_champions:
    if test_name in champions_data:
        data = champions_data[test_name]
        print(f"\n{test_name.title()}:")
        print(f"  Full Name: {data['name']}")
        print(f"  Class: {data['class']}")
        print(f"  Rank: {data['rank']}")
        print(f"  Tier: {data['tier']}")
        print(f"  Ranking: {data['ranking_display']}")
        print(f"  BG Rating: {data['battlegrounds_rating']}")
        print(f"  BG Type: {data['battlegrounds_type']}")
        print(f"  Has Relic Needed: {data['specific_relic_needed']}")
        print(f"  Early Prediction: {data['early_prediction']}")
        print(f"  Other Symbols: {data['other_symbols']}")
    else:
        print(f"\n{test_name.title()}: Not found in database")
        
        # Try to find similar names
        similar = [name for name in champions_data.keys() if test_name.split()[0].lower() in name.lower()]
        if similar:
            print(f"  Similar entries found: {similar[:3]}")  # First 3 similar