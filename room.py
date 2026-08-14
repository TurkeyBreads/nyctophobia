import random

DESCENT_CAPTIONS = {
    1: "The stone corridors feel cold and damp.",
    2: "The air grows heavy as you descend further down the stairwells.",
    3: "You stand in the bottom Abyss. The pitch-black silence is absolute."
}

def generate_random_caption(level, is_stairwell):
    if is_stairwell:
        return f"{DESCENT_CAPTIONS.get(level, '')} A winding stone STAIRWELL cuts deep into the bedrock."

    with open("data/atmospheres.txt", "r", encoding="utf-8") as f:
        atmospheres = [line.strip() for line in f if line.strip()]

    with open("data/sounds.txt", "r", encoding="utf-8") as f:
        sounds = [line.strip() for line in f if line.strip()]

    return f"{DESCENT_CAPTIONS.get(level, '')}\n{random.choice(atmospheres)}\n{random.choice(sounds)}"


class Room:
    def __init__(self, room_number, level, north=0, south=0, east=0, west=0, up=0, down=0, is_stairwell=False):
        self.room_number = room_number
        self.level = level
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.up = up
        self.down = down
        self.is_stairwell = is_stairwell
        self.items = []
        self.creatures = []
        self.description = generate_random_caption(level, is_stairwell)

    @property
    def living_creatures(self):
        return [c for c in self.creatures if c.alive]


class Maze:
    def __init__(self, rooms, monster=None):
        self.rooms = rooms
        self.monster = monster

    def get_room(self, room_number):
        for room in self.rooms:
            if room.room_number == room_number:
                return room

        return None
