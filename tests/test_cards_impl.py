import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cards_impl import SolRing, ArcaneSignet
from player import Player

class TestCardsImpl(unittest.TestCase):
    def setUp(self):
        # Mock deck and player
        self.deck = [] 
        self.player = Player(self.deck)
        self.player.manapool = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0, 'Generic': 0}

    def test_sol_ring(self):
        sol_ring = SolRing()
        sol_ring.owner = self.player
        
        # Initial state
        self.assertEqual(self.player.manapool['Colorless'], 0)
        
        # Use ability
        sol_ring.use_tapped_ability(0)
        
        # Check mana
        self.assertEqual(self.player.manapool['Colorless'], 2)
        self.assertTrue(sol_ring.is_tapped)

    def test_arcane_signet_default(self):
        signet = ArcaneSignet()
        signet.owner = self.player
        # No identity set, defaults to Colorless
        
        signet.use_tapped_ability(0)
        self.assertEqual(self.player.manapool['Colorless'], 1)

    def test_arcane_signet_identity(self):
        signet = ArcaneSignet()
        signet.owner = self.player
        self.player.commander_identity = ['Blue', 'Red']
        
        # Should pick first color (Blue) based on current impl
        signet.use_tapped_ability(0)
        self.assertEqual(self.player.manapool['Blue'], 1)

    def test_command_tower(self):
        from cards_impl import CommandTower
        tower = CommandTower()
        tower.owner = self.player
        self.player.commander_identity = ['Red', 'Green']
        
        # Should pick first color (Red)
        tower.use_tapped_ability(0)
        self.assertEqual(self.player.manapool['Red'], 1)

    def test_cultivate(self):
        from cards_impl import Cultivate
        from cards import Land
        
        # Setup deck with basics
        forest = Land("Forest", ["Basic Land", "Land"], "Forest", [])
        mountain = Land("Mountain", ["Basic Land", "Land"], "Mountain", [])
        other = Land("NonBasic", ["Land"], "Special", [])
        
        self.player.deck = [other, forest, mountain] # Stack: Top is Mountain (pop order)
        # Actually pop takes from end. 
        # deck = [other, forest, mountain]. pop() -> mountain.
        
        cultivate = Cultivate()
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = []
        
        game = MockGame()
        
        # Play cultivate
        cultivate.play(self.player, game)
        
        # Expectation:
        # Found 2 basics: Mountain, Forest.
        # Land 1 (Mountain) -> Battlefield Tapped.
        # Land 2 (Forest) -> Hand.
        # Deck should have 'other' left (and shuffled, but size is 1).
        
        self.assertEqual(len(game.battlefield), 1)
        self.assertEqual(game.battlefield[0].name, "Mountain")
        self.assertTrue(game.battlefield[0].is_tapped)
        
        self.assertEqual(len(self.player.hand), 1)
        self.assertEqual(self.player.hand[0].name, "Forest")
        
        self.assertEqual(len(self.player.deck), 1)
        self.assertEqual(self.player.deck[0].name, "NonBasic")

    def test_swords_to_plowshares(self):
        from cards_impl import SwordsToPlowshares
        from cards import Creature
        
        # Setup opponent and creature
        opponent = Player([])
        opponent.life = 40
        creature = Creature("Big Guy", ["Creature"], {'Green': 5}, 5, 5)
        creature.owner = opponent
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = [creature]
        
        game = MockGame()
        
        stp = SwordsToPlowshares()
        stp.play(self.player, game)
        
        # Expectation:
        # Creature removed from battlefield
        # Opponent life +5 (45)
        
        self.assertEqual(len(game.battlefield), 0)
        self.assertEqual(opponent.life, 45)

    def test_cyclonic_rift(self):
        from cards_impl import CyclonicRift
        from cards import Creature, Land
        
        # Setup opponent and permanents
        opponent = Player([])
        creature = Creature("Bouncer", ["Creature"], {'Blue': 2}, 2, 2)
        creature.owner = opponent
        land = Land("Island", ["Land"], "Island", [])
        land.owner = opponent
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = [creature, land]
        
        game = MockGame()
        
        rift = CyclonicRift()
        rift.play(self.player, game)
        
        # Expectation:
        # Creature returned to hand
        # Land stays (Nonland clause)
        
        self.assertEqual(len(game.battlefield), 1)
        self.assertEqual(game.battlefield[0].name, "Island")
        
        self.assertEqual(len(opponent.hand), 1)
        self.assertEqual(opponent.hand[0].name, "Bouncer")

    def test_rhystic_study(self):
        from cards_impl import RhysticStudy
        
        study = RhysticStudy()
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = []
        
        game = MockGame()
        
        study.play(self.player, game)
        
        self.assertEqual(len(game.battlefield), 1)
        self.assertEqual(game.battlefield[0].name, "Rhystic Study")

    def test_smothering_tithe(self):
        from cards_impl import SmotheringTithe
        
        tithe = SmotheringTithe()
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = []
        
        game = MockGame()
        
        tithe.play(self.player, game)
        
        self.assertEqual(len(game.battlefield), 1)
        self.assertEqual(game.battlefield[0].name, "Smothering Tithe")

    def test_dockside_extortionist(self):
        from cards_impl import DocksideExtortionist
        from cards import Artifact, Enchantment
        
        dockside = DocksideExtortionist()
        
        # Setup opponents with artifacts/enchantments
        opponent = Player([])
        art = Artifact("Rock", ["Artifact"], {'Generic': 0})
        art.owner = opponent
        ench = Enchantment("Rule", ["Enchantment"], {'Generic': 0})
        ench.owner = opponent
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = [art, ench]
        
        game = MockGame()
        
        dockside.play(self.player, game)
        
        # Expectation:
        # Dockside on battlefield (1)
        # 2 Treasures created (2)
        # Total battlefield items for player: 3 (Dockside + 2 Treasures)
        # Total items in game: 2 (opp) + 3 (player) = 5
        
        player_permanents = [p for p in game.battlefield if p.owner == self.player]
        self.assertEqual(len(player_permanents), 3)
        self.assertEqual(player_permanents[0].name, "Dockside Extortionist")
        self.assertEqual(player_permanents[1].name, "Treasure")
        self.assertEqual(player_permanents[2].name, "Treasure")

    def test_demonic_tutor(self):
        from cards_impl import DemonicTutor
        from cards import Card
        
        tutor = DemonicTutor()
        
        # Setup deck
        card1 = Card()
        card1.name = "Card 1"
        card2 = Card()
        card2.name = "Card 2"
        self.player.deck = [card1, card2]
        
        # Mock game
        class MockGame:
            def __init__(self):
                self.battlefield = []
        
        game = MockGame()
        
        tutor.play(self.player, game)
        
        # Expectation:
        # Card 1 (top of deck list logic in impl) moved to hand.
        # Deck has 1 card left.
        
        self.assertEqual(len(self.player.hand), 1)
        self.assertEqual(self.player.hand[0].name, "Card 1")
        self.assertEqual(len(self.player.deck), 1)

if __name__ == '__main__':
    unittest.main()
