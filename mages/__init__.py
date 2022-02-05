from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin
from mcapi import SERVER
from mage import Mage
from dimension import Dimension
from core.mageworld import MageWorld

#from com.denizenscript.depenizen.bukkit.bungee import BungeeBridge
from time import sleep

from core.logs import debug_log, console_log

from org.bukkit.event.inventory import InventoryType
from org.bukkit.entity import Player

from core.hivemind import HiveChat


class Plugin(BasePlugin):
    lib_name = "mages"
    config_files = ("default_mage", "config")
    storage_files = (["mages", Mage], ["dimensions", Dimension])

    #def on_load(self):

    #    # for player in SERVER.getOnlinePlayers():
    #    #    self.mages.get_or_create(player)

    #@asynchronous()
    #def on_server_load(self, event, mage):
    #    self.refresh_servers()

    @asynchronous()
    def on_player_join(self, event, mage):
        #self.refresh_servers()
        mage.login(event.getPlayer())
        event.setJoinMessage(None)

    """
    def refresh_servers(self):
        #while BungeeBridge.instance is None:
        #    console_log.info("Bungee: waiting for bungee")
        #    sleep(1)
        #for server_name in BungeeBridge.instance.knownServers:
        #    self.servers.get_or_create(str(server_name))
        #MageWorld.dimension = self.servers.get(BungeeBridge.instance.serverName)
        return MageWorld.dimension
    """

    @asynchronous()
    def on_player_quit(self, event, mage):
        #self.refresh_servers()
        mage.logoff()
        event.setQuitMessage(None)

    @synchronous()
    def on_player_chat(self, event, mage):
        HiveChat(player_name=mage.name, message=event.message).send()
        #dimension_names = [
        #    uuid
        #    for uuid, server in MageWorld.plugins["mages"].storage["servers"]
        #    if server != MageWorld.dimension
        #]
        #for dimension in dimension_names:
        #    announce_cmd = 'ex bungee {} {{ - announce "<&lt>{}<&gt> {}" }}'.format(
        #        dimension, mage.name, event.message
        #    )

        #    SERVER.dispatchCommand(SERVER.getConsoleSender(), announce_cmd)

    def on_inventoy_click(self, event, mage):
        inventory = event.getClickedInventory()
        if inventory and inventory.getType() is InventoryType.PLAYER:
            in_hand = event.getCursor()
            in_slot = event.getCurrentItem()
            if in_hand != in_slot:
                player = event.getInventory().getHolder()
                if isinstance(player, Player):
                    mage = self.storage['mages'].get(str(player.getUniqueId()))
                    debug_log.debug(
                        "{} replaced {} with {}".format(mage.name, in_slot, in_hand)
                    )
                    #mage.save_inventory()
