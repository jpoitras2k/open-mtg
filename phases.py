from enum import Enum


class Phases(Enum):
    UNTAP_STEP = 1
    UPKEEP_STEP = 2
    DRAW_STEP = 3
    MAIN_PHASE_PRE_COMBAT = 4
    BEGINNING_OF_COMBAT_STEP = 5
    DECLARE_ATTACKERS_STEP = 6
    DECLARE_BLOCKERS_STEP = 7
    DECLARE_BLOCKERS_STEP_509_2 = 8
    COMBAT_DAMAGE_STEP_510_1c = 9
    COMBAT_DAMAGE_STEP = 10
    END_OF_COMBAT_STEP = 11
    MAIN_PHASE_POST_COMBAT = 12
    END_STEP = 13
    CLEANUP_STEP = 14

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]
