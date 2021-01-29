import os
import logging
from mcapi import SERVER

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

# import spells

MageWorld.load_plugin(mages.Plugin)
MageWorld.load_plugin(towns.Plugin)
MageWorld.load_plugin(battles.Plugin)
# MageWorld.load_plugin(spells.Plugin)


### Import Commands #############################
# from mages import commands
from towns import commands
from mages import commands


### Run Tests ###################################
if os.environ.get("RUN_TESTS"):
    logging.info("~~~~~~~~~~~~~~~~~~~~~ Running MageArmor Tests ~~~~~~~~~~~~~~~~~~~~~")
    import unittest

    from core.tests import *
    from mages.tests import *
    from towns.tests import *
    from battles.tests import *

    test_program = unittest.main(verbosity=2, exit=False)
    logging.info("~~~~~~~~~~~~~~~~~~~~~~~~~~ Tests Complete ~~~~~~~~~~~~~~~~~~~~~~~~~~")
    if not test_program.result.wasSuccessful():
        logging.error("Failed tests, shutting down server")
        SERVER.shutdown()
