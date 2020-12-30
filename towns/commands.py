from mcapi import add_command
from core.mageworld import MageWorld
from core.commands import register_command
from . import Plugin
from core.exceptions import PlayerErrorMessage


@register_command(Plugin.lib_name, "claim")
def command_claim(mage, command):
    bukkit_chunk = mage.location.getChunk()

    MageWorld.plugins["towns"].claim(
        mage,
        bukkit_chunk.getX(),
        bukkit_chunk.getZ(),
        bukkit_chunk.getWorld().getUID(),
    )


@register_command(Plugin.lib_name, "unclaim")
def command_unclaim(mage, command):
    pass


@register_command(Plugin.lib_name, "create")
def command_create(mage, command):
    MageWorld.plugins["towns"].create_town(mage)
