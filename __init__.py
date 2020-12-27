import os
from mcapi import *


path = os.path.abspath(os.path.join("python-plugins", "storage"))
if not os.path.isdir(path):
    os.makedirs(path)

from core.mageworld import MageWorld

import battles
import spells

from mages.handler import Mages
from towns.handler import Towns

MageWorld.load_plugin(Mages)
MageWorld.load_plugin(Towns)


def claim_that_shit(player, command):
    player_location = player.getLocation()
    print("In claim func")
    if MageWorld.plugins["towns"].is_claimed(player_location.getChunk()):
        print("Already claimed")
        return
    player_uuid = str(player.getUniqueId())
    MageWorld.plugins["towns"].claim(player_uuid)


add_command("claim", claim_that_shit)


print("~~~~~~~~~~~~~~~~~~~~~ Running MageArmor Tests ~~~~~~~~~~~~~~~~~~~~~")
import unittest
from core.tests import *
from towns.tests import *
from mages.tests import *

suite = unittest.TestLoader()
tests = [
    TestMageWorld,
    TestDataStorage,
    TestIndexStorage,
    TestTownFiles,
    TestWilderness,
    TestMageFiles,
]
test_runner = []
for test in tests:
    test_runner.append(suite.loadTestsFromTestCase(test))

unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_runner))

if False:
    SERVER.shutdown()
