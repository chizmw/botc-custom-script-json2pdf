from __future__ import print_function
import json
import boto3  # type: ignore
import os
import time


def print_invalidation_url(id: str) -> None:
    print(
        f"https://us-east-1.console.aws.amazon.com/cloudfront/v3/home?region=eu-west-2#/distributions/E72U2QV2O1Z7/invalidations/details/{id}"
    )


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))
    paths = []
    for items in event["Records"]:
        message = items["Sns"]["Message"]

        # message is a string, so we need to convert it to a json object
        message = json.loads(message)

        for record in message["Records"]:
            key = record["s3"]["object"]["key"]
            if key.endswith("index.html"):
                paths.append("/" + key[:-10])
            paths.append("/" + key)

    print("Invalidating: " + ", ".join(paths))

    client = boto3.client("cloudfront")
    batch = {
        "Paths": {"Quantity": len(paths), "Items": paths},
        "CallerReference": str(time.time()),
    }
    invalidation = client.create_invalidation(
        DistributionId=os.environ["CLOUDFRONT_DISTRIBUTION_ID"],
        InvalidationBatch=batch,
    )
    invalidation_id = invalidation["Invalidation"]["Id"]
    print("Invalidation created: " + invalidation_id)
    print_invalidation_url(invalidation_id)
    return batch


if __name__ == "__main__":
    # load the json event from s3event.json
    with open("s3event.json", "r") as f:
        event = json.load(f)

    context = {}  # type: ignore
    lambda_handler(event, context)
