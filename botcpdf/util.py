"""Utility functions for botcpdf."""

import json
import shutil
import sys
import os
import requests  # type: ignore
from pdf2image import convert_from_path


def fetch_remote_data(url: str):
    """Fetch data from a remote URL."""

    response = requests.get(url, timeout=10, allow_redirects=True)
    response.raise_for_status()
    return response.json()


def load_data(filename: str):
    """Load data from a JSON file."""
    with open(filename, encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data


def load_role_data():
    """Load role data from a JSON file."""
    return load_data("gameinfo/roles-bra1n.json")


def load_fabled_data():
    """Load role data from a JSON file."""
    return load_data("gameinfo/roles-bra1n-fabled.json")


def load_jinxdata():
    """Load role data from a JSON file."""
    return load_data("gameinfo/jinx.json")


def load_nightdata():
    """Load role data from a JSON file."""
    return load_data("gameinfo/nightsheet.json")


def load_nightmeta():
    """Load role data from a JSON file."""
    return load_data("gameinfo/roles-nightmeta.json")


def pdf2images(pdf_file: str, output_dir: str):
    """Convert a PDF file to a set of images."""

    # this does require poppler on a mac
    # https://github.com/Belval/pdf2image#mac
    # if we're on a mac and we have BOTC_PDF2IMAGE set...
    if sys.platform == "darwin" and os.environ.get("BOTC_PDF2IMAGE"):
        # check that we have poppler installed
        if not shutil.which("pdftocairo"):
            raise RuntimeError("pdftocairo not found, please install poppler")

    if not os.path.exists(pdf_file):
        raise FileNotFoundError(f"File not found: {pdf_file}")

    # if output_dir doesn't exist, create it
    # there might be missing intermediate directories, so use makedirs
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # get the pages into memory
    pages = convert_from_path(
        pdf_path=pdf_file,
        dpi=200,
        fmt="png",
    )

    # we want to strip the extension from the filename
    basename = os.path.splitext(os.path.basename(pdf_file))[0]

    for page_num, page in enumerate(pages):
        # we a 0-indexed page number, so add 1 to it
        page.save(os.path.join(output_dir, f"{basename}-p{page_num+1}.png"), "PNG")

    # finally copy the PDF to the output directory
    shutil.copy(pdf_file, output_dir)


# we're outside the class now, and this is just helper functions
def cleanup_role_id(id_slug) -> str:
    """Cleanup the character ID."""

    # looking at other projects it seems that the ID in the (bra1n) script data is
    # _close_ to the ID in the role data
    # so we'll just do some cleanup to make it match
    # we do bra1n first, then clocktower.com because of the underscore removal
    id_slug = id_slug.replace("_", "")
    id_slug = id_slug.replace("-", "")  # just the pit-hag... why

    # data from clocktower.com doesn't match what we have in bra1n's data
    # so we'll just do some cleanup to make it match

    # remove all whitespace
    id_slug = id_slug.replace(" ", "")

    # remove all apostrophes
    id_slug = id_slug.replace("'", "")

    # prepend _ to DEMON, MINION, DUSK, and DAWN
    if id_slug in ["DEMON", "MINION", "DUSK", "DAWN"]:
        id_slug = f"_{id_slug}"

    # lowercase
    id_slug = id_slug.lower()

    return id_slug
