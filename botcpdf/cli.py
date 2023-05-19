""" Command line interface for botcpdf. """
import logging
import click
from botcpdf.script import Script
from botcpdf.util import load_data
from botcpdf.version import __version__


@click.group()
def cli():
    """Main entry point for the botcpdf package."""
    # this is a place holder for a command group
    # pylint: disable=unnecessary-pass
    pass


@click.command()
# paper size
@click.option(
    "--paper-size",
    type=click.Choice(["A4", "Letter"], case_sensitive=False),
    help="Paper size to use for the PDF.",
    default="A4",
)
# easyprint / regular
@click.option("-e", "--easyprint", "easyprint", flag_value=True, default=False)
@click.option("-r", "--regular", "easyprint", flag_value=False)
# double / single sided
@click.option("-1", "--double-sided", "doublesided", flag_value=True, default=False)
@click.option("-2", "--single-sided", "doublesided", flag_value=False)
# show players the night order
@click.option(
    "-p", "--player-night-order", "playernightorder", flag_value=True, default=False
)
# show a simple night order
@click.option(
    "-s", "--simple-night-order", "simplenightorder", flag_value=True, default=False
)
# player count; either a number or a special value
@click.option(
    "--village-size",
    "villagesize",
    type=click.Choice(
        ["sample", "teensyville", "ravenswood_regular", "ravenswood_traveler"],
        case_sensitive=False,
    ),
    default="ravenswood_regular",
)
@click.option("-n", "--script-name", "scriptname", default="A Script Has No Name")
@click.option("--debug", "debug", flag_value=True, default=False)
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
# pylint: disable=too-many-arguments
def make_pdf(
    doublesided,
    easyprint,
    filename,
    paper_size,
    playernightorder,
    scriptname,
    simplenightorder,
    villagesize,
    debug,
):
    """Make a PDF."""
    scriptdata = load_data(filename)

    options = {
        "paper_size": paper_size,
        "easy_print_pdf": easyprint,
        "double_sided": doublesided,
        "player_night_order": playernightorder,
        "simple_night_order": simplenightorder,
        "player_count": villagesize,
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
    logger.debug("Paper size: %s", paper_size)
    logger.debug("Easyprint: %s", easyprint)
    logger.debug("Double-sided: %s", doublesided)
    logger.debug("Player night order: %s", playernightorder)
    logger.debug("Simple night order: %s", simplenightorder)
    logger.debug("Village Size: %s", villagesize)
    logger.debug("Filename: %s", filename)
    logger.info("Options: %s", options)

    # log our project version
    logger.info("botcpdf version: %s", __version__)

    logger.info("Rendering script: %s…", scriptname)
    script = Script(scriptname, scriptdata, options, logger)
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
