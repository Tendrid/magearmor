import unittest
from mcapi import SERVER
from core.mageworld import MageWorld
from handler import Towns
from town import Town
from core.plugin import BasePlugin


class TestTownFiles(unittest.TestCase):
    def test_town_handler_loaded(self):
        # plugin has a valid name
        self.assertNotEquals(Towns.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Towns.lib_name], Towns)

        plugin = MageWorld.plugins[Towns.lib_name]

        self.assertEquals(plugin.config_files, ("default_town", "wilderness", "config"))

    def test_town_id_from_mage(self):
        tendrid_id = "0d909fe4-ddcf-4127-ba42-5e539a20ac2c"
        test_players = {}
        for player in SERVER.getOfflinePlayers():
            test_players[str(player.getUniqueId())] = player
        test_player = test_players[tendrid_id]

        self.assertEquals(str(test_player.getUniqueId()), tendrid_id)

        MageWorld.mage_join(test_player)
        test_mage = MageWorld.get_mage(tendrid_id)
        self.assertEquals(test_mage.player, test_player)

        plugin = MageWorld.plugins[Towns.lib_name]
        plugin.load()
        town_obj = plugin.get_town_by_player_uuid(test_mage.uuid)

        self.assertNotEquals(town_obj, None)

        self.assertIsInstance(town_obj, Town)

        self.assertNotEquals(town_obj.uuid, None)

    def test_set_owner(self):
        pass

    def test_add_member(self):
        pass

    def test_create_town(self):
        pass
        # claim chunk, and create new town
        # check town is created
        # check only one claim in town
        # check claim in town is type center

    def test_chunk_claimed(self):
        # test failure of claiming a chunk that is already claimed
        pass

    def test_claim_available_chunk(self):
        # test claim a chunk in an already created town
        pass

    def test_claim_chunk_not_connected(self):
        pass
        # claim chunk not connected, and fail
        # claim outpost not connected and pass


class TestWilderness(unittest.TestCase):
    def test_wilderness(self):
        plugin = MageWorld.plugins[Towns.lib_name]
        wilderness_config = MageWorld.get_config(Towns.lib_name, "wilderness")
        self.assertIsInstance(plugin.wilderness, Town)

        self.assertEquals(plugin.wilderness.name, wilderness_config["name"])
