class Display:
    WIDTH = 100

    @staticmethod
    def choice_input(question, choices):
        def decorator(func):
            def wrapper(*args, **kwargs):
                actual_choices = choices(*args, **kwargs)
                if not actual_choices:
                    return func(*args, choice=None, **kwargs)

                print(f"\n{question}")
                for i, choice in enumerate(actual_choices, 1):
                    print(f"{i}. {choice}")

                print(f"\n{'_' * Display.WIDTH}")
                while True:
                    value = input("Choice: ")
                    if value.isdigit() and 1 <= int(value) <= len(actual_choices):
                        return func(*args, choice=int(value), **kwargs)

                    print("Please enter a valid choice.")

            return wrapper

        return decorator

    @staticmethod
    def info(func):
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            if text is None:
                return None

            print(f"\n┌{'─' * (Display.WIDTH - 2)}┐")

            for line in str(text).split("\n"):
                line = line[:Display.WIDTH - 4]
                print(f"│ {line:<{Display.WIDTH - 4}} │")

            print(f"└{'─' * (Display.WIDTH - 2)}┘")

            return text

        return wrapper

    @staticmethod
    def battle(func):
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            if text is None:
                return None

            for line in str(text).split("\n"):
                print(f"            /BATTLE/  {line}")

            return text

        return wrapper

    @staticmethod
    def pause_buffer(msg="Press Enter to continue..."):
        print()
        print(f"  ◈ {msg} ◈")
        input("  └─> ")


def render_room_ascii(room):
    n = " N " if room.north != 0 else "───"
    s = " S " if room.south != 0 else "───"
    w = "W" if room.west != 0 else "│"
    e = "E" if room.east != 0 else "│"

    room_type = "STAIRWELL" if room.is_stairwell else f"ROOM {room.room_number:<2}"

    stairs = []
    if room.up != 0:
        stairs.append("STAIRS UP")
    if room.down != 0:
        stairs.append("STAIRS DOWN")

    stair_text = " | ".join(stairs)

    ascii_art = f"""
        ┌────{n}────┐
        │           │
        {w} {room_type:^9} {e}
        │           │
        └────{s}────┘
"""

    if stair_text:
        ascii_art += f"        [{stair_text}]\n"

    print(ascii_art)


def display_player_stats(player):
    player_art = r"""          
              {}
             .--.
            /.--.\
            |====|
            |`::`|
        .-;`\..../`;-.
       /  |...::...|  \
      |   /'''::'''\   |
      ;--'\   ::   /\--;
      <__>,>._::_.<,<__>
      |  |/   ^^   \|  |
      \::/|        |\::/
      |||\|        |/|||
      UUU |___/\___| UUU
           \_ || _/
           <_ >< _>
           |  ||  |
           |  ||  |
          _\.:||:./_
         /____/\____\
    """.splitlines()

    weapon_str = player.weapon.name if player.weapon else "None"
    item_names = ", ".join(i.name for i in player.items) or "Empty"

    stats_lines = [
        f"NAME:     {player.name}",
        f"FLOOR:    Level {player.level} (Room {player.position})",
        f"HEALTH:   {player.health}/{player.max_health} HP",
        f"ATTACK:   {player.attack}",
        f"DEFENCE:  {player.defence}",
        f"WEAPON:   {weapon_str}",
        f"KILLS:    {player.kills}"
    ]

    print("\n┌" + "─" * (Display.WIDTH - 32) + "┐")
    print(f"│ {'CHARACTER STATS':^{Display.WIDTH - 34}} │")
    print("├" + "─" * 32 + "┬" + "─" * (Display.WIDTH - 65) + "┤")

    for i in range(max(len(player_art), len(stats_lines))):
        art_part = player_art[i] if i < len(player_art) else ""
        stat_part = stats_lines[i] if i < len(stats_lines) else ""
        print(f"│ {art_part:<30} │ {stat_part:<{Display.WIDTH - 67}} │")

    print("├" + "─" * 32 + "┴" + "─" * (Display.WIDTH - 65) + "┤")
    print(f"│ INVENTORY: {item_names:<{Display.WIDTH - 45}} │")
    print("└" + "─" * (Display.WIDTH - 32) + "┘")

    Display.pause_buffer("Press Enter to close Player Stats")


def display_entity_stats(entity):
    print("\n┌" + "─" * (Display.WIDTH - 2) + "┐")
    print(f"│ {entity.name.upper():<{Display.WIDTH - 4}} │")
    print("├" + "─" * (Display.WIDTH - 2) + "┤")
    print(f"│ {'HEALTH:':<9}{f'{entity.health}/{entity.max_health} HP':<{Display.WIDTH - 13}} │")
    print(f"│ {'ATTACK:':<9}{str(entity.attack):<{Display.WIDTH - 13}} │")
    print(f"│ {'DEFENCE:':<9}{str(entity.defence):<{Display.WIDTH - 13}} │")
    print("└" + "─" * (Display.WIDTH - 2) + "┘")

    Display.pause_buffer("Press Enter to close Creature Stats")


def show_death_screen(player):
    death_art = """
 ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ 
██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║██║   ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝╚██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
                        ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⣶⠶⠶⣶⣤⣤⡀
                        ⠀⠀⠀⠀⠀⢀⣴⠾⠛⠉⠀⢠⣾⣴⡾⠛⠻⣷⣄
                        ⠀⠀⢶⣶⣶⣿⣁⠀⠀⠀⠀⢸⣿⠏⢀⣤⣶⣌⠻⣦⡀
                        ⠀⠀⣴⡟⠁⢉⣙⣿⣦⡀⠀⢸⡏⣴⠟⢡⣶⣿⣧⡹⣷⡀
                        ⠀⣼⠏⢀⣾⠟⠛⠛⠻⣿⡆⠀⠀⢿⣄⠀⠙⠉⠹⣷⡸⣷⠀
                        ⢠⣿⠀⢸⡿⢿⠇⠀⠀⣾⠇⠀⣀⣈⠻⢷⣤⣤⣤⡾⠃⢹⣇
                        ⢸⣿⠀⢸⣧⣀⣀⣠⣾⢋⣴⢿⣿⡛⠻⣶⣤⣉⠁⠀⠀⠀⣿
                        ⠈⣿⠀⠀⠙⠛⠛⠋⠁⣼⣯⣀⣿⠿⠶⠟⠉⠛⢷⣄⠀⠀⣿⡇
                        ⠀⣿⠀⠀⠀⠀⠀⠀⠀⣿⡏⠉⠁⠀⠀⢀⣴⢶⣄ ⢻⡇⠀ ⢸⡇
                        ⠀⢻⣇⠀⠀⠀⠀⠀⢠⡿⢀⣀⢠⣾⠷⣾⣧⡶⠿⠟⠁⠀⣾⡇
                        ⠀⠈⣿⣧⡀⠀⠀⣠⣿⣷⠟⢻⣿⣷⡾⠛⠉⠀⠀⠀⠀⢀⣿
                        ⠀⠀⢹⣿⢻⣦⡀⠉⠛⠛⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⣼⠏
                        ⠀⠀⠀⠛⠀⠈⠻⠷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠟
"""

    print("\n" + "=" * Display.WIDTH)
    print(death_art)
    print("=" * Display.WIDTH)
    print(f"\n       ┌──────────────────────────────────────────────────────────┐")
    print(f"       │                     FINAL STATS                          │")
    print(f"       ├──────────────────────────────────────────────────────────┤")
    print(f"       │ Depth Reached:       Level {player.level:<29} │")
    print(f"       │ Enemies Defeated:    {player.kills:<35} │")
    print(f"       │ Final Attack:        {player.attack:<35} │")
    print(f"       │ Final Defence:       {player.defence:<35} │")
    print(f"       └──────────────────────────────────────────────────────────┘")

    Display.pause_buffer("Press Enter to return to Main Menu")


if __name__ == "__main__":
    from room import Room
    from entities import Player, Shadowling

    room1 = Room(1, 1, 2, 3, 4, 5, 0, 0, is_stairwell=False)
    room2 = Room(2, 1, 0, 1, 0, 6, 0, 7, is_stairwell=True)
    human = Player(1, name="Christopher")
    shadowling1 = Shadowling()

    render_room_ascii(room1)
    render_room_ascii(room2)
    display_player_stats(human)
    display_entity_stats(shadowling1)
    show_death_screen(human)

    @Display.info
    def test_info():
        return "This is an information message."


    @Display.battle
    def test_battle():
        return f"{human.name} attacks {shadowling1.name}!"


    @Display.choice_input(
        "Choose an action:",
        lambda: ["Attack", "Defend", "Use Item", "Run"]
    )
    def test_choice(choice=None):
        print(f"You chose: {choice}")


    test_info()
    test_battle()
    test_choice()
    Display.pause_buffer()
