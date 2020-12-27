from core.mageworld import MageWorld
from core.storage import DataStorage
from mcapi import SERVER

from java.util import UUID


class Mage(DataStorage):
    __inventory = None
    __player = None

    armor = None

    @property
    def player(self):
        if self.__player is None:
            player = SERVER.getPlayer(self.uuid)
            if player is None:
                player = SERVER.getOfflinePlayer(UUID.fromString(self.uuid))
            self.__player = player
        return self.__player

    @property
    def inventory(self):
        if not self.__inventory:
            self.__inventory = self.player.getInventory()
        return self.__inventory
