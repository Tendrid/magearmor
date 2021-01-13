from mcapi import add_command
from core.mageworld import MageWorld
from functools import wraps
from core.exceptions import PlayerErrorMessage


def register_command(plugin_name, command):
    plugin = MageWorld.plugins[plugin_name]

    def wrapper(f):
        @wraps(f)
        def wrapped_f(bukkit_player, command):
            mage = MageWorld.get_mage(str(bukkit_player.getUniqueId()))
            try:
                return f(mage, list(command))
            except PlayerErrorMessage as e:
                if mage:
                    mage.player.sendMessage(e.message)
                elif e.player:
                    e.player.sendMessage(e.message)

        # register wrapped command
        add_command("{}-{}".format(plugin.lib_name, command), wrapped_f)

        return wrapped_f

    return wrapper
