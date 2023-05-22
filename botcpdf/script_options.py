"""This module contains the ScriptOptions class, which represents PDF rendering choices """


from typing import Optional

from botcpdf.util import ensure_logger


class ScriptOptions:
    """Represents PDF options for a script."""

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, options: Optional[dict], logger=None):
        self.logger = ensure_logger(logger=logger)
        self._process_options(options)

    def _default_options(self) -> dict:
        """Return a dict of default options."""

        return {
            # we always want to set the paper size
            # web: paperSize
            "paper_size": "A4",
            # scriptformat allows us to choose between the script formats
            # web: scriptFormat
            "pdf_format": "sample",
            # double sided printing is the default (requires easy_print_pdf)
            # web: printFormat
            "double_sided": True,
            # we want to print the player instructions in the night order
            # (requires easy_print_pdf)
            # web: playerNightInfo
            "player_night_order": True,
            # some STs like the simpler night order
            # web: stNightInfo
            "simple_night_order": False,
            # sensible numbers for number of player reference sheets
            # web: playerCount
            # - sample: 1
            # - teensyville: 7
            # - ravenswood_regular: 16
            # - ravenswood_max: 21
            "player_count": 3,
            # we don't require this, but we do allow it
            "filename": None,
        }

    def _process_options(self, options: Optional[dict]) -> None:
        """Process the options."""

        self.logger.debug("options: %s", options)

        self.options = self._default_options()

        # village size / player_count of 'sample' is a special case
        # we need to convert it to a number, and set some other options
        # which may get overwritten by the options passed in, but that's ok
        if self.options.get("pdf_format") == "sample":
            self.logger.debug("pdf_format is sample; setting related options")
            # we want easyprint, double sided, player night order, and not simple night order
            self.options["double_sided"] = True
            self.options["player_night_order"] = True
            self.options["simple_night_order"] = False
            # we want 1 player sheet - it's a short sample
            self.options["player_count"] = 1

        # maybe overwrite defaults with preferred options
        if options is not None:
            # raise an error if options contains any unexpected keys, i.e. not
            # in self.options as they are right now
            if not set(options.keys()).issubset(set(self.options.keys())):
                unexpected_keys = set(options.keys()) - set(self.options.keys())
                unexpected = ", ".join(sorted(unexpected_keys))
                raise ValueError(f"""Unexpected options: {unexpected}""")

            self.options.update(options)
            self.logger.debug("self.options: %s", self.options)

        # make sure we store the options as attributes
        self.paper_size = self.options.get("paper_size", "A4")
        self.pdf_format = self.options.get("pdf_format", "regular")
        self.double_sided = self.options.get("double_sided", False)
        self.player_night_order = self.options.get("player_night_order", False)
        self.simple_night_order = self.options.get("simple_night_order", False)
        self.player_count = self.options.get("player_count", 3)

        # player_count must be an integer; we need to convert from the special
        # values (teenyville, ravenswood_regular, ravenswood_max) to the actual
        # numbers
        if self.player_count == "sample":
            self.player_count = 1
        elif self.player_count == "teensyville":
            self.player_count = 7
        elif self.player_count == "ravenswood_regular":
            self.player_count = 16
        elif self.player_count == "ravenswood_traveler":
            self.player_count = 21

        # a safety net to make sure some crazy value hasn't slipped through
        if not isinstance(self.player_count, int):
            raise ValueError(
                f"""player_count must be an int, not {self.player_count}"""
            )
        # make sure it's a sensible number
        if self.player_count < 1 or self.player_count > 21:
            raise ValueError(
                f"""player_count must be between 1 and 21, not {self.player_count}"""
            )

    def __str__(self) -> str:
        # return a string representation of the options
        option_strings = []
        for key, value in self.options.items():
            option_strings.append(f"{key}={value}")

        return "ScriptOptions(" + ", ".join(option_strings) + ")"

    def get_filename_slug(self) -> str:
        """Return a slug for the filename based on the options."""
        # pylint: disable=too-many-branches

        # we want to include the paper size in the filename
        filename_slug = self.paper_size.lower()

        # we want to include the simple night order in the filename
        if self.simple_night_order:
            filename_slug += "_compactnight"

        # we want to include the easy print option in the filename
        if self.pdf_format == "easyprint":
            filename_slug += "_easyprint"

            # these are only meaningful if easy print is enabled

            # we want to include the double sided option in the filename
            if self.double_sided:
                filename_slug += "_2sided"

            # we want to include the night order in the filename
            if self.player_night_order:
                filename_slug += "_playernightorder"

            # we want to include the player count in the filename
            filename_slug += f"_{self.player_count}playersheets"

        return filename_slug
