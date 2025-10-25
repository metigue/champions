# Test the final database with the new system
from data_manager_json import DataManager

# Initialize the data manager
dm = DataManager()

print("Final Database Results:")
print(f"Total champions loaded: {sum(len(champs) for champs in dm.champions_data.values())}")
print(f"Vega (BGs) champions: {len(dm.champions_data.get('vega', []))}")
print(f"Illuminati (Ranking) champions: {len(dm.champions_data.get('illuminati', []))}")

# Test specific champion lookups
test_champions = ['nico minoru', 'venom', 'baron zemo', 'tigra']

for test_name in test_champions:
    print(f"\n{test_name.title()}:")
    matches = dm.get_champion_by_name(test_name)
    if matches:
        for match in matches:
            print(f"  Name: {match.name}")
            print(f"  Tier: {match.tier}")
            print(f"  Category: {match.category}")
            print(f"  Rating: {match.rating}")
            print(f"  Source: {match.source}")
            print(f"  Symbols: {match.symbols}")
    else:
        print("  Not found")