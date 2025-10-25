import json

def display_top_20_per_class():
    """Display the top 20 champions from each class"""
    
    # Load the database
    with open('champions_database.json', 'r', encoding='utf-8') as f:
        champions_data = json.load(f)
    
    print("Top 20 Champions by Class")
    print("=" * 50)
    
    # Group champions by class
    champions_by_class = {}
    for name_key, champion_data in champions_data.items():
        class_name = champion_data['class']
        if class_name not in champions_by_class:
            champions_by_class[class_name] = []
        champions_by_class[class_name].append(champion_data)
    
    # Sort each class by rank (ascending order - 1 is highest)
    for class_name in sorted(champions_by_class.keys()):
        champions = champions_by_class[class_name]
        # Sort by rank (ascending - 1 is best)
        sorted_champions = sorted(champions, key=lambda x: x['rank'])
        
        print(f"\n{class_name.upper()} CLASS (Top 20):")
        print("-" * 30)
        
        for i, champ in enumerate(sorted_champions[:20], 1):
            bg_info = f" ({champ['battlegrounds_type']} {champ['battlegrounds_rating']}/10)" if champ['battlegrounds_rating'] else ""
            tier_info = f" [{champ['tier']}]"
            print(f"{i:2d}. {champ['name']} - Rank #{champ['rank']}{bg_info}{tier_info}")
    
    # Also show some statistics
    print(f"\n\nDATABASE STATISTICS:")
    print("=" * 50)
    print(f"Total champions: {len(champions_data)}")
    
    total_with_bg = sum(1 for champ in champions_data.values() if champ['battlegrounds_rating'] is not None)
    print(f"Champions with Battlegrounds data: {total_with_bg}")
    
    bg_types = {}
    for champ in champions_data.values():
        bg_type = champ['battlegrounds_type']
        if bg_type:
            bg_types[bg_type] = bg_types.get(bg_type, 0) + 1
    
    print("Battlegrounds type distribution:")
    for bg_type, count in sorted(bg_types.items()):
        print(f"  {bg_type}: {count}")

if __name__ == "__main__":
    display_top_20_per_class()