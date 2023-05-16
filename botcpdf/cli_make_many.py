"""Make a variety of PDFs from a single script."""

import sys

from botcpdf.script import Script

from botcpdf.util import load_data

variations = [
    {
        "name": "Simple-Traveler",
        "options": {
            "paper_size": "A4",
            "simple_night_order": False,
            "easy_print_pdf": False,
            "double_sided": True,
            "player_night_order": True,
            "player_count": "ravenswood_traveler",
        },
    },
    {
        "name": "Double-Player-Teensy",
        "options": {
            "paper_size": "A4",
            "simple_night_order": False,
            "easy_print_pdf": True,
            "double_sided": True,
            "player_night_order": True,
            "player_count": "teensyville",
        },
    },
    {
        "name": "Double-PlayerNoNight-Regular",
        "options": {
            "paper_size": "A4",
            "simple_night_order": False,
            "easy_print_pdf": True,
            "double_sided": True,
            "player_night_order": False,
            "player_count": "ravenswood_regular",
        },
    },
]


def main():
    """Main entry point for the botcpdf package."""

    filename = sys.argv[1]
    # this is kinda rudimentary, but it works as a first pass
    # strip the path and extension from the filename
    script_name = filename.rsplit("/", maxsplit=1)[-1].split(".", maxsplit=1)[0]
    script_data = load_data(filename)

    for variation in variations:
        script_options = variation["options"]
        script = Script(script_name, script_data, script_options)
        print(f"""Rendering "{script.title}" as {variation["name"]}…""")
        script.render()


if __name__ == "__main__":
    main()
