from mcapi import asynchronous, synchronous
from core.mageworld import MageWorld
from core.plugin import BasePlugin, PluginData

from town import Town, TOWN_CLAIM_TYPE_CENTER, TOWN_CLAIM_TYPE_NORMAL

from core.storage import IndexStorage

import logging
from collections import defaultdict
from core.exceptions import PlayerErrorMessage


class Wilderness(Town):
    def __init__(self, *args, **kwargs):
        self.data = MageWorld.get_config("towns", "wilderness")

    def set_data(self, *args, **kwargs):
        pass

    def add_chunk(self, *args, **kwargs):
        pass


class Plugin(BasePlugin):
    lib_name = "towns"
    config_files = ("default_town", "wilderness", "config")
    claims_by_loc = defaultdict(dict)
    __wilderness = None

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
        player_data = self.player_data.get(player_uuid)
        if player_data.data.get("town"):
            return self.towns.get(player_data.data.get("town"))
        return None

    def claim(self, mage, x, z, world_uuid):
        # check if claim already owned
        # check if player is in town
        # if player in town. claim type TOWN_CLAIM_TYPE_NORMAL, else TOWN_CLAIM_TYPE_CENTER

        claimed_by = self.get_town_by_coords(x, z)
        if claimed_by:
            raise PlayerErrorMessage(
                "This plot is already clamed by {}".format(claimed_by.name)
            )

        player_town = self.get_town_by_player_uuid(mage.uuid)
        if not player_town:
            raise PlayerErrorMessage("You're not in a town!")

        town = self.get_town_by_player_uuid(mage.uuid)

        plot_type = TOWN_CLAIM_TYPE_NORMAL
        if not town:
            ref = self.towns.add(town.uuid)
            plot_type = TOWN_CLAIM_TYPE_CENTER
            town.set_owner(mage)

        town.add_chunk(
            int(x),
            int(z),
            str(world_uuid),
            plot_type,
            player_uuid,
        )

        self.claims_by_loc[x][z] = town
        self.towns.get(town.uuid).save()

    # def on_load_config(self):
    #     towns_default = MageWorld.get_config(self.lib_name, "towns_default")
    #     towns = MageWorld.get_config(self.lib_name, "towns")
    #     self.config = towns_default.update(towns)

    def on_load(self):
        self.player_data = IndexStorage(self.lib_name, "players")
        self.towns = IndexStorage(self.lib_name, "towns", Town)
        for town_uuid, town in self.towns:
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
                if town.welcome:
                    mage.player.sendTitle(town.name, town.welcome)

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
        block_chunk = block.getLocation().getChunk()
        town = self.claims_by_loc[bukkit_chunk.getX()].get(bukkit_chunk.getZ())
        if town:
            player_role = town.get_player_role(mage.uuid)
            print(player_role)
            event.setCancelled(True)

    def on_shutdown(self):
        """
        - foreach <server.list_online_players>:
          - run towns_checkunload_town def:<proc[towns_get_town].context[<def[value]>]>
        """
        pass

    def check_blockchange(self, mage, town):
        # if mage.has_role("admin")
        pass

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
