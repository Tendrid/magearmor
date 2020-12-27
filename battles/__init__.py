# Import some modules
from mcapi import *
from core.mageworld import MageWorld

from time import sleep
from random import randint

from org.bukkit.event.block import BlockDamageEvent
from org.bukkit.event.inventory import InventoryClickEvent, InventoryType
from org.bukkit.event.entity import EntityDamageByEntityEvent

from org.bukkit.entity import Player, LivingEntity, Projectile, AbstractArrow

from org.bukkit import Material

from battles.config import *


"""
/py from mcapi import *; remove_event_listeners();

    on player respawns:
    on player equips armor:
    on player unequips armor:
    on entity damages entity:
"""
listeners = []

# PlayerItemDamageEvent(Player player, ItemStack what, int damage)


def battles_calc_armor(player):
    mage = MageWorld.get_mage(str(player.getUniqueId()))

    contents = mage.inventory.getArmorContents()
    player_armor = {x: [] for x in DamageTypes.keys()}

    for item in contents:
        if item:
            stats = ARMOR_TYPE_MAP.get(item.getType())
        else:
            stats = DefaultArmorTypes
        for name, stat in stats.items():
            player_armor[name].append(stat)
    armor = {}
    for a_type, modifiers in player_armor.items():
        if modifiers:
            armor[a_type] = float(sum(modifiers)) / len(modifiers)
        else:
            armor[a_type] = 0
    mage.armor = armor


from org.bukkit import NamespacedKey
from org.bukkit.inventory.meta.tags import ItemTagType


# e.damager
# e.entity
@asynchronous()
def entity_damage(e):
    if hasattr(e, "damager"):
        if isinstance(e.damager, LivingEntity):
            material = e.damager.getItemInHand().getType()
        elif isinstance(e.damager, AbstractArrow):
            item_meta = e.damager.itemStack.getItemMeta()
            tagContainer = item_meta.getCustomTagContainer()

            key = NamespacedKey(PLUGIN, "spell-id")
            print(tagContainer.getCustomTag(key, ItemTagType.INTEGER))

            material = e.damager.itemStack.getType()
        else:
            material = None

        armor_set = BATTLES_ARMOR_SETS.get(e.entity.getType(), DEFAULT_ARMOR_SET)

        modifiers = []
        for damage_class in DamageClasses:
            mod = DAMAGE_TYPE_MAP[damage_class].get(
                material, DefaultDamageTypes.get(damage_class)
            )
            if mod:
                modifiers.append(armor_set.get(mod, 0))
            else:
                modifiers.append(0)

        final_damage = e.getFinalDamage() + (
            e.damage * (sum(modifiers) / len(modifiers))
        )
        e.setDamage(final_damage)


from org.bukkit.inventory import ItemStack


def make_item():
    item = ItemStack(Material.WOODEN_SWORD, 1)
    item.setItemFlags()
    print(item.getPersistentDataContainer()())


@asynchronous()
def move_item(e):
    inventory = e.getClickedInventory()
    entity = inventory.getHolder()
    if isinstance(entity, Player) and e.getSlotType() == InventoryType.SlotType.ARMOR:
        battles_calc_armor(entity)


MageWorld.listen(EntityDamageByEntityEvent, entity_damage)
# MageWorld.listen(InventoryClickEvent, move_item)
