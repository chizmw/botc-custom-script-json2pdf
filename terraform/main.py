def lambda_handler(event, context):
    print(event)
    print(context)
    response_msg = {
        "statusCode": 200,
        "body": "Hello world",
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
    return response_msg
