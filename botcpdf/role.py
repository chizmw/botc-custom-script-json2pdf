""" Holds information about a BOTC role """

from typing import Optional
from botcpdf.jinx import Jinx


class Role:
    """Holds information about a BOTC role"""

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case
    id_slug: str
    name: str
    edition: Optional[str] = None
    team: str
    first_night_position: int = 0
    first_night_reminder: str
    other_night_position: int = 0
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
        self.first_night_position = role_data.get("firstNight", None)
        self.first_night_reminder = role_data["firstNightReminder"]
        self.name = role_data["name"]
        self.other_night_position = role_data.get("otherNight", None)
        self.other_night_reminder = role_data.get("otherNightReminder", "")
        self.reminders = role_data.get("reminders", [])
        self.setup = role_data.get("setup", False)
        self.team = role_data["team"]

        # we need to know if we're stylizing or not before we can store the
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
        # build up night order info, if we have it
        night_order = ""
        if self.first_night_position is not None and self.first_night_position > 0:
            night_order += f"first_night_position={self.first_night_position}"
        if self.other_night_position is not None and self.other_night_position > 0:
            # if we already have a first night position, we'll add a comma
            if night_order:
                night_order += ", "
            night_order += f"other_night_position={self.other_night_position}"
        # if we have a night order, prefix it with a comma and a space
        if night_order:
            night_order = f", {night_order}"

        # jinxes, if we don't have them (empty list) strigify as 'None'
        if not self.jinxes:
            jinxes = "None"

        # pylint: disable=line-too-long
        return f"Role(name='{self.name}', id_slug='{self.id_slug}', team='{self.team}', edition='{self.edition}', jinxes={jinxes}{night_order})"

    def get_edition_name(self) -> str:
        """Get the name of the edition."""
        lookup: dict = {
            "tb": "Trouble Brewing",
            "snv": "Sects and Violets",
            "bmr": "Bad Moon Rising",
        }
        return lookup.get(self.edition, "Unknown Edition")
