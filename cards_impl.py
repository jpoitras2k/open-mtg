from cards import Artifact, Land, Sorcery, Instant, Enchantment, Creature
import random

class SolRing(Artifact):
    def __init__(self):
        super(SolRing, self).__init__("Sol Ring", ["Artifact"], {'Generic': 1})
        self.tapped_abilities = [self.add_mana]

    def add_mana(self, card):
        # owner is set in Card.play
        if card.owner:
            card.owner.manapool['Colorless'] += 2

class ArcaneSignet(Artifact):
    def __init__(self):
        super(ArcaneSignet, self).__init__("Arcane Signet", ["Artifact"], {'Generic': 2})
        self.tapped_abilities = [self.add_mana]

    def add_mana(self, card):
        if card.owner:
            # For now, just add one mana of a chosen color (simplified)
            # In a real game, we'd need to prompt the user for color choice based on identity
            # This requires a UI or input mechanism not fully defined yet.
            # We will assume the AI/User picks the first available color in identity or just 'Generic' for now if identity is missing.
            
            # Placeholder logic: Add 1 mana of the first color in identity, or Colorless if none.
            identity = getattr(card.owner, 'commander_identity', ['Colorless'])
            if not identity:
                identity = ['Colorless']
            
            # Ideally we return a choice, but for tapped_abilities currently it seems to just execute.
            # We might need to change how tapped_abilities work to support choices.
            # For this iteration, we'll just add the first color found.
            color = identity[0]
            card.owner.manapool[color] = card.owner.manapool.get(color, 0) + 1

class CommandTower(Land):
    def __init__(self):
        # Command Tower has no subtypes usually, but we can pass empty list
        # It has a tapped ability
        super(CommandTower, self).__init__("Command Tower", ["Land"], [], [self.add_mana])

    def add_mana(self, card):
        if card.owner:
            identity = getattr(card.owner, 'commander_identity', ['Colorless'])
            if not identity:
                identity = ['Colorless']
            # Simplified: Add first color in identity
            color = identity[0]
            card.owner.manapool[color] = card.owner.manapool.get(color, 0) + 1

class Cultivate(Sorcery):
    def __init__(self):
        super(Cultivate, self).__init__("Cultivate", ["Sorcery"], {'Generic': 2, 'Green': 1})

    def play(self, owner, game, verbose=False):
        super(Cultivate, self).play(owner, game, verbose)
        
        # Search logic
        # Find up to 2 basic lands
        found_lands_indices = []
        for i, card in enumerate(owner.deck):
            if isinstance(card, Land) and "Basic Land" in card.types:
                found_lands_indices.append(i)
                if len(found_lands_indices) >= 2:
                    break
        
        # Process found lands (reverse order to pop correctly)
        # Note: In real game, user chooses. Here we take first 2 found.
        found_lands_indices.sort(reverse=True)
        
        lands_to_process = []
        for index in found_lands_indices:
            lands_to_process.append(owner.deck.pop(index))
            
        if len(lands_to_process) > 0:
            # Put one onto battlefield tapped
            land1 = lands_to_process[0]
            land1.owner = owner # Ensure owner is set
            game.battlefield.append(land1)
            land1.is_tapped = True
            if verbose:
                print(f"    Cultivate: Put {land1.name} onto battlefield tapped.")
                
        if len(lands_to_process) > 1:
            # Put second into hand
            land2 = lands_to_process[1]
            owner.hand.append(land2)
            if verbose:
                print(f"    Cultivate: Put {land2.name} into hand.")
                
        owner.shuffle_deck()

class SwordsToPlowshares(Instant):
    def __init__(self):
        super(SwordsToPlowshares, self).__init__("Swords to Plowshares", ["Instant"], {'White': 1})

    def play(self, owner, game, verbose=False):
        super(SwordsToPlowshares, self).play(owner, game, verbose)
        
        # Simplified Targeting: Target first creature of an opponent
        # In real game, need target selection logic
        targets = []
        for permanent in game.battlefield:
            if hasattr(permanent, 'power') and permanent.owner != owner: # Is creature and opponent's
                targets.append(permanent)
        
        if targets:
            target = targets[0] # Just pick first for now
            if verbose:
                print(f"    Swords to Plowshares: Exiling {target.name}. Controller gains {target.power} life.")
            
            # Exile
            game.battlefield.remove(target)
            # Gain life
            target.owner.life += target.power

class CyclonicRift(Instant):
    def __init__(self):
        super(CyclonicRift, self).__init__("Cyclonic Rift", ["Instant"], {'Generic': 1, 'Blue': 1})
        # Overload not implemented yet as a cost choice

    def play(self, owner, game, verbose=False):
        super(CyclonicRift, self).play(owner, game, verbose)
        
        # Base effect: Return target nonland permanent to hand
        # Simplified Targeting: Target first nonland permanent of an opponent
        targets = []
        for permanent in game.battlefield:
            if not isinstance(permanent, Land) and permanent.owner != owner:
                targets.append(permanent)
        
        if targets:
            target = targets[0]
            if verbose:
                print(f"    Cyclonic Rift: Returning {target.name} to hand.")
            
            game.battlefield.remove(target)
            target.owner.hand.append(target)

class RhysticStudy(Enchantment):
    def __init__(self):
        super(RhysticStudy, self).__init__("Rhystic Study", ["Enchantment"], {'Generic': 2, 'Blue': 1})

    def play(self, owner, game, verbose=False):
        super(RhysticStudy, self).play(owner, game, verbose)
        # In a real implementation, this would register a trigger listener
        # For now, we just place it on the battlefield.
        # The trigger logic would need to be in Game.play_card or similar.
        if verbose:
            print("    Rhystic Study: (Trigger logic not fully implemented)")

class SmotheringTithe(Enchantment):
    def __init__(self):
        super(SmotheringTithe, self).__init__("Smothering Tithe", ["Enchantment"], {'Generic': 3, 'White': 1})

    def play(self, owner, game, verbose=False):
        super(SmotheringTithe, self).play(owner, game, verbose)
        # Similar to Rhystic Study, needs trigger listener on draw
        if verbose:
            print("    Smothering Tithe: (Trigger logic not fully implemented)")

class DocksideExtortionist(Creature):
    def __init__(self):
        super(DocksideExtortionist, self).__init__("Dockside Extortionist", ["Creature", "Goblin", "Pirate"], {'Generic': 1, 'Red': 1}, 1, 2)

    def play(self, owner, game, verbose=False):
        super(DocksideExtortionist, self).play(owner, game, verbose)
        
        # ETB: Create X Treasures where X is number of artifacts/enchantments opponents control
        count = 0
        for permanent in game.battlefield:
            if permanent.owner != owner:
                if isinstance(permanent, Artifact) or isinstance(permanent, Enchantment):
                    count += 1
        
        if verbose:
            print(f"    Dockside Extortionist: Creating {count} Treasures.")
            
        # Create Treasures (Simplified: just Artifacts named "Treasure")
        for _ in range(count):
            treasure = Artifact("Treasure", ["Artifact", "Token"], {'Generic': 0}, [lambda c: c.owner.add_mana({'Generic': 1})]) # Simplified mana ability
            treasure.owner = owner
            game.battlefield.append(treasure)

class DemonicTutor(Sorcery):
    def __init__(self):
        super(DemonicTutor, self).__init__("Demonic Tutor", ["Sorcery"], {'Generic': 1, 'Black': 1})

    def play(self, owner, game, verbose=False):
        super(DemonicTutor, self).play(owner, game, verbose)
        
        # Search library for any card
        if len(owner.deck) > 0:
            # Simplified: Just take the first card (or random)
            # In real game, user chooses.
            # For simulation/AI, we might pick best card.
            # Here, we just pick the last card (top of deck in pop order logic, though usually search implies choice)
            # Let's just pick the first card in the list for simplicity of test
            card = owner.deck.pop(0)
            owner.hand.append(card)
            if verbose:
                print(f"    Demonic Tutor: Put {card.name} into hand.")
            
            owner.shuffle_deck()
