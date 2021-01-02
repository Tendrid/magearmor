from core.mageworld import MageWorld
from core.exceptions import PlayerErrorMessage
from core.storage import DataStorage

import copy

TOWN_CLAIM_TYPE_NORMAL = 0
TOWN_CLAIM_TYPE_OUTPOST = 1

TOWN_RANK_OWNER = 4

from uuid import uuid4

MAX_TOWN_NAME_LENGTH = 32
MAX_RANK_NAME_LENGTH = 32


class Town(DataStorage):
    @property
    def name(self):
        return self.data.get("name", "Abandoned Ruins")

    @property
    def welcome(self):
        if self.get_rule("titlescreen"):
            return self.data.get("welcome", "")

    @property
    def ranks(self):
        return self.data["ranks"]

    @property
    def permissions(self):
        return self.data["permissions"]

    def set_permission(self, permission_name, rank_name):
        if self.data["permissions"].get(permission_name) is None:
            raise PlayerErrorMessage("Invalid permission name")
        try:
            rank_idx = self.data["ranks"].index(rank_name)
        except ValueError:
            raise PlayerErrorMessage("Invalid rank name")

        self.data["permissions"][permission_name] = rank_idx
        self.save()

    def set_data(self, data):
        # set town defaults
        self.data = MageWorld.get_config("towns", "default_town")
        # override defaults with town settings
        self.data.update(data)

        # add new second level items
        for k, v in MageWorld.get_config("towns", "default_town").items():
            if not self.data.get(k):
                self.data[k] = v
            elif type(self.data[k]) is dict:
                v.update(self.data[k])
                self.data[k] = v

    def add_memeber(self, mage):
        if self.data["members"].get(mage.uuid):
            raise PlayerErrorMessage(
                "{} is already a member of {}".format(mage.name, self.name)
            )
        self.data["members"][mage.uuid] = {"rank": 1}

    def rename_rank(self, rank_name, new_rank_name):
        try:
            rank_idx = self.ranks.index(rank_name)
        except ValueError:
            raise PlayerErrorMessage("There is no rank {}".format(rank_name))

        if len(new_rank_name) > MAX_RANK_NAME_LENGTH:
            raise PlayerErrorMessage(
                "That name is too long!  Please keep rank names under {} characters".format(
                    MAX_RANK_NAME_LENGTH
                )
            )
        self.data["ranks"][rank_idx] = new_rank_name
        self.save()

    def set_member_rank(self, mage, rank_name):
        if self.data["members"].get(mage.uuid) is None:
            raise PlayerErrorMessage(
                "{} is not a member of {}".format(mage.name, self.name)
            )
        try:
            rank_idx = self.data["ranks"].index(rank_name)
        except ValueError:
            raise PlayerErrorMessage("Invalid rank name")

        if rank_idx >= TOWN_RANK_OWNER:
            raise PlayerErrorMessage(
                "You cannot assign the rank of {}".format(rank_name)
            )

        self.data["members"]["rank"] = rank_idx
        self.save()

    def set_owner(self, mage):
        self.data["owner"] = mage.uuid
        # for uuid, member in self.data["members"].iteritems():
        #    if member["rank"] == TOWN_RANK_OWNER:
        #        member["rank"] = TOWN_RANK_OWNER - 1
        # self.set_member_rank(mage, self.ranks[TOWN_RANK_OWNER])

    def set_name(self, name):
        if len(name) > MAX_TOWN_NAME_LENGTH:
            raise PlayerErrorMessage(
                "That name is too long!  Please keep town names under {} characters".format(
                    MAX_TOWN_NAME_LENGTH
                )
            )
        self.data["name"] = name
        self.save()

    def get_rule(self, rule_name):
        return self.data["rule"].get(rule_name)

    def get_player_role(self, player_uuid):
        if self.owner == player_uuid:
            return TOWN_RANK_OWNER
        else:
            return self.data["members"].get(player_uuid, {}).get("rank", 0)

    def add_chunk(self, x, z, world, plot_type, claimed_by_player):
        self.data["chunks"].append((x, z, world, plot_type, claimed_by_player))
        self.save()

    def remove_chunk(self, x, z, world):
        flagged = []
        for idx, chunk in enumerate(self.data["chunks"]):
            if chunk[0] == x and chunk[1] == z and chunk[2] == world:
                flagged.append(idx)

        for idx in flagged:
            self.data["chunks"].pop(idx)
        self.save()
