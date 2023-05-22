""" Lambda function to render a PDF from a JSON script. """
import sys
import json
import logging
import traceback
from typing import Any, Dict, Optional

# https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-configuration.html
from aws_xray_sdk.core import xray_recorder  # type: ignore
from aws_xray_sdk.core import patch_all  # type: ignore

from aws_lambda_powertools.utilities.typing import LambdaContext
from botcpdf.multipart import MultipartDecoder

from botcpdf.script import Script
from botcpdf.util import upload_pdf_to_s3
from botcpdf.version import __version__


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    "[lambda] %(levelname)s: %(name)s, line %(lineno)d: %(message)s"
)
handler.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(handler)


xray_recorder.configure(service="pdf-api")
# PLUGINS = ("EC2Plugin", "ECSPlugin")
# xray_recorder.configure(plugins=PLUGINS)
patch_all()
logging.getLogger("aws_xray_sdk").setLevel(logging.DEBUG)


# JSON output format, service name can be set by environment variable "POWERTOOLS_SERVICE_NAME"
# LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
# logger: Logger = Logger(service="botc-custom-script-json2pdf", level=LOGLEVEL)


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def render(event: Dict[str, Any], context: Optional[LambdaContext]) -> dict[str, Any]:
    """Lambda function to render a PDF from a JSON script.

    Args:
        event (Dict[str, Any]): Lambda event
        context (LambdaContext): Lambda context

    Returns:
        dict[str, Any]: Lambda response for API Gateway
    """
    xray_recorder.begin_segment(__name__)

    # logger.set_correlation_id(context.aws_request_id)

    # pint our module name to make it easier to find in CloudWatch logs
    logger.debug("%s handler called", __name__)
    logger.debug(event)

    multipart = MultipartDecoder(event["body"])
    uploaded_files = multipart.get_file_names()
    if len(uploaded_files) != 1:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "Exactly one file must be uploaded",
                    "uploaded_files": uploaded_files,
                }
            ),
        }
    file_info = multipart.get_file(uploaded_files[0])
    if file_info["content_type"] != "application/json":
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "File must be JSON",
                    "content_type": file_info["content_type"],
                }
            ),
        }

    file_name = file_info["name"]
    file_contents = file_info["json"]

    # strip the .json extension to get the script_title
    file_name = file_name.replace(".json", "")

    # we"ve changed the upload/input format to work with the web page submission
    # which means the event body is now a multipart/form-data
    # so we need to parse it
    # we can use requests-toolbelt for this

    # start with nothing in the options
    script_options = {"filename": file_info["name"]}

    # deal with inncoming options
    # do it klunky way first, then refactor to be more elegant later
    # we could say "match the web and the backend" but that"s not a good idea
    # as we want to be able to change the web without breaking the backend
    # and vice versa

    # if we have paperSize, we need to add it to the options
    if option_value := multipart.get_field("paperSize"):
        script_options["paper_size"] = option_value
    else:
        # default to A4
        script_options["paper_size"] = "A4"

    if option_value := multipart.get_field("stNightInfo"):
        if option_value == "onesheet":
            script_options["simple_night_order"] = True
        else:
            # default to doublesided / non-simple
            script_options["simple_night_order"] = False

    if option_value := multipart.get_field("scriptFormat"):
        script_options["pdf_format"] = option_value
    else:
        script_options["pdf_format"] = "sample"

    if option_value := multipart.get_field("printFormat"):
        if option_value == "doubleSided":
            script_options["double_sided"] = True
        else:
            # default to singlesided
            script_options["double_sided"] = False

    if option_value := multipart.get_field("playerNightInfo"):
        if option_value == "yes":
            script_options["player_night_order"] = True
        else:
            # default to no
            script_options["player_night_order"] = False

    if option_value := multipart.get_field("playerCount"):
        script_options["player_count"] = option_value
    else:
        # default to teensyville
        script_options["player_count"] = "teensyville"

    script = Script(
        script_data=file_contents,
        options=script_options,
    )
    logger.info("Rendering %s…", script.title)

    # start with the common header information
    # we will ADD to this as required
    headers = {
        "x-botc-json2pdf-version": __version__,
        # we might want to improve this, but I believe this resolves the CORS console error
        # as APIG doesn"t provide headers here, just passes on what we give it
        # https://dev.to/aws-builders/your-complete-api-gateway-and-cors-guide-11jb
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD",
        # pylint: disable=line-too-long
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    }

    try:
        # it would be nice to have this return the filepath, or content to return to the user
        xray_recorder.begin_segment("script.render")
        pdf_path = script.render()
        xray_recorder.end_segment()

        # save to S3
        if context is not None:
            url = upload_pdf_to_s3(pdf_path, context.aws_request_id)
        else:
            url = "file://just-local.txt"

        script.post_to_discord()

    # we"re happy to catch _anything_ here
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

    xray_recorder.end_segment()

    return response


if __name__ == "__main__":
    # these are based on a real event (Reptiles!) but tweaked to test behaviour with weird options
    fake_events = [
        {
            # pylint: disable=line-too-long
            "body": '------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="paperSize"\r\n\r\nA4\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="stNightInfo"\r\n\r\ntwosheet\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="scriptFormat"\r\n\r\neasyprint\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="printFormat"\r\n\r\ndoubleSided\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerNightInfo"\r\n\r\nyes\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerCount"\r\n\r\nravenswood_regular\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="file"; filename="FakeLambda1.json"\r\nContent-Type: application/json\r\n\r\n[{"id": "_meta", "logo": "https://i.ibb.co/y6xbjrC/Reptiles-logo.png", "name": "FakeLambda1", "author": "Adam"}, {"id": "chef"}, {"id": "washerwoman"}, {"id": "librarian"}, {"id": "sailor"}, {"id": "general"}, {"id": "chambermaid"}, {"id": "snake_charmer"}, {"id": "flowergirl"}, {"id": "undertaker"}, {"id": "innkeeper"}, {"id": "philosopher"}, {"id": "fool"}, {"id": "tea_lady"}, {"id": "virgin"}, {"id": "saint"}, {"id": "sweetheart"}, {"id": "heretic"}, {"id": "drunk"}, {"id": "barber"}, {"id": "poisoner"}, {"id": "devils_advocate"}, {"id": "spy"}, {"id": "psychopath"}, {"id": "baron"}, {"id": "al-hadikhia"}, {"id": "storm_catcher"}, {"id": "djinn"}]\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY--\r\n',
            "isBase64Encoded": False,
        },
        {
            # pylint: disable=line-too-long
            "body": '------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="paperSize"\r\n\r\nA4\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="stNightInfo"\r\n\r\ntwosheet\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="scriptFormat"\r\n\r\nsample\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="printFormat"\r\n\r\ndoubleSided\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerNightInfo"\r\n\r\nyes\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerCount"\r\n\r\nravenswood_regular\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="file"; filename="FakeLambda2.json"\r\nContent-Type: application/json\r\n\r\n[{"id": "_meta", "logo": "https://i.ibb.co/y6xbjrC/Reptiles-logo.png", "name": "FakeLambda2", "author": "Beth"}, {"id": "chef"}, {"id": "washerwoman"}, {"id": "librarian"}, {"id": "sailor"}, {"id": "general"}, {"id": "chambermaid"}, {"id": "snake_charmer"}, {"id": "flowergirl"}, {"id": "undertaker"}, {"id": "innkeeper"}, {"id": "philosopher"}, {"id": "fool"}, {"id": "tea_lady"}, {"id": "virgin"}, {"id": "saint"}, {"id": "sweetheart"}, {"id": "heretic"}, {"id": "drunk"}, {"id": "barber"}, {"id": "poisoner"}, {"id": "devils_advocate"}, {"id": "spy"}, {"id": "psychopath"}, {"id": "baron"}, {"id": "al-hadikhia"}, {"id": "storm_catcher"}, {"id": "djinn"}]\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY--\r\n',
            "isBase64Encoded": False,
        },
        {
            # pylint: disable=line-too-long
            "body": '------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="paperSize"\r\n\r\nA4\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="stNightInfo"\r\n\r\ntwosheet\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="scriptFormat"\r\n\r\nsample\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="printFormat"\r\n\r\ndoubleSided\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerNightInfo"\r\n\r\nyes\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="playerCount"\r\n\r\nravenswood_regular\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY\r\nContent-Disposition: form-data; name="file"; filename="FakeLambda3.json"\r\nContent-Type: application/json\r\n\r\n[{"id": "_meta", "logo": "https://i.ibb.co/y6xbjrC/Reptiles-logo.png", "name": "FakeLambda3", "author": "Caroline"}, {"id": "knight"}, {"id": "steward"}, {"id": "organgrinder"}, {"id": "vizier"}, {"id": "general"}, {"id": "chambermaid"}, {"id": "snake_charmer"}, {"id": "flowergirl"}, {"id": "undertaker"}, {"id": "innkeeper"}, {"id": "philosopher"}, {"id": "fool"}, {"id": "tea_lady"}, {"id": "virgin"}, {"id": "saint"}, {"id": "sweetheart"}, {"id": "heretic"}, {"id": "drunk"}, {"id": "barber"}, {"id": "poisoner"}, {"id": "devils_advocate"}, {"id": "spy"}, {"id": "psychopath"}, {"id": "baron"}, {"id": "al-hadikhia"}, {"id": "storm_catcher"}, {"id": "djinn"}]\r\n------WebKitFormBoundaryZ378ssyY1ve75AZY--\r\n',
            "isBase64Encoded": False,
        },
    ]

    for fake_event in fake_events:
        render(fake_event, None)
    sys.exit(1)
