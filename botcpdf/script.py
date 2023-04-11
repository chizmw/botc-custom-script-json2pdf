"""This module contains the Script class, which represents a script."""

import os
from botcpdf.util import load_role_data
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML # type: ignore

class Role:
    """Holds information about a BOTC role"""
    id: str
    name: str
    edition: str
    team: str
    first_night: int
    first_night_reminder: str
    other_night: int
    other_night_reminder: str
    reminders: list[str]
    setup: bool
    ability: str

    def __init__(self, role_data: dict):
        """Initialize a role."""
        self.id = role_data['id']
        self.name = role_data['name']
        self.edition = role_data['edition']
        self.team = role_data['team']
        self.first_night = role_data['firstNight']
        self.first_night_reminder = role_data['firstNightReminder']
        self.other_night = role_data['otherNight']
        self.other_night_reminder = role_data['otherNightReminder']
        self.reminders = role_data['reminders']
        self.setup = role_data['setup']
        self.ability = role_data['ability']

    def __repr__(self):
        return f"""["{self.name}": ("{self.id}", "{self.team}", "{self.edition}")"""

class RoleData:
    """Holds information for all the roles in the game"""
    roles: dict[str,Role]

    def __init__(self):
        """Initialize role data."""
        role_data = load_role_data()
        self.roles = {}
        for role in role_data:
            self.roles[role['id']] = Role(role)

    def get_role(self, id: str) -> Role:
        """Get a role by ID."""
        return self.roles[id]

class Script:
    """Represents a script."""
    char_types: dict[str,list[Role]] = {'townsfolk': [], 'outsider': [], 'minion': [], 'demon': []}
    first_night: dict[int, Role] = {}
    other_nights: dict[int,Role] = {}

    role_data: RoleData = RoleData()

    def __init__(self, title: str, script_data: dict):
        """Initialize a script."""
        self.title = title

        # we want to preserve the order of the characters
        # so we'll use a list instead of a set
        for char in script_data:
            self.add_char(char)

        
    def __repr__(self):
        # for each character type, print the type and the characters
        for char_type in self.char_types:
            print(char_type)
            for char in self.char_types[char_type]:
                print(f"\t{char}")

        print(f"first night: {self.sorted_first_night()}")
        print(f"other nights: {self.sorted_other_nights()}")

    def cleanup_id(self, char: dict) -> dict:
        """Cleanup the character ID."""

        # looking at other projects it seems that the ID in the script data is _close_ to the ID in the role data
        # so we'll just do some cleanup to make it match
        char['id'] = char['id'].replace('_','')
        char['id'] = char['id'].replace('-','') # just the pit-hag... why

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
        role = self.role_data.get_role(char['id'])

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
        # write the rendered HTML to a file
        with open(f"{self.title}.html", "w") as f:
            f.write(html_out)
        # convert the HTML to PDF
        HTML(string=html_out).write_pdf(f"{self.title}.pdf",stylesheets=["templates/style.css"])
