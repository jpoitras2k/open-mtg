import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cards import Instant, Artifact, Enchantment, Planeswalker

class TestNewCardTypes(unittest.TestCase):
    def test_instant_instantiation(self):
        card = Instant("Lightning Bolt", ["Instant"], {'Red': 1})
        self.assertEqual(card.name, "Lightning Bolt")
        self.assertTrue(card.is_instant)

    def test_artifact_instantiation(self):
        card = Artifact("Sol Ring", ["Artifact"], {'Generic': 1})
        self.assertEqual(card.name, "Sol Ring")
        self.assertEqual(card.mc['Generic'], 1)

    def test_enchantment_instantiation(self):
        card = Enchantment("Rhystic Study", ["Enchantment"], {'Generic': 2, 'Blue': 1})
        self.assertEqual(card.name, "Rhystic Study")

    def test_planeswalker_instantiation(self):
        card = Planeswalker("Jace", ["Planeswalker"], {'Blue': 2}, loyalty=3)
        self.assertEqual(card.name, "Jace")
        self.assertEqual(card.loyalty, 3)

if __name__ == '__main__':
    unittest.main()
