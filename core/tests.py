from mcapi import SERVER

import unittest
from core.mageworld import MageWorld
from core.storage import DataStorage, IndexStorage, BASE_DIR
import mages

from org.bukkit import World
import os
import shutil
import json
import time

TEST_LIB = "test"


class TestMageWorld(unittest.TestCase):
    def test_world(self):
        self.assertIsInstance(MageWorld.world, World)

    def test_mages_loaded(self):
        # mages is considered to be a required plugin
        self.assertIsInstance(MageWorld.plugins.get("mages"), mages.Plugin)


class TestDataStorage(unittest.TestCase):
    def test_create_file(self):
        path = os.path.abspath(os.path.join(*(BASE_DIR + ("ds_test",))))
        os.makedirs(path)
        store = DataStorage("test", "{}/test.json".format(path), {"a": "b"})
        store.save()

        self.assertEquals(store.data["a"], "b")

        self.assertTrue(os.path.isfile("{}/test.json".format(path)))
        with open("{}/test.json".format(path)) as fh:
            j = json.load(fh)
        self.assertEquals(j.get("a"), "b")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.abspath(os.path.join(*(BASE_DIR + ("ds_test",)))))


class TestIndexStorage(unittest.TestCase):
    def test_a_create_dir(self):
        path = os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB, "test_a"))))
        store = IndexStorage(TEST_LIB, "test_a")
        self.assertTrue(os.path.isdir(path))

    def test_b_create_file(self):
        store = IndexStorage(TEST_LIB, "test_a")
        path = os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB, "test_a"))))

        test_obj = {
            "number": 12,
            "string": "here is my string",
            "list": ["a", "b", "c"],
            "dict": {"more": "data"},
            "bool": True,
        }

        store.add("file1", test_obj)

        self.assertTrue(os.path.isfile("{}/file1.json".format(path)))

    def test_c_read_check(self):
        store = IndexStorage(TEST_LIB, "test_a")
        test_file = store.get("file1")
        self.assertEquals(test_file.data["number"], 12)
        self.assertEquals(test_file.data["string"], "here is my string")
        self.assertEquals(test_file.data["list"], ["a", "b", "c"])
        self.assertEquals(test_file.data["dict"]["more"], "data")
        self.assertEquals(test_file.data["bool"], True)

    def test_d_remove_file(self):
        store = IndexStorage(TEST_LIB, "test_a")
        store.remove("file1")
        path = os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB, "test_a"))))
        self.assertFalse(os.path.isfile("{}/file1.json".format(path)))
        self.assertTrue(os.path.isfile("{}/file1.removed".format(path)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.abspath(os.path.join(*(BASE_DIR + (TEST_LIB,)))))
