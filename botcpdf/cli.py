""" Command line interface for botcpdf. """
import logging
import click
from botcpdf.script import Script
from botcpdf.util import load_data
from botcpdf.version import __version__

context_settings = {"help_option_names": ["-h", "--help"], "max_content_width": 200}


@click.group()
def cli():
    """Main entry point for the botcpdf package."""
    # this is a place holder for a command group
    # pylint: disable=unnecessary-pass
    pass


@click.command(context_settings=context_settings)
# paper size
@click.option(
    "--paper-size",
    type=click.Choice(["A4", "Letter"], case_sensitive=False),
    help="paper size to use for the PDF",
    default="A4",
)
@click.option(
    "-n",
    "--script-name",
    "scriptname",
    default="A Script Has No Name",
    help="name of the script to use if none in JSON metadata",
)
@click.option(
    "-f",
    "--format",
    "scriptformat",
    type=click.Choice(
        ["sample", "regular", "easyprint"],
        case_sensitive=False,
    ),
    default="sample",
    help="script format to use for the PDF",
)
# double / single sided
@click.option(
    "-1",
    "--single-sided",
    "doublesided",
    flag_value=False,
    help="disable double-sided printing (--easyprint required)",
)
@click.option(
    "-2",
    "--double-sided",
    "doublesided",
    flag_value=True,
    default=True,
    help="enable double-sided printing (--easyprint required)",
)
# show players the night order
@click.option(
    "-p",
    "--player-night-order",
    "playernightorder",
    flag_value=True,
    default=False,
    help="show players the night order (--double-sided required)",
)
# show a simple night order
@click.option(
    "-s",
    "--simple-night-order",
    "simplenightorder",
    flag_value=True,
    default=False,
    help="generate a simple one-page night order sheet for the ST",
)
# player count; either a number or a special value
@click.option(
    "--village-size",
    "villagesize",
    type=click.Choice(
        ["sample", "teensyville", "ravenswood_regular", "ravenswood_traveler"],
        case_sensitive=False,
    ),
    default="sample",
    help="guide the number of copies of the player "
    "reference sheet to generate. (--easyprint required)",
)
@click.option("--debug", "debug", flag_value=True, default=False)
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
# pylint: disable=too-many-arguments
def make_pdf(
    doublesided,
    scriptformat,
    filename,
    paper_size,
    playernightorder,
    scriptname,
    simplenightorder,
    villagesize,
    debug,
):
    """Use the JSON file at FILENAME to generate a PDF of a custom script."""
    scriptdata = load_data(filename)

    # if we have 'sample' as the format, we need to enable player night order
    if scriptformat == "sample":
        playernightorder = True

    options = {
        "paper_size": paper_size,
        "pdf_format": scriptformat,
        "double_sided": doublesided,
        "player_night_order": playernightorder,
        "simple_night_order": simplenightorder,
        "player_count": villagesize,
        "filename": filename,
    }

    # we can't know the final script title before we configure the logger
    # Script sets the title in the constructor, and we want to pass a logger to
    # the constructor
    # let's just use a generic name for the log file
    logfilename = "botcpdf.log"

    # create a logger
    logger = cli_logger(logfilename)
    # if we have debug, set the logger to debug
    if debug:
        logger.setLevel(logging.DEBUG)

    click.echo(f"Logging to {logfilename}, please wait…")

    # log the options
    logger.debug("Script name: %s", scriptname)
    logger.debug("Script Format: %s", scriptformat)
    logger.debug("Paper size: %s", paper_size)
    logger.debug("Double-sided: %s", doublesided)
    logger.debug("Player night order: %s", playernightorder)
    logger.debug("Simple night order: %s", simplenightorder)
    logger.debug("Village Size: %s", villagesize)
    logger.debug("Filename: %s", filename)
    logger.info("Options: %s", options)

    # log our project version
    logger.info("botcpdf version: %s", __version__)

    logger.info("Rendering script: %s…", scriptname)
    script = Script(
        script_data=scriptdata,
        options=options,
        logger=logger,
    )
    script.render()
    logger.info("Done!")

    # post to discord if we have a webhook
    script.post_to_discord()


cli.add_command(make_pdf)


def cli_logger(logfilename: str) -> logging.Logger:
    """create a logger that logs only to a file"""
    # have the logger in a variable so we can use it later
    logger = logging.getLogger(__name__)

    # set the log level to INFO by default
    logger.setLevel(logging.INFO)
    # create a file handler
    handler = logging.FileHandler(logfilename)
    # create a logging format
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(message)s")
    # set the formatter to the handler
    handler.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    cli()
