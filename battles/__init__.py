from mcapi import asynchronous, synchronous
from core.plugin import BasePlugin, PluginData
from mcapi import SERVER
from core.storage import IndexStorage
from core.mageworld import MageWorld
from hero import Hero
from modifier import ArmorModifier, DamageModifier


from org.bukkit.entity import EntityType, Player, LivingEntity, AbstractArrow
from org.bukkit import Material
from org.bukkit.event.inventory import InventoryType
from org.bukkit.entity.EntityType import PLAYER

# dmg hits armor


class Plugin(BasePlugin):
    lib_name = "battles"
    config_files = (
        "config",
        "entity_armor",
        "item_armor",
        "material_armor_map",
        "weapon_map",
    )
    __default_armor = None
    __default_weapon = None

    def on_load(self):
        self.heros = IndexStorage(self.lib_name, "heros", Hero)
        self.load_entities()
        self.load_materials()
        self.load_weapons()

    def load_entities(self):
        # load all the entity armor modifiers
        self.entities = {}
        for entity_name, modifiers in MageWorld.get_config(
            self.lib_name, "entity_armor"
        ).iteritems():
            if not hasattr(EntityType, entity_name):
                raise AttributeError("Invalid entity type: {}".format(entity_name))
            self.entities[getattr(EntityType, entity_name)] = ArmorModifier(modifiers)

    def load_materials(self):
        # map armor materials to modifiers
        armor_types = MageWorld.get_config(self.lib_name, "item_armor")
        self.materials = {}
        for material_name, material_type in MageWorld.get_config(
            self.lib_name, "material_armor_map"
        ).iteritems():
            if not hasattr(Material, material_name):
                raise AttributeError("Invalid material type: {}".format(material_name))
            self.materials[getattr(Material, material_name)] = ArmorModifier(
                armor_types[material_type]
            )

    def load_weapons(self):
        # load all the weapon damage modifiers
        self.weapons = {}
        for material_name, damge_types in MageWorld.get_config(
            self.lib_name, "weapon_map"
        ).iteritems():
            if not hasattr(Material, material_name):
                raise AttributeError("Invalid material type: {}".format(material_name))
            self.weapons[getattr(Material, material_name)] = DamageModifier(damge_types)

    @property
    def default_armor(self):
        if not self.__default_armor:
            self.__default_armor = ArmorModifier(self.config["default_armor_set"])
        return self.__default_armor

    @property
    def default_weapon(self):
        if not self.__default_weapon:
            self.__default_weapon = DamageModifier({})
        return self.__default_weapon

    def battles_calc_armor(self, mage):
        hero = self.heros.get_or_create(mage.uuid)
        player_armor = {x: [] for x in self.config["damage_types"].keys()}

        modifiers = [
            self.materials.get(x.getType()) if x else self.default_armor
            for x in mage.inventory.getArmorContents()
        ]

        armor = sum(modifiers) / len(modifiers)

        hero = self.heros.get_or_create(mage.uuid)
        hero.set_data(armor.modifiers)
        hero.save()

    @asynchronous()
    def on_inventoy_click(self, event, mage):
        inventory = event.getClickedInventory()
        if hasattr(inventory, "getHolder"):
            entity = inventory.getHolder()
            if (
                isinstance(entity, Player)
                and event.getSlotType() == InventoryType.SlotType.ARMOR
            ):
                mage = MageWorld.get_mage(str(entity.getUniqueId()))
                self.battles_calc_armor(mage)

    def calculate_damage(self, armor, weapon, final_damage):
        modifiers = []
        for damage_class, damage_type in weapon.modifiers.items():
            mod = armor.modifiers.get(damage_type)
            if mod:
                modifiers.append(mod)
        sum_mod = sum(modifiers)
        if sum_mod == 0:
            return final_damage
        else:
            return final_damage + (final_damage * (sum(modifiers) / len(modifiers)))

    def on_entity_damaged_by_entity(self, event, mage):
        if hasattr(event, "damager"):
            if event.getEntityType() == PLAYER:
                hero = self.heros.get_or_create(str(event.entity.getUniqueId()))
                armor_set = hero.armor_set
            else:
                armor_set = self.entities.get(
                    event.entity.getType(), self.default_armor
                )

            if isinstance(event.damager, LivingEntity) and hasattr(
                event.damager, "getItemInHand"
            ):
                weapon = self.weapons.get(
                    event.damager.getItemInHand().getType(), self.default_weapon
                )
            else:
                weapon = self.default_weapon

            damage = event.getFinalDamage()

            final_damage = self.calculate_damage(armor_set, weapon, damage)

            event.setDamage(final_damage)
