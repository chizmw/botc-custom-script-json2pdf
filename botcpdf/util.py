"""Utility functions for botcpdf."""

import json
import logging
import shutil
import sys
import os
from typing import Optional
import requests
from pdf2image import convert_from_path
from aws_xray_sdk.core import xray_recorder  # type: ignore

import boto3  # type: ignore
from botocore.exceptions import NoCredentialsError  # type: ignore
from botocore.config import Config  # type: ignore
from botcpdf.version import __version__


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


def external_data_filename() -> str:
    """Get the filename of the external data file."""
    return "data/imported/roles-combined.json"


def ensure_data_exists():
    """Ensure the data exists."""
    # we should have data/generate/roles-combined.json
    # if we don't, we should fetch it from the remote source
    if not os.path.exists(external_data_filename()):
        # fetch the data
        file_data = fetch_remote_data(
            "https://raw.githubusercontent.com/chizmw/json-on-the-clocktower/"
            "main/data/generated/roles-combined.json"
        )

        # write it to the file
        with open(external_data_filename(), "w", encoding="utf-8") as json_file:
            json.dump(file_data, json_file, indent=4, sort_keys=True)
            # add a newline to the end of the file
            json_file.write("\n")


def get_role_data():
    """Get the role data."""
    # ensure the data exists
    ensure_data_exists()

    # load the data
    with open(external_data_filename(), "r", encoding="utf-8") as json_file:
        full_data = json.load(json_file)

    return full_data


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


def load_extra_roles():
    """Load role data from a JSON file."""

    # loop through all json files in gameinfo/characters
    # and load them into a list
    extra_roles = []
    for filename in os.listdir("gameinfo/extra-characters"):
        if filename.endswith(".json"):
            extra_roles.append(load_data(f"gameinfo/extra-characters/{filename}"))

    return extra_roles


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

    # DO NOT change anything about these
    if id_slug in ["DEMON", "MINION", "DUSK", "DAWN"]:
        return id_slug

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

    # lowercase
    id_slug = id_slug.lower()

    return id_slug


def is_aws_env() -> Optional[str]:
    """Check if we're running in AWS Lambda.

    Returns:
        bool: true if we're running in AWS Lambda, false otherwise
    """
    return os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get(
        "AWS_EXECUTION_ENV"
    )


def upload_to_s3(
    local_file: str, s3_file: str, download_filename: Optional[str] = None
) -> str:
    """Upload a file to an S3 bucket.

    Args:
        local_file (str): local file to upload
        s3_file (str): name of the file in S3

    Raises:
        FileNotFoundError: local_file not found
        NoCredentialsError: problem with AWS credentials

    Returns:
        str: _description_
    """
    s3client = boto3.client(
        "s3", config=Config(signature_version="s3v4")
    )  # pylint: disable=invalid-name

    try:
        if download_filename is None:
            download_filename = os.path.basename(local_file)

        s3client.upload_file(
            local_file,
            os.environ["BUCKET_NAME"],
            s3_file,
            ExtraArgs={
                "ContentDisposition": f"attachment; filename={download_filename}"
            },
        )
        url = s3client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": os.environ["BUCKET_NAME"], "Key": s3_file},
            ExpiresIn=24 * 3600,
        )

        print(url)

        return url
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {local_file}") from exc

    except NoCredentialsError as exc:
        raise NoCredentialsError() from exc


def upload_pdf_to_s3(pdf_file: str, aws_request_id: str) -> str:
    """Upload a PDF file to S3.

    Args:
        pdf_file (str): local path to the PDF file

    Returns:
        str: signed URL to the uploaded file
    """

    # get the basename of the file
    basename = os.path.basename(pdf_file)

    # get the name and extension
    name, ext = os.path.splitext(basename)

    # we want the new filename to be: version, name, request id, and extension
    pdfname = f"{__version__}-{name}-{aws_request_id}{ext}"

    url = upload_to_s3(pdf_file, f"pdf/{pdfname}", basename)

    return url


def ensure_logger(logger) -> logging.Logger:
    """Ensure we have a logger."""
    # if we don't have a logger, we'll create one that will log to stdout
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(created)f [%(levelname)s] %(name)s, line %(lineno)d: %(message)s"
        )
        handler.setFormatter(formatter)
        # add the handlers to logger
        logger.addHandler(handler)
        logger.debug("No logger provided, creating one.")

        if is_aws_env():
            xray_recorder.configure(service="pdf-api")
            logging.getLogger("aws_xray_sdk").setLevel(logging.DEBUG)

    return logger
