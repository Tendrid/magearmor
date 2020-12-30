import unittest
from mcapi import SERVER
from java.util import UUID

from core.mageworld import MageWorld
from . import Plugin
from town import Town
from core.plugin import BasePlugin

from core.exceptions import PlayerErrorMessage

PLAYER_NOTCH = "069a79f4-44e9-4726-a5be-fca90e38aaf5"
PLAYER_TENDRID = "0d909fe4-ddcf-4127-ba42-5e539a20ac2c"


def activate_player(player_id):
    test_player = SERVER.getOfflinePlayer(UUID.fromString(player_id))
    MageWorld.mage_join(test_player)
    return MageWorld.get_mage(player_id)


class TestTownFiles(unittest.TestCase):
    def test_town_handler_loaded(self):
        # plugin has a valid name
        self.assertNotEquals(Plugin.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Plugin.lib_name], Plugin)

        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(plugin.config_files, ("default_town", "wilderness", "config"))

    def test_town_id_from_mage(self):
        mage = activate_player(PLAYER_TENDRID)
        self.assertEquals(str(mage.player.getUniqueId()), PLAYER_TENDRID)

        plugin = MageWorld.plugins[Plugin.lib_name]
        plugin.load()
        town_obj = plugin.get_town_by_player_uuid(mage.uuid)

        self.assertNotEquals(town_obj, None)

        self.assertIsInstance(town_obj, Town)

        self.assertNotEquals(town_obj.uuid, None)

    def test_set_owner(self):
        mage = activate_player(PLAYER_NOTCH)
        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(plugin.get_town_by_player_uuid(mage.uuid), None)

        # Fail claim when not an owner
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(mage, 0, 0, "SOME WORLD ID")
        self.assertEquals(
            claim_exception.exception.message,
            "This plot is already clamed by Sanctuary",
        )

        town = plugin.create_town(mage)
        with self.assertRaises(PlayerErrorMessage) as create_exception:
            town.set_name("this town name is far too long and should not be allowed")
        self.assertEquals(
            create_exception.exception.message,
            "That name is too long!  Please keep town names under 32 characters",
        )

        # claimed_by = plugin.get_town_by_coords(bukkit_chunk.getX(), bukkit_chunk.getZ())

        # check that town.owner == mage.uuid
        # check that uuid in town.members, and rank is owner
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
        plugin = MageWorld.plugins[Plugin.lib_name]
        wilderness_config = MageWorld.get_config(Plugin.lib_name, "wilderness")
        self.assertIsInstance(plugin.wilderness, Town)

        self.assertEquals(plugin.wilderness.name, wilderness_config["name"])
