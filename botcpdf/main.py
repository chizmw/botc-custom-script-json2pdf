"""Main entry point for the botcpdf package."""

import sys

from botcpdf.script import Script

from botcpdf.util import fetch_remote_data, load_data


def main():
    """Main entry point for the botcpdf package."""
    # default scriptname - change if just running

    # if we don't have any args, exit with an error
    if len(sys.argv) == 1:
        print("Usage: botcpdf <scriptname>|<scriptjsonurl>")
        sys.exit(1)

    # if our first arg starts with http, assume it's a URL
    if sys.argv[1].startswith("http"):
        script_name = "Unnamed Remote Script"
        print(f"Fetching remote script data from {sys.argv[1]}…")
        script_data = fetch_remote_data(sys.argv[1])
        # script_data should be a list of dicts
        # if there's an entry with id: meta, and a name, use that
        if isinstance(script_data, list):
            for entry in script_data:
                if entry.get("id") == "_meta" and entry.get("name"):
                    script_name = entry["name"]
                    break

    # otherwise, assume it's a filename
    else:
        filename = sys.argv[1]

        script_data = load_data(filename)

    # pylint: disable=duplicate-code
    script_options = {
        "paper_size": "A4",
        "simple_night_order": False,
        "easy_print_pdf": True,
        "double_sided": True,
        "player_night_order": True,
        "player_count": "teensyville",
        "filename": filename,
        "script_name": script_name,
    }

    script = Script(
        script_data=script_data,
        options=script_options,
    )

    script.render()


if __name__ == "__main__":
    main()
