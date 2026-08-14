class GameConfig:
    DIFFICULTIES = {
        "EASY": {"boss_hp": 100, "move_chance": 0.20},
        "MEDIUM": {"boss_hp": 150, "move_chance": 0.40},
        "HARD": {"boss_hp": 225, "move_chance": 0.80}
    }

    def __init__(self):
        self.difficulty = "MEDIUM"
        self.auto_equip = True

    @property
    def boss_hp(self):
        return self.DIFFICULTIES[self.difficulty]["boss_hp"]

    @property
    def move_chance(self):
        return self.DIFFICULTIES[self.difficulty]["move_chance"]
