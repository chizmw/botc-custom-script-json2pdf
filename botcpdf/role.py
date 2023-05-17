""" Holds information about a BOTC role """

from typing import Optional
from botcpdf.jinx import Jinx
from botcpdf.util import (
    cleanup_role_id,
    load_extra_roles,
    load_fabled_data,
    load_nightdata,
    load_nightmeta,
    load_role_data,
)


class Role:
    """Holds information about a BOTC role"""

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case
    id_slug: str
    name: str
    edition: Optional[str] = None
    team: str
    first_night: int = 0
    first_night_reminder: str
    other_night: int = 0
    other_night_reminder: str
    reminders: list[str]
    setup: bool
    ability: str
    stylized: bool
    jinxes: list[Jinx] = []

    def __init__(self, role_data: dict, stylize: bool = True):
        """Initialize a role."""

        # we expect these to always exist, so we don't need .get()
        self.id_slug = role_data["id"]
        self.name = role_data["name"]
        self.team = role_data["team"]
        self.first_night_reminder = role_data["firstNightReminder"]
        self.other_night_reminder = role_data.get("otherNightReminder", "")
        self.reminders = role_data.get("reminders", [])
        self.setup = role_data.get("setup", False)

        # we need to knoiw if we're stylizing or not before we can store the
        # ability
        self.stylized = stylize
        self.ability = self.stylize(role_data["ability"])

        # optional (e.g. fabled roles don't have an edition)
        self.edition = role_data.get("edition", None)

    # it's a bit clunkier than we'd like, but progress is progress
    def stylize(self, text: str) -> str:
        """Stylize a string of text for HTML/PDF rendering"""
        if not self.stylized:
            return text

        # this looks weird to me, and as we fetch this data from the json
        # we modify it here to suit our desired
        text = text.replace(
            "[Most players are Legion]",
            "&nbsp;<strong>[Most players are Legion]</strong>",
        )
        text = text.replace(
            "(Travellers don’t count)",
            "&nbsp;<strong>[Travellers don’t count]</strong>",
        )
        text = text.replace(
            "(not yourself)",
            "&nbsp;<strong>[not yourself]</strong>",
        )
        text = text.replace(
            "[1 Townsfolk is evil]",
            "&nbsp;<strong>[1 Townsfolk is evil]</strong>",
        )

        # replace '[+N Outsider]' with '<strong>[+N Outsider]</strong>'
        text = text.replace("[+", "&nbsp; <strong>[+")
        # the next two likes look visually similar, but are different
        # the json appears to have a unicode minus sign
        text = text.replace("[-", "&nbsp; <strong>[-")
        text = text.replace("[\u2212", "&nbsp; <strong>[-")

        # and close
        text = text.replace("]", "]</strong>")

        return text

    def __repr__(self):
        return (
            f"""["{self.name}": ("{self.id_slug}", "{self.team}", "{self.edition}")"""
        )

    def __str__(self):
        # pylint: disable=line-too-long
        return f"name: {self.name}, id: {self.id_slug}, team: {self.team}, edition: {self.edition}, jinxes: {self.jinxes}"

    def get_edition_name(self) -> str:
        """Get the name of the edition."""
        lookup: dict = {
            "tb": "Trouble Brewing",
            "snv": "Sects and Violets",
            "bmr": "Bad Moon Rising",
        }
        return lookup.get(self.edition, "Unknown Edition")


class RoleData:
    # pylint: disable=too-few-public-methods
    """Holds information for all the roles in the game"""

    roles: dict[str, Role] = {}

    def __init__(self):
        """Initialize role data."""

        # 'regular' role info from roles-bra1n.json
        self.add_character_roles()

        # extra characters not in the main json (yet)
        self.add_extra_roles()

        # we'll add fabled roles to the same dict
        self.add_fabled_roles()

        # Demon and Minion info, Dawn
        self.add_meta_roles()

        # work out values for first_night and other_night
        self.derive_night_values()

    def add_extra_roles(self) -> None:
        """Add extra roles to the role data."""
        role_data = load_extra_roles()
        for role in role_data:
            # if it already exists, we'll warn and preserve the existing data
            if role["id"] in self.roles:
                print(
                    f"Warning: role with id '{role['id']}' already exists; "
                    "preserving existing data"
                )
                continue

            self.roles[role["id"]] = Role(role)

    def derive_night_values(self):
        """Derive values for first_night and other_night"""
        night_data = load_nightdata()

        # loop through firstNight list in night_data; we need the index as well
        for index, role_id in enumerate(night_data["firstNight"]):
            # get the role object for the given id
            role = self.get_role(cleanup_role_id(role_id))
            # set the first_night attribute
            role.first_night = index + 1

        # loop through otherNight list in night_data; we need the index as well
        for index, role_id in enumerate(night_data["otherNight"]):
            # get the role object for the given id
            role = self.get_role(cleanup_role_id(role_id))
            # set the other_night attribute
            role.other_night = index + 1

    def get_role(self, id_slug: str) -> Role:
        """Get a role by ID."""

        # if there's no role with the given id, raise an error
        if id_slug not in self.roles:
            # print the sorted list of role ids for debugging
            raise ValueError(
                f"Role with ID '{id_slug}' not found; "
                f"""known role ids: {", ".join(sorted(self.roles.keys()))}"""
            )

        return self.roles[id_slug]

    def add_character_roles(self) -> None:
        """Add character roles to the role data."""
        role_data = load_role_data()
        for role in role_data:
            self.roles[role["id"]] = Role(role)

    def add_fabled_roles(self) -> None:
        """Add character roles to the role data."""
        role_data = load_fabled_data()
        for role in role_data:
            self.roles[role["id"]] = Role(role)

    def add_meta_roles(self) -> None:
        """Add meta roles to the role data.

        i.e. Minion/Demon info, Dawn, Dusk"""

        nightmeta = load_nightmeta()

        for role in nightmeta:
            self.roles[role["id"]] = Role(role)

    def get_first_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_minion"], self.roles["_demon"], self.roles["_dawn"]]

    def get_other_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_dawn"], self.roles["_dusk"]]
