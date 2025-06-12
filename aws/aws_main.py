import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from fontTools.varLib.errors import KeysDiffer

from ckan import create_dataset, add_resource_link  # Importing CKAN functions


def get_s3_client(aws_access_key, aws_secret_key, region="us-east-1"):
    """
    Create an S3 client using provided AWS credentials.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )

def get_bucket_metadata(s3_client, bucket_name):
    """Retrieve bucket-level metadata using the passed-in client."""
    bucket_metadata = {
        "BucketName": bucket_name,
        "CreationDate": None,
        "Region": None,
        "Tags": []
    }

    # Get bucket creation date
    try:
        buckets_response = s3_client.list_buckets()
        for bucket in buckets_response.get("Buckets", []):
            if bucket["Name"] == bucket_name:
                bucket_metadata["CreationDate"] = bucket.get("CreationDate").isoformat()
                break
    except ClientError as e:
        return None, f"Error getting bucket creation date: {e}"

    # Get bucket region
    try:
        location = s3_client.get_bucket_location(Bucket=bucket_name)
        bucket_metadata["Region"] = location.get("LocationConstraint") or "us-east-1"
    except ClientError as e:
        return None, f"Error getting bucket location: {e}"

    # Get bucket tags (Requires permission)
    try:
        tagging = s3_client.get_bucket_tagging(Bucket=bucket_name)
        bucket_metadata["Tags"] = tagging.get("TagSet", [])
    except ClientError:
        # Downgrade to warning if tags are missing or access denied
        pass

    return bucket_metadata, None

def get_objects_metadata(s3_client, bucket_name):
    """Retrieve metadata for all objects in a bucket using the passed-in client."""
    objects_metadata = []
    paginator = s3_client.get_paginator("list_objects_v2")
    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                object_meta = {
                    "Key": obj["Key"],
                    "Size": obj["Size"],
                    "LastModified": obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "StorageClass": obj.get("StorageClass", "STANDARD"),
                    "S3_URL": f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}",
                }
                # Additional metadata
                try:
                    head = s3_client.head_object(Bucket=bucket_name, Key=obj["Key"])
                    object_meta["ContentType"] = head.get("ContentType", "Unknown")
                    object_meta["ETag"] = head.get("ETag")
                    object_meta["CustomMetadata"] = head.get("Metadata", {})
                except ClientError:
                    pass

                objects_metadata.append(object_meta)
    except ClientError as e:
        return None, f"Error listing objects in bucket: {e}"

    return objects_metadata, None


def replicate_aws_bucket_to_ckan(bucket_name, s3_client):
    """
    Replicates an AWS S3 bucket to CKAN by:
      1. Extracting bucket and object metadata.
      2. Creating a CKAN dataset.
      3. Adding resource links for each object.
    Returns a status message string.
    """

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            return f"Error: AWS bucket '{bucket_name}' not found or you do not have permission to access it."
        else:
            return f"Error accessing AWS bucket '{bucket_name}': {e}"

    log_messages = []

    bucket_metadata, error = get_bucket_metadata(s3_client, bucket_name)
    if error:
        return f"Failed to get bucket metadata: {error}"
    log_messages.append(f"Bucket metadata retrieved for '{bucket_name}'.")

    objects_metadata, error = get_objects_metadata(s3_client, bucket_name)
    if error:
        return f"Failed to list objects in bucket: {error}"
    log_messages.append(f"Retrieved metadata for {len(objects_metadata)} objects.")

    # Prepare CKAN dataset
    dataset_data = {
        "name": bucket_metadata["BucketName"].replace("_", "-").lower(),
        "title": bucket_metadata["BucketName"],
        "notes": f"Dataset imported from AWS S3 bucket: {bucket_metadata['BucketName']}",
        "owner_org": "cyverse",
        "tags": [{"name": tag["Key"], "display_name": tag["Value"]} for tag in bucket_metadata["Tags"]],
        "extras": [
            {"key": "Region", "value": bucket_metadata["Region"]},
            {"key": "CreationDate", "value": bucket_metadata["CreationDate"]},
        ],
    }

    dataset_response = create_dataset(dataset_data)
    if not dataset_response.get("success"):
        return f"Failed to create dataset: {dataset_response}"
    dataset_id = dataset_response["result"]["id"]
    log_messages.append(f"Dataset created in CKAN with id {dataset_id}.")

    # Add each object as a resource link
    for obj in objects_metadata:
        resource_data = {
            "package_id": dataset_id,
            "name": obj["Key"],
            "url": obj["S3_URL"],
            "format": obj.get("ContentType", "Unknown"),
            "size": obj["Size"],
            "Last Modified AWS": obj["LastModified"],
        }
        response = add_resource_link(resource_data)
        if response.get("success"):
            log_messages.append(f"Added resource: {obj['Key']}")
        else:
            log_messages.append(f"Failed to add resource '{obj['Key']}': {response}")

    # Save metadata locally (optional)
    # try:
    #     with open("s3_metadata.json", "w") as outfile:
    #         json.dump({"BucketMetadata": bucket_metadata, "ObjectsMetadata": objects_metadata}, outfile, indent=4)
    #     log_messages.append("Metadata saved to s3_metadata.json")
    # except Exception as e:
    #     log_messages.append(f"Error saving metadata: {e}")
    #
    # return "\n".join(log_messages)


if __name__ == "__main__":
    bucket_name = "YOUR_BUCKET_NAME"  # CHANGE TO YOUR BUCKET NAME
    s3_client = get_s3_client("YOUR_ACCESS_KEY", "YOUR_SECRET_KEY")

    result = replicate_aws_bucket_to_ckan(bucket_name, s3_client)
    print(result)

