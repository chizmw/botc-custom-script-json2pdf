"""This module contains the ScriptOptions class, which represents PDF rendering choices """


from typing import Any, Optional

from botcpdf.util import ensure_logger


class ScriptOptions:
    """Represents PDF options for a script."""

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, option_overrides: Optional[dict], logger=None):
        self.logger = ensure_logger(logger=logger)

        # make sure attributes "exist"
        self.__paper_size: str
        self.__pdf_format: str
        self.__double_sided: bool
        self.__player_night_order: int
        self.__simple_night_order: int
        self.__player_count: int
        self.__filename: Optional[str]
        # this is where we store the defaults
        self.__option_defaults: dict[str, Any] = {}

        # set the actual values from the defaults
        self._set_values_from_defaults()

        # process the incoming options
        self._process_options(option_overrides)

    # PROPERTIES

    @property
    def paper_size(self) -> str:
        """Return the paper size."""
        return self.__paper_size

    @paper_size.setter
    def paper_size(self, value: str) -> None:
        """Set the paper size."""
        self.__paper_size = value

    @property
    def pdf_format(self) -> str:
        """Return the pdf format."""
        return self.__pdf_format

    @pdf_format.setter
    def pdf_format(self, value: str) -> None:
        """Set the pdf format."""
        self.logger.warning("pdf_format is being set to %s", value)
        self.__pdf_format = value

        if value == "sample":
            self._set_pdf_sample_options()

    @property
    def double_sided(self) -> bool:
        """Return the double sided setting."""
        return self.__double_sided

    @double_sided.setter
    def double_sided(self, value: bool) -> None:
        """Set the double sided setting."""
        self.__double_sided = value

    @property
    def player_night_order(self) -> int:
        """Return the player night order setting."""
        return self.__player_night_order

    @player_night_order.setter
    def player_night_order(self, value: int) -> None:
        """Set the player night order setting."""
        self.__player_night_order = value

    @property
    def simple_night_order(self) -> int:
        """Return the simple night order setting."""
        return self.__simple_night_order

    @simple_night_order.setter
    def simple_night_order(self, value: int) -> None:
        """Set the simple night order setting."""
        self.__simple_night_order = value

    @property
    def player_count(self) -> int:
        """Return the player count setting."""
        return self.__player_count

    @player_count.setter
    def player_count(self, value: int) -> None:
        """Set the player count setting."""
        self.__player_count = value

    @property
    def filename(self) -> Optional[str]:
        """Return the filename setting."""
        return self.__filename

    @filename.setter
    def filename(self, value: Optional[str]) -> None:
        """Set the filename setting."""
        self.__filename = value

    @property
    def option_defaults(self) -> dict[str, Any]:
        """Return the option defaults."""
        return self.__option_defaults

    @option_defaults.setter
    def option_defaults(self, value: dict[str, Any]) -> None:
        """Set the option defaults."""
        self.__option_defaults = value

    # METHODS

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
            # we could just set the option default to match, but I wanted to
            # catch/test the behaviour of this when paired with 'sample'
            # pdf_format
            "player_count": 3,
            # we don't require this, but we do allow it
            "filename": None,
        }

    def _set_default_options(self) -> None:
        # loop through the dict returned by _default_options
        # and set the attributes on self.options
        for key, value in self._default_options().items():
            self.option_defaults[key] = value

    def _set_pdf_sample_options(self) -> None:
        # as a default is we have a pdf_format of 'sample', we want to set
        # player_count to 1
        if self.pdf_format == "sample":
            self.logger.debug("pdf_format is sample; setting related options")
            # we want easyprint, double sided, player night order, and not simple night order
            self.double_sided = True
            self.player_night_order = True
            self.simple_night_order = False
            # we want 1 player sheet - it's a short sample
            self.player_count = 1

    def _set_values_from_defaults(self) -> None:
        # store them for easier access later
        self._set_default_options()

        # get the keys from self.option_defaults
        # move 'pdf_format' to the end of the list
        # so that it's set last, dealing with any craziness that we have in the
        # defaults
        keys = list(self.option_defaults.keys())
        keys.remove("pdf_format")
        keys.append("pdf_format")

        # loop through the keys
        for key in keys:
            # get the value from self.option_defaults
            value = self.option_defaults[key]
            # set the attribute on self
            setattr(self, key, value)

    def _process_options(self, option_overrides: Optional[dict]) -> None:
        """Process the options."""

        self.logger.debug("default option overrides: %s", option_overrides)

        # if we DO have option overrides, straying from the defaults
        if option_overrides is not None:
            # raise an error if options contains any unexpected keys, i.e. not
            # a key we know about from self.default_options
            if not set(option_overrides.keys()).issubset(
                set(self.option_defaults.keys())
            ):
                unexpected_keys = set(option_overrides.keys()) - set(
                    self.option_defaults.keys()
                )
                unexpected = ", ".join(sorted(unexpected_keys))
                raise ValueError(f"""Unexpected options: {unexpected}""")

            # village size / player_count of 'sample' is a special case
            # we need to convert it to a number, and set some other options
            # which may get overwritten by the options passed in, but that's ok
            if option_overrides.get("pdf_format") == "sample":
                self.pdf_format = "sample"

            # now we can set the options from the overrides by looping through
            # and setting the attributes
            for key, value in option_overrides.items():
                # if they're different frm what we have, print a debug message
                if value != self.option_defaults[key]:
                    self.logger.debug("setting %s to %s", key, value)
                    setattr(self, key, value)

            # player_count must be an integer; we need to convert from the
            # special values (teenyville, ravenswood_regular, ravenswood_max)
            # to the actual numbers
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
        # loop through the self._default_options dict for the values we want,
        # then add the key and the attribute value to the list
        # pylint: disable=consider-iterating-dictionary
        for key in self._default_options().keys():
            option_strings.append(f"{key}={getattr(self, key)}")

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

        if self.pdf_format == "sample":
            filename_slug += "_showcase"

        # these are only meaningful if easy print is enabled, or if we're
        # using the sample format
        if self.pdf_format in ("easyprint", "sample"):
            # we want to include the double sided option in the filename
            if self.double_sided:
                filename_slug += "_2sided"

            # we want to include the night order in the filename
            if self.player_night_order:
                filename_slug += "_playernightorder"

            # we want to include the player count in the filename
            filename_slug += f"_{self.player_count}playersheets"

        return filename_slug
