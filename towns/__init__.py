from mcapi import asynchronous, synchronous
from core.mageworld import MageWorld
from core.plugin import BasePlugin, PluginData

from town import Town, TOWN_CLAIM_TYPE_NORMAL

from core.storage import IndexStorage

import logging
from collections import defaultdict
from core.exceptions import PlayerErrorMessage

from uuid import uuid4


class Wilderness(Town):
    def __init__(self, *args, **kwargs):
        self.set_data(MageWorld.get_config("towns", "wilderness"))

    def add_chunk(self, *args, **kwargs):
        pass


class Plugin(BasePlugin):
    lib_name = "towns"
    config_files = ("default_town", "wilderness", "config")
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
        player_data = self.player_data.get_or_create(mage.uuid)

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
        self.towns.get(town.uuid).save()

    def unclaim(self, mage, x, z, world_uuid):
        claimed_by = self.get_town_by_coords(x, z)
        if not claimed_by:
            raise PlayerErrorMessage("This plot not clamed")
        town = self.get_town_by_player_uuid(mage.uuid)
        if town != claimed_by:
            raise PlayerErrorMessage("You do not have permission to unclaim this plot")

        town.remove_chunk(int(x), int(z), str(world_uuid))

        del self.claims_by_loc[x][z]
        self.towns.get(town.uuid).save()

    def create_town(self, mage):
        player_town = self.get_town_by_player_uuid(mage.uuid)
        if player_town:
            raise PlayerErrorMessage(
                "You're already the owner of {}".format(player_town.name)
            )

        town = self.towns.add(str(uuid4()))
        town.set_owner(mage)
        town.save()
        self.towns_by_player[mage.uuid] = town
        return town

    def remove_town(self, uuid):
        self.towns.remove(uuid)

    # def on_load_config(self):
    #     towns_default = MageWorld.get_config(self.lib_name, "towns_default")
    #     towns = MageWorld.get_config(self.lib_name, "towns")
    #     self.config = towns_default.update(towns)

    def on_load(self):
        self.player_data = IndexStorage(self.lib_name, "players")
        self.towns = IndexStorage(self.lib_name, "towns", Town)
        for town_uuid, town in self.towns:
            self.towns_by_player[town.data["owner"]] = town
            for chunk in town.data.get("chunks"):
                self.claims_by_loc[chunk[0]][chunk[1]] = town
        # run towns_fix_cuboids
        # run towns_update_dynmap_all_towns

    @asynchronous()
    def on_player_move(self, event, mage):
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

    @asynchronous()
    def on_player_join(self, event, mage):
        if not mage.data.keys():
            logging.debug("Player doesnt have a town")

    @asynchronous()
    def on_player_quit(self, event, mage):
        # save player data
        # player_uuid = str(event.getPlayer().getUniqueId())
        # pd = self.player_data.get(player_uuid)
        # pd.save()
        mage.save()
        town = self.get_town_by_player_uuid(mage.uuid)
        if town:
            self.towns.get(town.uuid).save()

        # save town data

    def on_player_breaks_block(self, event, mage):
        # if in town:
        #     check_blockchange()
        #     town.xp += 1
        # else:
        #     if server flag no_build:
        #         "Building in wilderness is forbidden"
        #     else:
        #         "You can only alter blocks once every <proc[towns_get_setting].context[towns.world_edit_freq]> seconds outside of your town"
        #         do the math

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

        # if player has permission towns.override.build:
        #     return True
        # if town:
        #   Town
        #   if town == player_town:
        #       ok

        # else:
        #   Wilderness


"""
  - if <def[location].exists.not> define location <context.location>
  - define town <proc[towns_get_town_from_chunk].context[<def[location].chunk>]>
  - if <player.has_permission[towns.override.build]||false> goto finish
  - define player <player||null>
  - if <def[town]> == null {
    - define player_town Wilderness
    } else {
    - define player_town <def[town]>
    }


  - if <proc[towns_get_town].context[<player||null>]||null> == <def[player_town]> && <def[checkfor]||null> != pvp {
    - goto finish
    }
  - if <player.has_flag[contrib]||false> && <proc[towns_get_members].context[<def[town]>].size> == 0 {
    - goto finish
    }
  - if <def[checkfor].exists> {
    - if <proc[towns_get_rule].context[<def[town]>|<def[checkfor]>]||false> goto finish
    - if <player||false> != false {
      - if <proc[towns_get_grant].context[<def[town]>|<def[checkfor]>|<player>]||false> goto finish
      }
    }
  - if if <def[alert_player]||true> {
    - narrate "<&c>You are not allowed to do this in the town of <proc[towns_get_name].context[<def[town]>]>" format:towns_format1
    }
  - determine cancelled
  - mark finish
"""
