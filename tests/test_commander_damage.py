import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from player import Player
from cards import Creature, Card

class TestCommanderDamage(unittest.TestCase):
    def setUp(self):
        # Setup 4 players
        # Setup 4 players with cards in deck to prevent drawing from empty deck
        self.players = [Player([Card() for _ in range(20)]) for _ in range(4)]
        self.game = Game(self.players)
        self.game.start_game()

    def test_commander_damage_accumulation(self):
        attacker = self.players[0]
        victim = self.players[1]
        
        # Setup Commander
        commander = Creature("Commander 1", ["Creature"], {'Generic': 0}, 5, 5)
        commander.is_commander = True
        commander.owner = attacker
        self.game.battlefield.append(commander)
        
        # Setup Game State for Combat
        self.game.active_player = attacker
        self.game.nonactive_player = victim
        
        # Deal Damage
        commander.deal_combat_damage_to_opponent(self.game)
        
        # Check Tracker
        self.assertIn(commander, self.game.commander_damage)
        self.assertEqual(self.game.commander_damage[commander][victim.index], 5)
        
        # Deal more damage
        commander.deal_combat_damage_to_opponent(self.game)
        self.assertEqual(self.game.commander_damage[commander][victim.index], 10)

    def test_non_commander_damage(self):
        attacker = self.players[0]
        victim = self.players[1]
        
        # Setup Regular Creature
        creature = Creature("Minion", ["Creature"], {'Generic': 0}, 5, 5)
        creature.is_commander = False
        creature.owner = attacker
        self.game.battlefield.append(creature)
        
        # Setup Game State
        self.game.active_player = attacker
        self.game.nonactive_player = victim
        
        # Deal Damage
        creature.deal_combat_damage_to_opponent(self.game)
        
        # Check Tracker (Should be empty or not contain this creature)
        self.assertNotIn(creature, self.game.commander_damage)

    def test_commander_damage_loss_condition(self):
        attacker = self.players[0]
        victim = self.players[1]
        
        # Setup Commander
        commander = Creature("Commander Lethal", ["Creature"], {'Generic': 0}, 21, 21)
        commander.is_commander = True
        commander.owner = attacker
        self.game.battlefield.append(commander)
        
        # Setup Game State
        self.game.active_player = attacker
        self.game.nonactive_player = victim
        
        # Deal 21 Damage
        commander.deal_combat_damage_to_opponent(self.game)
        
        # Verify Damage
        self.assertEqual(self.game.commander_damage[commander][victim.index], 21)
        
        # Check State Based Actions
        self.game.check_state_based_actions()
        
        # Verify Loss
        self.assertTrue(victim.has_lost)

    def test_separate_commander_tracking(self):
        attacker1 = self.players[0]
        attacker2 = self.players[2]
        victim = self.players[1]
        
        # Commander 1
        cmd1 = Creature("Cmd1", ["Creature"], {'Generic': 0}, 10, 10)
        cmd1.is_commander = True
        cmd1.owner = attacker1
        
        # Commander 2
        cmd2 = Creature("Cmd2", ["Creature"], {'Generic': 0}, 15, 15)
        cmd2.is_commander = True
        cmd2.owner = attacker2
        
        # Deal Damage from Cmd1
        self.game.nonactive_player = victim
        cmd1.deal_combat_damage_to_opponent(self.game)
        
        # Deal Damage from Cmd2
        cmd2.deal_combat_damage_to_opponent(self.game)
        
        # Verify separate tracking
        self.assertEqual(self.game.commander_damage[cmd1][victim.index], 10)
        self.assertEqual(self.game.commander_damage[cmd2][victim.index], 15)
        
        # Verify victim hasn't lost (neither is >= 21)
        self.game.check_state_based_actions()
        self.assertFalse(victim.has_lost)

if __name__ == '__main__':
    unittest.main()
