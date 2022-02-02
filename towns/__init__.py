from mcapi import asynchronous, synchronous, SERVER
from core.mageworld import MageWorld
from core.plugin import BasePlugin

from town import Town, TOWN_CLAIM_TYPE_NORMAL

from core.storage import IndexStorage

from collections import defaultdict
from core.exceptions import PlayerErrorMessage

from uuid import uuid4

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


def hack_func_for_overworld(thing):
    if MageWorld.dimension is not None:
        is_kingdoms = MageWorld.dimension != "kingdoms"
    else:
        is_kingdoms = True

    return (
        thing.getWorld().getName() in ["world_nether", "world_the_end"] or is_kingdoms
    )


class Wilderness(Town):
    def __init__(self, *args, **kwargs):
        self.set_data(MageWorld.get_config("towns", "wilderness"))

    def add_chunk(self, *args, **kwargs):
        pass

#self.player_data = IndexStorage(self.lib_name, "players")
#self.towns = IndexStorage(self.lib_name, "towns", Town)

class Plugin(BasePlugin):
    lib_name = "towns"
    config_files = ("default_town", "wilderness", "config")
    storage_files = (["players"], ["towns", Town])
    __wilderness = None

    claims_by_loc = defaultdict(dict)
    towns_by_player = {}

    @property
    def wilderness(self):
        if not self.__wilderness:
            self.__wilderness = Wilderness()
        return self.__wilderness

    def get_town_by_coords(self, x, z):
        return self.claims_by_loc[x].get(z)

    def player_town(self, uuid):
        player_data = self.storage["players"].get_or_create(mage.uuid)

    def get_town_by_player_uuid(self, player_uuid):
        return self.towns_by_player.get(player_uuid)

    def claim(self, mage, x, z, world_uuid, plot_type=TOWN_CLAIM_TYPE_NORMAL):
        # check if claim already owned
        # check if player is in town

        claimed_by = self.get_town_by_coords(x, z)
        if claimed_by:
            raise PlayerErrorMessage(
                "This plot is already clamed by {}".format(claimed_by.name)
            )

        town = self.get_town_by_player_uuid(mage.uuid)
        if not town:
            town = self.create_town(mage)

        chunk_count = len(town.data["chunks"])
        if plot_type == TOWN_CLAIM_TYPE_NORMAL and chunk_count > 0:
            # check surrounding plots
            surrounding_pattern = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            claim_fail = True
            for _x, _z in surrounding_pattern:
                town_check = self.get_town_by_coords(x + _x, z + _z)
                if town_check == town:
                    claim_fail = False

            if claim_fail:
                raise PlayerErrorMessage(
                    "You can only claim adjacent chunks to your town"
                )
        base_claim_count = MageWorld.get_config(self.lib_name, "config")[
            "base_claim_count"
        ]
        if chunk_count >= (town.data["bonus_chunks"] + base_claim_count):
            raise PlayerErrorMessage(
                "Your town can only have up to {} plots right now".format(
                    town.data["bonus_chunks"] + base_claim_count
                )
            )

        town.add_chunk(
            int(x), int(z), str(world_uuid), plot_type, mage.uuid,
        )

        self.claims_by_loc[x][z] = town
        self.storage["towns"].get(town.uuid).save()
        self.dynmap_update_chunk(int(x), int(z))

    def unclaim(self, mage, x, z, world_uuid):
        claimed_by = self.get_town_by_coords(x, z)
        if not claimed_by:
            raise PlayerErrorMessage("This plot not clamed")
        town = self.get_town_by_player_uuid(mage.uuid)
        if town != claimed_by:
            raise PlayerErrorMessage("You do not have permission to unclaim this plot")

        town.remove_chunk(int(x), int(z), str(world_uuid))

        del self.claims_by_loc[x][z]
        self.storage["towns"].get(town.uuid).save()
        self.dynmap_update_chunk(int(x), int(z))

    def create_town(self, mage):
        player_town = self.get_town_by_player_uuid(mage.uuid)
        if player_town:
            raise PlayerErrorMessage(
                "You're already the owner of {}".format(player_town.name)
            )

        town = self.storage["towns"].add(str(uuid4()))
        town.set_owner(mage)
        town.save()
        self.towns_by_player[mage.uuid] = town
        return town

    def remove_town(self, uuid):
        self.storage["towns"].remove(uuid)

    # def on_load_config(self):
    #     towns_default = MageWorld.get_config(self.lib_name, "towns_default")
    #     towns = MageWorld.get_config(self.lib_name, "towns")
    #     self.config = towns_default.update(towns)

    def dynmap_update_chunk(self, chunk_x, chunk_z, reset=False):
        x = chunk_x * 16
        z = chunk_z * 16
        town = self.claims_by_loc.get(chunk_x, {}).get(chunk_z)
        chunk_id = "chunk_{}_{}".format(chunk_x, chunk_z)
        if town and not reset:
            out = []
            out.append("dmarker addcorner {} 0 {} world".format(x, z))
            out.append("dmarker addcorner {} 0 {} world".format(x + 16, z))
            out.append("dmarker addcorner {} 0 {} world".format(x + 16, z + 16))
            out.append("dmarker addcorner {} 0 {} world".format(x, z + 16))
            out.append('dmarker addarea id:{} "{}"'.format(chunk_id, town.name))
            out.append(
                "dmarker updatearea id:{} fillcolor:21B9DB color:52C2F2 opacity:0.0 fillopacity:0.3".format(
                    chunk_id
                )
            )
            for cmd in out:
                SERVER.dispatchCommand(SERVER.getConsoleSender(), cmd)
        else:
            SERVER.dispatchCommand(
                SERVER.getConsoleSender(), "dmarker deletearea id:{}".format(chunk_id)
            )

    def dynmap_reset_town(self, town):
        for chunk in town.data["chunks"]:
            self.dynmap_update_chunk(chunk[0], chunk[1], True)
            self.dynmap_update_chunk(chunk[0], chunk[1])

    def on_load(self):
        for town_uuid, town in self.storage["towns"]:
            if town.data["owner"]:
                self.towns_by_player[town.data["owner"]] = town
            for chunk in town.data.get("chunks"):
                self.claims_by_loc[chunk[0]][chunk[1]] = town
        # run towns_fix_cuboids
        # run towns_update_dynmap_all_towns
        for uuid, town in self.storage["towns"]:
            self.dynmap_reset_town(town)

    @asynchronous()
    def on_player_move(self, event, mage):
        if hack_func_for_overworld(mage.player):
            return
        if event.getFrom().getChunk() != event.getTo().getChunk():
            to_chunk = event.getTo().getChunk()
            to_town = self.claims_by_loc[to_chunk.getX()].get(to_chunk.getZ())
            from_chunk = event.getFrom().getChunk()
            from_town = self.claims_by_loc[from_chunk.getX()].get(from_chunk.getZ())
            if to_town != from_town:
                if to_town:
                    town = to_town
                else:
                    town = self.wilderness
                rank_idx = town.get_player_rank(mage.uuid)
                try:
                    rank = town.ranks[rank_idx]
                except ValueError:
                    rank = "Unknown"
                mage.player.sendTitle(
                    town.name,
                    "Rank: {} PvP: {}".format(
                        rank, "Enabled" if town.get_rule("pvp") else "Disabled"
                    ),
                )

    def on_player_join(self, event, mage):
        town = self.get_town_by_player_uuid(mage.uuid)
        if town:
            self.dynmap_reset_town(town)

    def on_player_quit(self, event, mage):
        town = self.get_town_by_player_uuid(mage.uuid)
        if town:
            town.save()
            self.dynmap_reset_town(town)

    def on_player_breaks_block(self, event, mage):
        # print(">> BlockBreakEvent")
        if hack_func_for_overworld(mage.player):
            return
        block = event.getBlock()
        bukkit_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if town and not self.check_town_permission(mage, town, "build"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def on_block_can_build(self, event, mage):
        # print(">> BlockCanBuildEvent")
        if hack_func_for_overworld(mage.player):
            return

        block = event.getBlock()
        bukkit_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if mage and not self.check_town_permission(mage, town, "build"):
            event.setBuildable(False)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def check_town_permission(self, mage, town, permission):
        # config = MageWorld.get_config(self.lib_name, "config")
        # if mage.has_role("admin")
        return town.get_player_rank(mage.uuid) >= town.data["permissions"].get(
            permission, 9
        )

    def on_entity_breaks_hanging(self, event, mage):
        # check for build role
        # print(">> HangingBreakEvent")

        hanging_entity = event.getEntity()
        if hack_func_for_overworld(hanging_entity):
            return
        player = None
        if hasattr(event, "getRemover"):
            player = event.getRemover()
        if event.getCause() == HangingBreakEvent.RemoveCause.ENTITY and isinstance(
            player, Player
        ):
            mage = MageWorld.get_mage(str(player.getUniqueId()))

            bukkit_chunk = hanging_entity.getLocation().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if town and not self.check_town_permission(mage, town, "build"):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to build in {}".format(town.name),
                    player,
                )
        else:
            # not a player
            event.setCancelled(True)

    def on_player_places_hanging(self, event, mage):
        # check for build role
        # print(">> HangingPlaceEvent")
        hanging_entity = event.getEntity()
        if hack_func_for_overworld(hanging_entity):
            return
        bukkit_chunk = hanging_entity.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if town and not self.check_town_permission(mage, town, "build"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def on_player_manipulate_armor_stand(self, event, mage):
        # check for build role
        # print(">> PlayerArmorStandManipulateEvent")
        armor_stand_entity = event.getRightClicked()
        if hack_func_for_overworld(armor_stand_entity):
            return

        bukkit_chunk = armor_stand_entity.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if town and not self.check_town_permission(mage, town, "build"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def on_player_opens_inventory(self, event, mage):
        # check for chests role
        # print(">> InventoryOpenEvent")
        holder = event.getInventory().getHolder()
        if hack_func_for_overworld(mage.player):
            return
        if holder and hasattr(holder, "getLocation"):
            bukkit_chunk = holder.getLocation().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if town and not self.check_town_permission(mage, town, "chests"):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to open chests in {}".format(town.name)
                )

    def on_entity_destroys_vehicle(self, event, mage):
        # check for build role
        # print(">> VehicleDestroyEvent")
        player = event.getAttacker()
        cart_entity = event.getVehicle()
        if hack_func_for_overworld(cart_entity):
            return
        if isinstance(player, Player):
            mage = MageWorld.get_mage(str(player.getUniqueId()))
            bukkit_chunk = cart_entity.getLocation().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if town and not self.check_town_permission(mage, town, "build"):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to build in {}".format(town.name),
                    player,
                )
        else:
            # not a player
            event.setCancelled(True)

    def on_player_empties_bucket(self, event, mage):
        # check for build role
        # print(">> PlayerBucketEmptyEvent")
        block = event.getBlock()
        if hack_func_for_overworld(block):
            return

        bukkit_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if mage and not self.check_town_permission(mage, town, "build"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def on_player_fills_bucket(self, event, mage):
        # print(">> PlayerBucketFillEvent")
        block = event.getBlock()
        if hack_func_for_overworld(block):
            return

        bukkit_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if mage and not self.check_town_permission(mage, town, "build"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "You do not have permission to build in {}".format(town.name)
            )

    def on_entity_damaged_by_entity(self, event, mage):
        # check for pve flag
        # print(">> EntityDamageByEntityEvent")

        damager = event.getDamager() if hasattr(event, "getDamager") else None
        target = event.getEntity()
        if hack_func_for_overworld(target):
            return

        # if damager is player:
        if isinstance(damager, Player) or isinstance(damager, TNTPrimed):
            mage = MageWorld.get_mage(str(damager.getUniqueId()))

            location = target.getLocation()
            bukkit_chunk = location.getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )

            if isinstance(target, Monster):
                # killing monsters is ok
                pass
            elif isinstance(target, Player):
                # check pvp flag
                if not town.get_rule("pvp"):
                    event.setCancelled(True)
                    raise PlayerErrorMessage(
                        "PvP is forbidden in {}".format(town.name), mage.player,
                    )
            elif isinstance(target, ArmorStand):
                if not self.check_town_permission(mage, town, "build"):
                    event.setCancelled(True)
                    raise PlayerErrorMessage(
                        "You do not have permission to build in {}".format(town.name),
                        mage.player,
                    )
            # elif isinstance(target, AbstractVillager):
            #     if not town.get_rule("pve"):
            #         event.setCancelled(True)
            #         raise PlayerErrorMessage(
            #             "PvE is forbidden in {}".format(town.name), mage.player,
            #         )
            else:
                if not self.check_town_permission(mage, town, "pve"):
                    event.setCancelled(True)
                    raise PlayerErrorMessage(
                        "PvE is forbidden in {}".format(town.name), mage.player,
                    )
        elif isinstance(damager, Creeper):
            location = target.getLocation()
            bukkit_chunk = location.getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if isinstance(target, ArmorStand):
                if not town.get_rule("creeper"):
                    # dont let creepers kill ArmorStand if rule
                    event.setCancelled(True)
            elif not isinstance(target, Player) and not isinstance(target, Monster):
                # creepers can kill players and other monsters
                event.setCancelled(True)

    def on_creature_spawns(self, event, mage):
        # check mob spawn
        # print(">> EntitySpawnEvent")
        entity = event.getEntity()
        if hack_func_for_overworld(entity):
            return

        location = event.getLocation()
        bukkit_chunk = location.getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if town:
            if (
                hasattr(event, "getSpawnReason")
                and event.getSpawnReason() == SpawnReason.BUILD_WITHER
                and not town.get_rule("wither")
            ):
                event.setCancelled(True)
            if isinstance(entity, Monster) and not town.get_rule("mobspawn"):
                event.setCancelled(True)

    # lever: check block type is lever abstract
    # trapdoor: check if block type is trapdoor abstract
    # button: check if block type is button abstract
    # door: check if block type is door abstract
    def on_player_interact(self, event, mage):
        # Action.RIGHT_CLICK_BLOCK, Action.PHYSICAL, Action.LEFT_CLICK_BLOCK
        # print(">> PlayerInteractEvent")
        if hack_func_for_overworld(mage.player):
            return

        action = event.getAction()
        if action == Action.RIGHT_CLICK_BLOCK:
            # check if armor stand
            block = event.getClickedBlock()
            bukkit_chunk = block.getLocation().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            material = block.getType()
            if material == LEVER and not self.check_town_permission(
                mage, town, "levers"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to use levers in {}".format(town.name)
                )
            elif material in TRAPDOORS and not self.check_town_permission(
                mage, town, "trapdoors"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to use trap doors in {}".format(
                        town.name
                    )
                )
            elif material in BUTTONS and not self.check_town_permission(
                mage, town, "buttons"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to use buttons in {}".format(town.name)
                )
            elif material in DOORS and not self.check_town_permission(
                mage, town, "doors"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to use doors in {}".format(town.name)
                )
            # check for armor stand placement last
            elif (
                not self.check_town_permission(mage, town, "build")
                and mage.player.inventory.getItemInMainHand().getType() in ENTITY_ITEMS
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to build in {}".format(town.name)
                )

    def on_player_interact_with_entity(self, event, mage):
        # name print(">> PlayerInteractEntityEvent")
        if hack_func_for_overworld(mage.player):
            return
        hand = event.getHand()
        if hand == EquipmentSlot.HAND:
            entity = event.getRightClicked()
            bukkit_chunk = entity.getLocation().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )

            if (
                isinstance(entity, Nameable)
                and mage.inventory.getItemInMainHand().getType() == NAME_TAG
                and not self.check_town_permission(mage, town, "pve")
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage("PvE is forbidden in {}".format(town.name))

            # check if using an armor stand
            if isinstance(entity, ItemFrame) and not self.check_town_permission(
                mage, town, "build"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "You do not have permission to build in {}".format(town.name)
                )

            # check if unleashing animal
            if isinstance(entity, LeashHitch) and not self.check_town_permission(
                mage, town, "pve"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage("PvE is forbidden in {}".format(town.name))

            # check if they're trying to mount an animal
            if (
                isinstance(entity, Vehicle)
                and isinstance(entity, LivingEntity)
                and not self.check_town_permission(mage, town, "pve")
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage("PvE is forbidden in {}".format(town.name))

            # check if sheering or coloring sheep
            if isinstance(entity, Sheep) and not self.check_town_permission(
                mage, town, "pve"
            ):
                event.setCancelled(True)
                raise PlayerErrorMessage("PvE is forbidden in {}".format(town.name))

    def on_player_teleport(self, event, mage):
        # print(">> PlayerTeleportEvent")
        if hack_func_for_overworld(mage.player):
            return
        if event.getCause() == TeleportCause.ENDER_PEARL:
            bukkit_chunk = event.getTo().getChunk()
            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if town and not town.get_rule("teleport"):
                event.setCancelled(True)
                raise PlayerErrorMessage(
                    "Teleportation is forbidden in {}".format(town.name)
                )

    def on_liquid_spreads(self, event, mage):
        # print(">> BlockFromToEvent")
        to_chunk = event.getToBlock().getChunk()
        if hack_func_for_overworld(to_chunk):
            return
        to_town = self.get_town_by_coords(to_chunk.getX(), to_chunk.getZ())
        if to_town:
            from_chunk = event.getBlock().getChunk()
            from_town = self.get_town_by_coords(from_chunk.getX(), from_chunk.getZ())
            if from_town != to_town:
                event.setCancelled(True)

    def on_entity_explode(self, event, mage):
        damager = event.getEntity()
        if hack_func_for_overworld(damager):
            return
        for block in event.blockList():
            bukkit_chunk = block.getLocation().getChunk()

            town = self.claims_by_loc[bukkit_chunk.getX()].get(
                bukkit_chunk.getZ(), self.wilderness
            )
            if isinstance(damager, TNTPrimed):
                if not town.get_rule("tnt"):
                    event.setCancelled(True)
            elif isinstance(damager, Creeper):
                if not town.get_rule("creeper"):
                    event.setCancelled(True)
            else:
                event.setCancelled(True)

    def on_entity_change_block(self, event, mage):
        block = event.getBlock()
        if hack_func_for_overworld(block):
            return
        bukkit_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if town and event.getEntityType() == WITHER and not town.get_rule("wither"):
            event.getEntity().remove()
            event.setCancelled(True)

    def on_player_leash_entity(self, event, mage):
        entity = event.getEntity()
        if hack_func_for_overworld(entity):
            return
        bukkit_chunk = entity.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )
        if mage and not self.check_town_permission(mage, town, "pve"):
            event.setCancelled(True)
            raise PlayerErrorMessage(
                "PvE is forbidden in {}".format(town.name), mage.player,
            )

    def can_piston_move(self, event):
        bukkit_chunk = event.block.location.chunk
        if hack_func_for_overworld(bukkit_chunk):
            return true
        town = self.claims_by_loc[bukkit_chunk.getX()].get(
            bukkit_chunk.getZ(), self.wilderness
        )

        for block in event.getBlocks():

            if town != self.claims_by_loc[block.location.chunk.getX()].get(
                block.location.chunk.getZ(), self.wilderness
            ):
                return False
        return True

    def on_piston_extend(self, event, mage):
        # print(">> BlockPistonExtendEvent")
        if not self.can_piston_move(event):
            event.setCancelled(True)

    def on_piston_retract(self, event, mage):
        # print(">> BlockPistonRetractEvent")
        if not self.can_piston_move(event):
            event.setCancelled(True)
