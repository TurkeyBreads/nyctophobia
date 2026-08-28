import random
from config import GameConfig
from data_loader import load_3d_maze
from display import Display, render_room_ascii, show_death_screen
from entities import Player, Monster
from items import DebuffItem, AbilityItem

config = GameConfig()


@Display.info
def render_room_items(room):
    if not room.items:
        return None

    item_list = ", ".join(i.name for i in room.items)
    return f"ITEMS FOUND IN THE ROOM: {item_list}"


@Display.info
def render_turn_log(messages):
    return "\n".join(messages)


def display_room(player, maze):
    room = maze.get_room(player.position)
    print("\n" + "~" * 30)
    print(f"{f'DEPTH LEVEL {room.level}  |  ROOM {room.room_number}':^30}")
    print("~" * 30)

    render_room_ascii(room)
    print(room.description)

    if room.living_creatures:
        print("\nCreatures: " + ", ".join(c.name for c in room.living_creatures))

    if maze.monster and maze.monster.position == player.position and maze.monster.alive:
        print("\n!!! THE DARKNESS STIRS !!!")
        print(f"!!! {maze.monster.name} IS HERE !!!")

    print("=" * Display.WIDTH)
    render_room_items(room)


def run_backstory(player_name):
    story = (
        f"The cold mountain wind howled behind {player_name}, but it was instantly swallowed by\n"
        f"the pitch-black maw of the ancient catacombs. For centuries, whispers spoke of\n"
        f"Nyctophobia—an ancient dark force lurking within the subterranean depths.\n\n"
        f"Step by agonizing step, {player_name} descended down into the damp bedrock.\n"
        f"The stone door slammed shut above with a deafening thud, locking away all warmth.\n"
        f"Equipped with faint hope and grit, the abyss demands your total focus..."
    )

    @Display.info
    def show_story():
        return story

    show_story()

    Display.pause_buffer("Press Enter to step into the dark...")


def _connected_rooms(player, maze):
    room = maze.get_room(player.position)
    return [
        r for r in [room.north, room.south, room.east, room.west, room.down, room.up]
        if r != 0 and maze.get_room(r) is not None
    ]


def _choose_target(enemies):
    living = [e for e in enemies if e.alive]
    if len(living) == 1:
        return living[0]

    choices = [f"{e.name} — {e.health}/{e.max_health} HP" for e in living]

    @Display.choice_input("Select target", lambda: choices)
    def select(choice=None):
        return living[choice - 1]

    return select()


def battle(player, enemies, maze):
    enemies = [e for e in enemies if e.alive]
    if not enemies:
        return "DEFEATED", ""

    print("\n" + "#" * Display.WIDTH)
    print(f"BATTLE: {player.name} vs {', '.join(e.name for e in enemies)}")
    print("#" * Display.WIDTH)

    while player.alive and any(e.alive for e in enemies):
        player.process_effects()
        for enemy in enemies:
            if enemy.alive:
                enemy.process_effects()

        living = [e for e in enemies if e.alive]
        print(f"\n{player.name}: {player.health}/{player.max_health} HP")
        for enemy in living:
            print(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")

        choices = ["Attack", "Use Item", "View Stats", "Run"]

        @Display.choice_input("What would you like to do?", lambda: choices)
        def process_battle(choice=None):
            return choices[choice - 1]

        action = process_battle()

        if action == "Attack":
            target = _choose_target(living)
            player.fight(target)

        elif action == "Use Item":
            item_choices = [f"{i.name} — {i.description}" for i in player.items] + ["Cancel"]

            @Display.choice_input("Select item to use", lambda: item_choices)
            def select_item(choice=None):
                return choice

            item_choice = select_item()
            if item_choice == len(item_choices):
                continue

            selected_item = player.items[item_choice - 1]
            target = None
            if isinstance(selected_item, (DebuffItem, AbilityItem)):
                target = _choose_target(living)

            result = player.use_item_at(item_choice, target)
            if result == "CANCELLED":
                continue

        elif action == "View Stats":
            player.get_stats()
            for enemy in living:
                enemy.get_stats()
            continue

        elif action == "Run":
            connected = _connected_rooms(player, maze)
            if not connected:
                render_turn_log(["[FLEE] There is nowhere to run! You are trapped and must fight!"])
                continue

            target_room = random.choice(connected)
            flee_msg = f"You panicked and fled to Room {target_room}!"

            if player.items:
                dropped = random.choice(player.items)
                player.items.remove(dropped)
                if player.weapon is dropped:
                    player.attack -= dropped.attack_bonus
                    player.weapon = None
                maze.get_room(player.position).items.append(dropped)
                flee_msg += f"\nIn your rush, you accidentally dropped your {dropped.name}!"
            else:
                trip_dmg = random.randint(10, 20)
                player.health = max(0, player.health - trip_dmg)
                flee_msg += f"\nWith nothing to drop, you tripped and took {trip_dmg} damage!"

            player.position = target_room
            player.level = maze.get_room(target_room).level
            return "FLED", flee_msg

        for enemy in living:
            if isinstance(enemy, Monster) and enemy.check_phase_transition():
                print("\n" + "!" * Display.WIDTH)
                print(f"THE SHADOWS CONVERGE! {enemy.name} ENTERS PHASE 2 WITH REGENERATED HEALTH AND GREATER ATTACK!")
                print("!" * Display.WIDTH)

        for enemy in [e for e in enemies if e.alive]:
            enemy.fight(player)
            if not player.alive:
                return "DEFEATED", ""

    defeated = [e for e in enemies if not e.alive]
    for enemy in defeated:
        if isinstance(enemy, Monster) and enemy.phase == 2:
            continue
        player.kills += 1
        stat_gain = random.choice(["attack", "defence"])
        amount = random.randint(1, 3)
        setattr(player, stat_gain, getattr(player, stat_gain) + amount)
        print(f"\nDefeated {enemy.name}! Empowered by victory, your {stat_gain.upper()} increased by +{amount}!")

    return "DEFEATED", ""

def game_loop():
    print("\n" + "_" * Display.WIDTH)
    while True:
        player_name = input("Enter your Adventurer's name: ").strip()
        if player_name and len(player_name) <= 20 and player_name.replace(" ", "").isalnum():
            break
        print("Please enter a name containing only letters/numbers/spaces (1–20 characters).")
    print("_" * Display.WIDTH)

    run_backstory(player_name)

    p_hp, p_atk, p_def = config.player_stats
    maze = load_3d_maze(boss_hp=config.boss_hp)
    player = Player(position=1, name=player_name, health=p_hp, attack=p_atk, defence=p_def)

    display_room(player, maze)

    while player.alive:
        room = maze.get_room(player.position)
        fled = False
        turn_logs = []

        living_creatures = list(room.living_creatures)
        if living_creatures:
            result, combat_msg = battle(player, living_creatures, maze)
            if result == "FLED":
                fled = True
                turn_logs.append(f"[FLEE] {combat_msg}")

        if not player.alive:
            break

        if maze.monster and not maze.monster.alive and maze.monster.phase == 2:
            render_turn_log(["THE DARKNESS HAS FALLEN!\nYou have slain Nycta and escaped the underground abyss."])
            player.get_stats()
            Display.pause_buffer("Press Enter to finish")
            return

        room = maze.get_room(player.position)
        choices = ["Move", "Use Item", "View Stats", "Quit"]
        if room.items:
            choices.insert(1, "Pick Up Item")
        if config.debug_mode:
            choices.insert(len(choices) - 1, "Debug")

        if not fled:
            @Display.choice_input("What would you like to do?", lambda: choices)
            def process_turn(choice=None):
                return choices[choice - 1]

            action = process_turn()
            match action:
                case "Move":
                    turn_logs.append(f"[ACTION] {player.move(maze)}")
                case "Pick Up Item":
                    item = room.items.pop(0)
                    turn_logs.append(f"[ACTION] {player.pick_up(item, config.auto_equip)}")
                case "Use Item":
                    result = player.use_item()
                    if result != "CANCELLED":
                        turn_logs.append(f"[ACTION] {result}")
                case "View Stats":
                    player.get_stats()
                case "Debug":
                    debug_menu(player, maze)
                case "Quit":
                    return

        if maze.monster and maze.monster.alive:
            moved = maze.monster.choose_action(player, maze, config.move_chance)
            if moved:
                turn_logs.append("[NOTIFICATION] Something vast and unseen moves through the corridors...")

        display_room(player, maze)
        if turn_logs:
            render_turn_log(turn_logs)

    if not player.alive:
        show_death_screen(player)


def debug_menu(player, maze):
    choices = ["Teleport", "Give All Items", "Heal to Full", "Back"]

    @Display.choice_input("DEBUG MENU", lambda: choices)
    def choose(choice=None):
        return choices[choice - 1]

    while True:
        match choose():
            case "Back":
                return
            case "Teleport":
                rooms = [r for r in maze.rooms if r.level in (1, 2, 10)]

                @Display.choice_input("Select room", lambda: [f"Room {r.room_number} (Level {r.level})" for r in rooms])
                def select_room(choice=None):
                    return rooms[choice - 1]
                
                room = select_room()
                player.position = room.room_number
                player.level = room.level
            case "Give All Items":
                from items import create_items
                
                player.items.extend(create_items().values())
                print("All items added to inventory.")
                Display.pause_buffer()
            case "Heal to Full":
                player.health = player.max_health
                print("Player healed to full health.")
                Display.pause_buffer()


@Display.choice_input(
    "OPTIONS MENU",
    lambda: [
        f"Difficulty: [{config.difficulty}]",
        f"Auto-Equip Weapons: [{config.auto_equip}]",
        f"Debug Mode: [{config.debug_mode}]",
        "Back to Main Menu"
    ]
)
def options_menu(choice=None):
    match choice:
        case 1:
            diffs = ["EASY", "MEDIUM", "HARD"]
            config.difficulty = diffs[(diffs.index(config.difficulty) + 1) % len(diffs)]
        case 2:
            config.auto_equip = not config.auto_equip
        case 3:
            config.debug_mode = not config.debug_mode
        case 4:
            return "BACK"

    return None


def main_menu():
    while True:
        title_art = r"""
 ███▄    █▓██   ██▓ ▄████▄  ▄▄▄█████▓ ▒█████   ██▓███   ██░ ██  ▒█████   ▄▄▄▄    ██▓ ▄▄▄      
 ██ ▀█   █ ▒██  ██▒▒██▀ ▀█  ▓  ██▒ ▓▒▒██▒  ██▒▓██░  ██▒▓██░ ██▒▒██▒  ██▒▓█████▄ ▓██▒▒████▄    
▓██  ▀█ ██▒ ▒██ ██░▒▓█    ▄ ▒ ▓██░ ▒░▒██░  ██▒▓██░ ██▓▒▒██▀▀██░▒██░  ██▒▒██▒ ▄██▒██▒▒██  ▀█▄  
▓██▒  ▐▌██▒ ░ ▐██▓░▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒██   ██░▒██▄█▓▒ ▒░▓█ ░██ ▒██   ██░▒██░█▀  ░██░░██▄▄▄▄██ 
▒██░   ▓██░ ░ ██▒▓░▒ ▓███▀ ░  ▒██▒ ░ ░ ████▓▒░▒██▒ ░  ░░▓█▒░██▓░ ████▓▒░░▓█  ▀█▓░██░ ▓█   ▓██▒
░ ▒░   ▒ ▒   ██▒▒▒ ░ ░▒ ▒  ░  ▒ ░░   ░ ▒░▒░▒░ ▒▓▒░ ░  ░ ▒ ░░▒░▒░ ▒░▒░▒░ ░▒▓███▀▒░▓   ▒▒   ▓▒█░
░ ░░   ░ ▒░▓██ ░▒░   ░  ▒       ░      ░ ▒ ▒░ ░▒ ░      ▒ ░▒░ ░  ░ ▒ ▒░ ▒░▒   ░  ▒ ░  ▒   ▒▒ ░
   ░   ░ ░ ▒ ▒ ░░  ░          ░      ░ ░ ░ ▒  ░░        ░  ░░ ░░ ░ ░ ▒   ░    ░  ▒ ░  ░   ▒   
         ░ ░ ░     ░ ░                   ░ ░            ░  ░  ░    ░ ░   ░       ░        ░  ░
           ░ ░     ░                                                          ░               
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣠⢴⢴⡴⣤⢤⣄⠄⠄⢀⠄⣀⡤⣴⣺⡽⣯⡷⣦⣄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣔⢞⢝⢝⠽⡽⣽⣳⢿⡽⣏⣗⢗⢯⢯⣗⡯⡿⣽⢽⣷⣟⣷⣄ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⡗⡟⡼⣸⣁⢋⠎⠎⢯⢯⡧⡫⣎⡽⡹⠊⢍⠙⠜⠽⣳⢯⣿⣳ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢕⠕⠁⣁⢬⢬⣌⠆⠅⢯⡻⣜⢷⠁⠌⡼⠲⠺⢮⡆⡉⢹⣺⣽ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⡀⢐⠄⠄⠄⠈⠳⠁⡂⢟⣞⡏⠄⡹⠄⠄⠄⠄⠈⣺⡐⣞⣾ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢰⡳⡹⢦⣀⣠⡠⠤⠄⡐⢝⣾⣳⣐⣌⠳⠦⠤⠤⣞⢼⢽⣻⡷ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢸⣚⢆⢄⣈⠨⢊⢐⢌⠞⣞⣞⡗⡟⡾⣝⢦⣳⡳⣯⢿⣻⣽⣟ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠘⡢⡫⢒⠒⣘⠰⣨⢴⣸⣺⣳⢥⢷⣳⣽⣳⢮⢝⢽⡯⣿⣺⡽ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠁⠪⠤⢑⢄⢽⡙⢽⣺⢾⢽⢯⡟⡽⣾⣎⡿⣮⡳⣹⣳⣗⠇ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠁⠄⡸⡡⠑⠤⣠⡑⠙⠍⡩⡴⣽⡗⣗⣟⣷⣫⢳⢕⡏ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢈⡇⡇⡆⡌⡀⡉⠫⡯⢯⡫⡷⣽⣺⣗⣟⡾⡼⡺ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⡮⡎⡎⡎⣞⢲⡹⡵⡕⣇⡿⣽⣳⣟⣾⣳⡯⠉ ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
"""

        print("\n" + "=" * Display.WIDTH)
        print(title_art)
        print(f"{'N Y C T O P H O B I A':^100}\n"
              f"{'The darkness is not empty beneath the maze...':^100}")
        print("=" * Display.WIDTH)

        choices = ["Start Game", "Options", "Quit"]

        @Display.choice_input("What would you like to do?", lambda: choices)
        def process_main_menu(choice=None):
            return choices[choice - 1]

        match process_main_menu():
            case "Start Game":
                game_loop()
            case "Options":
                while options_menu() != "BACK":
                    pass
            case "Quit":
                print("Exiting darkness...")
                return


if __name__ == "__main__":
    main_menu()
