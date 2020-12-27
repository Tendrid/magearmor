from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin, PluginData
from mcapi import SERVER
from core.storage import IndexStorage
from mage import Mage


class Mages(BasePlugin):
    lib_name = "mages"
    config_files = ("default_mage", "config")

    def on_load(self):
        self.mages = IndexStorage(self.lib_name, "mages", Mage)
        for player in SERVER.getOnlinePlayers():
            self.players.get_or_create(player)

    def on_player_join(self, event, mage):
        self.mage_join(event.player)

    def mage_join(self, player):
        player_uuid = str(player.getUniqueId())
        mage = self.mages.get_or_create(player_uuid)
        return mage
