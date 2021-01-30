from mcapi import add_command
from core.mageworld import MageWorld
from core.commands import player_command, console_command
from . import Plugin
from core.exceptions import PlayerErrorMessage


def only_kingdoms():
    if MageWorld.dimension.uuid != "kingdoms":
        raise PlayerErrorMessage("Towns only available in kingdoms right now")


@player_command(Plugin.lib_name, "claim")
def command_claim(mage, command):
    only_kingdoms()
    bukkit_chunk = mage.location.getChunk()

    MageWorld.plugins["towns"].claim(
        mage,
        bukkit_chunk.getX(),
        bukkit_chunk.getZ(),
        bukkit_chunk.getWorld().getUID(),
    )
    mage.player.sendMessage("Plot claimed")


@player_command(Plugin.lib_name, "unclaim")
def command_unclaim(mage, command):
    only_kingdoms()
    bukkit_chunk = mage.location.getChunk()

    MageWorld.plugins["towns"].unclaim(
        mage,
        bukkit_chunk.getX(),
        bukkit_chunk.getZ(),
        bukkit_chunk.getWorld().getUID(),
    )
    mage.player.sendMessage("Plot unclaimed")


@player_command(Plugin.lib_name, "create")
def command_create(mage, command):
    only_kingdoms()
    MageWorld.plugins["towns"].create_town(mage)
    mage.player.sendMessage("Village created!")


@player_command(Plugin.lib_name, "name")
def command_name(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You must make a town before you can set the name")
    old_name = town.name
    town.set_name(" ".join(command))
    mage.player.sendMessage("{} renamed to {}".format(old_name, town.name))


@player_command(Plugin.lib_name, "permissions")
def command_permissions(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You do not own a town")

    if len(command) == 0:
        for permission, rank in town.permissions.iteritems():
            mage.player.sendMessage("{}: {}".format(permission, town.ranks[rank]))
    elif command[0] in town.permissions.keys():
        town.set_permission(command[0], command[1])
        mage.player.sendMessage("{}: {}".format(command[0], command[1]))
    else:
        raise PlayerErrorMessage("use /towns-permissions <permission_name> <rank_name>")


@player_command(Plugin.lib_name, "ranks")
def command_ranks(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You do not own a town")

    if len(command) == 0:
        for idx, rank in enumerate(town.ranks):
            mage.player.sendMessage("Rank {}: {}".format(idx, rank))
    elif command[0] in town.ranks:
        town.rename_rank(command[0], command[1])
        mage.player.sendMessage("{} renamed to {}".format(command[0], command[1]))
    else:
        raise PlayerErrorMessage("use /towns-rank <rank_name> <new_rank_name>")


@player_command(Plugin.lib_name, "member-add")
def command_add_member(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You do not own a town")

    if len(command) != 1:
        raise PlayerErrorMessage("use /towns-member-add <playername>")
    else:
        new_member = MageWorld.get_mage_by_name(command[0])
        if not new_member:
            raise PlayerErrorMessage("Unknown Player {}".format(command[0]))
        else:
            town.add_member(new_member)
            mage.player.sendMessage("{} added to {}".format(command[0], town.name))


@player_command(Plugin.lib_name, "member-remove")
def command_remove_member(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You do not own a town")

    if len(command) != 1:
        raise PlayerErrorMessage("use /towns-member-remove <playername>")
    else:
        new_member = MageWorld.get_mage_by_name(command[0])
        if not new_member:
            raise PlayerErrorMessage("Unknown Player {}".format(command[0]))
        else:
            town.remove_member(new_member)
            mage.player.sendMessage("{} removed from {}".format(command[0], town.name))


@player_command(Plugin.lib_name, "member-rank")
def member_rank(mage, command):
    only_kingdoms()
    town = MageWorld.plugins["towns"].get_town_by_player_uuid(mage.uuid)
    if not town:
        raise PlayerErrorMessage("You do not own a town")

    cmd_len = len(command)
    if cmd_len in [1, 2]:
        member = MageWorld.get_mage_by_name(command[0])
        if not member:
            raise PlayerErrorMessage("Unknown Player {}".format(command[0]))

        rank = command[1] if cmd_len == 2 else None
        new_rank = town.member_rank(member, rank)
        mage.player.sendMessage("{} rank: {}".format(member.name, new_rank))
    else:
        raise PlayerErrorMessage(
            "use /towns-member-rank <playername> <{}>".format(
                ", ".join(town.ranks[1:4])
            )
        )
