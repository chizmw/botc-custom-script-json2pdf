import json


def lambda_handler(event, context):
    print(event)
    print(context)

    some_response = {
        "person": "John Doe",
        "age": 30,
        "city": "New York",
        "mood": "happy",
        "url": "https://www.johndoe.com",
    }

    response_msg = {
        "statusCode": 200,
        "body": json.dumps(some_response),
        "headers": {
            # "Access-Control-Allow-Origin": "http://127.0.0.1:5500",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,access-control-allow-origin,X-Chisel-Info",
        },
    }
    return response_msg
