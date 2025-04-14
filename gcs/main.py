from google.cloud import storage
from datetime import timezone
import json
from ckan import get_dataset_id, create_dataset, add_resource_link


def list_public_bucket_objects(bucket_name):
    # REPLACE WITH YOUR CREDENTIALS FILE NAME
    client = storage.Client.from_service_account_json('gcs-credentials.json')
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    object_list = []
    for blob in blobs:
        metadata = {
            "name": blob.name,
            "size_bytes": blob.size,
            "public_url": f"https://storage.googleapis.com/{bucket_name}/{blob.name}",
            "content_type": blob.content_type,
            "storage_class": blob.storage_class,
            "crc32c": blob.crc32c,
            "md5_hash": blob.md5_hash,
            "updated": blob.updated.astimezone(timezone.utc).isoformat() if blob.updated else None,
            "generation": blob.generation,
            "metageneration": blob.metageneration,
            "component_count": blob.component_count,
            "custom_time": blob.custom_time.isoformat() if blob.custom_time else None,
        }
        object_list.append(metadata)
    return object_list


def replicate_gcs_bucket_to_ckan(bucket_name):
    # Dataset name based on bucket
    dataset_name = bucket_name.lower().replace('_', '-')
    dataset_title = f"GCS Bucket: {bucket_name}"

    #Check if dataset exists
    dataset_id = get_dataset_id(dataset_name)

    # Create dataset if needed
    if not dataset_id:
        dataset_metadata = {
            "name": dataset_name,
            "title": dataset_title,
            "notes": f"This dataset was imported from the public Google Cloud bucket '{bucket_name}'.",
            "owner_org": "cyverse"
        }

        created = create_dataset(dataset_metadata)

        if created.get("success"):
            dataset_id = created["result"]["name"]
        else:
            print("Failed to create dataset!")
            return
        print(f"Created CKAN dataset '{dataset_name}'")
    else:
        print(f"Using existing CKAN dataset '{dataset_name}'")

    # List bucket objects
    print(f"Listing objects in bucket: {bucket_name}")
    object_metadata_list = list_public_bucket_objects(bucket_name)

    # add each object as a resource link in CKAN
    for obj in object_metadata_list:
        resource_payload = {
            "package_id": dataset_id,
            "url": obj["public_url"],
            "name": obj["name"].split("/")[-1] or obj["name"],
            "format": obj.get("content_type") or "Unknown",
            "description": f"GCS object from {bucket_name}, last modified {obj['updated'] or 'unknown'}",
        }

        print("Resource payload being sent:")
        print(json.dumps(resource_payload, indent=2))

        response = add_resource_link(resource_payload)
        if response.get("success"):
            print(f"Added resource: {obj['name']}")
        else:
            print(f"Failed to add resource: {obj['name']}, reason: {response.get('error')}")


if __name__ == "__main__":
    # REPLACE WITH YOUR ACTUAL PUBLIC GCS BUCKET NAME
    bucket_name = "gcs-to-ckan-test-bucket"
    replicate_gcs_bucket_to_ckan(bucket_name)
