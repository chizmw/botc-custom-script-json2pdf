import sys
from typing import Any, Dict

from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from botcpdf.script import Script

logger: Logger = Logger(service='botc-custom-script-json2pdf')  # JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"

def render(event: Dict[str, Any], context: LambdaContext):
    logger.set_correlation_id(context.aws_request_id)

    # pint our module name to make it easier to find in CloudWatch logs
    logger.debug(f"{__name__} handler called")
    logger.debug(f"event: {event}")

    script = Script(
        title="docker test",
        script_data=event,
        logger=logger,
    )
    logger.info(f"""Rendering "{script.title}"…""")
    return script.render()

if __name__ == "__main__":
    print("try: make docker-test")
    sys.exit(1)
