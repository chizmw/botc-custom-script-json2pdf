""" Holds information for all the roles in the game """


from botcpdf.role import Role
from botcpdf.util import get_role_data


class RoleData:
    # pylint: disable=too-few-public-methods
    """Holds information for all the roles in the game"""

    roles: dict[str, Role] = {}
    json_filename: str = "data/imported/roles-combined.json"

    def __init__(self):
        """Initialize role data."""

        full_data = get_role_data()

        # we have { "character_by_id": { id: {...} }  }
        # in our data; loop through the roles and create Role objects
        # for each one
        for role_id, role_data in full_data["character_by_id"].items():
            # create the role
            role = Role(role_data)

            # store it in the dict
            self.roles[role_id] = role

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

    def get_first_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_minion"], self.roles["_demon"], self.roles["_dawn"]]

    def get_other_night_meta_roles(self) -> list[Role]:
        """Get a list of meta roles."""
        return [self.roles["_dawn"], self.roles["_dusk"]]
