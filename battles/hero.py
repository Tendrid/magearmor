from core.mageworld import MageWorld
from core.exceptions import PlayerErrorMessage
from core.storage import HiveStorage
from modifier import ArmorModifier


class Hero(HiveStorage):
    @property
    def armor_set(self):
        return ArmorModifier(self.data)
