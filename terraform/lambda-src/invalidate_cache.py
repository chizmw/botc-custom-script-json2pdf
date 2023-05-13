from __future__ import print_function
import json
import boto3  # type: ignore
import time


def print_invalidation_url(id: str, cfid: str) -> None:
    print(
        f"https://us-east-1.console.aws.amazon.com/cloudfront/v3/home?region=eu-west-2#/distributions/{cfid}/invalidations/details/{id}"
    )


def lambda_handler(event, context):
    print(event)
    paths = []
    for items in event["Records"]:
        # print(items)

        s3info = items.get("s3", None)
        if s3info is None:
            print("No s3info")
            continue

        changed_object = s3info.get("object", None)
        if changed_object is None:
            print("No changedObject")
            continue

        bucket = s3info.get("bucket", None)
        if bucket is None:
            print("No bucket")
            continue

        key = changed_object.get("key", None)
        if key is None:
            print("No key")
            continue

        # get the BelongsToDist tag for the object in the bucket
        s3 = boto3.client("s3")
        print(f"Getting tags for s3://{bucket['name']}/{key}")
        response = s3.get_object_tagging(
            Bucket=bucket["name"],
            Key=key,
        )

        tagset = response.get("TagSet", None)
        if tagset is None:
            print("No tagset")
            continue

        print(f"TagSet: {tagset}")

        belongs_to_dist = None
        for tag in tagset:
            if tag["Key"] == "BelongsToDist":
                belongs_to_dist = tag["Value"]
                break

        if belongs_to_dist is None:
            print("No belongs_to_dist")
            continue

        print(f"BelongsToDist: {belongs_to_dist}")

        if key.endswith("index.html"):
            paths.append("/" + key[:-10])

        paths.append("/" + key)

    print(f"{belongs_to_dist}: Invalidating: " + ", ".join(paths))

    client = boto3.client("cloudfront")
    batch = {
        "Paths": {"Quantity": len(paths), "Items": paths},
        "CallerReference": str(time.time()),
    }
    invalidation = client.create_invalidation(
        DistributionId=belongs_to_dist,
        InvalidationBatch=batch,
    )
    invalidation_id = invalidation["Invalidation"]["Id"]
    print("Invalidation created: " + invalidation_id)
    print_invalidation_url(invalidation_id, belongs_to_dist)
    return batch


if __name__ == "__main__":
    # load the json event from s3event.json
    with open("s3event.json", "r") as f:
        event = json.load(f)

    context = {}  # type: ignore
    lambda_handler(event, context)
