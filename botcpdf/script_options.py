"""This module contains the ScriptOptions class, which represents PDF rendering choices """


from typing import Optional


class ScriptOptions:
    """Represents PDF options for a script."""

    # pylint: disable=too-few-public-methods

    def __init__(self, options: Optional[dict]):
        self._process_options(options)

    def _default_options(self) -> dict:
        """Return a dict of default options."""

        return {
            # we always want to set the paper size
            "paper_size": "A4",
            # easy print allows us to print the PDF in one job
            # (not: here's the player instructions n-times; here's the night
            # order once)
            "easy_print_pdf": True,
            # double sided printing is the default (requires easy_print_pdf)
            "double_sided": True,
            # we want to print the player instructions in the night order
            # (requires easy_print_pdf)
            "player_night_order": True,
            # some STs like the simpler night order
            "simple_night_order": False,
        }

    def _process_options(self, options: Optional[dict]) -> None:
        """Process the options."""
        self.options = self._default_options()

        # maybe overwrite defaults with preferred options
        if options is not None:
            # raise an error if options contains any unexpected keys, i.e. not
            # in self.options as they are right now
            if not set(options.keys()).issubset(set(self.options.keys())):
                unexpected_keys = set(options.keys()) - set(self.options.keys())
                unexpected = ", ".join(sorted(unexpected_keys))
                raise ValueError(f"""Unexpected options: {unexpected}""")

            self.options.update(options)

        self.paper_size = self.options.get("paper_size", "A4")
        self.easy_print_pdf = self.options.get("easy_print_pdf", False)
        self.double_sided = self.options.get("double_sided", False)
        self.player_night_order = self.options.get("player_night_order", False)
        self.simple_night_order = self.options.get("simple_night_order", False)

    def __str__(self) -> str:
        # return a string representation of the options
        option_strings = []
        for key, value in self.options.items():
            option_strings.append(f"{key}={value}")

        return "ScriptOptions(" + ", ".join(option_strings) + ")"
