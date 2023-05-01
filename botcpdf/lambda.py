""" Lambda function to render a PDF from a JSON script. """
import re
import sys
import json
import logging
import traceback
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext

from botcpdf.script import Script
from botcpdf.util import upload_pdf_to_s3
from botcpdf.version import __version__


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(levelname)s: %(name)s, line %(lineno)d: %(message)s")
handler.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(handler)


# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
# LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
# logger: Logger = Logger(service="botc-custom-script-json2pdf", level=LOGLEVEL)


def extract_file_contents(multipart_string) -> tuple[str, Any]:
    """
    Extracts the filename and file contents from a multipart/form-data string.

    If the content type is JSON, it converts the file contents to a Python object.
    Otherwise, it raises a ValueError.

    Args:
        multipart_string (str): The multipart/form-data string to parse.

    Returns:
        tuple: A tuple containing the filename (str) and the file contents
        (object), converted to a Python object if the content type is JSON.

    Raises:
        ValueError: If the boundary or file contents are not found in the
        multipart_string, or if the content type is unsupported.
    """
    boundary_match = re.search(r"^--(.+?)\r\n", multipart_string)
    if not boundary_match:
        raise ValueError("Boundary not found in the multipart_string")

    boundary = boundary_match.group(1)
    file_contents_pattern = re.compile(
        rf'Content-Disposition: form-data; name="file"; filename="(.+?)"\r\n'
        rf"Content-Type: (.+?)\r\n"
        rf"\r\n"
        rf"(.*?)\r\n--{boundary}",
        re.DOTALL,
    )

    match = file_contents_pattern.search(multipart_string)
    if match:
        filename = match.group(1)
        content_type = match.group(2)
        file_contents = match.group(3)

        if content_type == "application/json":
            return filename, json.loads(file_contents)
        raise ValueError("Unsupported content type")

    raise ValueError("File contents not found in the multipart_string")


def render(event: Dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda function to render a PDF from a JSON script.

    Args:
        event (Dict[str, Any]): Lambda event
        context (LambdaContext): Lambda context

    Returns:
        dict[str, Any]: Lambda response for API Gateway
    """
    # logger.set_correlation_id(context.aws_request_id)

    # pint our module name to make it easier to find in CloudWatch logs
    logger.debug("%s handler called", __name__)
    logger.debug(event)

    file_name, file_contents = extract_file_contents(event["body"])

    # strip the .json extension to get the script_title
    file_name = file_name.replace(".json", "")

    # we've changed the upload/input format to work with the web page submission
    # which means the event body is now a multipart/form-data
    # so we need to parse it
    # we can use requests-toolbelt for this

    script = Script(
        title=file_name,
        script_data=file_contents,
        logger=logger,
    )
    logger.info("Rendering %s…", script.title)

    # start with the common header information
    # we will ADD to this as required
    headers = {
        "x-botc-json2pdf-version": __version__,
        # we might want to improve this, but I believe this resolves the CORS console error
        # as APIG doesn't provide headers here, just passes on what we give it
        # https://dev.to/aws-builders/your-complete-api-gateway-and-cors-guide-11jb
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD",
        # pylint: disable=line-too-long
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    }

    try:
        # it would be nice to have this return the filepath, or content to return to the user
        pdf_path = script.render()

        # save to S3
        url = upload_pdf_to_s3(pdf_path, context.aws_request_id)

    # we're happy to catch _anything_ here
    # pylint: disable=broad-except
    except Exception as err:
        response = {
            "statusCode": 500,
            "headers": headers,
            "isBase64Encoded": False,
            "body": f"Error: {err}",
        }
        logger.error(response)
        traceback.print_stack()
        return response

    # redirect in the response
    # we ned to add script name and version to the common headers
    headers.update(
        {
            "pdf_url": url,
            "script_name": script.title,
        }
    )
    response = {
        "statusCode": 200,
        "headers": headers,
        "isBase64Encoded": False,
        "body": json.dumps(
            {
                "url": url,
                "script_name": script.title,
                "version": __version__,
            }
        ),
    }
    logger.info(response)

    return response


if __name__ == "__main__":
    print("try: make docker-test")
    sys.exit(1)
