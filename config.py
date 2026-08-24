class GameConfig:
    DIFFICULTIES = {
        "EASY": {"boss_hp": 100, "move_chance": 0.25, "p_hp": 100, "p_atk": 10, "p_def": 10},
        "MEDIUM": {"boss_hp": 150, "move_chance": 0.50, "p_hp": 80, "p_atk": 8, "p_def": 7},
        "HARD": {"boss_hp": 250, "move_chance": 0.80, "p_hp": 60, "p_atk": 6, "p_def": 5}
    }

    def __init__(self):
        self.difficulty = "MEDIUM"
        self.auto_equip = True
        self.debug_mode = False

    @property
    def boss_hp(self):
        return self.DIFFICULTIES[self.difficulty]["boss_hp"]

    @property
    def move_chance(self):
        return self.DIFFICULTIES[self.difficulty]["move_chance"]

    @property
    def player_stats(self):
        d = self.DIFFICULTIES[self.difficulty]
        return d["p_hp"], d["p_atk"], d["p_def"]


if __name__ == "__main__":
    pass
