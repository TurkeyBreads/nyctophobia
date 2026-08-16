import random
from display import Display, display_player_stats, display_entity_stats
from items import Weapon, HealingItem, BuffItem, DebuffItem, AbilityItem

class Entity:
    def __init__(self, health, attack, defence, armour=None, name="Entity"):
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defence = defence
        self.armour = armour
        self.name = name
        self.effects = []

    def change_stat(self, attribute, amount):
        if attribute == "attack":
            self.attack += amount
        elif attribute == "defence":
            self.defence += amount
        elif attribute == "health":
            self.health += amount

    @property
    def alive(self):
        return self.health > 0

    @Display.battle
    def fight(self, other):
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

    def get_stats(self):
        display_entity_stats(self)


class Creature(Entity):
    def __init__(self, creature_type, health, attack, defence, armour=None):
        variable_health = int(health * random.uniform(0.85, 1.15))
        variable_attack = max(1, int(attack * random.uniform(0.85, 1.15)))
        variable_defence = max(0, int(defence * random.uniform(0.85, 1.15)))
        super().__init__(variable_health, variable_attack, variable_defence, armour, creature_type)


class Shadowling(Creature):
    def __init__(self):
        super().__init__("Shadowling", 30, 7, 4)


class HollowStalker(Creature):
    def __init__(self):
        super().__init__("Hollow Stalker", 50, 11, 7)


class GloomWraith(Creature):
    def __init__(self):
        super().__init__("Gloom Wraith", 65, 13, 9)


class AbyssalHorror(Creature):
    def __init__(self):
        super().__init__("Abyssal Horror", 90, 16, 12)


class Monster(Entity):
    def __init__(self, position, health=130, attack=18, defence=11, name="Nycta"):
        super().__init__(health, attack, defence, "Living Darkness", name)
        self.position = position
        self.phase = 1

    def choose_action(self, player, maze, move_chance):
        current_room = maze.get_room(self.position)

        if (
                not self.alive
                or self.position == player.position
                or not current_room
        ):
            return False

        if random.random() < move_chance:
            possible_rooms = [
                r for r in [current_room.north, current_room.south, current_room.east, current_room.west, current_room.down, current_room.up]
                if r != 0
            ]
            if possible_rooms:
                self.position = random.choice(possible_rooms)

                return True

        return False

    def check_phase_transition(self):
        if self.health <= 0 and self.phase == 1:
            self.phase = 2
            self.max_health = int(self.max_health * 1.2)
            self.health = self.max_health
            self.attack += 6

            return True

        return False


class Player(Entity):
    def __init__(self, position, name="Adventurer", health=100, attack=10, defence=10):
        super().__init__(health, attack, defence, name=name)
        self.position = position
        self.items = []
        self.weapon = None
        self.kills = 0
        self.level = 1

    @Display.choice_input(
        "Select direction to move",
        lambda self, maze, *args, **kwargs: [
            d for d, r in [
                ("North", maze.get_room(self.position).north),
                ("South", maze.get_room(self.position).south),
                ("East", maze.get_room(self.position).east),
                ("West", maze.get_room(self.position).west),
                ("Descend Down Stairs", maze.get_room(self.position).down),
                ("Ascend Up Stairs", maze.get_room(self.position).up),
            ] if r != 0
        ]
    )
    @Display.info
    def move(self, maze, choice=None):
        room = maze.get_room(self.position)

        available = [(d, r) for d, r in [
            ("North", room.north), ("South", room.south),
            ("East", room.east), ("West", room.west),
            ("Down", room.down), ("Up", room.up)
        ] if r != 0]

        direction, target_room = available[choice - 1]
        self.position = target_room
        self.level = maze.get_room(self.position).level

        return f"You move {direction.lower()} into Room {self.position}."

    @Display.info
    def pick_up(self, item, auto_equip=True):
        self.items.append(item)
        msg = f"You pick up the {item.name}."

        if auto_equip and isinstance(item, Weapon):
            if not self.weapon or item.attack_bonus > self.weapon.attack_bonus:
                msg += " " + item.use(self)

        return msg

    @Display.choice_input(
        "Select item to use",
        lambda self, *args, **kwargs: [f"{i.name} — {i.description}" for i in self.items]
    )
    @Display.info
    def use_item(self, choice=None, target=None):
        if not self.items:
            return "You have no items."

        item = self.items[choice - 1]
        result = item.use(self, target)

        if isinstance(item, (HealingItem, BuffItem, DebuffItem, AbilityItem)):
            if result != "There is no target.":
                self.items.remove(item)

        return result

    def get_stats(self):
        display_player_stats(self)


if __name__ == "__main__":
    e = Entity(100, 10, 5)
    e.get_stats()

    e.change_stat("attack", 2)
    e.change_stat("defence", 2)
    e.change_stat("health", 5)
    print("e is alive" if e.alive else "e is dead")
    e.get_stats()

    creatures = [Shadowling(), HollowStalker(), GloomWraith(), AbyssalHorror()]
    for c in creatures:
        c.get_stats()
