from functools import wraps
from mcapi import *
import logging
import json
import copy

from core.exceptions import PlayerErrorMessage

from org.bukkit.event.player import PlayerJoinEvent
from org.bukkit.event.server import ServerCommandEvent
from org.bukkit.event import EventPriority


class EventListener(Listener):
    def __init__(self, func):
        self.func = func

    def execute(self, event):
        mage = None
        if hasattr(event, "getPlayer"):
            mage = MageWorld.get_mage(str(event.getPlayer().getUniqueId()))
        try:
            self.func(event, mage)
        except PlayerErrorMessage as e:
            if mage:
                mage.player.sendMessage(e.message)
            else:
                logging.error(e.message)


class WorldInstance(object):
    world = SERVER.getWorlds().get(0)
    players = {}
    config = {}
    plugins = {}
    listeners = []
    logger = logging.getLogger("magearmor")

    def __init__(self, *args, **kwargs):
        # self.logger.setLevel(logging.INFO)
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

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
        logging.info("Registering config: {} {}".format(lib_name, config_name))
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
