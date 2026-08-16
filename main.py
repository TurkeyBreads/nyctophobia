import random
from config import GameConfig
from data_loader import load_3d_maze
from display import Display, render_room_ascii, show_death_screen
from entities import Player, Monster

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


def battle(player, enemy, maze):
    print("\n" + "#" * Display.WIDTH)
    print(f"BATTLE: {player.name} vs {enemy.name}")
    print("#" * Display.WIDTH)

    while player.alive and enemy.alive:
        player.process_effects()
        enemy.process_effects()

        print(f"\n{player.name}: {player.health}/{player.max_health} HP")
        print(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")

        choices = ["Attack", "View Stats", "Run"]
        if player.items:
            choices.insert(1, "Use Item")

        @Display.choice_input("What would you like to do?", lambda: choices)
        def process_battle(choice=None):
            return choices[choice - 1]

        match process_battle():
            case "Attack":
                player.fight(enemy)
            case "Use Item":
                player.use_item(target=enemy)
                continue
            case "View Stats":
                player.get_stats()
                enemy.get_stats()
                continue
            case "Run":
                current_room = maze.get_room(player.position)
                connected = [r for r in [
                    current_room.north, current_room.south, current_room.east,
                    current_room.west, current_room.down, current_room.up
                ] if r != 0]

                if not connected:
                    render_turn_log(["[FLEE] There is nowhere to run! You are trapped and must fight!"])
                    continue

                target_room = random.choice(connected)
                flee_msg = f"You panicked and fled to Room {target_room}!"

                if player.items:
                    dropped = random.choice(player.items)
                    player.items.remove(dropped)

                    if hasattr(player, 'weapon') and player.weapon == dropped:
                        player.attack -= dropped.attack_bonus
                        player.weapon = None

                    current_room.items.append(dropped)
                    flee_msg += f"\nIn your rush, you accidentally dropped your {dropped.name}!"
                else:
                    trip_dmg = random.randint(10, 20)
                    player.health = max(0, player.health - trip_dmg)
                    flee_msg += f"\nWith nothing to drop, you tripped flat on your face taking {trip_dmg} damage!"

                player.position = target_room
                player.level = maze.get_room(target_room).level

                return "FLED", flee_msg

        if isinstance(enemy, Monster) and enemy.check_phase_transition():
            print("\n" + "!" * Display.WIDTH)
            print(f"THE SHADOWS CONVERGE! {enemy.name} ENTERS PHASE 2 WITH REGENERATED HEALTH AND GREATER ATTACK!")
            print("!" * Display.WIDTH)

        if not enemy.alive:
            player.kills += 1
            stat_gain = random.choice(["attack", "defence"])
            amount = random.randint(1, 3)
            setattr(player, stat_gain, getattr(player, stat_gain) + amount)
            print(f"\nDefeated {enemy.name}! Empowered by victory, your {stat_gain.upper()} increased by +{amount}!")
            return True

        enemy.fight(player)
        if not player.alive:
            return False

    return player.alive


def game_loop():
    print("\n" + "_" * Display.WIDTH)
    player_name = input("Enter your Adventurer's name: ").strip() or "Adventurer"
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

        for creature in list(room.living_creatures):
            result, combat_msg = battle(player, creature, maze)
            if result == "FLED":
                fled = True
                turn_logs.append(f"[FLEE] {combat_msg}")
                break
            if not player.alive:
                break

        if maze.monster and not maze.monster.alive:
            render_turn_log(["THE DARKNESS HAS FALLEN!\nYou have slain the Nycta and escaped the underground abyss."])
            Display.pause_buffer("Press Enter to finish")
            return

        choices = ["Move", "Use Item", "View Stats", "Quit"]
        if room.items:
            choices.insert(1, "Pick Up Item")

        if not fled:
            @Display.choice_input("What would you like to do?", lambda: choices)
            def process_turn(choice=None):
                return choices[choice - 1]

            match process_turn():
                case "Move":
                    turn_logs.append(f"[ACTION] {player.move(maze)}")
                case "Pick Up Item":
                    item = room.items.pop(0)
                    turn_logs.append(f"[ACTION] {player.pick_up(item, config.auto_equip)}")
                case "Use Item":
                    turn_logs.append(f"[ACTION] {player.use_item()}")
                case "View Stats":
                    player.get_stats()
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


@Display.choice_input(
    "OPTIONS MENU",
    lambda: [
        f"Difficulty: [{config.difficulty}]",
        f"Auto-Equip Weapons: [{config.auto_equip}]",
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
