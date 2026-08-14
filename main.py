import random
from config import GameConfig
from data_loader import load_3d_maze
from display import Display, render_room_ascii, show_death_screen
from entities import Player, Monster

config = GameConfig()


def display_room(player, maze):
    room = maze.get_room(player.position)
    print("\n" + "=" * Display.WIDTH)
    print(f"DEPTH LEVEL {room.level}  |  ROOM {room.room_number}")
    print("=" * Display.WIDTH)

    render_room_ascii(room)
    print(room.description)

    if room.living_creatures:
        print("\nCreatures: " + ", ".join(c.name for c in room.living_creatures))
    if room.items:
        print("\nItems: " + ", ".join(i.name for i in room.items))
    if maze.monster and maze.monster.position == player.position and maze.monster.alive:
        print("\n!!! THE DARKNESS STIRS !!!")
        print(f"!!! {maze.monster.name} IS HERE !!!")
    print("=" * Display.WIDTH)


def battle(player, enemy):
    print("\n" + "#" * Display.WIDTH)
    print(f"BATTLE: {player.name} vs {enemy.name}")
    print("#" * Display.WIDTH)

    while player.alive and enemy.alive:
        player.process_effects()
        enemy.process_effects()

        print(f"\n{player.name}: {player.health}/{player.max_health} HP")
        print(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")

        print("\n1. Attack  2. Use Item  3. View Stats")
        choice = input("Choice: ")

        if choice == "1":
            player.fight(enemy)
        elif choice == "2":
            if player.items:
                player.use_item(target=enemy)
            else:
                print("No items.")
                continue
        elif choice == "3":
            player.get_stats()
            enemy.get_stats()
            continue

        # Check Boss Phase 2 Transition
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
    maze = load_3d_maze(boss_hp=config.boss_hp)
    player = Player(position=1)

    while player.alive:
        display_room(player, maze)

        # Process non-boss creatures in room
        room = maze.get_room(player.position)
        for creature in list(room.living_creatures):
            if not battle(player, creature):
                break

        if not player.alive:
            break

        if maze.monster and not maze.monster.alive:
            print("\n" + "#" * Display.WIDTH)
            print("THE DARKNESS HAS FALLEN!")
            print("You have slain Nyctophobia and escaped the underground abyss.")
            print("#" * Display.WIDTH)
            return

        print("\nWhat would you like to do?")
        print("1. Move")
        print("2. Pick Up Item")
        print("3. Use Item")
        print("4. View Stats")
        print("5. Quit")
        c = input("Choice: ")

        if c == "1":
            player.move(maze)
        elif c == "2":
            if room.items:
                item = room.items.pop(0)
                player.pick_up(item, config.auto_equip)
            else:
                print("\nThere are no items here.")
        elif c == "3":
            player.use_item()
        elif c == "4":
            player.get_stats()
        elif c == "5":
            return

        # Monster turn movement logic
        if maze.monster and maze.monster.alive:
            moved = maze.monster.choose_action(player, maze, config.move_chance)
            if moved:
                print("\n[NOTIFICATION] Something vast and unseen moves through the corridors...")

    if not player.alive:
        show_death_screen(player)


def options_menu():
    while True:
        print("\n" + "=" * Display.WIDTH)
        print("                      OPTIONS")
        print("=" * Display.WIDTH)
        print(f"1. Difficulty: [{config.difficulty}]")
        print(f"2. Auto-Equip Weapons: [{config.auto_equip}]")
        print("3. Back to Main Menu")

        choice = input("Choice: ")
        if choice == "1":
            diffs = ["EASY", "MEDIUM", "HARD"]
            config.difficulty = diffs[(diffs.index(config.difficulty) + 1) % len(diffs)]
        elif choice == "2":
            config.auto_equip = not config.auto_equip
        elif choice == "3":
            break


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
        print(f"{"N Y C T O P H O B I A":^100}\n"
              f"{"The darkness is not empty beneath the maze...":^100}")
        print("=" * Display.WIDTH)
        print("1. Start Game")
        print("2. Options")
        print("3. Quit")

        choice = input("Choice: ")
        if choice == "1":
            game_loop()
        elif choice == "2":
            options_menu()
        elif choice == "3":
            print("Exiting darkness...")
            break


if __name__ == "__main__":
    main_menu()
