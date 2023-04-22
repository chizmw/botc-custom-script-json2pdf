import os
import sys
import json
from typing import Any, Dict

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from botcpdf.script import Script

# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logger: Logger = Logger(service='botc-custom-script-json2pdf', level=LOGLEVEL)

def render(event: Dict[str, Any], context: LambdaContext):
    logger.set_correlation_id(context.aws_request_id)

    # pint our module name to make it easier to find in CloudWatch logs
    logger.debug(f"{__name__} handler called")
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
    logger.info(f"""Rendering "{script.title}"…""")

    # it would be nice to have this return the filepath, or content to return to the user
    script.render()
    # for now return a 200 OK response with the body_json as the response
    return {
        "statusCode": 200,
        "body": json.dumps(body_json),
        "headers": {
            "Content-Type": "application/json"
        }
    }

if __name__ == "__main__":
    print("try: make docker-test")
    sys.exit(1)
