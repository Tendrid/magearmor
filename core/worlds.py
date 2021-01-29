from org.bukkit import Bukkit
from org.bukkit.command import Command
from org.bukkit.command import ConsoleCommandSender
from core.storage import IndexStorage
import logging

SERVER = Bukkit.getServer()
WORLD = SERVER.getWorlds().get(0)

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


def save_all(caller, parameters):
    for name, storage in IndexStorage.codex.iteritems():
        logging.info("saving {}".format(name))
        storage.save_all()


_commandMap.register("jycraft", SpigotCommand("mageadmin-save-all", save_all))


class SpigotCommand(Command):
    def __init__(self, name, execfunc):
        Command.__init__(self, name)
        self.execfunc = execfunc

    def execute(self, caller, label, parameters):
        self.execfunc(caller, parameters)


class Worlds(object):
    pass
