from google.cloud import storage, exceptions
from datetime import timezone
import json
from ckan import get_dataset_id, create_dataset, add_resource_link


def list_public_bucket_objects(gcs_client, bucket_name):
    bucket = gcs_client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    object_list = []
    for blob in blobs:
        object_list.append({
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
        })
    return object_list


def replicate_gcs_bucket_to_ckan(bucket_name, gcs_client):
    """
    Replicates a public GCS bucket to CKAN by:
      1. Checking/creating the CKAN dataset.
      2. Listing objects from the bucket.
      3. Adding each object as a resource to CKAN.
    Returns a status message string.
    """

    try:
        # This will raise NotFound if the bucket does not exist or is not accessible
        gcs_client.get_bucket(bucket_name)
    except exceptions.NotFound:
        return f"Error: GCS bucket '{bucket_name}' not found or you do not have permission to access it."
    except Exception as e:
        return f"Error accessing GCS bucket '{bucket_name}': {e}"

    log_messages = []
    dataset_name = bucket_name.lower().replace('_', '-')
    dataset_title = f"GCS Bucket: {bucket_name}"

    # Check or create dataset
    dataset_id = get_dataset_id(dataset_name)
    if not dataset_id:
        created = create_dataset({
            "name": dataset_name,
            "title": dataset_title,
            "notes": f"Imported from GCS bucket '{bucket_name}'",
            "owner_org": "cyverse"
        })
        if not created.get("success"):
            return f"Failed to create dataset: {created}"
        dataset_id = created["result"]["name"]
        log_messages.append(f"Created dataset '{dataset_name}'.")
    else:
        log_messages.append(f"Using existing dataset '{dataset_name}'.")

    # List objects
    log_messages.append(f"Listing objects in '{bucket_name}'...")
    objects = list_public_bucket_objects(gcs_client, bucket_name)
    log_messages.append(f"Found {len(objects)} objects.")

    # Add resources
    for obj in objects:
        payload = {
            "package_id": dataset_id,
            "url": obj["public_url"],
            "name": obj["name"].split("/")[-1] or obj["name"],
            "format": obj.get("content_type", "Unknown"),
            "description": f"Last modified {obj['updated'] or 'unknown'}"
        }
        resp = add_resource_link(payload)
        if resp.get("success"):
            log_messages.append(f"Added resource: {obj['name']}")
        else:
            log_messages.append(f"Failed to add {obj['name']}: {resp.get('error')}")

    return "\n".join(log_messages)


if __name__ == "__main__":
    # When run directly, replace with your actual public GCS bucket name and credentials JSON path
    bucket_name = "YOUR_GCS_BUCKET_NAME"
    gcs_client = storage.Client.from_service_account_json("YOUR_CREDENTIALS_JSON_PATH")
    result = replicate_gcs_bucket_to_ckan(bucket_name, gcs_client)
    print(result)

