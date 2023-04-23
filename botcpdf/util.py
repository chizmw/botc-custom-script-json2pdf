"""Utility functions for botcpdf."""

import json
import shutil
import sys
import os
from typing import Optional
import requests  # type: ignore
from pdf2image import convert_from_path

import boto3  # type: ignore
from botocore.exceptions import NoCredentialsError  # type: ignore
from botocore.config import Config # type: ignore



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


def load_extra_roles():
    """Load role data from a JSON file."""

    # loop through all json files in gameinfo/characters
    # and load them into a list
    extra_roles = []
    for filename in os.listdir("gameinfo/characters"):
        if filename.endswith(".json"):
            extra_roles.append(load_data(f"gameinfo/characters/{filename}"))

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


def is_aws_env() -> Optional[str]:
    """Check if we're running in AWS Lambda.

    Returns:
        bool: true if we're running in AWS Lambda, false otherwise
    """
    return os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get(
        "AWS_EXECUTION_ENV"
    )


def upload_to_s3(local_file: str, s3_file: str) -> str:
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
    s3 = boto3.client("s3", config=Config(signature_version='s3v4'))  # pylint: disable=invalid-name

    try:
        s3.upload_file(local_file, os.environ["BUCKET_NAME"], s3_file)
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": os.environ["BUCKET_NAME"], "Key": s3_file},
            ExpiresIn=24 * 3600,
        )

        print("Upload Successful", url)
        return url
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {local_file}") from exc

    except NoCredentialsError as exc:
        raise NoCredentialsError() from exc


def upload_pdf_to_s3(pdf_file: str) -> str:
    """Upload a PDF file to S3.

    Args:
        pdf_file (str): local path to the PDF file

    Returns:
        str: signed URL to the uploaded file
    """

    # get the basename of the file
    basename = os.path.basename(pdf_file)

    url = upload_to_s3(pdf_file, f"pdf/{basename}")

    return url
