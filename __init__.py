from mcapi import SERVER
import os
from core.logs import console_log

### Initialize Directories ######################
path = os.path.abspath(os.path.join("python-plugins", "storage"))
if not os.path.isdir(path):
    os.makedirs(path)


### Import Core World ###########################
from core.mageworld import MageWorld

### Import Plugins ##############################
import mages
import towns
import battles
import mobscale

### Import Telepath #############################
from core.hivemind import Telepath

# import spells

MageWorld.load_plugin(mages.Plugin)
MageWorld.load_plugin(towns.Plugin)
MageWorld.load_plugin(battles.Plugin)
MageWorld.load_plugin(mobscale.Plugin)
# MageWorld.load_plugin(spells.Plugin)

Telepath.start()

### Import Commands #############################
# from mages import commands
from towns import commands
from mages import commands

### Import Admin ################################
from core import admin

### Run Tests ###################################
if os.environ.get("RUN_TESTS"):
    console_log.info(
        "~~~~~~~~~~~~~~~~~~~~~ Running MageArmor Tests ~~~~~~~~~~~~~~~~~~~~~"
    )
    import unittest

    from core.tests import *
    from mages.tests import *
    from towns.tests import *
    from battles.tests import *

    test_program = unittest.main(verbosity=2, exit=False)
    console_log.info(
        "~~~~~~~~~~~~~~~~~~~~~~~~~~ Tests Complete ~~~~~~~~~~~~~~~~~~~~~~~~~~"
    )
    if not test_program.result.wasSuccessful():
        console_log.error("Failed tests, shutting down server")
        SERVER.shutdown()
