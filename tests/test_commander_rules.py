import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from player import Player
from deck import get_bear_wars_deck

class TestCommanderRules(unittest.TestCase):
    def setUp(self):
        # Create 4 players with bear decks
        self.players = [Player(get_bear_wars_deck()) for _ in range(4)]
        self.game = Game(self.players)

    def test_initialization(self):
        # Verify 4 players
        self.assertEqual(len(self.game.players), 4)
        # Verify 40 life
        for player in self.game.players:
            self.assertEqual(player.life, 40)
            self.assertEqual(player.command_zone, [])
            self.assertEqual(player.commander_cast_count, 0)

    def test_turn_cycle(self):
        # Force active player to be index 0 for deterministic testing
        self.game.active_player = self.game.players[0]
        # Ensure indices are set (Game.__init__ does this, but good to be sure)
        for i, p in enumerate(self.game.players):
            p.index = i

        # Current active: 0
        self.assertEqual(self.game.active_player.index, 0)

        # Start new turn -> Should be 1
        self.game.start_new_turn()
        self.assertEqual(self.game.active_player.index, 1)

        # Start new turn -> Should be 2
        self.game.start_new_turn()
        self.assertEqual(self.game.active_player.index, 2)

        # Start new turn -> Should be 3
        self.game.start_new_turn()
        self.assertEqual(self.game.active_player.index, 3)

        # Start new turn -> Should be 0
        self.game.start_new_turn()
        self.assertEqual(self.game.active_player.index, 0)

    def test_commander_tax(self):
        import cards
        player = self.players[0]
        # Create a commander: 1 Green, 1 Generic
        commander = cards.Creature("Commander Bear", "Bear", {'Green': 1, 'Generic': 1}, 2, 2)
        player.command_zone.append(commander)
        
        # Initial state
        self.assertEqual(player.commander_cast_count, 0)
        
        # Give mana for base cost (1G, 1Gen)
        player.manapool = {'Green': 1, 'Generic': 1}
        # Check afford
        self.assertTrue(player.can_afford_card(commander))
        
        # Play it
        # get_playable_cards should return it as ('command_zone', 0)
        playable = player.get_playable_cards(self.game)
        self.assertIn(('command_zone', 0), playable)
        
        # Play
        player.play_card(('command_zone', 0), self.game, verbose=False)
        
        # Check cast count
        self.assertEqual(player.commander_cast_count, 1)
        # Check mana spent (should be empty)
        self.assertEqual(player.manapool['Green'], 0)
        # Generic might be negative if debt logic? 
        # subtract_color_mana: self.manapool[key] -= mana[key]. Returns generic debt.
        # 1 Green - 1 Green = 0.
        # Generic 1. manapool has 1 Generic?
        # player.manapool has 'Generic' key?
        # player.manapool initialized as {'White': 0, ... 'Colorless': 0}. No 'Generic'.
        # Usually 'Generic' cost is paid by any mana.
        # subtract_color_mana returns the generic amount needed.
        # Then `pay_generic_debt` is called?
        # `play_card` calls `subtract_color_mana` which returns `generic_debt`.
        # It does NOT automatically pay generic debt from pool.
        # So `player.generic_debt` should be 1.
        # But I gave `{'Generic': 1}` in manapool.
        # `subtract_color_mana` iterates `self.manapool`.
        # If I put 'Generic' in manapool, it might not be used by `subtract_color_mana` unless I modify it.
        # `player.py`: `self.manapool = {'White': 0, ...}`.
        # `add_mana` updates it.
        # `subtract_color_mana`: `for key in self.manapool: self.manapool[key] -= mana[key]`.
        # If `mana` (cost) has 'Generic', and `self.manapool` doesn't have 'Generic' key (it has 'Colorless'?), it won't subtract 'Generic'.
        # `subtract_color_mana` returns `mana['Generic']`.
        
        # So for this test, I should give specific mana.
        # Cost: 1 Green, 1 Generic.
        # Give: 2 Green.
        player.manapool = {'Green': 2, 'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Colorless': 0}
        player.generic_debt = 0
        
        # Play
        # Reset command zone
        player.command_zone.append(commander)
        player.commander_cast_count = 0
        
        player.play_card(('command_zone', 0), self.game, verbose=False)
        
        # 1 Green spent for Green cost. 1 Green remaining.
        self.assertEqual(player.manapool['Green'], 1)
        # Generic debt should be 1.
        self.assertEqual(player.generic_debt, 1)
        
        # Pay debt
        player.pay_generic_debt('Green')
        self.assertEqual(player.manapool['Green'], 0)
        self.assertEqual(player.generic_debt, 0)
        
        # Now put back to command zone
        player.command_zone.append(commander)
        
        # Try to cast again. Cost: 1 Green, 1 Generic + 2 Tax = 1G, 3Gen.
        # Give 2 Green (Base cost). Should fail.
        player.manapool = {'Green': 2, 'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Colorless': 0}
        self.assertFalse(player.can_afford_card(commander))
        
        # Give 4 Green (Enough).
        player.manapool = {'Green': 4, 'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Colorless': 0}
        self.assertTrue(player.can_afford_card(commander))
        
        # Play
        player.play_card(('command_zone', 0), self.game, verbose=False)
        self.assertEqual(player.commander_cast_count, 2)
        # 1 Green spent for Green cost. 3 Green remaining.
        self.assertEqual(player.manapool['Green'], 3)
        # Generic debt: 1 + 2 = 3.
        self.assertEqual(player.generic_debt, 3)

    def test_simultaneous_loss(self):
        # 4 players alive
        self.assertFalse(self.game.is_over())
        
        # Kill player 1
        self.game.players[1].has_lost = True
        self.assertFalse(self.game.is_over())
        
        # Kill player 2
        self.game.players[2].has_lost = True
        self.assertFalse(self.game.is_over())
        
        # Kill player 3
        self.game.players[3].has_lost = True
        # Now only player 0 is alive. Game should be over.
        self.assertTrue(self.game.is_over())
        
        # Test turn skipping
        # Active is 0. Next should be 1, but 1 is dead. 2 is dead. 3 is dead.
        # Should loop back to 0? Or stay 0?
        # start_new_turn logic: find next alive.
        self.game.active_player = self.game.players[0]
        self.game.start_new_turn()
        self.assertEqual(self.game.active_player.index, 0)
        
        # Revive player 2
        self.game.players[2].has_lost = False
        self.game.active_player = self.game.players[0]
        self.game.start_new_turn()
        # Should skip 1 and go to 2
        self.assertEqual(self.game.active_player.index, 2)

if __name__ == '__main__':
    unittest.main()
