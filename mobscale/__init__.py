from mcapi import asynchronous, synchronous, SERVER, PLUGIN
from core.mageworld import MageWorld
from core.plugin import BasePlugin, PluginData
from org.bukkit.persistence import PersistentDataType

from core.storage import IndexStorage

from collections import defaultdict
from core.exceptions import PlayerErrorMessage

from uuid import uuid4
from core.logs import debug_log, console_log

import math
from org.bukkit import NamespacedKey
from org.bukkit.event.hanging import HangingBreakEvent
from org.bukkit.entity import (
    Player,
    TNTPrimed,
    Monster,
    ArmorStand,
    AbstractVillager,
    Creeper,
    ItemFrame,
    LeashHitch,
    LivingEntity,
    Sheep,
    Vehicle,
)
from org.bukkit import Nameable
from org.bukkit.event.player.PlayerTeleportEvent import TeleportCause
from org.bukkit.entity.EntityType import WITHER
from org.bukkit.event.block import Action
from org.bukkit.inventory import EquipmentSlot

from core.collections import DOORS, TRAPDOORS, BUTTONS, ENTITY_ITEMS
from org.bukkit.Material import LEVER, NAME_TAG

from org.bukkit.event.entity.CreatureSpawnEvent import SpawnReason

class Plugin(BasePlugin):
    lib_name = "mobscale"
    config_files = ("config",)

    def calculate_level(self, location):
        xDistance = abs(location.getChunk().getX())
        zDistance = abs(location.getChunk().getZ())
        config = MageWorld.get_config(self.lib_name, "config")
        level = int(math.ceil(math.sqrt(math.pow(xDistance, 2) + math.pow(zDistance, 2)) / config["lvl_divider"]))
        return level

    def update_name(self, entity):
        store = entity.getPersistentDataContainer()
        key = NamespacedKey(PLUGIN, "mobscale_level")
        config = MageWorld.get_config(self.lib_name, "config")

        name = entity.getType().name().title().replace("_", " ")
        health = int(math.ceil(entity.getHealth()))

        level = store.get(key, PersistentDataType.INTEGER)
        if not level:
            level = self.calculate_level(entity.getLocation())
            store.set(key, PersistentDataType.INTEGER, level)
        else:
            entity.setCustomNameVisible(True)


        entity.setCustomName(unicode("{} [{}{} {}{}]".format(name, config['lvl_icon'], level, config['health_icon'], health )))


    def on_entity_damaged_by_entity(self, event, mage):
        damager = event.getDamager() if hasattr(event, "getDamager") else None
        entity = event.getEntity()

        # if damager is player:
        if isinstance(damager, Player) or isinstance(damager, TNTPrimed):
            console_log.info("mobscale mob hit!")
            config = MageWorld.get_config(self.lib_name, "config")
            mage = MageWorld.get_mage(str(damager.getUniqueId()))

            if isinstance(entity, Monster):
                self.update_name(entity)

    def on_creature_spawns(self, event, mage):
        entity = event.getEntity()
        if isinstance(entity, Monster):
            self.update_name(entity)
