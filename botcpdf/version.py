""" Version information for botcpdf. """
from pkg_resources import get_distribution  # type: ignore

__version__ = get_distribution("botc-json2pdf").__dict__.get("_version")
