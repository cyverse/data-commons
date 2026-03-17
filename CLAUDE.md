# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CyVerse Data Commons — tools for managing and migrating datasets between the CyVerse Discovery Environment (DE), CKAN data catalog, and cloud storage (AWS S3, Google Cloud Storage). Two main components:

- **kando/** — Python/Gradio web app for dataset migration, metadata generation (DCAT/Croissant JSON-LD), and cloud bucket replication to CKAN
- **ckan/** — Ansible playbook and configuration for deploying CKAN 2.11 on Ubuntu with HTTPS, Solr, and Keycloak OIDC authentication

## Build & Run Commands

### Kando (Gradio App)

```bash
# Build Docker image
docker build -t cyverse-gradio-app kando

# Run container (Gradio UI on port 7860)
docker run -p 7860:7860 cyverse-gradio-app

# Run locally without Docker
cd kando
pip install -r requirements.txt
python app.py

# Bulk migration script (migrates curated commons_repo datasets to CKAN)
cd kando
python bulk_migration.py <username> <password>
```

### CKAN Deployment

```bash
# Run Ansible playbook (requires vault.yml with secrets)
ansible-playbook ckan/ansible_script.yml
```

## Architecture

### Kando Module Layout

```
kando/
├── app.py              # Gradio UI entry point — defines all tabs and request handlers
├── ckan.py             # CKAN API client (create datasets, upload files, manage resources)
├── de.py               # CyVerse DE API client (auth, metadata retrieval, file listing)
├── bulk_migration.py   # CLI script for batch-migrating commons_repo directories
├── helpers/
│   ├── migration.py    # Metadata cleaning: licenses, tags, dataset name normalization
│   ├── croissant.py    # Croissant JSON-LD metadata generator
│   ├── dcat.py         # DCAT JSON-LD metadata generator
│   ├── check_metadata_availability.py  # Validates DE metadata completeness
│   └── validate_dcat_json.py           # DCAT schema validation
├── utils/
│   ├── file.py         # File utilities: metadata extraction, CSV→Parquet, JSON-LD generation
│   ├── log.py          # In-memory logging (StringIO handler) for validation output
│   └── migrate.py      # Orchestrates full DE→CKAN migration pipeline
├── aws/aws_main.py     # AWS S3 bucket → CKAN replication
└── gcs/gcs_main.py     # GCS bucket → CKAN replication
```

### Data Flow

1. User authenticates via DE credentials → `de.py` gets API token
2. Metadata fetched from DE → validated by `check_metadata_availability.py`
3. Migration: `utils/migrate.py` orchestrates download from DE, optional CSV→Parquet conversion, dataset creation in CKAN via `ckan.py`, and resource linking
4. Metadata export: `helpers/croissant.py` or `helpers/dcat.py` generates JSON-LD files

### CKAN Deployment Stack

Ansible playbook (`ckan/ansible_script.yml`) provisions: PostgreSQL → Solr 9.5 → CKAN 2.11 → Nginx (HTTPS) → Supervisor. Authentication via Keycloak OIDC (`ckanext-oidc-pkce`). Target domain: `dc.cyverse.org`.

## Environment Variables

Kando requires these in `.env` (see `kando/example.env`):

- `TERRAIN_URL` — CyVerse Terrain API URL
- `WEB_DAV_URL` — WebDAV URL for file access
- `CKAN_URL` — Target CKAN instance URL
- `CKAN_API_KEY` — CKAN API key for dataset operations

## Key Dependencies

- **gradio** — Web UI framework
- **mlcroissant** — Croissant metadata validation
- **rdflib** — RDF/DCAT metadata handling
- **boto3** — AWS S3 integration
- **google-cloud-storage** — GCS integration
- **pyarrow/pandas** — CSV→Parquet conversion
- **python-dotenv** — Environment config
