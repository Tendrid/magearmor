from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin, PluginData
from mcapi import SERVER
from core.storage import IndexStorage
from mage import Mage


class Plugin(BasePlugin):
    lib_name = "mages"
    config_files = ("default_mage", "config")

    def on_load(self):
        self.mages = IndexStorage(self.lib_name, "mages", Mage)
        for player in SERVER.getOnlinePlayers():
            self.players.get_or_create(player)

    @asynchronous()
    def on_player_join(self, event, mage):
        mage.login()

    @asynchronous()
    def on_player_quit(self, event, mage):
        mage.logoff()
