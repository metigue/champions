import unittest
from data_manager import DataManager
from champion_model import Champion

class TestDataManager(unittest.TestCase):
    def test_champion_creation(self):
        """Test that we can create a Champion object"""
        champion = Champion(
            name="Wolverine",
            tier="S-Tier",
            category="Mutant",
            rating=9.5,
            symbols=["⚔️", "🛡️"],
            source="test"
        )
        
        self.assertEqual(champion.name, "Wolverine")
        self.assertEqual(champion.tier, "S-Tier")
        self.assertEqual(champion.category, "Mutant")
        self.assertEqual(champion.rating, 9.5)
        self.assertIn("⚔️", champion.symbols)
        self.assertEqual(champion.source, "test")

if __name__ == '__main__':
    unittest.main()