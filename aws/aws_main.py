import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from fontTools.varLib.errors import KeysDiffer

from ckan import create_dataset, add_resource_link  # Importing CKAN functions

# Initialize S3 client
s3_client = boto3.client("s3")

def get_bucket_metadata(bucket_name):
    """Retrieve bucket-level metadata."""
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
        print(f"Error getting bucket creation date: {e}")

    # Get bucket region
    try:
        location = s3_client.get_bucket_location(Bucket=bucket_name)
        bucket_metadata["Region"] = location.get("LocationConstraint") or "us-east-1"
    except ClientError as e:
        print(f"Error getting bucket location: {e}")

    # Get bucket tags (Requires permission)
    try:
        tagging = s3_client.get_bucket_tagging(Bucket=bucket_name)
        bucket_metadata["Tags"] = tagging.get("TagSet", [])
    except ClientError as e:
        print(f"Bucket has no tags or access denied: {e}")

    return bucket_metadata

def get_objects_metadata(bucket_name):
    """Retrieve metadata for all objects in a bucket."""
    objects_metadata = []
    paginator = s3_client.get_paginator("list_objects_v2")

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                object_meta = {
                    "Key": obj["Key"],
                    "Size": obj["Size"],
                    "LastModified": obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),  # FIXED DATE FORMAT
                    "StorageClass": obj.get("StorageClass", "STANDARD"),
                    "S3_URL": f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}",

                }
                # Try to fetch additional metadata
                try:
                    head = s3_client.head_object(Bucket=bucket_name, Key=obj["Key"])
                    object_meta["ContentType"] = head.get("ContentType", "Unknown")
                    object_meta["ETag"] = head.get("ETag")
                    object_meta["CustomMetadata"] = head.get("Metadata", {})
                except ClientError as e:
                    print(f"Skipping additional metadata for {obj['Key']} (Access Denied)")

                objects_metadata.append(object_meta)
    except ClientError as e:
        print(f"Error listing objects in bucket: {e}")

    return objects_metadata

def main():
    bucket_name = "your-bucket-name" # CHANGE TO YOUR BUCKET NAME

    # Step 1: Extract metadata
    bucket_metadata = get_bucket_metadata(bucket_name)
    objects_metadata = get_objects_metadata(bucket_name)

    # Step 2: Prepare CKAN dataset
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

    # Step 3: Create dataset in CKAN
    dataset_response = create_dataset(dataset_data)
    if not dataset_response.get("success"):
        print(f"Failed to create dataset: {dataset_response}")
        return

    dataset_id = dataset_response["result"]["id"]
    print(f"Dataset '{bucket_metadata['BucketName']}' created successfully in CKAN.")

    # Step 4: Add resources (file links) to CKAN
    for obj in objects_metadata:
        resource_data = {
            "package_id": dataset_id,
            "name": obj["Key"],
            "url": obj["S3_URL"],
            "format": obj.get("ContentType", "Unknown"),
            "size": obj["Size"],
            "Last Modified AWS": obj["LastModified"],  # This is now in ISO 8601 format
        }
        resource_response = add_resource_link(resource_data)
        if not resource_response.get("success"):
            print(f"Failed to add resource {obj['Key']}: {resource_response}")

    # Step 5: Save metadata locally for reference
    complete_metadata = {
        "BucketMetadata": bucket_metadata,
        "ObjectsMetadata": objects_metadata,
    }
    with open("s3_metadata.json", "w") as outfile:
        json.dump(complete_metadata, outfile, indent=4)
    print("Metadata saved to s3_metadata.json")

if __name__ == "__main__":
    main()
