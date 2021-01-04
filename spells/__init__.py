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


"""
    def on_entity_damaged_by_entity(self, event, mage):
        if hasattr(event, "damager"):
            if isinstance(event.damager, LivingEntity):
                material = event.damager.getItemInHand().getType()
            elif isinstance(event.damager, AbstractArrow):
                item_meta = event.damager.itemStack.getItemMeta()
                tagContainer = item_meta.getCustomTagContainer()

                key = NamespacedKey(PLUGIN, "spell-id")
                print(tagContainer.getCustomTag(key, ItemTagTypevent.INTEGER))

                material = event.damager.itemStack.getType()
            else:
                material = None

            armor_set = BATTLES_ARMOR_SETS.get(
                event.entity.getType(), DEFAULT_ARMOR_SET
            )

            modifiers = []
            for damage_class in DamageClasses:
                mod = DAMAGE_TYPE_MAP[damage_class].get(
                    material, DefaultDamageTypes.get(damage_class)
                )
                if mod:
                    modifiers.append(armor_set.get(mod, 0))
                else:
                    modifiers.append(0)

            final_damage = event.getFinalDamage() + (
                event.damage * (sum(modifiers) / len(modifiers))
            )
            event.setDamage(final_damage)
"""

MageWorld.listen(EntityShootBowEvent, shoot)
