import csv
# import random


class Display:
    """Utility class for handling game input and output."""

    WIDTH = 60

    @staticmethod
    def choice_input(question, choices):
        """
        Create a decorator that displays a numbered choice menu.

        Args:
            question: The question to display above the choices.
            choices: A function that returns the available choices.

        Returns:
            A decorator that handles user choice input.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                actual_choices = choices(*args, **kwargs)

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
        """
        Decorate a function to display its returned text in an information box.

        Args:
            func: The function whose returned text should be displayed.

        Returns:
            A decorated function that prints the returned text.
        """
        def wrapper(*args, **kwargs):
            """Display the function's returned text inside an information box."""
            text = func(*args, **kwargs)

            print(f"\n┌{'─' * (Display.WIDTH - 2)}┐")

            for line in str(text).split("\n"):
                print(f"│ {line:<{Display.WIDTH - 4}} │")

            print(f"└{'─' * (Display.WIDTH - 2)}┘")

            return text
        return wrapper

    @staticmethod
    def battle(func):
        """
        Decorate a function to display its text in battle mode.

        Args:
            func: The function whose returned text should be displayed.

        Returns:
            A decorated function that prints text with a battle prefix.
        """
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)

            print()

            for line in str(text).split("\n"):
                print(f"          /BATTLE/  {line}")

            return text
        return wrapper


class Room:
    """Represents a single room within the game's maze."""

    def __init__(
        self,
        is_starting_room=False,
        north=0,
        south=0,
        east=0,
        west=0,
        items=0,
        creatures=0,
        room_number=0
    ):
        """
        Initialise a room and its connections and contents.

        Args:
            is_starting_room: Whether this room is the starting room.
            north: The room number connected to the north.
            south: The room number connected to the south.
            east: The room number connected to the east.
            west: The room number connected to the west.
            items: Items currently present in the room.
            creatures: Creatures currently present in the room.
            room_number: The unique number identifying the room.
        """
        self.is_starting_room = is_starting_room
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.items = items
        self.creatures = creatures
        self.room_number = room_number


class Maze:
    """Represents the collection of rooms that make up the game maze."""

    def __init__(self, rooms: list[Room], starting_room: Room):
        """
        Initialise a maze with its rooms and starting room.

        Args:
            rooms: A list containing the rooms in the maze.
            starting_room: The room where the player begins the game.
        """
        self.rooms = rooms
        self.starting_room = starting_room

    def get_room(self, room_number: int):
        """
        Retrieve a room from its room number.

        Args:
            room_number: The room number to search for.

        Returns:
            The matching Room object, or None if no room is found.
        """
        for room in self.rooms:
            if room.room_number == room_number:
                return room

        return None


class Entity:
    """Represents a game entity with combat-related statistics."""

    def __init__(self, health, attack, defence, armour=None):
        """
        Initialise an entity with its combat statistics.

        Args:
            health: The entity's current health.
            attack: The entity's attack value.
            defence: The entity's defence value.
            armour: The armour equipped by the entity, if any.
        """
        self.health = health
        self.attack = attack
        self.defence = defence
        self.armour = armour

    def fight(self, other):
        """
        Make this entity attack another entity.

        Damage is calculated by subtracting the other entity's defence
        from this entity's attack. At least one point of damage is dealt.

        Args:
            other: The entity being attacked.

        Returns:
            The amount of damage dealt.
        """
        damage = max(1, self.attack - other.defence)
        other.health -= damage

        if other.health < 0:
            other.health = 0

        return damage

    @Display.info
    def get_stats(self):
        """
        Retrieve the entity's current combat statistics.

        Returns:
            A formatted string containing the entity's statistics.
        """
        return (
            f"Health: {self.health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}"
        )

    def set_health(self, health):
        """
        Set the entity's health value.

        Args:
            health: The new health value.
        """
        self.health = health

    def set_attack(self, attack):
        """
        Set the entity's attack value.

        Args:
            attack: The new attack value.
        """
        self.attack = attack

    def set_defence(self, defence):
        """
        Set the entity's defence value.

        Args:
            defence: The new defence value.
        """
        self.defence = defence


class Creature(Entity):
    """Represents a creature that inherits combat abilities from Entity."""

    def __init__(self, creature_type, health, attack, defence, armour=None):
        """
        Initialise a creature with its combat statistics.

        Args:
            creature_type: The creature's type.
            health: The creature's health.
            attack: The creature's attack value.
            defence: The creature's defence value.
            armour: The armour equipped by the creature, if any.
        """
        super().__init__(health, attack, defence, armour)
        self.type = creature_type

    @Display.info
    def get_stats(self):
        """
        Retrieve the creature's current combat statistics.

        Returns:
            A formatted string containing the creature's statistics.
        """
        return (
            f"Health: {self.health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}\n"
            f"Type: {self.type}"
        )


class Player(Entity):
    """Represents a playable character that can move through the maze."""

    def __init__(
        self,
        position,
        items,
        health,
        attack,
        defence,
        armour=None
    ):
        """
        Initialise a player with a position, inventory, and combat statistics.

        Args:
            position: The player's current position in the maze.
            items: Items associated with the player.
            health: The player's health.
            attack: The player's attack value.
            defence: The player's defence value.
            armour: The armour equipped by the player, if any.
        """
        super().__init__(health, attack, defence, armour)
        self.position = position
        self.items = items

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
        ]
    )
    def move(self, maze: Maze, choice=None):
        """
        Move the player to another room in the maze.

        Args:
            maze: The maze containing the player's current room.
            choice: The numbered direction selected by the player.

        Raises:
            Exception: If the player's current position is invalid.
        """
        current_room = maze.get_room(self.position)

        if current_room is None:
            raise Exception("Player currently in invalid position")

        directions = [
            ("North", current_room.north),
            ("South", current_room.south),
            ("East", current_room.east),
            ("West", current_room.west),
        ]

        available = [
            (direction, room)
            for direction, room in directions
            if room != 0
        ]

        direction, room_number = available[choice - 1]

        self.position = room_number

    @Display.info
    def get_stats(self):
        """
        Retrieve the player's current combat and player statistics.

        Returns:
            A formatted string containing the player's statistics.
        """
        return (
            f"Health: {self.health}\n"
            f"Attack: {self.attack}\n"
            f"Defence: {self.defence}\n"
            f"Armour: {self.armour if self.armour else 'No armour'}\n"
            f"Position: {self.position}\n"
            f"Items: {self.items}"
        )


class Human(Player):
    """Represents a human player character."""

    def __init__(
        self,
        position,
        items,
        health,
        attack,
        defence,
        armour=None
    ):
        """
        Initialise a human player.

        Args:
            position: The human player's starting position.
            items: Items associated with the human player.
            health: The human player's health.
            attack: The human player's attack value.
            defence: The human player's defence value.
            armour: The armour equipped by the human player, if any.
        """
        super().__init__(
            position,
            items,
            health,
            attack,
            defence,
            armour
        )


class Monster(Player):
    """Represents a monster character that inherits from Player."""

    def __init__(
        self,
        position,
        items,
        health,
        attack,
        defence,
        armour=None
    ):
        """
        Initialise a monster player.

        Args:
            position: The monster's starting position.
            items: Items associated with the monster.
            health: The monster's health.
            attack: The monster's attack value.
            defence: The monster's defence value.
            armour: The armour equipped by the monster, if any.
        """
        super().__init__(
            position,
            items,
            health,
            attack,
            defence,
            armour
        )


def import_maze(maze_name: str):
    """
    Import a maze from a CSV file.

    The CSV file is read as a collection of room records, with each
    record containing the room's directional connections and room number.

    Args:
        maze_name: The name or path of the CSV file containing the maze.

    Returns:
        A Maze object containing the imported rooms and starting room.
    """
    with open(maze_name, newline="") as f:
        dict_reader = csv.DictReader(f)

        records = [
            {key: int(value) for key, value in row.items()}
            for row in dict_reader
        ]

        maze = Maze(
            rooms=[
                Room(
                    north=record["north"],
                    south=record["south"],
                    east=record["east"],
                    west=record["west"],
                    room_number=record["room_number"],
                )
                for record in records
            ],

            starting_room=Room(
                is_starting_room=True,
                north=records[0]["north"],
                south=records[0]["south"],
                east=records[0]["east"],
                west=records[0]["west"],
                room_number=records[0]["room_number"],
            )
        )

    return maze


def main():
    maze1 = import_maze("maze1.csv")

    human = Human(
        position=maze1.starting_room.room_number,
        health=100,
        attack=10,
        defence=10,
        items=[]
    )

    while True:
        human.move(maze=maze1)
        human.get_stats()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
