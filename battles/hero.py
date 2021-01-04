from core.mageworld import MageWorld
from core.exceptions import PlayerErrorMessage
from core.storage import DataStorage
from modifier import ArmorModifier


class Hero(DataStorage):
    @property
    def armor_set(self):
        return ArmorModifier(self.data)
