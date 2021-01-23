from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin, PluginData
from mcapi import SERVER
from core.storage import IndexStorage
from mage import Mage
from dimension import Dimension

from com.denizenscript.depenizen.bukkit.bungee import BungeeBridge


class Plugin(BasePlugin):
    lib_name = "mages"
    config_files = ("default_mage", "config")

    def on_load(self):
        self.mages = IndexStorage(self.lib_name, "mages", Mage)
        self.servers = IndexStorage(self.lib_name, "dimensions", Dimension)

        # for player in SERVER.getOnlinePlayers():
        #    self.mages.get_or_create(player)

    @asynchronous()
    def on_player_join(self, event, mage):
        mage.login(event.getPlayer())
        self.refresh_servers()

    def refresh_servers(self):
        if BungeeBridge.instance:
            for server_name in BungeeBridge.instance.knownServers:
                self.servers.get_or_create(str(server_name))

    @asynchronous()
    def on_player_quit(self, event, mage):
        mage.logoff()
