DAMAGE_TYPES = [
    "bludgeoning",
    "hacking",
    "slashing",
    "piercing",
    "acid",
    "fire",
    "cold",
    "energy",
    "necrotic",
    "divine",
    "arcane",
]

DAMAGE_CLASSES = ["physical", "elemental", "magic"]

DEFAULT_MODIFIER = 0


class ArmorModifier(object):
    def __init__(self, modifiers):
        self.__modifiers = {}
        for dt in DAMAGE_TYPES:
            self.__modifiers[dt] = modifiers.get(dt, DEFAULT_MODIFIER)

    def __radd__(self, armor_modifier):
        if armor_modifier == 0:
            return self
        else:
            return self.__add__(armor_modifier)

    def __add__(self, other):
        if type(other) is not ArmorModifier:
            raise TypeError(
                "unsupported operand type(s) for +: '{}' and 'ArmorModifier'".format(
                    type(other)
                )
            )

        return ArmorModifier(
            {mod: self.__modifiers[mod] + other.modifiers[mod] for mod in DAMAGE_TYPES}
        )

    def __div__(self, num):
        if type(num) is not int:
            raise TypeError(
                "unsupported operand type(s) for /: '{}' and 'ArmorModifier'".format(
                    type(armor_modifier)
                )
            )

        return ArmorModifier({mod: self.__modifiers[mod] / num for mod in DAMAGE_TYPES})

    def __iter__(self):
        for dt in DAMAGE_TYPES:
            yield self.__modifiers.get(dt, DEFAULT_MODIFIER)

    @property
    def modifiers(self):
        return {mod: round(val, 2) for mod, val in self.__modifiers.items()}


class DamageModifier(object):
    def __init__(self, modifiers):
        self.__modifiers = {}
        for dc in DAMAGE_CLASSES:
            self.__modifiers[dc] = modifiers.get(dc)

        # default physical attack is bludgeoning
        if (
            self.__modifiers["physical"] is None
            and modifiers.get("physical", False) is not None
        ):
            self.__modifiers["physical"] = "bludgeoning"

    @property
    def modifiers(self):
        return self.__modifiers
