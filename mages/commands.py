from mcapi import add_command
from core.mageworld import MageWorld
from core.commands import player_command
from . import Plugin
from core.exceptions import PlayerErrorMessage


@player_command(Plugin.lib_name, "tp")
def command_tp(mage, command):
    if command:
        mage.teleport(command[0])
    else:
        mage.player.sendMessage("/mages-tp <dimension>")
        mage.player.sendMessage(
            "Available Dimensions: {}".format(
                [name for name, dimension in MageWorld.plugins["mages"].servers]
            )
        )
