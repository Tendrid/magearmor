from core.mageworld import MageWorld

from org.bukkit.event import EventPriority

from org.bukkit.event.server import ServerLoadEvent
from org.bukkit.event.player import (
    PlayerJoinEvent,
    PlayerQuitEvent,
    PlayerMoveEvent,
    PlayerHarvestBlockEvent,
)
from org.bukkit.event.entity import EntityDamageByEntityEvent
from org.bukkit.event.inventory import InventoryClickEvent
from org.bukkit.event.block import BlockBreakEvent, BlockCanBuildEvent

# from org.bukkit.event.block import BlockDamageEvent

CALLBACKS_METHODS = {
    "on_player_join": PlayerJoinEvent,
    "on_player_quit": PlayerQuitEvent,
    "on_server_load": ServerLoadEvent,
    "on_player_move": PlayerMoveEvent,
    "on_player_breaks_block": BlockBreakEvent,
    "on_player_harvest_block": PlayerHarvestBlockEvent,
    "on_block_can_build": BlockCanBuildEvent,
    "on_entity_damaged_by_entity": EntityDamageByEntityEvent,
    "on_inventoy_click": InventoryClickEvent,
}


class PluginData(object):
    lib_name = "unknown"

    def __init__(self, data):
        self.data = data


class BasePlugin(object):
    lib_name = "unknown"

    def __init__(self):
        self.load()
        self.on_load()
        self.register_callbacks()

    @property
    def config(self):
        return MageWorld.get_config(self.lib_name, "config")

    def register_callbacks(self):
        for method_name, event_handler in CALLBACKS_METHODS.items():
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    MageWorld.listen(event_handler, method)

    def on_load(self):
        pass

    def load(self):
        self._load_config()

    def _load_config(self):
        for config_name in self.config_files:
            MageWorld.register_config(self.lib_name, config_name)
        self.on_load_config()

    def on_load_config(self):
        pass
