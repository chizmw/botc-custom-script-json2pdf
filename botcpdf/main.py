"""Main entry point for the botcpdf package."""

import sys

from botcpdf.script import Script

from botcpdf.util import load_data


def main():
    """Main entry point for the botcpdf package."""
    # default scriptname - change if just running
    # if using a commandline, specify the name as the first arg
    filename = "Trouble Brewing.json"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    script_data = load_data(filename)

    # this is kinda rudimentary, but it works as a first pass
    # strip the path and extension from the filename
    script_name = filename.rsplit("/", maxsplit=1)[-1].split(".", maxsplit=1)[0]

    script = Script(script_name, script_data)
    print(f"""Rendering "{script.title}"…""")
    script.render()


if __name__ == "__main__":
    main()
