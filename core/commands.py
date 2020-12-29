from mcapi import add_command
from core.mageworld import MageWorld
from functools import wraps


def register_command(plugin_name, command):
    plugin = MageWorld.plugins[plugin_name]

    def wrapper(f):
        @wraps(f)
        def wrapped_f(bukkit_player, command):
            mage = MageWorld.get_mage(str(bukkit_player.getUniqueId()))
            return f(mage, list(command))

        # register wrapped command
        add_command(command, wrapped_f)

        return wrapped_f

    return wrapper
