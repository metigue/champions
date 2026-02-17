from champion_model import Champion

# Test the emoji translation
test_champion = Champion(
    name="Nico Minoru",
    tier="Above All",
    category="Mystic #1",
    rating=9.5,
    symbols=['🌟', '🚀', '🎲'],
    source="illuminati"
)

# Test the emoji translation
symbols_meanings = {
    '🌟': 'Ranking depends on Awakening',
    '🚀': 'Top candidate for Ascension',
    '💎': 'Requires High Skill',
    '👾': 'Saga Champion: Fantastic Force',
    '🥂': 'Big Caution, Ranking May Change A Lot',
    '⛰️': 'Great in Everest Content',
    '⚔️': 'Defense potential uses',
    '🤺': 'Offense potential uses',
    '🎲': 'Early predictions/uncertain rankings',
    '💣': 'Effective in Recoil Metas',
    '🐣': 'Newness enhancing effectiveness',
    '7️⃣': '7 Star enhancing effectiveness',
    '6️⃣': '6 Star Lock Hurting Performance',
    '💬': 'Skilled use required',
    '💾': 'Specific Relic needed',
    '🎙️': 'Referenced in videos',
    '🛡️': 'Defense potential',
    '🎯': 'Offense potential',
    '🔥': 'Hot pick'
}

print(f"Champion: {test_champion.name}")
print(f"Tier: {test_champion.tier}")
print(f"Ranking: {test_champion.category}")
print(f"Rating: {test_champion.rating}/10")
print(f"Source: {test_champion.source}")

if test_champion.symbols:
    translated_notes = []
    for symbol in test_champion.symbols:
        if symbol in symbols_meanings:
            translated_notes.append(symbols_meanings[symbol])
        else:
            translated_notes.append(symbol)
    print(f"Special Notes: {', '.join(translated_notes)}")
else:
    print("Special Notes: No special notes")

# Test vega champion with battlegrounds rating
vega_champion = Champion(
    name="Venom",
    tier="Information",
    category="Cosmic #7",
    rating=7.0,
    symbols=['🌟', '💾'],
    source="vega"
)

print("\n--- Vega Champion ---")
print(f"Champion: {vega_champion.name}")
print(f"Tier: {vega_champion.tier}")
print(f"Ranking: {vega_champion.category}")
print(f"Battlegrounds: Attacker {vega_champion.rating}/10")
print(f"Source: {vega_champion.source}")

if vega_champion.symbols:
    translated_notes = []
    for symbol in vega_champion.symbols:
        if symbol in symbols_meanings:
            translated_notes.append(symbols_meanings[symbol])
        else:
            translated_notes.append(symbol)
    print(f"Special Notes: {', '.join(translated_notes)}")