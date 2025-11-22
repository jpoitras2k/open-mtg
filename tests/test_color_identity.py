import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from player import Player
from cards import Card, Creature, Land

class TestColorIdentity(unittest.TestCase):
    def test_card_identity_mana_cost(self):
        # White Card
        c1 = Card()
        c1.mc = {'White': 1, 'Generic': 2}
        self.assertEqual(c1.color_identity, ['White'])
        
        # Multi-color Card
        c2 = Card()
        c2.mc = {'Blue': 1, 'Red': 1}
        self.assertEqual(set(c2.color_identity), {'Blue', 'Red'})
        
        # Colorless Card
        c3 = Card()
        c3.mc = {'Generic': 5}
        self.assertEqual(c3.color_identity, [])

    def test_card_identity_basic_lands(self):
        # Forest
        forest = Land("Forest", ["Land"], ["Basic", "Forest"], [])
        self.assertEqual(forest.color_identity, ['Green'])
        
        # Island
        island = Land("Island", ["Land"], ["Basic", "Island"], [])
        self.assertEqual(island.color_identity, ['Blue'])

    def test_deck_validation_valid(self):
        # Commander: Blue/Green
        commander = Creature("Simic Cmd", ["Creature"], {'Blue': 1, 'Green': 1}, 2, 2)
        commander.is_commander = True
        
        # Deck: Blue card, Green card, Colorless card
        c1 = Card()
        c1.mc = {'Blue': 1}
        c1.name = "Blue Card"
        
        c2 = Card()
        c2.mc = {'Green': 1}
        c2.name = "Green Card"
        
        c3 = Card()
        c3.mc = {'Generic': 1}
        c3.name = "Colorless Card"
        
        player = Player([c1, c2, c3])
        player.commanders = [commander]
        
        game = Game([player])
        # Should not raise exception
        game.validate_decks()

    def test_deck_validation_invalid(self):
        # Commander: Mono-Red
        commander = Creature("Red Cmd", ["Creature"], {'Red': 1}, 2, 2)
        commander.is_commander = True
        
        # Deck: Red card, Blue card (Invalid)
        c1 = Card()
        c1.mc = {'Red': 1}
        c1.name = "Red Card"
        
        c2 = Card()
        c2.mc = {'Blue': 1}
        c2.name = "Blue Card"
        
        player = Player([c1, c2])
        player.commanders = [commander]
        
        game = Game([player])
        
        with self.assertRaises(ValueError) as context:
            game.validate_decks()
        
        self.assertIn("Deck Validation Failed", str(context.exception))
        self.assertIn("Blue Card", str(context.exception))

if __name__ == '__main__':
    unittest.main()
