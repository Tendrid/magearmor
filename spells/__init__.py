from mcapi import *
from core.mageworld import MageWorld

from org.bukkit.event.entity import EntityShootBowEvent
from org.bukkit.persistence import PersistentDataType
from org.bukkit import NamespacedKey

from org.bukkit.inventory.meta.tags import ItemTagType


def shoot(e):
    arrow = e.getArrowItem()
    item_meta = arrow.getItemMeta()
    key = NamespacedKey(PLUGIN, "spell-id")
    item_meta.getCustomTagContainer().setCustomTag(key, ItemTagType.INTEGER, 12345)

    arrow.setItemMeta(item_meta)
    # container = arrow.getPersistentDataContainer()
    # container.set(
    #    NamespacedKey("MinecraftPyServer", "spell_id"), 1234, PersistentDataType.INTEGER
    # )

    # arrow.setPortalCooldown(1239999)


MageWorld.listen(EntityShootBowEvent, shoot)
