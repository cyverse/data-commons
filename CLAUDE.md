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
├── sync/
│   ├── sync_avu.py     # AVU sync orchestrator — CLI entry point, source config, sync loop
│   ├── irods_client.py # Terrain API client — auth, directory listing, AVU metadata retrieval
│   ├── mapping.py      # Pure functions: AVU metadata → CKAN dataset dict transformation
│   └── state.py        # JSON state manifest for incremental sync tracking
├── aws/aws_main.py     # AWS S3 bucket → CKAN replication
└── gcs/gcs_main.py     # GCS bucket → CKAN replication
```

### Data Flow

#### Gradio UI Migration (interactive)

1. User authenticates via DE credentials → `de.py` gets API token
2. Metadata fetched from DE → validated by `check_metadata_availability.py`
3. Migration: `utils/migrate.py` orchestrates download from DE, optional CSV→Parquet conversion, dataset creation in CKAN via `ckan.py`, and resource linking
4. Metadata export: `helpers/croissant.py` or `helpers/dcat.py` generates JSON-LD files

#### AVU Metadata Sync (automated CLI)

The `sync/` module provides automated, incremental synchronization of iRODS collections to CKAN via the Terrain API — including both AVU metadata and resource (file) links. This replicates what `utils/migrate.py` does interactively, but in batch for all datasets:

1. Authenticate → `irods_client.py` calls `GET /terrain/token/keycloak` with DE credentials to get a Bearer token
2. List collections → `GET /terrain/secured/filesystem/directory?path=<base_path>` returns subdirectories with folder IDs and timestamps
3. Filter (ESIIL/NCEMS only) → anonymous WebDAV HEAD request checks if each folder is publicly readable
4. Fetch AVUs → `GET /terrain/filesystem/<folder-id>/metadata` returns `{"avus": [{"attr": "title", "value": "..."}, ...]}` per collection
5. Map → `mapping.py` transforms AVU key-value pairs to CKAN dataset fields (title, author, license, tags, extras, citation)
6. Create/update dataset → `package_create` or `package_update` in CKAN, assigned to the correct organization (`cyverse`, `esiil`, or `ncems`)
7. Sync resource links → `GET /terrain/secured/filesystem/paged-directory?path=<collection>` lists files/folders, then `resource_create` adds WebDAV download URLs (e.g., `https://data.cyverse.org/dav-anon/...`) to CKAN, deduplicated by URL
8. Track state → JSON manifests record each dataset's `modify_time` and CKAN ID for incremental runs

```bash
python -m kando.sync.sync_avu --source all        # sync curated + esiil + ncems
python -m kando.sync.sync_avu --source esiil       # sync esiil only
python -m kando.sync.sync_avu --dry-run            # preview without CKAN writes
echo '{"datasets": {}}' > kando/sync_state_curated.json  # force full re-sync
```

### CKAN Deployment Stack

Ansible playbook (`ckan/ansible_script.yml`) provisions: PostgreSQL → Solr 9.5 → CKAN 2.11 → Nginx (HTTPS) → Supervisor. Authentication via Keycloak OIDC (`ckanext-oidc-pkce`). Target domain: `dc.cyverse.org`.

## Environment Variables

Kando requires these in `.env` (see `kando/example.env`):

- `TERRAIN_URL` — CyVerse Terrain API URL (default: `https://de.cyverse.org/terrain`)
- `WEB_DAV_URL` — WebDAV URL for file access
- `CKAN_URL` — Target CKAN instance URL
- `CKAN_API_KEY` — CKAN API key for dataset operations
- `DE_USERNAME` — CyVerse username (required for AVU sync)
- `DE_PASSWORD` — CyVerse password (required for AVU sync)

## Key Dependencies

- **gradio** — Web UI framework
- **mlcroissant** — Croissant metadata validation
- **rdflib** — RDF/DCAT metadata handling
- **boto3** — AWS S3 integration
- **google-cloud-storage** — GCS integration
- **pyarrow/pandas** — CSV→Parquet conversion
- **python-dotenv** — Environment config
