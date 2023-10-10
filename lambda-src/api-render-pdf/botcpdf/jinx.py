""" Holds information for jinx behaviour in custom scripts """

# jinx data is a list of character: [{jinxes, reason}, ...]
# as we're experimenting with this we'll keep it simple and just
# use {slug-jinxer}-{slug-jinxee} as the key

from botcpdf.util import cleanup_role_id, get_role_data


class Jinx:
    """A representation of jinks in a game"""

    # pylint: disable=too-few-public-methods

    jinxer_id: str
    jinxee_id: str
    reason: str

    def __init__(self, jinxer_id: str, jinxee_id: str, reason: str):
        self.jinxer_id = jinxer_id
        self.jinxee_id = jinxee_id
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.jinxer_id}-{self.jinxee_id}"

    def __repr__(self) -> str:
        return self.__str__()


class Jinxes:
    """A representation of jinxes in a game"""

    def __init__(self) -> None:
        """Initialize jinx data"""

        self.hatred: dict[str, dict] = {}

        full_data = get_role_data()
        jinx_data = full_data["jinxes"]

        for jinx_block in jinx_data:
            for jinxed_char in jinx_block["jinx"]:
                jinxer_id = cleanup_role_id(jinx_block["id"])
                jinxed_id = cleanup_role_id(jinxed_char["id"])
                reason = jinxed_char["reason"]

                jinx_info = Jinx(jinxer_id, jinxed_id, reason)

                # if we don't yet have a hatred entry for the jinxer, create it
                if jinxer_id not in self.hatred:
                    self.hatred[jinxer_id] = {}
                # add the jinxer to the bibble
                self.hatred[jinxer_id][jinxed_id] = jinx_info

    def player_jinxed(self, jinxer_id: str, jinxed_id: str) -> bool:
        """Check if a player has been jinxed by another player"""
        return jinxer_id in self.hatred and jinxed_id in self.hatred[jinxer_id]

    def get_jinx(self, jinxer_id: str, jinxed_id: str) -> Jinx:
        """Get a jinx by jinxer and jinxed from the hatred"""
        if not self.player_jinxed(jinxer_id, jinxed_id):
            raise ValueError(f"Jinx {jinxer_id}->{jinxed_id} not found")

        return self.hatred[jinxer_id][jinxed_id]

    def get_hatred(self, jinxer_id: str):
        """Get a list of jinxes for a jinxer"""
        if jinxer_id not in self.hatred:
            raise ValueError(f"Jinxer {jinxer_id} not found")

        # we want to return the jinked_id for hatred[jinxer_id]
        # but we don't want to modify the original data
        # so we'll make a copy of the data and return that
        return self.hatred[jinxer_id].copy()

    def hated_by(self, jinxed_id: str):
        """Get a list of jinxers that have jinxed a player"""
        jinxers = []

        for jinxer_id, info in self.hatred.items():
            if jinxed_id in info:
                jinxers.append(jinxer_id)

        return jinxers
