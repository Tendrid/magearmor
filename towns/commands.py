from mcapi import add_command
from core.mageworld import MageWorld
from core.commands import register_command
from . import Plugin
from core.exceptions import PlayerErrorMessage


@register_command(Plugin.lib_name, "claim")
def command_claim(mage, command):
    towns_plugin = MageWorld.plugins["towns"]
    bukkit_chunk = mage.location.getChunk()

    try:
        towns_plugin.claim(
            mage,
            bukkit_chunk.getX(),
            bukkit_chunk.getZ(),
            bukkit_chunk.getWorld().getUID(),
        )
    except PlayerErrorMessage as e:
        mage.player.sendMessage(e.message)

    # claimed_by = towns_plugin.get_town_by_coords(
    #     bukkit_chunk.getX(), bukkit_chunk.getZ()
    # )
    # if claimed_by:
    #     mage.player.sendMessage(
    #         "This plot is already clamed by {}".format(claimed_by.name)
    #     )
    #     return

    # player_town = towns_plugin.get_town_by_player_uuid(mage.uuid)
    # if not player_town:
    #     mage.player.sendMessage("You're not in a town!")
    #     return

    # mage.player.sendMessage("claimed")
    # towns_plugin.claim(
    #     mage.uuid,
    #     bukkit_chunk.getX(),
    #     bukkit_chunk.getZ(),
    #     bukkit_chunk.getWorld().getUID(),
    # )


@register_command(Plugin.lib_name, "unclaim")
def command_unclaim(mage, command):
    pass
