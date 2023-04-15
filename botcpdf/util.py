"""Utility functions for botcpdf."""

import json
import shutil
import sys
import os
from pdf2image import convert_from_path


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
