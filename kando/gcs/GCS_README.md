# Instruction Guide for Uploading a Google Cloud Bucket to CKAN

This guide walks through the process of replicating a public Google Cloud Storage bucket and its metadata into CKAN using a Python script.

---

## Step 1: Prerequisites

You must have:

- A public Google Cloud Storage bucket you want to replicate.
- Files in the bucket must be publicly accessible via: <https://storage.googleapis.com/YOUR_BUCKET_NAME/YOUR_FILE.EXT>

Your environment must have:

- python 3
- The following Python packages installed: "google-cloud-storage" & "requests"
- A Google cloud service account JSON key file for authenticated access

---

## Step 2: Make Sure Your GCS Bucket is Public

1. Make the bucket public:
   - Go to your bucket in the [Google Cloud Console](https://console.cloud.google.com/storage/browser)
   - Navigate to **Permissions > Add Principal**
   - Add:

     ```
     Principal: allUsers
     Role: Storage Object Viewer
     ```

2. Verify public access:
   - Copy a file’s path (ex. `data/sample.json`)
   - Visit: "<https://storage.googleapis.com/YOUR_BUCKET_NAME/data/sample.json>" (replace bucket name and file name)
   - If it loads in the browser its public

---

## Step 3: Update the Script Settings

In the gcs_to_ckan.py script:

1. Set the bucket name:

   ```python
   bucket_name = "YOUR_GCS_BUCKET_NAME"
   ```

2. Use your service account JSON for authentication:
   Make sure the file (ex. gcs-credentials.json) is in your working directory, and replace the default client call with:

   ```python
   gcs_client = storage.Client.from_service_account_json("YOUR_CREDENTIALS_JSON_PATH")
   ```

---

## Step 4: Run the Script

From the terminal:

```bash
python gcs_to_ckan.py
```

This will:

- Authenticate using your service account key file
- Fetch all objects from the GCS bucket
- Extract metadata (filename, size, last modified date, content type, etc.)
- Create a new CKAN dataset (named after your bucket)
- Add each GCS object as a linked resource using its public URL

---

## Step 5: Verify the Dataset in CKAN

1. Visit: <https://ckan.cyverse.rocks/>
2. Log in with your CKAN account
3. Search for the dataset with the same name as your GCS bucket
4. Click into the dataset to see your files as resources with public links
