from core.mageworld import MageWorld
from core.storage import DataStorage
from mcapi import SERVER

from java.util import UUID


SERVER_ROLE_ADMIN = "admin"
SERVER_ROLE_MOD = "mod"

from com.denizenscript.depenizen.bukkit.bungee import BungeeBridge

from com.denizenscript.depenizen.bukkit.bungee.packets.out import (
    ExecuteCommandPacketOut,
)

from org.bukkit.inventory import ItemStack


class Mage(DataStorage):
    __inventory = None
    __player = None

    armor = None

    def login(self, player=None):
        self.__player = player or SERVER.getPlayer(self.uuid)
        self.load()
        self.load_inventory()

    def logoff(self):
        self.save_inventory()
        self.save()
        self.__player = SERVER.getOfflinePlayer(UUID.fromString(self.uuid))

    @property
    def player(self):
        if self.__player is None:
            self.login()
        if self.__player is None:
            self.logoff()
        return self.__player

    @property
    def name(self):
        return self.player.name

    @property
    def location(self):
        return self.player.getLocation()

    @property
    def inventory(self):
        return self.player.getInventory()

    def load_inventory(self):
        inventory = []
        for stack in self.data["inventory"]:
            if stack:
                inventory.append(ItemStack.deserializeBytes(stack))
            else:
                inventory.append(stack)
        self.inventory.setContents(inventory)

    def save_inventory(self):
        self.data["inventory"] = []
        for stack in self.inventory.getContents():
            if stack:
                self.data["inventory"].append(list(stack.serializeAsBytes()))
            else:
                self.data["inventory"].append(None)

    def teleport(self, dimension_name):
        # adjust players location on target server
        adjust_cmd = 'ex bungee {} {{ - adjust <p@{}> "location:<l@0.5,100,0.5,0,0,world>" }}'.format(
            dimension_name, self.uuid
        )
        SERVER.dispatchCommand(SERVER.getConsoleSender(), adjust_cmd)

        # send command to bungee
        cmd = ExecuteCommandPacketOut("send {} {}".format(self.name, dimension_name))
        BungeeBridge.instance.sendPacket(cmd)
