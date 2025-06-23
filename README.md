# CyVerse Data Commons Management Tool

## Overview

This project provides a **user-friendly interface using Gradio** to manage datasets in the **CyVerse Discovery Environment (DE)** and other cloud storage services.

The tool facilitates:

1. **Migration of datasets** from CyVerse to **CKAN** (a data management system).
1. **Conversion of metadata** into **DCAT and Croissant JSON-LD formats**.
1. **CSV to Parquet conversion** for efficient storage.
1. **Uploading metadata files** directly to CKAN.
1. **Replication of cloud buckets** (AWS S3 and Google Cloud Storage) to CKAN.

Using this application, users can seamlessly move datasets between platforms, validate metadata, and ensure compliance with DCAT and Croissant standards.

---

## Features

- **Migrate datasets** from CyVerse DE to CKAN with metadata.
- **Generate DCAT or Croissant metadata files** for datasets.
- **Upload and manage datasets** with ease using CKAN's API.
- **Support for CSV-to-Parquet conversion** for efficient data handling.
- **Replicate AWS S3 buckets** (with credential input) to CKAN.
- **Replicate GCS buckets** (by uploading a `gcs-credentials.json` file) to CKAN.

---

## How to Build and Use the Docker Image

### Setup Options

You have **two ways to launch the app**:

1. **Option 1**: Using the **Docker image** available at `tdewangan63/my-gradio-app`.
1. **Option 2**: **Clone the repository** and build the Docker image locally.

## Option 1: Run the App Using the Pre-built Docker Image

### Option 1 Steps

1. **Pull the Docker image** from Docker Hub:

   ```bash
   docker pull tdewangan63/my-gradio-app
   ```

1. **Run the Docker container**:

   ```bash
   docker run -p 7860:7860 tdewangan63/my-gradio-app
   ```

1. **Access the App**:

   Open a browser and go to: `http://localhost:7860`.

## Option 2: Clone the Repository and Build the Image Locally

### Prerequisites

1. **Docker** installed on your system. [Install Docker](https://docs.docker.com/get-docker/) if you don't have it.

2. **Git** installed to clone the repository.

### Option 2 Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/cyverse/data-commons
   cd data-commons
   ```

2. Build the Docker image:

   ```bash
   docker build -t cyverse-gradio-app .
   ```

3. Run the Docker container:

   ```bash
   docker run -p 7860:7860 cyverse-gradio-app
   ```

4. Access the App:

   Open a browser and go to: `http://localhost:7860`.

---

## Application Structure and File Descriptions

### Main Components

#### 1. `gradio_main.py`

- **Purpose**: Defines the **Gradio-based user interface** and its various tabs.
- **Features**:
  - Provides tabs for dataset migration, metadata generation (Croissant and DCAT), file uploads, and Cloud bucket replication (AWS S3 and Google Cloud).
  - Calls helper functions from other modules to handle migration and metadata operations.

---

### Helper Modules

#### 2. `ckan.py`

- **Purpose**: Handles **interactions with the CKAN API**.
- **Functions**:
  - Create datasets, upload files, and update metadata in CKAN.
  - Manage datasets and resources (e.g., adding or deleting datasets).

#### 3. `de.py`

- **Purpose**: Manages communication with the **CyVerse Discovery Environment (DE)**.
- **Functions**:
  - Retrieve metadata and datasets from DE.
  - Authenticate users and fetch files or directories using the DE API.

#### 4. `migrate.py`

- **Purpose**: Orchestrates the **migration process** from DE to CKAN.
- **Functions**:
  - Prepares datasets by cleaning and validating metadata.
  - Ensures that datasets and files are correctly transferred.

---

### Metadata Generation

#### 5. `croissant.py`

- **Purpose**: Generates **Croissant JSON-LD metadata** for datasets.
- **Functions**:
  - Converts metadata to **Croissant format** with fields like title, description, and author.
  - Adds files or resources as **distributions** in the metadata.

#### 6. `dcat.py`

- **Purpose**: Creates **DCAT-compliant JSON-LD files** for datasets.
- **Functions**:
  - Converts metadata into the **DCAT format** for interoperability.
  - Adds distributions (e.g., CSV, Parquet files) with unique hashes.

#### 7. `file_utils.py`

- **Purpose**: Provides **utility functions for file and metadata handling**.
- **Functions**:
  - Extract metadata from JSON files.
  - Generate Croissant and DCAT metadata.
  - Convert **CSV files to Parquet** for optimized storage.

---

### Logging and Validation

#### 8. `log_utils.py`

- **Purpose**: Captures and stores **logs** from the application.
- **Functions**:
  - Uses a **StringIO logging handler** to keep logs in memory.
  - Parses logs to separate **errors and warnings** during validation.

#### 9. `validate_dcat_json.py`

- **Purpose**: **Validates DCAT JSON** against a schema.
- **Functions**:
  - Ensures that the **DCAT metadata** complies with the required structure before uploading to CKAN.

---

### Supporting Scripts

#### 10. `migration.py`

- **Purpose**: Provides **helper functions** to clean and structure metadata for migration.
- **Functions**:
  - Handles licenses, tags, and dataset descriptions.
  - Checks if datasets or files need to be **re-uploaded or updated** in CKAN.

---

### Cloud Buckets Integration

#### 10. `aws/aws_main.py`

- **Purpose**: Handles **AWS S3 bucket replication** to CKAN.
- **Features**:
  - Dynamically accepts AWS credentials (Access Key ID and Secret Access Key) entered via the Gradio UI.
  - Verifies bucket existence using `head_bucket`.
  - Extracts bucket-level and object-level metadata.
  - Creates or updates a corresponding dataset in CKAN and links all S3 objects as CKAN resources.
- **Related Documentation**: See [`aws/AWS_README.md`](aws/AWS_README.md) for detailed usage instructions.

#### 11. `gcs/gcs_main.py`

- **Purpose**: Handles **Google Cloud Storage bucket replication** to CKAN.
- **Features**:
  - Allows users to upload their Google Cloud Credentials file via the Gradio UI.
  - Verifies bucket existence using `get_bucket`.
  - Extracts object metadata from the bucket.
  - Creates or updates a corresponding dataset in CKAN and links all GCS objects as CKAN resources.
- **Related Documentation**: See [`gcs/GCS_README.md`](gcs/GCS_README.md) for detailed usage instructions.

---

### Docker Configuration

#### 12. Dockerfile

- **Purpose**: Defines the **Docker configuration** for the project.
- **Details**:
  - Uses **Python 3.11 slim** as the base image.
  - **Copies only the `.py` files** to the container for a smaller image size.
  - Installs dependencies from `requirements.txt` and **exposes port 7860** for the Gradio UI.

---

### Deployment

#### 13. `deployment/ansible_script.yml`

- **Purpose**: Provides an **Ansible playbook** to deploy a new instance of CKAN.
- **Features**:
  - Automates installation and configuration of CKAN and its dependencies.
  - Can be used to deploy a CKAN instance on a cloud VM or on-premise server.
  - Highly customizable to match different deployment environments.

#### 14. `deployment/ansible_ckan_deployment.md`

- **Purpose**: Provides **documentation** and step-by-step instructions for using the provided Ansible script.
- **Details**:
  - Describes prerequisites (Ansible installation, target machine setup).
  - Explains how to run the playbook and verify the deployed CKAN instance.

---
