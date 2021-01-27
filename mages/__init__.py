from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin, PluginData
from mcapi import SERVER
from core.storage import IndexStorage
from mage import Mage
from dimension import Dimension
from core.mageworld import MageWorld

from com.denizenscript.depenizen.bukkit.bungee import BungeeBridge
from time import sleep

import logging


class Plugin(BasePlugin):
    lib_name = "mages"
    config_files = ("default_mage", "config")

    def on_load(self):
        self.mages = IndexStorage(self.lib_name, "mages", Mage)
        self.servers = IndexStorage(self.lib_name, "dimensions", Dimension)

        # for player in SERVER.getOnlinePlayers():
        #    self.mages.get_or_create(player)

    @asynchronous()
    def on_server_load(self, event, mage):
        self.refresh_servers()

    @asynchronous()
    def on_player_join(self, event, mage):
        self.refresh_servers()
        mage.login(event.getPlayer())

    def refresh_servers(self):
        while BungeeBridge.instance is None:
            logging.info("Bungee: waiting for bungee")
            sleep(1)
        for server_name in BungeeBridge.instance.knownServers:
            self.servers.get_or_create(str(server_name))
        MageWorld.dimension = self.servers.get(BungeeBridge.instance.serverName)
        return MageWorld.dimension

    @asynchronous()
    def on_player_quit(self, event, mage):
        self.refresh_servers()
        mage.logoff()
