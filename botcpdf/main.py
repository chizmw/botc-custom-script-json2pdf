"""Main entry point for the botcpdf package."""

import sys

from botcpdf.script import Script

from botcpdf.util import load_data


def main():
    # default scriptname - change if just running
    # if using a commandline, specify the name as the first arg
    filename = "Trouble Brewing.json"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    script_data = load_data(filename)
    # this is kinda rudimentary, but it works as a first pass
    script_name = filename.split(".")[0]
    script = Script(script_name, script_data)
    script.render()


if __name__ == "__main__":
    main()
