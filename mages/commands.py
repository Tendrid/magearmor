from mcapi import add_command
from core.mageworld import MageWorld
from core.commands import register_command
from . import Plugin
from core.exceptions import PlayerErrorMessage


@register_command(Plugin.lib_name, "tp")
def command_tp(mage, command):
    if command:
        mage.teleport(command[0])
