class Effect:
    def __init__(self, name, attribute, amount, duration):
        self.name = name
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def apply(self, entity):
        entity.change_stat(self.attribute, self.amount)

    def remove(self, entity):
        entity.change_stat(self.attribute, -self.amount)


class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, user, target=None):
        return f"{user.name} uses {self.name}."


class HealingItem(Item):
    def __init__(self, name, description, healing):
        super().__init__(name, description)
        self.healing = healing

    def use(self, user, target=None):
        old_health = user.health
        user.health = min(user.max_health, user.health + self.healing)

        return f"{user.name} uses {self.name} and restores {user.health - old_health} HP."


class Weapon(Item):
    def __init__(self, name, description, attack_bonus):
        super().__init__(name, description)
        self.attack_bonus = attack_bonus

    def use(self, user, target=None):
        if hasattr(user, 'weapon') and user.weapon is self:
            return f"{user.name} is already wielding the {self.name}."

        if hasattr(user, 'weapon') and user.weapon is not None:
            user.attack -= user.weapon.attack_bonus

        user.weapon = self
        user.attack += self.attack_bonus

        return f"{user.name} equips the {self.name}, attack +{self.attack_bonus}."


class BuffItem(Item):
    def __init__(self, name, description, attribute, amount, duration):
        super().__init__(name, description)
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def use(self, user, target=None):
        effect = Effect(self.name, self.attribute, self.amount, self.duration)
        effect.apply(user)
        user.effects.append(effect)

        return f"{user.name} uses {self.name}, {self.attribute} +{self.amount} for {self.duration} turns."


class DebuffItem(Item):
    def __init__(self, name, description, attribute, amount, duration):
        super().__init__(name, description)
        self.attribute = attribute
        self.amount = amount
        self.duration = duration

    def use(self, user, target=None):
        if target is None:
            return "There is no target."

        effect = Effect(self.name, self.attribute, -self.amount, self.duration)
        effect.apply(target)
        target.effects.append(effect)

        return f"{target.name}'s {self.attribute} is reduced by {self.amount} for {self.duration} turns."


class AbilityItem(Item):
    def __init__(self, name, description, damage, effect=None):
        super().__init__(name, description)
        self.damage = damage
        self.effect = effect

    def use(self, user, target=None):
        if target is None:
            return "There is no target."

        target.health = max(0, target.health - self.damage)

        if self.effect:
            self.effect.apply(target)
            target.effects.append(self.effect)

        return f"{user.name} uses {self.name}, dealing {self.damage} damage to {target.name}!"


def create_items():
    return {
        "W": Weapon("Shadow Blade", "A weapon forged from condensed darkness.", 8),
        "W2": Weapon("Abyssal Cleaver", "A heavy blade carved from void stone.", 14),
        "L": HealingItem("Light Fragment", "Restores health.", 35),
        "L2": HealingItem("Elixir of Life", "Deeply restores lost health.", 70),
        "B": BuffItem("Flare", "Temporarily increases attack.", "attack", 7, 3),
        "B2": BuffItem("Shadow Ward", "Temporarily boosts defence.", "defence", 8, 3),
        "D": DebuffItem("Bright Powder", "Weakens enemy defence.", "defence", 5, 3),
        "X": AbilityItem("Flash Bomb", "Deals direct damage.", 25),
        "X2": AbilityItem("Void Blast", "Unleashes raw force for massive damage.", 50)
    }
