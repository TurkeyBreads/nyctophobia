import csv
import os
from room import Room, Maze
from items import create_items
from entities import Shadowling, HollowStalker, GloomWraith, AbyssalHorror, Monster

MAZE_CSV_CONTENT = """room_number,level,north,south,east,west,up,down,is_stairwell,creature,items
1,1,0,0,2,0,0,0,0,,
2,1,0,7,3,0,0,0,0,,
3,1,0,0,4,0,0,0,0,,
4,1,0,9,5,3,0,0,0,,W
5,1,0,0,6,4,0,0,0,,
6,1,0,11,0,5,0,0,0,,
7,1,2,0,8,0,0,0,0,S,
8,1,0,0,9,0,0,0,0,,
9,1,4,13,10,8,0,0,0,S,
10,1,0,14,0,9,0,0,0,,
11,1,6,15,0,0,0,0,0,H,
12,1,0,0,13,0,0,0,0,,D
13,1,9,18,14,12,0,0,0,,
14,1,10,0,0,13,0,0,0,,
15,1,11,0,0,0,0,0,0,,B
16,1,0,20,0,0,0,0,0,,
17,1,0,21,18,0,0,0,0,,L
18,1,0,0,19,17,0,0,0,,X
19,1,0,23,0,18,0,0,0,,
20,1,16,25,21,0,0,0,0,H,
21,1,0,26,22,20,0,0,0,,
22,1,0,0,0,21,0,0,0,,
23,1,19,0,24,22,0,0,0,,
24,1,0,0,0,23,0,0,0,G,
25,1,20,0,0,0,0,35,1,,
26,1,21,0,0,0,0,0,0,A,B2
27,2,0,0,28,0,25,0,1,,
28,2,0,0,29,27,0,0,0,,
29,2,0,32,0,28,0,0,0,,
30,2,0,33,31,0,0,0,0,,
31,2,0,34,0,30,0,0,0,H,
32,2,29,0,33,0,0,0,0,,
33,2,30,38,34,32,0,0,0,,
34,2,31,0,0,33,0,0,0,,
35,2,0,41,0,0,0,-35,1,,
36,2,0,43,37,0,0,0,0,,
37,2,0,0,0,36,0,0,0,G,
38,2,0,0,39,37,0,0,0,,
39,2,0,45,40,38,0,0,0,A,
40,2,0,46,0,39,0,0,0,,
41,2,35,0,42,0,0,0,0,,
42,2,0,0,43,41,0,0,0,H,
43,2,36,0,44,42,0,0,0,,
44,2,0,0,0,43,0,0,0,,X
45,2,39,0,46,0,0,0,0,,
46,2,40,0,47,45,0,0,0,,
47,2,0,0,0,46,0,0,0,,L2
-35,10,-3,0,-1,0,0,0,0,,
-1,10,-4,0,-2,0,0,0,0,,
-2,10,-5,0,0,-1,0,0,0,,
-3,10,-6,-35,-4,0,0,0,0,,
-4,10,-7,-1,-5,-3,0,0,0,,
-5,10,-8,-2,0,-4,0,0,0,,
-6,10,0,-3,-7,0,0,0,0,,
-7,10,0,-4,-8,-6,0,0,0,,
-8,10,0,-5,-9,-7,0,0,0,A,
-9,10,0,-12,-10,-8,0,0,0,,W
-10,10,0,-13,-11,-9,0,0,0,,L
-11,10,0,-14,0,-10,0,0,0,,B
-12,10,-9,-15,-13,0,0,0,0,,L2
-13,10,-10,-16,-14,-12,0,0,0,N,
-14,10,-11,-17,0,-13,0,0,0,,B2
-15,10,-12,0,-16,0,0,0,0,,D
-16,10,-13,0,-17,-15,0,0,0,,X
-17,10,-14,0,0,-16,0,0,0,,X2
"""

def generate_csv_if_missing(filename="data/maze3d.csv"):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(MAZE_CSV_CONTENT)

def load_3d_maze(filename="data/maze3d.csv", boss_hp=150):
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
            if c_data:
                for c_code in c_data.split(","):
                    c_code = c_code.strip()
                    if c_code == "N":
                        boss = Monster(position=room.room_number, health=boss_hp)
                        room.creatures.append(boss)
                    elif c_code in creature_map:
                        room.creatures.append(creature_map[c_code]())

            i_data = row.get("items", "").strip()
            if i_data:
                for i_code in i_data.split(","):
                    i_code = i_code.strip()
                    if i_code in item_map:
                        room.items.append(item_map[i_code])

            rooms.append(room)

    return Maze(rooms, monster=boss)


if __name__ == "__main__":
    pass
