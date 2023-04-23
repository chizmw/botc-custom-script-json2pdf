"""This module contains the Script class, which represents a script."""

import logging
import os
from typing import Optional
from pkg_resources import get_distribution  # type: ignore
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML  # type: ignore
from botcpdf.benchmark import timeit  # type: ignore
from botcpdf.jinx import Jinxes  # type: ignore
from botcpdf.role import Role, RoleData
from botcpdf.util import cleanup_role_id, is_aws_env, pdf2images  # type: ignore


class ScriptMeta:
    """Represents script metadata."""

    # pylint: disable=too-few-public-methods

    # some scripts have an entry with id: _meta
    # this is where we'll store that data
    # I don't know what all the fields are, but from what I've seen
    # it seems to be at least: name - author - logo
    name: Optional[str]
    author: Optional[str]
    logo: Optional[str]

    def __init__(self, data: dict):
        """Initialize script metadata."""

        # ignore the id field if it's _meta
        if data.get("id") == "_meta":
            data.pop("id")

        # make sure we only use known fields; not all required
        if not set(data.keys()).issubset({"name", "author", "logo"}):
            raise ValueError("Unexpected fields in script metadata")

        self.name = data.get("name", None)
        self.author = data.get("author", None)
        self.logo = data.get("logo", None)

    def __repr__(self):
        return f"ScriptMeta(name='{self.name}', author='{self.author}', logo='{self.logo}')"  # pylint: disable=line-too-long


class Script:
    """Represents a script."""

    char_types: dict[str, list[Role]] = {
        "townsfolk": [],
        "outsider": [],
        "minion": [],
        "demon": [],
        "fabled": [],
    }
    first_night: dict[float, Role] = {}
    other_nights: dict[float, Role] = {}

    role_data: RoleData = RoleData()

    meta: Optional[ScriptMeta] = None

    hatred: dict[str, list[str]] = {}
    hate_pair: dict[str, str] = {}

    def __init__(self, title: str, script_data: dict, logger = None):
        """Initialize a script."""
        self.title = title
        self.logger = logger

        self._ensure_logger()

        # we want to preserve the order of the characters
        # so we'll use a list instead of a set
        for char in script_data:
            self.logger.debug(f"Processing character: {char}")
            self._add_char(char)

        # add meta roles to night instructions
        self._add_meta_roles()

        # now we've loaded all the core information we can examine what we have
        # and see if there are any jinxes
        self._process_jinxes()

    @timeit
    def _ensure_logger(self) -> None:
        # if we don't have a logger, we'll create one that will log to stdout
        if self.logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                '%(created)f [%(levelname)s] %(name)s, line %(lineno)d: %(message)s'
            )
            ch.setFormatter(formatter)
            # add the handlers to logger
            logger.addHandler(ch)

            self.logger = logger

            self.logger.info("No logger provided, creating one.")

    @timeit
    def _add_meta_roles(self) -> None:
        """Add meta roles to the night instructions."""
        for role in self.role_data.get_first_night_meta_roles():
            self.first_night[role.first_night] = role

        for role in self.role_data.get_other_night_meta_roles():
            self.other_nights[role.other_night] = role

    @timeit
    def _process_jinxes(self) -> None:
        """Load the jinxes from the script data."""
        jinxes = Jinxes()

        # loop through each character in the script
        for char_type in self.char_types.values():
            for role in char_type:
                # if something 'hates us' then add jinx information to the hater
                # if the hater is in the script
                # e.g. chambermaid hates mathemtician
                # so we add the jinx information to the chambermaid when we see
                # the mathematician
                hates_us: list[str] = jinxes.hated_by(role.id_slug)

                # if the hater is in the script, add the jinx information
                for slug in hates_us:
                    if self.role_in_script(slug):
                        if slug not in self.hatred:
                            self.hatred[slug] = []
                        self.hatred[slug].append(role.id_slug)
                        jinx_info = jinxes.get_jinx(slug, role.id_slug)
                        self.hate_pair[f"{slug}-{role.id_slug}"] = jinx_info.reason

    def __repr__(self):
        repr_str = ""
        for char_type in self.char_types.items():
            repr_str += char_type
            for char in self.char_types[char_type]:
                repr_str += f"\t{char}"

        repr_str += f"first night: {self.sorted_first_night()}"
        repr_str += f"other nights: {self.sorted_other_nights()}"

        return repr_str

    def role_in_script(self, role_id: str) -> bool:
        """Return True if the role is in the script."""
        for char_type in self.char_types.values():
            for role in char_type:
                if role.id_slug == role_id:
                    return True

        return False

    def sorted_first_night(self) -> list[Role]:
        """Return the first night characters in order."""
        return [self.first_night[i] for i in sorted(self.first_night.keys())]

    def sorted_other_nights(self) -> list[Role]:
        """Return the other night characters in order."""
        return [self.other_nights[i] for i in sorted(self.other_nights.keys())]

    @timeit
    def _add_char(self, char: dict):
        """Add a character to the script."""
        # before we do anything at all we need to check for _meta in the data
        if char.get("id") == "_meta":
            # store the metadata
            self.meta = ScriptMeta(char)
            # if we have 'name' then update the title
            if self.meta.name:
                self.logger.debug(f"Updating title to {self.meta.name} from {self.title}")
                self.title = self.meta.name

            return

        # manage all the normal character data
        # clean up the role id
        char["id"] = cleanup_role_id(char["id"])
        role = self.role_data.get_role(char["id"])

        # add to the appropriate list
        self.char_types[role.team].append(role)
        # if it's a first night character, add it to the first night list
        if role.first_night != 0:
            # if there's already a character in the slot, raise an error
            if role.first_night in self.first_night:
                raise ValueError(
                    f"Duplicate first night character in {role.first_night} position. "
                    f"{role} trying to replace {self.first_night[role.first_night]}"
                )

            self.first_night[role.first_night] = role

        # if it's an other night character, add it to the other night list
        if role.other_night != 0:
            # if there's already a character in the slot, raise an error
            if role.other_night in self.other_nights:
                raise ValueError(f"Duplicate other night character: {role.other_night}")

            self.other_nights[role.other_night] = role

    @timeit
    def render(self) -> str:
        """Render the script as a PDF.

        Returns:
            str: local path to the PDF file
        """

        env = Environment(
            loader=FileSystemLoader("templates"), extensions=["jinja2.ext.loopcontrols"]
        )
        template = env.get_template("script.jinja")

        # so we can actually use images in the PDF
        this_folder = os.path.dirname(os.path.abspath(__file__))
        # use this_folder to get the path to the icons and templates folders
        icon_folder = os.path.abspath(os.path.join(this_folder, "..", "icons"))
        template_folder = os.path.abspath(os.path.join(this_folder, "..", "templates"))

        template_vars = {
            "_project": get_distribution("botc-json2pdf").__dict__,
            "title": self.title,
            "characters": self.char_types,
            "first_night": self.sorted_first_night(),
            "other_nights": self.sorted_other_nights(),
            "icon_folder": icon_folder,
            "template_folder": template_folder,
            "hatred": self.hatred,
            "hate_pair": self.hate_pair,
        }

        html_out = template.render(template_vars)

        self.logger.info(template_vars)

        # if we have BOTC_DEBUG set...
        if os.environ.get("BOTC_DEBUG"):
            # write the rendered HTML to a file
            with open(f"{self.title}.html", "w", encoding="utf-8") as fhandle:
                fhandle.write(html_out)

        # convert the HTML to PDF
        if is_aws_env():
            pdf_folder = "/tmp"
        else:
            pdf_folder = os.path.abspath(os.path.join(this_folder, "..", "pdfs"))
            # if non-tmp pdf_folder doesn't exist, create it
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
        # save the PDF in the pdfs folder
        HTML(string=html_out).write_pdf(
            os.path.join(pdf_folder, f"{self.title}.pdf"),
            stylesheets=["templates/style.css"],
            optimize_size=(),
        )
        print("PDF saved to " + os.path.join(pdf_folder, f"{self.title}.pdf"))

        # if we have BOTC_PDF2IMAGE set...
        if os.environ.get("BOTC_PDF2IMAGE"):
            pdf2images(
                os.path.join(pdf_folder, f"{self.title}.pdf"),
                f"generated/{self.title}",
            )

        return os.path.join(pdf_folder, f"{self.title}.pdf")
