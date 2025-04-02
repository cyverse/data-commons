## **Instruction Guide for Uploading an S3 Bucket to CKAN**

This guide walks through the  process of replicating your own public S3 bucket and its metadata into CKAN using the Python script.

---

### **Step 1: Prerequisites**

You must have the following:
- An AWS account with access to the bucket you want to migrate
- The bucket must be owned by your IAM user.
- The bucket must be public so that links in CKAN work.

Your environment must have:
- Python 3
- boto3 installed
- requests installed
- AWS CLI configured: `aws configure` (using your IAM credentials)

---

### **Step 2: Set Up Your S3 Bucket**

Make sure your your bucket is public and owned by your user.

1. Set a public bucket policy:
Go to the S3 console > your bucket > Permissions > Bucket Policy and paste this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

2. Disable “Block Public Access”:
Go to the "Permissions" tab in your bucket.
Click "Edit" on “Block public access (bucket settings)”.
Uncheck all boxes and confirm the change.

3. You can verify that the bucket is accessible:
Visit a file directly in the browser:
```
https://YOUR_BUCKET_NAME.s3.amazonaws.com/EXAMPLE.txt
```

---

### **Step 3: Update Your Script Settings**

In `main.py`, update the following line with your bucket name:
```python
bucket_name = "your-bucket-name"
```

---

### **Step 4: Run the Script**

Run the script in your terminal:
```bash
python aws_main.py
```

What this program does :
- Extract bucket metadata (creation date, region, tags)
- List all files and collect object-level metadata (size, content type, etc)
- Generate public URLs to each file
- Create a new dataset in CKAN using your bucket metadata
- Add each object as a resource (using its public S3 URL)
- Save the metadata to a local JSON file (`s3_metadata.json`)

---

### **Step 5: Verify in CKAN**

1. Go to the CKAN  (https://ckan.cyverse.rocks/)
2. Log in with your account
3. Find the dataset created (named after your bucket)

