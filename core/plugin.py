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

from org.bukkit.event.hanging import HangingBreakEvent
from org.bukkit.event.hanging import HangingPlaceEvent
from org.bukkit.event.inventory import InventoryOpenEvent
from org.bukkit.event.vehicle import VehicleDestroyEvent
from org.bukkit.event.entity import CreatureSpawnEvent, PlayerLeashEntityEvent
from org.bukkit.event.block import BlockFromToEvent
from org.bukkit.event.player import (
    PlayerInteractEvent,
    PlayerTeleportEvent,
    PlayerInteractEntityEvent,
    AsyncPlayerChatEvent,
    PlayerBucketEmptyEvent,
    PlayerBucketFillEvent,
    PlayerArmorStandManipulateEvent,
)
from org.bukkit.event.entity import EntityExplodeEvent, EntityChangeBlockEvent
from org.bukkit.event.block import BlockPistonExtendEvent, BlockPistonRetractEvent

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
    "on_entity_breaks_hanging": HangingBreakEvent,
    "on_player_places_hanging": HangingPlaceEvent,
    "on_player_manipulate_armor_stand": PlayerArmorStandManipulateEvent,
    "on_player_opens_inventory": InventoryOpenEvent,
    "on_entity_destroys_vehicle": VehicleDestroyEvent,
    "on_player_empties_bucket": PlayerBucketEmptyEvent,
    "on_player_fills_bucket": PlayerBucketFillEvent,
    "on_creature_spawns": CreatureSpawnEvent,
    "on_liquid_spreads": BlockFromToEvent,
    "on_player_interact": PlayerInteractEvent,
    "on_player_interact_with_entity": PlayerInteractEntityEvent,
    "on_player_teleport": PlayerTeleportEvent,
    "on_entity_explode": EntityExplodeEvent,
    "on_entity_change_block": EntityChangeBlockEvent,
    "on_player_leash_entity": PlayerLeashEntityEvent,
    "on_piston_extend": BlockPistonExtendEvent,
    "on_piston_retract": BlockPistonRetractEvent,
    "on_player_chat": AsyncPlayerChatEvent,
}

from core.storage import IndexStorage

class BasePlugin(object):
    lib_name = "unknown"
    storage = {}
    storage_files = ()

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
        self._load_storage()

    def _load_config(self):
        for config_name in self.config_files:
            MageWorld.register_config(self.lib_name, config_name)
        self.on_load_config()
    
    def _load_storage(self):
        for storage_tup in self.storage_files:
            self.storage[storage_tup[0]] = IndexStorage(self.lib_name, *storage_tup)
        

    def on_load_config(self):
        pass
