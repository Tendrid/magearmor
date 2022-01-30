from functools import wraps
from core.logs import console_log
import json
import copy
import os

from worlds import Worlds

from core.exceptions import PlayerErrorMessage
from org.bukkit.event.player import PlayerJoinEvent
from org.bukkit.event.server import ServerCommandEvent
from org.bukkit.event import Listener, EventPriority
from org.bukkit.plugin import EventExecutor
from org.bukkit import Bukkit

SERVER = Bukkit.getServer()
PLUGIN = SERVER.getPluginManager().getPlugin('MinecraftPyServer')

#SERVER.dispatchCommand(SERVER.getConsoleSender, "command goes here");

# use this to schedule a task for the next tick
# BukkitScheduler.runTask(Plugin, Runnable)
# https://hub.spigotmc.org/javadocs/spigot/org/bukkit/scheduler/BukkitScheduler.html#runTask(org.bukkit.plugin.Plugin,java.lang.Runnable)

class EventListener(Listener):
    def __init__(self, func):
        self.func = func

    def execute(self, event):
        mage = None
        if hasattr(event, "getPlayer"):
            mage = MageWorld.plugins["mages"].mages.get_or_create(
                str(event.getPlayer().getUniqueId())
            )
        try:
            self.func(event, mage)
        except PlayerErrorMessage as e:
            if mage:
                mage.player.sendMessage(e.message)
            elif e.player and hasattr(e.player, "sendMessage"):
                e.player.sendMessage(e.message)
            else:
                console_log.error(e.message)

class Executor(EventExecutor):
    def execute(self, listener, event):
        listener.execute(event)


class WorldInstance(object):
    dimension = os.environ.get("SERVER_NAME")
    world = SERVER.getWorlds().get(0)
    players = {}
    config = {}
    plugins = {}
    listeners = []
    logger = console_log

    def __init__(self, *args, **kwargs):
        pass
        # self.logger.setLevel(logging.INFO)
        # logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

        # for player in SERVER.getOnlinePlayers():
        #     if self.players.get(str(player.getUniqueId())) is None:
        #         self.mage_join(player)

    def listen(self, event_type, execfunc, priority=EventPriority.NORMAL):
        # execfunc signature: execfunc(event)
        listener = EventListener(execfunc)
        executor = Executor()
        SERVER.getPluginManager().registerEvent(
            event_type, listener, priority, executor, PLUGIN
        )
        return listener

    def get_mage(self, player_id):
        return self.plugins["mages"].mages.get(player_id)

    def get_mage_by_name(self, player_name):
        mages = self.plugins["mages"].mages.get_by("name", player_name)
        if mages:
            return mages[0]
        else:
            return None

    def mage_join(self, player_uuid):
        mage = self.plugins["mages"].mages.get_or_create(player_uuid)
        self.players[player_uuid] = mage
        return mage

    """
    def player_joins(self, event):
        # SERVER.broadcastMessage("Player joined")
        self.mage_join(event.player)
        # print(event.getJoinMessage())
        # event.setJoinMessage("ur mom joind teh gam lol")
    """

    def register_config(self, lib_name, config_name):
        console_log.info("Registering config: {} {}".format(lib_name, config_name))
        path = os.path.abspath(
            os.path.join("python-plugins", lib_name, "config", config_name)
        )
        with open("{0}.json".format(path)) as fh:
            j = json.load(fh)
            self.config["{0}.{1}".format(lib_name, config_name)] = j

    def get_config(self, lib_name, config_name):
        config_name = "{0}.{1}".format(lib_name, config_name)
        config = self.config.get(config_name)
        if config:
            return copy.deepcopy(config)
        else:
            raise KeyError("Invalid config: {}".format(config_name))

    def load_plugin(self, lib):
        l = lib()
        self.plugins[l.lib_name] = l


MageWorld = WorldInstance()
