import unittest
import os
from mcapi import SERVER
from java.util import UUID

from core.mageworld import MageWorld
from . import Plugin
from town import Town
from core.plugin import BasePlugin
from core.storage import BASE_DIR
from core.exceptions import PlayerErrorMessage

PLAYER_NOTCH = "069a79f4-44e9-4726-a5be-fca90e38aaf5"
PLAYER_TENDRID = "0d909fe4-ddcf-4127-ba42-5e539a20ac2c"


def activate_player(player_id):
    test_player = SERVER.getOfflinePlayer(UUID.fromString(player_id))
    MageWorld.mage_join(test_player)
    return MageWorld.get_mage(player_id)


class TestTownPermissions(unittest.TestCase):
    def test_permissions_exist(self):
        pass


class TestTownFiles(unittest.TestCase):
    def test_a1_town_handler_loaded(self):
        # plugin has a valid name
        self.assertNotEquals(Plugin.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Plugin.lib_name], Plugin)

        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(plugin.config_files, ("default_town", "wilderness", "config"))

    def test_town_set_data(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        path = os.path.abspath(os.path.join(*(BASE_DIR + ("towns", "towns"))))

        # test saved town file with limited deep data (like permissions)
        # make sure they get updated from default
        town = Town(
            "towns", "{}/00000000-0000-0000-0000-000000000001.json".format(path), {},
        )
        town.data["permissions"] = {"unknown": "permission", "build": 99}
        town.save()
        self.assertEquals(len(town.data["permissions"].keys()), 2)

        # load the town properly, and make sure the defaults are in there
        mage_town = plugin.towns.get("00000000-0000-0000-0000-000000000001")

        default_data = MageWorld.get_config(Plugin.lib_name, "default_town")
        self.assertEquals(
            len(mage_town.data["permissions"].keys()),
            len(default_data["permissions"].keys()) + 1,
        )

        self.assertEquals(mage_town.data["permissions"]["unknown"], "permission")
        self.assertEquals(mage_town.data["permissions"]["build"], 99)

        os.remove(mage_town.path)

    def test_town_id_from_mage(self):
        mage = activate_player(PLAYER_TENDRID)
        self.assertEquals(str(mage.player.getUniqueId()), PLAYER_TENDRID)

        plugin = MageWorld.plugins[Plugin.lib_name]
        plugin.load()
        town_obj = plugin.get_town_by_player_uuid(mage.uuid)

        self.assertNotEquals(town_obj, None)

        self.assertIsInstance(town_obj, Town)

        self.assertNotEquals(town_obj.uuid, None)

    def test_b1_town_create(self):
        mage = activate_player(PLAYER_NOTCH)
        plugin = MageWorld.plugins[Plugin.lib_name]

        # make sure player does not own a town
        self.assertEquals(plugin.get_town_by_player_uuid(mage.uuid), None)

        # Fail claim when not an owner
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            # XXX TODO: currently, there is no check against world ID for towns.
            plugin.claim(mage, 0, 0, "00000000-0000-0000-0000-000000000000")
        self.assertEquals(
            claim_exception.exception.message,
            "This plot is already clamed by Sanctuary",
        )

        # create a new town
        TestTownFiles.town = plugin.create_town(mage)

        # check that uuid in town.members
        self.assertEquals(TestTownFiles.town.data["owner"], PLAYER_NOTCH)

        # and rank is owner
        # todo (fix town members, so owner isnt a member, but mixin town.get_members from owner)

    def test_b2_town_name(self):
        with self.assertRaises(PlayerErrorMessage) as create_exception:
            TestTownFiles.town.set_name(
                "this town name is far too long and should not be allowed"
            )

        # check name is too long
        self.assertEquals(
            create_exception.exception.message,
            "That name is too long!  Please keep town names under 32 characters",
        )

        TestTownFiles.town.set_name("Notchville")
        self.assertEquals(TestTownFiles.town.data["name"], "Notchville")

    def test_b3_claim(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        mage = MageWorld.get_mage(PLAYER_NOTCH)

        # check no claims in town
        self.assertEquals(len(TestTownFiles.town.data["chunks"]), 0)

        CLAIM_X = 10000
        CLAIM_Z = 10000
        # claim plot
        plugin.claim(mage, CLAIM_X, CLAIM_Z, "00000000-0000-0000-0000-000000000000")

        self.assertEquals(len(TestTownFiles.town.data["chunks"]), 1)
        self.assertEquals(plugin.get_town_by_coords(10000, 10000), TestTownFiles.town)

        # test failure of claiming a chunk that is already claimed
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(mage, CLAIM_X, CLAIM_Z, "00000000-0000-0000-0000-000000000000")
        self.assertEquals(
            claim_exception.exception.message,
            "This plot is already clamed by Notchville",
        )

        # fail on corner chunks
        # top left
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(
                mage, CLAIM_X - 1, CLAIM_Z - 1, "00000000-0000-0000-0000-000000000000"
            )
        self.assertEquals(
            claim_exception.exception.message,
            "You can only claim adjacent chunks to your town",
        )

        # top right
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(
                mage, CLAIM_X - 1, CLAIM_Z + 1, "00000000-0000-0000-0000-000000000000"
            )
        self.assertEquals(
            claim_exception.exception.message,
            "You can only claim adjacent chunks to your town",
        )

        # bottom right
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(
                mage, CLAIM_X + 1, CLAIM_Z + 1, "00000000-0000-0000-0000-000000000000"
            )
        self.assertEquals(
            claim_exception.exception.message,
            "You can only claim adjacent chunks to your town",
        )

        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(
                mage, CLAIM_X - 1, CLAIM_Z + 1, "00000000-0000-0000-0000-000000000000"
            )
        self.assertEquals(
            claim_exception.exception.message,
            "You can only claim adjacent chunks to your town",
        )

        # claim attached plot (2nd claim)
        plugin.claim(mage, CLAIM_X, CLAIM_Z + 1, "00000000-0000-0000-0000-000000000000")
        self.assertEquals(plugin.get_town_by_coords(10000, 10001), TestTownFiles.town)

        # claim 7 more plots
        for i in range(1, 8):
            plugin.claim(
                mage, CLAIM_X + i, CLAIM_Z, "00000000-0000-0000-0000-000000000000"
            )

        # try to claim too many plots
        with self.assertRaises(PlayerErrorMessage) as claim_exception:
            plugin.claim(
                mage, CLAIM_X, CLAIM_Z - 1, "00000000-0000-0000-0000-000000000000"
            )
        self.assertEquals(
            claim_exception.exception.message,
            "Your town can only have up to 9 plots right now",
        )

    def test_b4_add_member(self):
        pass

    def test_z_remove_town(self):
        MageWorld.plugins[Plugin.lib_name].remove_town(TestTownFiles.town.uuid)

    @classmethod
    def tearDownClass(cls):
        # clean up test town
        if TestTownFiles.town:
            os.remove(TestTownFiles.town.path.replace(".json", ".removed"))


class TestWilderness(unittest.TestCase):
    def test_wilderness(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        wilderness_config = MageWorld.get_config(Plugin.lib_name, "wilderness")
        self.assertIsInstance(plugin.wilderness, Town)

        self.assertEquals(plugin.wilderness.name, wilderness_config["name"])
