from mcapi import SERVER

import unittest
from core.logs import debug_log
from core.mageworld import MageWorld
from core.storage import IndexStorage, BASE_DIR, HiveStorage
import mages

from core.hivemind import Telepath, TelepathicMessage

from org.bukkit import World
import json
import time

TEST_LIB = "test"

"""
TODO:
- test that config handler copies data

"""


class TestMageWorld(unittest.TestCase):
    def test_world(self):
        self.assertIsInstance(MageWorld.world, World)

    def test_mages_loaded(self):
        # mages is considered to be a required plugin
        self.assertIsInstance(MageWorld.plugins.get("mages"), mages.Plugin)

    def test_no_mage(self):
        self.assertEquals(MageWorld.get_mage("invalid-mage-uuid"), None)

class TestHiveStorage(unittest.TestCase):

    #hive1 = Telepath("localhost", 9009)

    def test_create_file(self):
        #TelepathicMessage.telepath = self.hive1
        # uuid, plugin_name, storage_name
        store = HiveStorage("0d909fe4-ddcf-4127-ba42-5e539a20ac2c", TEST_LIB, "test_store")


        store.set_data({"a": "b"})
        store.save()

        self.assertEquals(store.data["a"], "b")

class TestIndexStorage(unittest.TestCase):

    def test_b_create_file(self):
        store = IndexStorage(TEST_LIB, "test_a")

        test_obj = {
            "number": 12,
            "string": "here is my string",
            "list": ["a", "b", "c"],
            "dict": {"more": "data"},
            "bool": True,
        }

        file = store.add("file1")
        file.set_data(test_obj)
        file.save()

    def test_c_read_check(self):
        store = IndexStorage(TEST_LIB, "test_a")
        test_file = store.get("file1")
        debug_log.debug(test_file)
        
        self.assertEquals(test_file.data["number"], 12)
        self.assertEquals(test_file.data["string"], "here is my string")
        self.assertEquals(test_file.data["list"], ["a", "b", "c"])
        self.assertEquals(test_file.data["dict"]["more"], "data")
        self.assertEquals(test_file.data["bool"], True)

        self.assertEquals(store.get_by("number", 12)[0], test_file)
        self.assertEquals(len(store.get_by("number", "12")), 0)

        self.assertEquals(store.get_by("string", "here is my string")[0], test_file)

    def test_d_remove_file(self):
        store = IndexStorage(TEST_LIB, "test_a")
        store.remove("file1")
        
        #path = os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB, "test_a"))))
        #self.assertFalse(os.path.isfile("{}/file1.json".format(path)))
        #self.assertTrue(os.path.isfile("{}/file1.removed".format(path)))

    @classmethod
    def tearDownClass(cls):
        pass
        #shutil.rmtree(os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB,)))))
