import itertools


class Card:
    def __init__(self):
        self.mc = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0, 'Generic': 0}
        self.tapped_abilities = []
        self.deck_location_known = False
        self.owner = None
        self.is_tapped = False
        self.is_commander = False

    def play(self, owner, game, verbose=False):
        self.owner = owner

    @property
    def color_identity(self):
        identity = set()
        # 1. Check Mana Cost
        for color, amount in self.mc.items():
            if color in ['White', 'Blue', 'Black', 'Red', 'Green'] and amount > 0:
                identity.add(color)
        
        # 2. Check Basic Land Types (if applicable)
        if hasattr(self, 'subtypes'):
            if 'Plains' in self.subtypes: identity.add('White')
            if 'Island' in self.subtypes: identity.add('Blue')
            if 'Swamp' in self.subtypes: identity.add('Black')
            if 'Mountain' in self.subtypes: identity.add('Red')
            if 'Forest' in self.subtypes: identity.add('Green')
            
        return list(identity)

    def __repr__(self):
        return self.name


class Land(Card):
    def __init__(self, name, types, subtypes, tapped_abilities):
        super(Land, self).__init__()
        self.name = name
        self.types = types
        self.subtypes = subtypes
        self.tapped_abilities = tapped_abilities

    def play(self, owner, game, verbose=False):
        super(Land, self).play(owner, game, verbose)
        if verbose:
            print("    playing %s" % (self.name))

        game.battlefield.append(self)
        self.owner.can_play_land = False

    def use_tapped_ability(self, index):
        if not self.is_tapped:
            self.is_tapped = True
            self.tapped_abilities[index](self)

    def __str__(self):
        return self.name


class Sorcery(Card):
    def __init__(self, name, subtypes, mc):
        super(Sorcery, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.subtypes = subtypes

    def play(self, owner, game, verbose=False):
        super(Sorcery, self).play(owner, game)
        if verbose:
            print("    casting %s" % (self.name))
        owner.casting_spell = self.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Creature(Card):
    def __init__(self, name, subtypes, mc, power, toughness, cannot_block=False):
        super(Creature, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.base_power = power
        self.power = power
        self.base_toughness = toughness
        self.toughness = toughness
        self.subtypes = subtypes
        self.is_dead = False
        self.summoning_sick = True
        self.damage_taken = 0
        self.damage_to_assign = 0
        self.is_attacking = []
        self.is_blocked_by = []
        self.is_blocking = []
        self.damage_assignment_order = []
        self.damage_assignment = []
        # Consider adding a functional creature card instantiation argument that sets text automatically
        self.cannot_block = cannot_block

    def play(self, owner, game, verbose=False):
        super(Creature, self).play(owner, game)
        if verbose:
            print("    casting %s" % (self.name))
        game.battlefield.append(self)

    def take_damage(self, amount):
        self.damage_taken += amount
        if self.damage_taken >= self.toughness:
            self.is_dead = True

    def deal_combat_damage_to_opponent(self, game):
        # In current engine, combat is 1v1 (active vs nonactive)
        victim = game.nonactive_player
        victim.lose_life(self.power)
        
        if self.is_commander:
            if self not in game.commander_damage:
                game.commander_damage[self] = {}
            
            current_damage = game.commander_damage[self].get(victim.index, 0)
            game.commander_damage[self][victim.index] = current_damage + self.power

    def set_damage_assignment_order(self, order):
        all_permutations = list(itertools.permutations(self.is_blocked_by))
        self.damage_assignment_order = list(all_permutations[order])
        self.damage_to_assign = self.power
        self.damage_assignment = [0] * len(self.damage_assignment_order)

    def assign_damage(self, index, amount):
        self.damage_assignment[index] += amount
        self.damage_to_assign -= amount

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Instant(Card):
    def __init__(self, name, subtypes, mc):
        super(Instant, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.subtypes = subtypes
        self.is_instant = True

    def play(self, owner, game, verbose=False):
        super(Instant, self).play(owner, game)
        if verbose:
            print("    casting %s" % (self.name))
        owner.casting_spell = self.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Artifact(Card):
    def __init__(self, name, subtypes, mc, tapped_abilities=None):
        super(Artifact, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.subtypes = subtypes
        if tapped_abilities is None:
            self.tapped_abilities = []
        else:
            self.tapped_abilities = tapped_abilities

    def play(self, owner, game, verbose=False):
        super(Artifact, self).play(owner, game)
        if verbose:
            print("    playing %s" % (self.name))
        game.battlefield.append(self)

    def use_tapped_ability(self, index):
        if not self.is_tapped:
            self.is_tapped = True
            self.tapped_abilities[index](self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Enchantment(Card):
    def __init__(self, name, subtypes, mc):
        super(Enchantment, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.subtypes = subtypes

    def play(self, owner, game, verbose=False):
        super(Enchantment, self).play(owner, game)
        if verbose:
            print("    playing %s" % (self.name))
        game.battlefield.append(self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Planeswalker(Card):
    def __init__(self, name, subtypes, mc, loyalty):
        super(Planeswalker, self).__init__()
        self.name = name
        self.mc = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.subtypes = subtypes
        self.loyalty = loyalty

    def play(self, owner, game, verbose=False):
        super(Planeswalker, self).play(owner, game)
        if verbose:
            print("    playing %s" % (self.name))
        game.battlefield.append(self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
