from core.mageworld import MageWorld
from core.exceptions import PlayerErrorMessage
from core.storage import HiveStorage
from mcapi import SERVER
from core.logs import console_log
from java.util import UUID


SERVER_ROLE_ADMIN = "admin"
SERVER_ROLE_MOD = "mod"

#from com.denizenscript.depenizen.bukkit.bungee import BungeeBridge

#from com.denizenscript.depenizen.bukkit.bungee.packets.out import (
#    ExecuteCommandPacketOut,
#)

from org.bukkit.inventory import ItemStack


class Mage(HiveStorage):
    __inventory = None
    __player = None

    armor = None

    def login(self, player=None):
        self.__player = player or SERVER.getPlayer(self.uuid)
        if self.__player:
            self.data["name"] = player.getName()
            if MageWorld.dimension:
                self.data["dimension"] = MageWorld.dimension
            self.load_inventory()

    def logoff(self):
        if self.__player:
            if self.data.get("dimension") is None:
                console_log.warn(
                    "mage.dimension was None on {}!  This should never happen!".format(
                        self.__player
                    )
                )
            elif self.data.get("dimension") == MageWorld.dimension:
                self.save_inventory()
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
        return self.player.getName()

    @property
    def location(self):
        return self.player.getLocation()

    @property
    def inventory(self):
        return self.player.getInventory()

    def set_data(self, data):
        # set town defaults
        self.data = MageWorld.get_config("mages", "default_mage")
        # override defaults with town settings
        self.data.update(data)

        # add new second level items
        for k, v in MageWorld.get_config("mages", "default_mage").items():
            if not self.data.get(k):
                self.data[k] = v
            elif type(self.data[k]) is dict:
                v.update(self.data[k])
                self.data[k] = v
        if MageWorld.dimension:
            self.data["dimension"] = MageWorld.dimension
        if self.player.isOnline():
            print("PLAYER IS ONLINE")
            self.load_inventory()

    def load_inventory(self):
        inventory = []
        for stack in self.data["inventory"]:
            if stack:
                inventory.append(ItemStack.deserializeBytes(stack))
                #inventory.append(ItemStack.deserialize(stack))

            else:
                inventory.append(stack)
        self.inventory.setContents(inventory)

    def save_inventory(self):
        self.data["inventory"] = []
        for stack in self.inventory.getContents():
            if stack:
                #print(stack.toString())
                self.data["inventory"].append(list(stack.serializeAsBytes()))
                #self.data["inventory"].append(stack.serialize())
            else:
                self.data["inventory"].append(None)
        self.save()

    def teleport(self, dimension_name):
        dimension_names = [uuid for uuid, server in MageWorld.plugins["mages"].storage["servers"]]
        if dimension_name not in dimension_names:
            raise PlayerErrorMessage("Unknown Dimension")
        # save _before_ we do any teleporting to avoid race conditions
        self.data["dimension"] = dimension_name
        self.save_inventory()
        # adjust players location on target server
        # REMOVED ADJUST FOR NOW
        # adjust_cmd = 'ex bungee {} {{ - adjust <p@{}> "location:<l@0.5,76,0.5,0,0,world>" }}'.format(
        #     dimension_name, self.uuid
        # )
        # SERVER.dispatchCommand(SERVER.getConsoleSender(), adjust_cmd)

        # send command to bungee
        cmd = ExecuteCommandPacketOut("send {} {}".format(self.name, dimension_name))
        BungeeBridge.instance.sendPacket(cmd)

    def __repr__(self):
        return "{} {}".format(self.__class__, self.name)
