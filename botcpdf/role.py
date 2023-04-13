""" Holds information about a BOTC role """

from botcpdf.util import load_role_data


class Role:
    """Holds information about a BOTC role"""

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case
    id_slug: str
    name: str
    edition: str
    team: str
    first_night: float
    first_night_reminder: str
    other_night: int
    other_night_reminder: str
    reminders: list[str]
    setup: bool
    ability: str
    stylized: bool

    def __init__(self, role_data: dict, stylize: bool = True):
        """Initialize a role."""
        self.id_slug = role_data["id"]
        self.name = role_data["name"]
        self.edition = role_data["edition"]
        self.team = role_data["team"]
        self.first_night = role_data["firstNight"]
        self.first_night_reminder = role_data["firstNightReminder"]
        self.other_night = role_data["otherNight"]
        self.other_night_reminder = role_data["otherNightReminder"]
        self.reminders = role_data["reminders"]
        self.setup = role_data["setup"]
        self.stylized = stylize
        self.ability = self.stylize(role_data["ability"])

    # it's a bit clunkier than we'd like, but progress is progress
    def stylize(self, text: str) -> str:
        """Stylize a string of text for HTML/PDF rendering"""
        if not self.stylized:
            return text

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

    def get_edition_name(self) -> str:
        """Get the name of the edition."""
        lookup: dict[str, str] = {
            "tb": "Trouble Brewing",
            "snv": "Sects and Violets",
            "bmr": "Bad Moon Rising",
        }
        return lookup.get(self.edition, "Unknown Edition")


class RoleData:
    # pylint: disable=too-few-public-methods
    """Holds information for all the roles in the game"""

    roles: dict[str, Role]

    def __init__(self):
        """Initialize role data."""
        role_data = load_role_data()
        self.roles = {}
        for role in role_data:
            self.roles[role["id"]] = Role(role)

        self.add_meta_roles()

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

    def add_meta_roles(self) -> None:
        """Add meta roles to the role data.

        i.e. Minion/Demon info, Dawn"""
        self.roles["_minion"] = Role(
            {
                "id": "_minion-info",
                "name": "Minion Info",
                "edition": "",
                "team": "",
                "firstNight": 5,
                # pylint: disable=line-too-long
                "firstNightReminder": "If 7 or more players: wake up all of the Minions. They make eye contact with each other. Show the 'This is the Demon' card. Point to the Demon.",
                "otherNight": 0,
                "otherNightReminder": "",
                "reminders": [],
                "setup": False,
                "ability": "",
            }
        )

        self.roles["_demon"] = Role(
            {
                "id": "_demon-info",
                "name": "Demon Info",
                "edition": "",
                "team": "",
                "firstNight": 7.5,
                # pylint: disable=line-too-long
                "firstNightReminder": "If 7 or more players: wake up the Demon. Show the 'These are your minions' card. Point to each Minion. Show the 'These characters are not in play' card. Show 3 character tokens of Good characters that are not in play",
                "otherNight": 0,
                "otherNightReminder": "",
                "reminders": [],
                "setup": False,
                "ability": "",
            }
        )

        # pylint: disable=line-too-long
        dawn_reminder = "Wait approximately 10 seconds. Call for eyes open, then immediately announce which players (if any) died."
        self.roles["_dawn"] = Role(
            {
                "id": "_dawn",
                "name": "Dawn",
                "edition": "",
                "team": "",
                "firstNight": 9999,
                "firstNightReminder": dawn_reminder,
                "otherNight": 9999,
                "otherNightReminder": dawn_reminder,
                "reminders": [],
                "setup": False,
                "ability": "",
            }
        )

    def get_first_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_minion"], self.roles["_demon"], self.roles["_dawn"]]

    def get_other_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_dawn"]]
