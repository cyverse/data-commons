# Kando (CyVerse Data Commons Management Tool)

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

1. **Git** installed to clone the repository.

### Option 2 Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/cyverse/data-commons
   cd data-commons
   ```

1. Build the Docker image:

   ```bash
   docker build -t cyverse-gradio-app kando
   ```

1. Run the Docker container:

   ```bash
   docker run -p 7860:7860 cyverse-gradio-app
   ```

1. Access the App:

   Open a browser and go to: `http://localhost:7860`.

---

## Application Structure and File Descriptions

### Main Components

### Docker Configuration

#### 1. Dockerfile

- **Purpose**: Defines the **Docker configuration** for the project.
- **Details**:
  - Uses **Python 3.11 slim** as the base image.
  - **Copies only the `.py` files** to the container for a smaller image size.
  - Installs dependencies from `requirements.txt` and **exposes port 7860** for the Gradio UI.

---

#### 2. `gradio_main.py`

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

### Automated AVU Metadata Sync (iRODS → CKAN)

#### `sync/` module

The `sync/` module provides automated, incremental synchronization of iRODS collections to CKAN — including both metadata and resource (file) links. The goal is to replicate the production [dc.cyverse.org](https://dc.cyverse.org) catalog from the iRODS Data Store, so that each CKAN dataset page shows the same metadata and downloadable file links as production.

#### Background: How the Existing Helpers Work

Before the `sync/` module existed, Kando already had helpers for migrating datasets one at a time via the Gradio UI. Understanding these is important because the sync module reuses the same concepts:

- **`de.py`** — Authenticates with the CyVerse Terrain API (`GET /terrain/token/keycloak`) and provides functions to list directories (`get_datasets`), list files within a directory (`get_files` via `/secured/filesystem/paged-directory`), and extract per-file metadata (`get_all_metadata_file`) including WebDAV download URLs.
- **`ckan.py`** — Wraps the CKAN API for creating datasets (`package_create`), adding resource links (`resource_create`), and uploading files.
- **`helpers/migration.py`** — Pure functions for cleaning metadata: normalizing titles into URL-safe CKAN names, mapping license strings to CKAN license IDs, extracting tags from `subject` AVUs, and building citation strings.
- **`utils/migrate.py`** — The original migration orchestrator. For each dataset it: (1) fetches metadata from DE, (2) creates the CKAN dataset, (3) lists all files and subfolders in the collection, (4) adds each as a CKAN resource link pointing to the WebDAV URL. **This is where file links come from** — without step 4, CKAN datasets appear as empty metadata-only records.

The `sync/` module was built to do the same thing as `utils/migrate.py`, but in batch, unattended, and incrementally (only syncing new or modified datasets on each run).

#### How the Sync Pipeline Works

The sync module uses the **CyVerse Terrain API** — the REST gateway to the iRODS-based Data Store. Here is the complete pipeline, step by step:

##### Step 1: Authentication

`IRODSClient` authenticates with CyVerse credentials (`DE_USERNAME` / `DE_PASSWORD`) via:

```
GET /terrain/token/keycloak
Authorization: Basic <base64(username:password)>
```

This returns a Keycloak access token used as a Bearer token for all subsequent Terrain API requests.

##### Step 2: Directory Discovery

```
GET /terrain/secured/filesystem/directory?path=<base_path>
```

Lists all subdirectories (collections) under a source path. Each source has a configured base path:

| Source | iRODS Base Path | CKAN Organization |
|--------|----------------|-------------------|
| `curated` | `/iplant/home/shared/commons_repo/curated` | `cyverse` |
| `esiil` | `/iplant/home/shared/esiil` | `esiil` |
| `ncems` | `/iplant/home/shared/NCEMS/working-groups` | `ncems` |

The response includes each folder's `label`, `path`, `date-created`, `date-modified`, and iRODS `id`. Deprecated directories (prefixed `_deprecated_`) are automatically skipped.

##### Step 3: Public Access Filtering (ESIIL/NCEMS only)

For working group folders (not curated), the sync checks whether each folder is publicly readable by making an **unauthenticated** HEAD request to the CyVerse WebDAV endpoint:

```
HEAD https://data.cyverse.org/dav/<collection_path>
Authorization: Basic anonymous:
```

A `200` or `207` response means the folder is public. Private folders are skipped — they won't appear in the catalog.

##### Step 4: AVU Metadata Retrieval

For each eligible folder, the Terrain metadata endpoint returns all AVU (Attribute-Value-Unit) pairs:

```
GET /terrain/filesystem/<folder-id>/metadata
```

Response format:
```json
{
  "avus": [
    {"attr": "title", "value": "Maize Leaf Metabolome GWAS"},
    {"attr": "datacite.creator", "value": "Shaoqun Zhou"},
    {"attr": "description", "value": "LC-MS GWAS results..."},
    {"attr": "subject", "value": "GWAS"},
    {"attr": "subject", "value": "Zea mays"},
    {"attr": "rights", "value": "ODC PDDL"},
    {"attr": "identifier", "value": "10.25739/9dsj-kw33"}
  ]
}
```

Common AVU attributes and what they map to in CKAN:

| AVU Attribute | CKAN Field | Notes |
|---------------|-----------|-------|
| `title` / `datacite.title` | `title` | Also normalized to generate `name` (URL slug) |
| `datacite.creator` / `creator` | `author` | |
| `description` | `notes` | CKAN's description field |
| `subject` | `tags` | Multi-value; split on commas, special chars cleaned |
| `rights` | `license_id` | Mapped to CKAN license: CC0, ODC-PDDL, or "not specified" |
| `identifier` | extras: Citation | Used to build citation string with DOI |
| `datacite.publicationyear` | extras: Citation | Included in citation string |
| All other AVUs | `extras` | Preserved as key-value pairs |

The mapping logic lives in `sync/mapping.py` — it was extracted from `helpers/migration.py` so the sync module has no dependency on Gradio or the interactive migration code.

##### Step 5: File and Folder Listing (Resource Links)

This is the step that makes CKAN datasets look like production. After creating/updating the dataset metadata, the sync lists the **contents** of each collection:

```
GET /terrain/secured/filesystem/paged-directory?path=<collection_path>&limit=1000
```

This returns all files and subfolders. For each item, a **CKAN resource link** is created pointing to the public WebDAV URL:

```
https://data.cyverse.org/dav-anon/iplant/home/shared/commons_repo/curated/<dataset>/<filename>
```

For example, the Maize Leaf Metabolome GWAS dataset gets these resources:

| Resource Name | Format | WebDAV URL |
|--------------|--------|------------|
| `readme.txt` | txt | `https://data.cyverse.org/dav-anon/.../readme.txt` |
| `MasterInventory.csv` | csv | `https://data.cyverse.org/dav-anon/.../MasterInventory.csv` |
| `Raw_MS_Files` | folder | `https://data.cyverse.org/dav-anon/.../Raw_MS_Files` |
| ... | ... | ... |

Resources are deduplicated by URL — if a resource link already exists in CKAN, it is not re-created.

##### Step 6: Incremental State Tracking

The `SyncState` class maintains a JSON manifest (e.g., `sync_state_curated.json`) that records each dataset's:
- `irods_modify_time` — last-known modification timestamp from iRODS
- `ckan_dataset_id` — the CKAN dataset UUID
- `last_synced` — when the sync last ran for this dataset

On subsequent runs, **only new or modified datasets are synced** — unchanged datasets are skipped entirely. To force a full re-sync (e.g., after code changes), reset the state file:

```bash
echo '{"datasets": {}}' > kando/sync_state_curated.json
```

#### Comparison: What Gets Replicated vs. Production

| Feature | Production (dc.cyverse.org) | Sync Module |
|---------|---------------------------|-------------|
| Dataset metadata (title, author, description) | From iRODS AVUs | Same — via Terrain API |
| Tags/subjects | From iRODS AVUs | Same |
| License | From `rights` AVU | Same mapping logic |
| Citation with DOI | Generated from AVUs | Same — author + year + title + DOI |
| File/folder resource links | WebDAV URLs | Same — `dav-anon` URLs |
| CKAN organization assignment | Manual | Automatic per source config |
| Custom extras (all other AVUs) | Preserved | Same |
| CKAN groups | Manual | Automatic (cyverse-curated, esiil, ncems) |

**Known limitations** (things that are not yet replicated):

- **CKAN theming/styling** — The production site at dc.cyverse.org has custom CSS and branding. The local dev CKAN uses the default theme. This is configured in the CKAN deployment (`ckan/`), not in the sync module.
- **Dataset images/thumbnails** — Production datasets may have custom images. The sync does not handle image uploads.
- **Nested folder contents** — Resource links are created for the top-level files and folders in each collection, matching production behavior. The contents *within* subfolders are not individually listed (users browse into folders via WebDAV).
- **File uploads** — Resources are linked by URL, not uploaded to CKAN storage. This is the same approach production uses — files live in the iRODS Data Store and CKAN just points to them.

#### Usage

```bash
# Sync curated datasets (default)
python -m kando.sync.sync_avu

# Sync ESIIL working group datasets
python -m kando.sync.sync_avu --source esiil

# Sync NCEMS working group datasets
python -m kando.sync.sync_avu --source ncems

# Sync all sources
python -m kando.sync.sync_avu --source all

# Preview changes without writing to CKAN
python -m kando.sync.sync_avu --source esiil --dry-run
```

#### Required Environment Variables

Add these to `kando/.env`:

```bash
# CyVerse credentials (for Terrain API authentication)
DE_USERNAME=your_cyverse_username
DE_PASSWORD=your_cyverse_password

# CKAN target instance
CKAN_URL=http://localhost:5000       # local dev
CKAN_API_KEY=your_ckan_api_key       # from CKAN admin user

# Terrain API (defaults shown — override if needed)
TERRAIN_URL=https://de.cyverse.org/terrain
WEB_DAV_URL=https://data.cyverse.org/dav-anon
```

#### Module Files

| File | Purpose |
|------|---------|
| `sync/sync_avu.py` | Main orchestrator — CLI entry point, source configuration, sync loop, resource linking |
| `sync/irods_client.py` | Terrain API client — auth, directory listing, file listing, AVU retrieval, public access checks |
| `sync/mapping.py` | Pure functions to transform AVU metadata dicts into CKAN dataset dicts (extracted from `helpers/migration.py`) |
| `sync/state.py` | JSON state manifest for incremental sync tracking |

#### Relationship to Existing Helper Files

The `sync/` module was designed to complement, not replace, the existing Kando helpers:

```
Existing helpers (interactive, Gradio UI):
  de.py → utils/migrate.py → ckan.py
  └── One dataset at a time, user-driven

Sync module (automated, CLI):
  sync/irods_client.py → sync/mapping.py → sync/sync_avu.py
  └── All datasets in batch, incremental, unattended
```

Both paths use the same Terrain API endpoints and produce the same CKAN result. The sync module's `irods_client.py` is functionally equivalent to `de.py` but with a cleaner interface (no global state, explicit auth). The sync module's `mapping.py` was extracted from `helpers/migration.py` to remove the Gradio dependency. The resource-linking logic in `sync_resources()` mirrors what `utils/migrate.py` does in its file loop (lines 88-126).

---

### Cloud Buckets Integration

#### 11. `aws/aws_main.py`

- **Purpose**: Handles **AWS S3 bucket replication** to CKAN.
- **Features**:
  - Dynamically accepts AWS credentials (Access Key ID and Secret Access Key) entered via the Gradio UI.
  - Verifies bucket existence using `head_bucket`.
  - Extracts bucket-level and object-level metadata.
  - Creates or updates a corresponding dataset in CKAN and links all S3 objects as CKAN resources.
- **Related Documentation**: See [`aws/AWS_README.md`](aws/AWS_README.md) for detailed usage instructions.

#### 12. `gcs/gcs_main.py`

- **Purpose**: Handles **Google Cloud Storage bucket replication** to CKAN.
- **Features**:
  - Allows users to upload their Google Cloud Credentials file via the Gradio UI.
  - Verifies bucket existence using `get_bucket`.
  - Extracts object metadata from the bucket.
  - Creates or updates a corresponding dataset in CKAN and links all GCS objects as CKAN resources.
- **Related Documentation**: See [`gcs/GCS_README.md`](gcs/GCS_README.md) for detailed usage instructions.
