from mcapi import asynchronous, synchronous
from core.mageworld import MageWorld
from core.plugin import BasePlugin, PluginData

from town import Town, TOWN_CLAIM_TYPE_CENTER, TOWN_CLAIM_TYPE_NORMAL

from core.storage import IndexStorage

import logging
from collections import defaultdict


class Wilderness(Town):
    def __init__(self, *args, **kwargs):
        self.data = MageWorld.get_config("towns", "wilderness")

    def set_data(self, *args, **kwargs):
        pass

    def add_chunk(self, *args, **kwargs):
        pass


class Towns(BasePlugin):
    lib_name = "towns"
    config_files = ("default_town", "wilderness", "config")
    claims_by_loc = defaultdict(dict)
    __wilderness = None

    @property
    def wilderness(self):
        if not self.__wilderness:
            self.__wilderness = Wilderness()
        return self.__wilderness

    def is_claimed(self, bukkit_chunk):
        return (
            self.claims_by_loc[bukkit_chunk.getX()].get(bukkit_chunk.getZ()) is not None
        )

    def player_town(self, uuid):
        player_data = self.player_data.get_or_create(mage.uuid)

    def get_town_by_chunk(self, bukkit_chunk):
        return self.claims_by_loc[bukkit_chunk.getX()].get(bukkit_chunk.getZ())

    def get_town_by_player_uuid(self, player_uuid):
        player_data = self.player_data.get(player_uuid)
        if player_data.data.get("town"):
            return self.towns.get(player_data.data.get("town"))
        return None

    def claim(self, player_uuid, player_location=None):
        # check if claim already owned
        # check if player is in town
        # if player in town. claim type TOWN_CLAIM_TYPE_NORMAL, else TOWN_CLAIM_TYPE_CENTER

        mage = MageWorld.get_mage(player_uuid)
        town = self.get_town_by_player_uuid(player_uuid)

        plot_type = TOWN_CLAIM_TYPE_NORMAL
        if not town:
            ref = self.towns.add(town.uuid)
            plot_type = TOWN_CLAIM_TYPE_CENTER
            town.set_owner(mage)

        if not player_location:
            player_location = mage.player.location
        chunk = player_location.getChunk()

        town.add_chunk(
            int(chunk.getX()),
            int(chunk.getZ()),
            str(chunk.getWorld().getUID()),
            plot_type,
            player_uuid,
        )

        self.claims_by_loc[chunk.getX()][chunk.getZ()] = town

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
                    event.getPlayer().sendTitle(town.name, town.welcome)

    @asynchronous()
    def on_player_join(self, event, mage):
        player = event.getPlayer()

        player_data = self.player_data.get_or_create(mage.uuid)
        if not player_data.data.keys():
            logging.debug("Player doesnt have a town")

        # mage.load_plugin_data(self.lib_name, PluginData(player_data))

    @asynchronous()
    def on_player_quit(self, event, mage):
        # save player data
        player_uuid = str(event.getPlayer().getUniqueId())
        pd = self.player_data.get(player_uuid)
        pd.save()
        town = self.get_town_by_player_uuid(player_uuid)
        if town:
            self.towns.get(town.uuid).save()

        # save town data

    def on_player_breaks_block(self, event, mage):
        block = event.getBlock()
        block_chunk = block.getLocation().getChunk()
        town = self.get_town_by_chunk(block_chunk)
        if town:
            mage = MageWorld.get_mage(str(event.getPlayer().getUniqueId()))
            player_role = town.get_player_role(mage.uuid)
            print(player_role)
            event.setCancelled(True)

    def on_shutdown(self):
        """
        - foreach <server.list_online_players>:
          - run towns_checkunload_town def:<proc[towns_get_town].context[<def[value]>]>
        """
        pass
