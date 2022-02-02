import unittest
from core.mageworld import MageWorld, SERVER
from . import Plugin
from mage import Mage
from core.plugin import BasePlugin
from core.storage import IndexStorage
from core.logs import debug_log


class TestMageFiles(unittest.TestCase):
    def test_mage_handler_loaded(self):
        # plugin has a valid name
        self.assertNotEquals(Plugin.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Plugin.lib_name], Plugin)

        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(plugin.config_files, ("default_mage", "config"))

        self.assertIsInstance(plugin.storage["mages"], IndexStorage)

    def test_mage(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        debug_log.debug(SERVER.getOfflinePlayers())

        #tendrid_id = "0d909fe4-ddcf-4127-ba42-5e539a20ac2c"
        tendrid_offline_id = "f68fc0fc-680a-3878-9307-6c909bbb1050"
        test_players = {}
        for player in SERVER.getOfflinePlayers():
            print(str(player.getUniqueId()))
            test_players[str(player.getUniqueId())] = player
        test_player = test_players.get(tendrid_offline_id)
        self.assertEquals(str(test_player.getUniqueId()), tendrid_offline_id)

        MageWorld.mage_join(tendrid_offline_id)
        test_mage = MageWorld.get_mage(tendrid_offline_id)
        self.assertEquals(test_mage.player, test_player)
