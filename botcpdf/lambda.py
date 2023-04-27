""" Lambda function to render a PDF from a JSON script. """
import os
import sys
import json
import traceback
from typing import Any, Dict

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from requests_toolbelt import MultipartDecoder

from botcpdf.script import Script
from botcpdf.util import upload_pdf_to_s3
from botcpdf.version import __version__

# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
logger: Logger = Logger(service="botc-custom-script-json2pdf", level=LOGLEVEL)


def render(event: Dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda function to render a PDF from a JSON script.

    Args:
        event (Dict[str, Any]): Lambda event
        context (LambdaContext): Lambda context

    Returns:
        dict[str, Any]: Lambda response for API Gateway
    """
    logger.set_correlation_id(context.aws_request_id)

    # pint our module name to make it easier to find in CloudWatch logs
    logger.debug("%s handler called", __name__)
    logger.debug(event)

    # we've changed the upload/input format to work with the web page submission
    # which means the event body is now a multipart/form-data
    # so we need to parse it
    # we can use requests-toolbelt for this
    multipart_data = MultipartDecoder(
        event["body"],
        event["headers"]["content-type"],
    )

    for part in multipart_data.parts:
        # we're only interested in the JSON part
        if not part.headers[b"Content-Disposition"].startswith(
            b'form-data; name="json"'
        ):
            logger.debug("skipping part %s", part.headers[b"Content-Disposition"])
            continue

        # we need to convert event["body"] from a JSON string to a Python dict
        # we can do this with the json module
        body_json = json.loads(part.content)
        logger.debug(body_json)

        # we should only have one part, so we can break out of the loop
        break

    script = Script(
        title="A Script Has No Name",
        script_data=body_json,
        logger=logger,
    )
    logger.info("Rendering %s…", script.title)

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
            "headers": {
                "x-botc-json2pdf-version": __version__,
            },
            "isBase64Encoded": False,
            "body": f"Error: {err}",
        }
        traceback.print_stack()
        return response

    # redirect in the response
    response = {
        "statusCode": 200,
        "headers": {
            "Location": url,
            "x-botc-json2pdf-version": __version__,
        },
        "isBase64Encoded": False,
        "body": json.dumps(
            {
                "url": url,
                "script_name": script.title,
                "version": __version__,
            }
        ),
    }

    return response


if __name__ == "__main__":
    print("try: make docker-test")
    sys.exit(1)
