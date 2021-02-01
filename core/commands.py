from mcapi import add_command
from core.mageworld import MageWorld
from functools import wraps
from core.exceptions import PlayerErrorMessage

from org.bukkit import Bukkit
from org.bukkit.command import Command
from org.bukkit.command import ConsoleCommandSender

SERVER = Bukkit.getServer()

_commandMapField = SERVER.getClass().getDeclaredField("commandMap")
_commandMapField.setAccessible(True)
_commandMap = _commandMapField.get(SERVER)


class SpigotCommand(Command):
    def __init__(self, name, execfunc):
        Command.__init__(self, name)
        self.execfunc = execfunc
        self.setPermission("minecraft.command.save-all")

    def execute(self, caller, label, parameters):
        if isinstance(caller, ConsoleCommandSender):
            self.execfunc(caller, parameters)


def player_command(plugin_name, command):
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


def console_command(command):
    def wrapper(f):
        @wraps(f)
        def wrapped_f(console_sender, command):
            try:
                return f(list(command))
            except PlayerErrorMessage as e:
                console_sender.sendMessage(e.message)

        # register wrapped command
        _commandMap.register(
            "jycraft", SpigotCommand("mageadmin-{}".format(command), wrapped_f),
        )

        return wrapped_f

    return wrapper
