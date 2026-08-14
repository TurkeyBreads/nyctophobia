import csv
import random


# ============================================================
# DISPLAY
# ============================================================

class Display:
    """Utility class for handling game input and output."""

    WIDTH = 60

    @staticmethod
    def choice_input(question, choices):
        """Decorator for displaying a numbered choice menu."""

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
        """Decorator for displaying returned information or print calls in a box."""

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
        """Decorator for displaying battle messages."""

        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)

            print()

            for line in str(text).split("\n"):
                print(f"          /BATTLE/  {line}")

            return text

        return wrapper


# ============================================================
# ASCII MAP HELPER
# ============================================================

def render_room_ascii(room):
    """Renders a visual 2D box representing the room and its doorways."""
    n = "   N   " if room.north != 0 else "───────"
    s = "   S   " if room.south != 0 else "───────"
    w = "W" if room.west != 0 else "│"
    e = "E" if room.east != 0 else "│"

    ascii_art = f"""
        ┌───{n}───┐
        │             │
        {w}   ROOM {room.room_number:<2}   {e}
        │             │
        └───{s}───┘
    """
    print(ascii_art)


# ============================================================
# EFFECTS
# ============================================================

class Effect:
    """Represents a temporary buff or debuff."""

    def __init__(self, name, attribute, amount, duration):
        self.name = name
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def apply(self, entity):
        setattr(
            entity,
            self.attribute,
            getattr(entity, self.attribute) + self.amount
        )

    def remove(self, entity):
        setattr(
            entity,
            self.attribute,
            getattr(entity, self.attribute) - self.amount
        )


# ============================================================
# ITEMS
# ============================================================

class Item:
    """Base class for all items."""

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, player, target=None):
        raise NotImplementedError

    def __str__(self):
        return self.name


class HealingItem(Item):
    """Restores player health."""

    def __init__(self, name, description, healing):
        super().__init__(name, description)
        self.healing = healing

    def use(self, player, target=None):
        old_health = player.health
        player.health = min(player.max_health, player.health + self.healing)
        return f"You use {self.name} and restore {player.health - old_health} HP."


class Weapon(Item):
    """A weapon that increases attack."""

    def __init__(self, name, description, attack_bonus):
        super().__init__(name, description)
        self.attack_bonus = attack_bonus

    def use(self, player, target=None):
        if player.weapon is self:
            return f"You are already wielding the {self.name}."

        if player.weapon is not None:
            player.attack -= player.weapon.attack_bonus

        player.weapon = self
        player.attack += self.attack_bonus

        return f"You equip the {self.name}. Attack +{self.attack_bonus}."


class BuffItem(Item):
    """Temporarily increases one of the player's attributes."""

    def __init__(self, name, description, attribute, amount, duration):
        super().__init__(name, description)
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def use(self, player, target=None):
        effect = Effect(self.name, self.attribute, self.amount, self.duration)
        effect.apply(player)
        player.effects.append(effect)

        return (
            f"You use the {self.name}. "
            f"{self.attribute.capitalize()} +{self.amount} for {self.duration} turns."
        )


class DebuffItem(Item):
    """Temporarily weakens an enemy."""

    def __init__(self, name, description, attribute, amount, duration):
        super().__init__(name, description)
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def use(self, player, target=None):
        if target is None:
            return "There is no target."

        effect = Effect(self.name, self.attribute, -self.amount, self.duration)
        effect.apply(target)
        target.effects.append(effect)

        return (
            f"The {target.name}'s {self.attribute} "
            f"is reduced by {self.amount} for {self.duration} turns."
        )


class AbilityItem(Item):
    """An item with a special combat ability."""

    def __init__(self, name, description, damage, effect=None):
        super().__init__(name, description)
        self.damage = damage
        self.effect = effect

    def use(self, player, target=None):
        if target is None:
            return "There is no target."

        target.health = max(0, target.health - self.damage)
        message = f"You use {self.name} and deal {self.damage} damage to {target.name}."

        if self.effect is not None:
            self.effect.apply(target)
            target.effects.append(self.effect)
            message += f" {target.name}'s {self.effect.attribute} is reduced."

        return message


def create_items():
    return {
        # Base Weapons & Restoratives
        "W": Weapon("Shadow Blade", "A weapon forged from condensed darkness.", attack_bonus=8),
        "W2": Weapon("Nightmare Blade", "A jagged blade that drinks light from the air.", attack_bonus=12),
        "L": HealingItem("Light Fragment", "A fragment of pure light that restores health.", healing=35),
        "L2": HealingItem("Elixir of Life", "A glowing vial that deeply heals severe wounds.", healing=70),
        # Buff & Debuff Items
        "F": BuffItem("Flare", "Temporarily increases attack.", attribute="attack", amount=7, duration=3),
        "F2": BuffItem("Shadow Veil", "Encases you in shadow, greatly boosting defence.", attribute="defence", amount=8,
                       duration=3),
        "B": DebuffItem("Bright Powder", "Weakens an enemy's defence.", attribute="defence", amount=5, duration=3),
        "B2": DebuffItem("Shatter Dust", "Significantly strips away an enemy's attack power.", attribute="attack",
                         amount=6, duration=3),
        # Direct Offense Abilities
        "X": AbilityItem("Flash Bomb", "A burst of light that deals direct damage.", damage=25),
        "X2": AbilityItem("Void Blast", "Unleashes raw localized force for massive damage.", damage=45),
    }


# ============================================================
# ENTITY
# ============================================================

class Entity:
    """Base class for all combat entities."""

    def __init__(self, health, attack, defence, armour=None, name="Entity"):
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defence = defence
        self.armour = armour
        self.name = name
        self.effects = []

    @property
    def alive(self):
        return self.health > 0

    @Display.battle
    def fight(self, other):
        # Weighted random attack and defence rolls centered on current stats (+/- 20%)
        rolled_attack = max(1, int(random.uniform(self.attack * 0.8, self.attack * 1.2)))
        rolled_defence = max(0, int(random.uniform(other.defence * 0.8, other.defence * 1.2)))

        damage = max(1, rolled_attack - rolled_defence)
        other.health = max(0, other.health - damage)
        return f"{self.name} attacks {other.name} and deals {damage} damage!"

    def process_effects(self):
        expired = []
        for effect in self.effects:
            effect.duration -= 1
            if effect.duration <= 0:
                effect.remove(self)
                expired.append(effect)

        for effect in expired:
            self.effects.remove(effect)

    @Display.info
    def get_stats(self):
        return (
            f"Name: {self.name}\n"
            f"Health: {self.health}/{self.max_health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}"
        )


# ============================================================
# CREATURES & MONSTER
# ============================================================

class Creature(Entity):
    """A normal creature found within the maze with variable stats."""

    def __init__(self, creature_type, health, attack, defence, armour=None, name=None):
        # Introduce +/- 15% random variance to base stats
        v_health = int(health * random.uniform(0.85, 1.15))
        v_attack = max(1, int(attack * random.uniform(0.85, 1.15)))
        v_defence = max(0, int(defence * random.uniform(0.85, 1.15)))

        super().__init__(v_health, v_attack, v_defence, armour, name or creature_type)
        self.type = creature_type

    @Display.info
    def get_stats(self):
        return (
            f"Name: {self.name}\n"
            f"Type: {self.type}\n"
            f"Health: {self.health}/{self.max_health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}"
        )


class Shadowling(Creature):
    def __init__(self):
        super().__init__("Shadowling", 30, 7, 4)


class HollowStalker(Creature):
    def __init__(self):
        super().__init__("Hollow Stalker", 50, 11, 7)


class GloomWraith(Creature):
    def __init__(self):
        super().__init__("Gloom Wraith", 65, 13, 9)


class DuskStalker(Creature):
    def __init__(self):
        super().__init__("Dusk Stalker", 40, 15, 5)


class ObsidianSentinel(Creature):
    def __init__(self):
        super().__init__("Obsidian Sentinel", 85, 10, 14, armour="Stone Plates")


class Monster(Entity):
    """The central Monster entity in the game."""

    def __init__(self, position, health=130, attack=18, defence=11, armour="Living darkness", name="Nyctophobia"):
        super().__init__(health, attack, defence, armour, name)
        self.position = position
        self.items = []
        self.ai_enabled = True
        self.aggressive = True

    def choose_action(self, player, maze):
        if not self.alive:
            return

        if self.position == player.position:
            self.fight(player)
            return

        if not self.ai_enabled:
            return

        current_room = maze.get_room(self.position)
        if current_room is None:
            return

        possible_rooms = [
            room
            for room in [current_room.north, current_room.south, current_room.east, current_room.west]
            if room != 0
        ]

        if not possible_rooms:
            return

        if random.random() < 0.5:
            self.position = random.choice(possible_rooms)


# ============================================================
# PLAYER
# ============================================================

class Player(Entity):
    """The playable character."""

    def __init__(self, position, items, health=100, attack=10, defence=10, armour=None):
        super().__init__(health, attack, defence, armour, "Explorer")
        self.position = position
        self.items = items
        self.weapon = None

    @Display.choice_input(
        "Select direction to move",
        lambda self, maze: [
            direction
            for direction, room in [
                ("North", maze.get_room(self.position).north),
                ("South", maze.get_room(self.position).south),
                ("East", maze.get_room(self.position).east),
                ("West", maze.get_room(self.position).west),
            ]
            if room != 0
        ],
    )
    @Display.info
    def move(self, maze, choice=None):
        current_room = maze.get_room(self.position)
        if current_room is None:
            raise Exception("Player currently in invalid position")

        directions = [
            ("North", current_room.north),
            ("South", current_room.south),
            ("East", current_room.east),
            ("West", current_room.west),
        ]

        available = [(direction, room) for direction, room in directions if room != 0]
        direction, room_number = available[choice - 1]

        self.position = room_number
        return f"You move {direction.lower()} into Room {self.position}."

    @Display.info
    def pick_up(self, item):
        self.items.append(item)
        return f"You pick up the {item.name}."

    @Display.choice_input(
        "Select item to use",
        lambda self: [f"{item.name} — {item.description}" for item in self.items],
    )
    @Display.info
    def use_item(self, choice=None, target=None):
        if not self.items:
            return "You have no items."

        item = self.items[choice - 1]
        result_msg = item.use(self, target)

        if isinstance(item, (HealingItem, BuffItem, DebuffItem, AbilityItem)):
            if result_msg != "There is no target.":
                self.items.remove(item)

        return result_msg

    @Display.info
    def get_stats(self):
        item_names = ", ".join(item.name for item in self.items)
        return (
            f"Name: {self.name}\n"
            f"Health: {self.health}/{self.max_health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}\n"
            f"Position: {self.position}\n"
            f"Weapon: {self.weapon.name if self.weapon else 'None'}\n"
            f"Inventory: {item_names if item_names else 'Empty'}"
        )


class Human(Player):
    pass


# ============================================================
# ROOM & MAZE
# ============================================================

def generate_random_caption():
    """Generates procedural descriptions so rooms feel unique and non-repetitive."""
    atmospheres = [
        "The damp stone walls hum with a faint, unnatural resonance.",
        "Thick, suffocating shadows hang heavy in the chilly air.",
        "Dust motes dance lazily in the oppressive darkness.",
        "Slick, obsidian-like stone forms the chamber floor.",
        "Rusted chains dangle motionless from the arched ceiling.",
        "An ancient, geometric pattern is carved deep into the floor stone."
    ]
    sounds = [
        "A soft, rhythmic scratching echoes from somewhere nearby.",
        "You hear the distant dripping of water... or something thicker.",
        "A cold breeze whispers eerie, unintelligible sounds past your ears.",
        "An unsettling stillness settles over the entire chamber.",
        "Far below, something heavy drags across uneven rock."
    ]
    feelings = [
        "You feel a sinister gaze watching your every step.",
        "Your instincts scream at you to keep moving.",
        "The hairs on the back of your neck stand on end.",
        "A sudden chill pierces straight to your bones."
    ]

    return f"{random.choice(atmospheres)} {random.choice(sounds)} {random.choice(feelings)}"


class Room:
    def __init__(self, is_starting_room=False, north=0, south=0, east=0, west=0, items=None, creatures=None,
                 room_number=0, description=""):
        self.is_starting_room = is_starting_room
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.items = items if items is not None else []
        self.creatures = creatures if creatures is not None else []
        self.room_number = room_number
        self.description = description or generate_random_caption()

    @property
    def living_creatures(self):
        return [creature for creature in self.creatures if creature.alive]


class Maze:
    def __init__(self, rooms, starting_room, monster=None):
        self.rooms = rooms
        self.starting_room = starting_room
        self.monster = monster

    def get_room(self, room_number):
        for room in self.rooms:
            if room.room_number == room_number:
                return room
        return None

    def get_player_room(self, player):
        return self.get_room(player.position)


# ============================================================
# CSV IMPORT
# ============================================================

def import_maze(maze_name):
    creature_ids = {
        "S": Shadowling,
        "H": HollowStalker,
        "G": GloomWraith,
        "D": DuskStalker,
        "O": ObsidianSentinel,
    }

    item_ids = create_items()
    rooms = []

    with open(maze_name, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            room = Room(
                north=int(row["north"]),
                south=int(row["south"]),
                east=int(row["east"]),
                west=int(row["west"]),
                room_number=int(row["room_number"]),
            )

            # Creatures
            creature_data = row.get("creature", "").strip()
            if creature_data:
                for creature_id in creature_data.split(","):
                    creature_id = creature_id.strip().upper()

                    if creature_id == "N":
                        creature = Monster(position=room.room_number)
                    elif creature_id in creature_ids:
                        creature = creature_ids[creature_id]()
                    else:
                        raise ValueError(f"Unknown creature ID '{creature_id}' in room {room.room_number}")

                    room.creatures.append(creature)

            # Items
            item_data = row.get("items", "").strip()
            if item_data:
                for item_id in item_data.split(","):
                    item_id = item_id.strip().upper()

                    if item_id not in item_ids:
                        raise ValueError(f"Unknown item ID '{item_id}' in room {room.room_number}")

                    room.items.append(item_ids[item_id])

            rooms.append(room)

    if not rooms:
        raise ValueError("Maze CSV contains no rooms.")

    starting_room = rooms[0]
    starting_room.is_starting_room = True

    maze = Maze(rooms=rooms, starting_room=starting_room)

    monster = None
    for room in rooms:
        for creature in room.creatures:
            if isinstance(creature, Monster):
                if monster is not None:
                    raise ValueError("Maze cannot contain more than one Monster.")
                monster = creature

    maze.monster = monster
    return maze


# ============================================================
# GAME LOOPS & UI
# ============================================================

def display_room(player, maze):
    room = maze.get_player_room(player)
    if room is None:
        raise Exception("Player is in an invalid room.")

    print("\n" + "=" * Display.WIDTH)
    print(f"ROOM {room.room_number}")
    print("=" * Display.WIDTH)

    # Render 2D Visual Map
    render_room_ascii(room)

    print(room.description)

    if room.living_creatures:
        print("\nCreatures: " + ", ".join(creature.name for creature in room.living_creatures))

    if room.items:
        print("\nItems: " + ", ".join(item.name for item in room.items))

    if maze.monster and maze.monster.position == player.position and maze.monster.alive:
        print("\n!!! THE DARKNESS STIRS !!!")
        print(f"!!! {maze.monster.name} IS HERE !!!")

    print("=" * Display.WIDTH)


def pick_up_item(player, maze):
    room = maze.get_player_room(player)
    if not room.items:
        print_box("There are no items here.")
        return

    print("\nItems available:")
    for i, item in enumerate(room.items, 1):
        print(f"{i}. {item.name} — {item.description}")

    print("0. Cancel")

    while True:
        value = input("Choice: ")
        if value == "0":
            return
        if value.isdigit() and 1 <= int(value) <= len(room.items):
            item = room.items.pop(int(value) - 1)
            player.pick_up(item)
            return

        print("Please enter a valid choice.")


@Display.info
def print_box(message):
    return message


def battle(player, enemy):
    print("\n" + "#" * Display.WIDTH)
    print(f"BATTLE: {player.name} vs {enemy.name}")
    print("#" * Display.WIDTH)

    while player.alive and enemy.alive:
        player.process_effects()
        enemy.process_effects()

        print(f"\n{player.name}: {player.health}/{player.max_health} HP")
        print(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")

        print("\n1. Attack")
        print("2. Use Item")
        print("3. View Stats")

        choice = input("Choice: ")

        if choice == "1":
            player.fight(enemy)
        elif choice == "2":
            if not player.items:
                print_box("You have no items.")
                continue
            player.use_item(target=enemy)
        elif choice == "3":
            player.get_stats()
            enemy.get_stats()
            continue
        else:
            print("Please enter a valid choice.")
            continue

        if not enemy.alive:
            # Player Stat Gain Reward upon defeat
            stat_gain = random.choice(["attack", "defence"])
            amount = random.randint(1, 3)
            current_val = getattr(player, stat_gain)
            setattr(player, stat_gain, current_val + amount)

            print_box(
                f"{enemy.name} has been defeated!\nEmpowered by victory, your base {stat_gain.upper()} permanently increases by +{amount}!")
            return True

        if enemy.alive:
            enemy.fight(player)

        if not player.alive:
            print_box("You have been defeated.")
            return False

    return player.alive


def process_creatures(player, maze):
    room = maze.get_player_room(player)
    if room is None:
        return True

    for creature in list(room.living_creatures):
        if isinstance(creature, Monster):
            continue

        if not player.alive:
            return False

        battle(player, creature)

    return player.alive


def process_monster(player, maze):
    monster = maze.monster
    if monster is None:
        return True

    if monster.position == player.position and monster.alive:
        print_box(f"The darkness suddenly becomes completely silent...\n{monster.name} emerges from the darkness!")
        return battle(player, monster)

    return True


def monster_turn(player, maze):
    monster = maze.monster
    if monster is None or not monster.alive:
        return

    monster.choose_action(player, maze)
    if not player.alive:
        print_box("The darkness consumes you.")


def show_title_screen():
    """Displays the main title screen and waits for user to start."""
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


                       N Y C T O P H O B I A
             "The darkness is not empty beneath the maze..."
    """

    print("\n" + "=" * Display.WIDTH)
    print(title_art)
    print("=" * Display.WIDTH)
    print("\n┌──────────────────────────────────────────────────────────┐")
    print("│             [ PRESS ENTER TO ENTER THE DARKNESS ]        │")
    print("└──────────────────────────────────────────────────────────┘")
    input()


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    try:
        maze = import_maze("maze1.csv")
    except FileNotFoundError:
        print("Error: maze1.csv could not be found.")
        return

    # Show title screen before initializing the game state
    show_title_screen()

    player = Human(
        position=maze.starting_room.room_number,
        items=[],
        health=100,
        attack=10,
        defence=10,
    )

    print("\n" + "#" * Display.WIDTH)
    print("                    NYCTOPHOBIA")
    print("#" * Display.WIDTH)
    print("\nThe darkness is not empty.")
    print("Something is moving beneath the maze.")
    print("Find a way through the darkness and destroy its central creature.")

    while player.alive:
        display_room(player, maze)

        if not process_creatures(player, maze):
            break

        if maze.monster and maze.monster.position == player.position:
            if not process_monster(player, maze):
                break

            if not maze.monster.alive:
                print("\n" + "#" * Display.WIDTH)
                print("THE DARKNESS HAS FALLEN.")
                print("You have defeated Nyctophobia's central creature.")
                print("You escape the underground maze.")
                print("#" * Display.WIDTH)
                return

        print("\nWhat would you like to do?")
        print("1. Move")
        print("2. Pick Up Item")
        print("3. Use Item")
        print("4. View Stats")
        print("5. Quit")

        choice = input("Choice: ")

        if choice == "1":
            player.move(maze)
        elif choice == "2":
            pick_up_item(player, maze)
        elif choice == "3":
            if player.items:
                player.use_item()
            else:
                print_box("You have no items.")
        elif choice == "4":
            player.get_stats()
        elif choice == "5":
            print_box("You leave the maze.")
            return
        else:
            print("Please enter a valid choice.")

        if player.alive:
            monster_turn(player, maze)

    if not player.alive:
        print("\n" + "#" * Display.WIDTH)
        print("                    GAME OVER")
        print("The darkness has claimed you.")
        print("#" * Display.WIDTH)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame terminated.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")