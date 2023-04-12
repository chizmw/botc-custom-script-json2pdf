"""This module contains the Script class, which represents a script."""

import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML  # type: ignore
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


class Script:
    """Represents a script."""

    char_types: dict[str, list[Role]] = {
        "townsfolk": [],
        "outsider": [],
        "minion": [],
        "demon": [],
    }
    first_night: dict[float, Role] = {}
    other_nights: dict[float, Role] = {}

    role_data: RoleData = RoleData()

    def __init__(self, title: str, script_data: dict):
        """Initialize a script."""
        self.title = title

        # we want to preserve the order of the characters
        # so we'll use a list instead of a set
        for char in script_data:
            self.add_char(char)

        # add meta roles to night instructions
        self.add_meta_roles()

    def add_meta_roles(self) -> None:
        """Add meta roles to the night instructions."""
        for role in self.role_data.get_first_night_meta_roles():
            self.first_night[role.first_night] = role

        for role in self.role_data.get_other_night_meta_roles():
            self.other_nights[role.other_night] = role

    def __repr__(self):
        repr_str = ""
        for char_type in self.char_types.items():
            repr_str += char_type
            for char in self.char_types[char_type]:
                repr_str += f"\t{char}"

        repr_str += f"first night: {self.sorted_first_night()}"
        repr_str += f"other nights: {self.sorted_other_nights()}"

        return repr_str

    def cleanup_id(self, char: dict) -> dict:
        """Cleanup the character ID."""

        # looking at other projects it seems that the ID in the script data is
        # _close_ to the ID in the role data
        # so we'll just do some cleanup to make it match
        char["id"] = char["id"].replace("_", "")
        char["id"] = char["id"].replace("-", "")  # just the pit-hag... why

        return char

    def sorted_first_night(self) -> list[Role]:
        """Return the first night characters in order."""
        return [self.first_night[i] for i in sorted(self.first_night.keys())]

    def sorted_other_nights(self) -> list[Role]:
        """Return the other night characters in order."""
        return [self.other_nights[i] for i in sorted(self.other_nights.keys())]

    def add_char(self, char: dict):
        """Add a character to the script."""
        char = self.cleanup_id(char)
        role = self.role_data.get_role(char["id"])

        # add to the appropriate list
        self.char_types[role.team].append(role)
        # if it's a first night character, add it to the first night list
        if role.first_night != 0:
            # if there's already a character in the slot, raise an error
            if role.first_night in self.first_night:
                raise ValueError(f"Duplicate first night character: {role.first_night}")

            self.first_night[role.first_night] = role

        # if it's an other night character, add it to the other night list
        if role.other_night != 0:
            # if there's already a character in the slot, raise an error
            if role.other_night in self.other_nights:
                raise ValueError(f"Duplicate other night character: {role.other_night}")

            self.other_nights[role.other_night] = role

    def render(self):
        """Render the script to PDF"""
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("script.jinja")

        # so we can actually use images in the PDF
        this_folder = os.path.dirname(os.path.abspath(__file__))
        # use this_folder to get the path to the icons and templates folders
        icon_folder = os.path.abspath(os.path.join(this_folder, "..", "icons"))
        template_folder = os.path.abspath(os.path.join(this_folder, "..", "templates"))

        template_vars = {
            "title": self.title,
            "characters": self.char_types,
            "first_night": self.sorted_first_night(),
            "other_nights": self.sorted_other_nights(),
            "icon_folder": icon_folder,
            "template_folder": template_folder,
        }
        html_out = template.render(template_vars)

        # if we have BOTC_DEUG set...
        if os.environ.get("BOTC_DEBUG"):
            # write the rendered HTML to a file
            with open(f"{self.title}.html", "w", encoding="utf-8") as fhandle:
                fhandle.write(html_out)

        # convert the HTML to PDF
        pdf_folder = os.path.abspath(os.path.join(this_folder, "..", "pdfs"))
        # if pdf_folder doesn't exist, create it
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        # save the PDF in the pdfs folder
        HTML(string=html_out).write_pdf(
            os.path.join(pdf_folder, f"{self.title}.pdf"),
            stylesheets=["templates/style.css"],
            optimize_size=(),
        )
