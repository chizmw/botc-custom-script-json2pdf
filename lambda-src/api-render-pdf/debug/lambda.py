import sys
import os

from weasyprint import HTML  # type: ignore


def render(event, context):
    # print our current working directory
    print(os.getcwd())

    # a list of directories we want to query for contents
    dirs = ["/opt", "/opt/lib", "/opt/python", "/var/task"]

    # for each one, fetch the contents and store in  a dict
    dir_contents = {}
    for dir in dirs:
        # if the directory doesn't exist, skip it
        if not os.path.exists(dir):
            dir_contents[dir] = "Does not exist"
            continue
        dir_contents[dir] = os.listdir(dir)

    return {
        "statusCode": 501,
        "body": "Not Implemented by Chisel ... yet",
        "cwd": os.getcwd(),
        "dirs": dir_contents,
        "sys_path": sys.path,
    }
