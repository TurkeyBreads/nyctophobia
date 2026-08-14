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

            print()
            for line in str(text).split("\n"):
                print(f"          /BATTLE/  {line}")

            return text

        return wrapper


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

    print("\n┌" + "─" * 68 + "┐")
    print("│                         CHARACTER STATS                            │")
    print("├" + "─" * 32 + "┬" + "─" * 35 + "┤")

    for i in range(max(len(player_art), len(stats_lines))):
        art_part = player_art[i] if i < len(player_art) else ""
        stat_part = stats_lines[i] if i < len(stats_lines) else ""
        print(f"│ {art_part:<30} │ {stat_part:<33} │")

    print("├" + "─" * 32 + "┴" + "─" * 35 + "┤")
    print(f"│ INVENTORY: {item_names[:55]:<55} │")
    print("└" + "─" * 68 + "┘")


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

    ending_art = """
                    ⢕⢕⢕⢕⠁⢜⠕⢁⣴⣿⡇⢓⢕⢵⢐⢕⢕⠕⢁⣾⢿⣧⠑⢕⢕⠄⢑⢕⠅⢕
                    ⢕⢕⠵⢁⠔⢁⣤⣤⣶⣶⣶⡐⣕⢽⠐⢕⠕⣡⣾⣶⣶⣶⣤⡁⢓⢕⠄⢑⢅⢑
                    ⠍⣧⠄⣶⣾⣿⣿⣿⣿⣿⣿⣷⣔⢕⢄⢡⣾⣿⣿⣿⣿⣿⣿⣿⣦⡑⢕⢤⠱⢐
                    ⢠⢕⠅⣾⣿⠋⢿⣿⣿⣿⠉⣿⣿⣷⣦⣶⣽⣿⣿⠈⣿⣿⣿⣿⠏⢹⣷⣷⡅⢐
                    ⣔⢕⢥⢻⣿⡀⠈⠛⠛⠁⢠⣿⣿⣿⣿⣿⣿⣿⣿⡀⠈⠛⠛⠁⠄⣼⣿⣿⡇⢔
                    ⢕⢕⢽⢸⢟⢟⢖⢖⢤⣶⡟⢻⣿⡿⠻⣿⣿⡟⢀⣿⣦⢤⢤⢔⢞⢿⢿⣿⠁⢕
                    ⢕⢕⠅⣐⢕⢕⢕⢕⢕⣿⣿⡄⠛⢀⣦⠈⠛⢁⣼⣿⢗⢕⢕⢕⢕⢕⢕⡏⣘⢕
    ╻ ╻╻ ╻╻ ╻       ⢕⢕⠅⢓⣕⣕⣕⣕⣵⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣷⣕⢕⢕⢕⢕⡵⢀⢕⢕
    ┃ ┃┃╻┃┃ ┃       ⢑⢕⠃⡈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⢕⢕⢕
    ┗━┛┗┻┛┗━┛       ⣆⢕⠄⢱⣄⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢁⢕⢕⠕⢁"""

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
    print(ending_art)


if __name__ == "__main__":
    from room import Room
    from entities import Player

    room1 = Room(1, 1, 2, 3, 4, 5, 0, 0, is_stairwell=False)
    room2 = Room(2, 1, 0, 1, 0, 6, 0, 7, is_stairwell=True)
    human = Player(1)

    render_room_ascii(room1)
    render_room_ascii(room2)
    display_player_stats(human)
    show_death_screen(human)
