from core.mageworld import MageWorld
from core.storage import DataStorage
from mcapi import SERVER

from java.util import UUID


class Mage(DataStorage):
    __inventory = None
    __player = None

    armor = None

    def login(self):
        self.__player = SERVER.getPlayer(self.uuid)

    def logoff(self):
        self.__player = SERVER.getOfflinePlayer(UUID.fromString(self.uuid))

    @property
    def player(self):
        if self.__player is None:
            self.login()
        if self.__player is None:
            self.logoff()
        return self.__player

    @property
    def inventory(self):
        if not self.__inventory:
            self.__inventory = self.player.getInventory()
        return self.__inventory
