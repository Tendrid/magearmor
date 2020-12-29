import unittest
from mcapi import SERVER
from core.mageworld import MageWorld
from . import Plugin
from mage import Mage
from core.plugin import BasePlugin
from core.storage import IndexStorage


class TestMageFiles(unittest.TestCase):
    def test_mage_handler_loaded(self):
        # plugin has a valid name
        self.assertNotEquals(Plugin.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Plugin.lib_name], Plugin)

        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(plugin.config_files, ("default_mage", "config"))

        self.assertIsInstance(plugin.mages, IndexStorage)

    def test_mage(self):
        plugin = MageWorld.plugins[Plugin.lib_name]

        tendrid_id = "0d909fe4-ddcf-4127-ba42-5e539a20ac2c"
        test_players = {}
        for player in SERVER.getOfflinePlayers():
            test_players[str(player.getUniqueId())] = player
        test_player = test_players[tendrid_id]

        self.assertEquals(str(test_player.getUniqueId()), tendrid_id)

        MageWorld.mage_join(test_player)
        test_mage = MageWorld.get_mage(tendrid_id)
        self.assertEquals(test_mage.player, test_player)
