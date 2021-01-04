import unittest
from core.mageworld import MageWorld
from . import Plugin
from core.plugin import BasePlugin
from core.storage import IndexStorage

from modifier import ArmorModifier, DamageModifier

from org.bukkit import Material
from org.bukkit.entity import EntityType


class TestBattlesFiles(unittest.TestCase):
    def test_battles_handler_loaded(self):
        self.assertNotEquals(Plugin.lib_name, BasePlugin.lib_name)

        # plugin has loaded
        self.assertIsInstance(MageWorld.plugins[Plugin.lib_name], Plugin)

        plugin = MageWorld.plugins[Plugin.lib_name]

        self.assertEquals(
            plugin.config_files,
            (
                "config",
                "entity_armor",
                "item_armor",
                "material_armor_map",
                "weapon_map",
            ),
        )

    def test_battles_entities(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        self.assertTrue(len(plugin.entities.keys()) > 0)
        for entity_type, armor_modifiers in plugin.entities.items():
            self.assertIsInstance(entity_type, EntityType)
            self.assertIsInstance(armor_modifiers, ArmorModifier)

    def test_battles_materials(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        self.assertTrue(len(plugin.materials.keys()) > 0)
        for material_type, armor_modifiers in plugin.materials.items():
            self.assertIsInstance(material_type, Material)
            self.assertIsInstance(armor_modifiers, ArmorModifier)

    def test_battles_weapons(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        self.assertTrue(len(plugin.weapons.keys()) > 0)
        for material_type, damage_modifiers in plugin.weapons.items():
            self.assertIsInstance(material_type, Material)
            self.assertIsInstance(damage_modifiers, DamageModifier)

    def test_default_armor_set(self):
        plugin = MageWorld.plugins[Plugin.lib_name]
        self.assertIsInstance(plugin.default_armor, ArmorModifier)

    def test_calculate_damage(self):
        # armor: ArmorModifier
        # weapon: DamageModifier
        # final_damage: Float
        plugin = MageWorld.plugins[Plugin.lib_name]

        dmg = plugin.calculate_damage(
            ArmorModifier({}), DamageModifier({"physical": None}), 5.0
        )
        self.assertEquals(dmg, 5.0)

        dmg = plugin.calculate_damage(
            plugin.materials[Material.CHAINMAIL_CHESTPLATE],
            DamageModifier({"elemental": "energy", "physical": None}),
            5.0,
        )
        self.assertEquals(dmg, 0.0)
