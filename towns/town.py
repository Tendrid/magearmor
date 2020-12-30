from core.mageworld import MageWorld
from core.exceptions import PlayerErrorMessage
from core.storage import DataStorage

import copy

TOWN_CLAIM_TYPE_CENTER = 0
TOWN_CLAIM_TYPE_NORMAL = 1
TOWN_CLAIM_TYPE_PVP = 2

TOWN_RANK_OWNER = 9
TOWN_RANK_ADMIN = 8
TOWN_RANK_MEMBER = 3

from uuid import uuid4

MAX_TOWN_NAME_LENGTH = 32


class Town(DataStorage):
    @property
    def name(self):
        return self.data.get("name", "Abandoned Ruins")

    @property
    def welcome(self):
        if self.get_rule("titlescreen"):
            return self.data.get("welcome", "")

    def set_data(self, data):
        # set town defaults
        self.data = MageWorld.get_config("towns", "default_town")
        # override defaults with town settings
        self.data.update(data)

    def set_member_rank(self, mage, rank):
        if self.data["members"].get(mage.uuid) is None:
            self.data["members"] = {}
        self.data["members"]["rank"] = rank

    def set_owner(self, mage):
        self.data["owner"] = mage.uuid
        for uuid, member in self.data["members"].iteritems():
            if member["rank"] == TOWN_RANK_OWNER:
                member["rank"] = TOWN_RANK_ADMIN
        self.set_member_rank(mage, TOWN_RANK_OWNER)

    def set_name(self, name):
        if len(name) > MAX_TOWN_NAME_LENGTH:
            raise PlayerErrorMessage(
                "That name is too long!  Please keep town names under {} characters".format(
                    MAX_TOWN_NAME_LENGTH
                )
            )
        self.data["name"] = name

    def get_rule(self, rule_name):
        return self.data["rule"].get(rule_name)

    def get_player_role(self, player_uuid):
        return self.data["members"].get(player_uuid, {}).get("rank")

    def add_chunk(self, x, z, world, plot_type, claimed_by_player):
        # x, z, world, plot_type, claimed_by_player
        self.data["chunks"].append((x, z, world, plot_type, claimed_by_player))
