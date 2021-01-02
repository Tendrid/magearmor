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


@register_command(Plugin.lib_name, "name")
def command_create(mage, command):
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You must make a town before you can set the name")
    old_name = town.name
    town.set_name(" ".join(command))
    mage.player.sendMessage("{} renamed to {}".format(old_name, town.name))
