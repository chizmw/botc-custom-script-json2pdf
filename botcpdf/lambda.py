""" Lambda function to render a PDF from a JSON script. """
import os
import sys
import json
from typing import Any, Dict

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pkg_resources import get_distribution

from botcpdf.script import Script
from botcpdf.util import upload_pdf_to_s3

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

    # we need to convert event["body"] from a JSON string to a Python dict
    # we can do this with the json module
    body_json = json.loads(event.get("body", "{'error': 'no body'}"))
    logger.debug(body_json)

    script = Script(
        title="docker test",
        script_data=body_json,
        logger=logger,
    )
    logger.info("Rendering %s…", script.title)

    try:
        # it would be nice to have this return the filepath, or content to return to the user
        pdf_path = script.render()

        # save to S3
        url = upload_pdf_to_s3(
            pdf_path,
        )

    except Exception as err:
        response = {
            "statusCode": 500,
            "headers": {
                "x-botc-json2pdf-version": get_distribution("botc-json2pdf").__dict__.get("version"),
            },
            "isBase64Encoded": False,
            "body": f"Error: {err}",
        }
        logger.error(err)
        return response

    # redirect in the response
    response = {
        "statusCode": 302,
        "headers": {
            "Location": url,
            "x-botc-json2pdf-version": get_distribution("botc-json2pdf").__dict__.get("version"),
        },
        "isBase64Encoded": False,
        "body": "",
    }

    return response


if __name__ == "__main__":
    print("try: make docker-test")
    sys.exit(1)
