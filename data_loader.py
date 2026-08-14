import csv
import os
from room import Room, Maze
from items import create_items
from entities import Shadowling, HollowStalker, GloomWraith, AbyssalHorror, Monster

MAZE_CSV_CONTENT = """room_number,level,north,south,east,west,up,down,is_stairwell,creature,items
"""

def generate_csv_if_missing(filename="data/maze3d.csv"):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(MAZE_CSV_CONTENT)

def load_3d_maze(filename="data/maze3d.csv", boss_hp=130):
    generate_csv_if_missing(filename)
    item_map = create_items()
    creature_map = {
        "S": Shadowling,
        "H": HollowStalker,
        "G": GloomWraith,
        "A": AbyssalHorror
    }
    rooms = []
    boss = None

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            room = Room(
                room_number=int(row["room_number"]),
                level=int(row["level"]),
                north=int(row["north"]),
                south=int(row["south"]),
                east=int(row["east"]),
                west=int(row["west"]),
                up=int(row["up"]),
                down=int(row["down"]),
                is_stairwell=bool(int(row["is_stairwell"]))
            )

            c_data = row.get("creature", "").strip()
            if c_data == "N":
                boss = Monster(position=room.room_number, health=boss_hp)
                room.creatures.append(boss)
            elif c_data in creature_map:
                room.creatures.append(creature_map[c_data]())

            i_data = row.get("items", "").strip()
            if i_data in item_map:
                room.items.append(item_map[i_data])

            rooms.append(room)

    return Maze(rooms, monster=boss)
