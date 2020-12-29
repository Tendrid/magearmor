import os
import logging
from mcapi import *


path = os.path.abspath(os.path.join("python-plugins", "storage"))
if not os.path.isdir(path):
    os.makedirs(path)


from core.mageworld import MageWorld

### Import Plugins #############################

import battles
import spells

import mages
import towns

MageWorld.load_plugin(mages.Plugin)
MageWorld.load_plugin(towns.Plugin)


### Import Commands #############################
# from mages import commands
from towns import commands


logging.info("~~~~~~~~~~~~~~~~~~~~~ Running MageArmor Tests ~~~~~~~~~~~~~~~~~~~~~")

import unittest

from core.tests import *
from towns.tests import *
from mages.tests import *

test_program = unittest.main(verbosity=2, exit=False)
logging.info("~~~~~~~~~~~~~~~~~~~~~~~~~~ Tests Complete ~~~~~~~~~~~~~~~~~~~~~~~~~~")
if len(test_program.result.failures) > 0:
    logging.error("Failed tests, shutting down server")
    SERVER.shutdown()
