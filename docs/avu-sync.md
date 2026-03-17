# AVU Metadata Sync: iRODS to CKAN

Automated synchronization of iRODS AVU (Attribute-Value-Unit) metadata from CyVerse curated datasets to the CKAN data catalog at [dc.cyverse.org](https://dc.cyverse.org).

## How It Works

The sync reads metadata from every curated dataset directory under `/iplant/home/shared/commons_repo/curated` via the CyVerse Terrain API, maps it to CKAN dataset fields, and creates or updates the corresponding CKAN record. A local state file tracks what has already been synced so only new or modified datasets are processed on each run.

### Sync Flow

```
iRODS curated collection
        |
        v
  Terrain API  ──>  list subdirectories
        |
        v
  State check  ──>  new? modified? unchanged?
        |                              |
        v                              v
  Fetch AVU metadata               skip
        |
        v
  Validate (title required)
        |
        v
  Map AVUs to CKAN fields
        |
        v
  Create or update CKAN dataset
        |
        v
  Record result in sync_state.json
```

## Source Path

All curated datasets live under:

```
/iplant/home/shared/commons_repo/curated
```

Directories prefixed with `_deprecated_` are automatically skipped.

## Metadata Field Mapping

| iRODS AVU Attribute | CKAN Field | Notes |
|---------------------|-----------|-------|
| `title` / `Title` / `datacite.title` | `title` | **Required** — datasets without a title are skipped |
| `datacite.creator` / `creator` | `author` | Multiple values joined |
| `description` / `Description` | `notes` | Maps to CKAN description |
| `subject` | `tags` | Comma-split, special characters removed |
| `rights` / `Rights` | `license_id` | e.g. `ODC PDDL` -> `odc-pddl`, `CC0` -> `cc-zero` |
| `datacite.publicationyear` | (extras) | Used in auto-generated citation |
| `Identifier` / `datacite.identifier` | (extras) | DOI, also used for name collision resolution |
| `version` / `Version` | `version` | Dataset version |
| All other AVUs | `extras` | Stored as key-value pairs |

Every synced dataset is assigned to the `cyverse` organization and the `cyverse-curated` group in CKAN.

### Auto-Generated Citation

A citation extra is built from the mapped fields:

```
{author} {year}. {title}. CyVerse Data Commons. DOI {identifier}
```

### Dataset Name Normalization

CKAN dataset names (URL slugs) are derived from the title: lowercased, spaces replaced with underscores, special characters stripped, truncated to 100 characters. If a name collision occurs, the DOI is appended as a suffix.

## Change Detection

The sync maintains a JSON state file (`sync_state.json`) that records each dataset's last-known iRODS modification time and CKAN dataset ID. On each run:

- **New** — directory not in state file -> create in CKAN
- **Modified** — iRODS `date-modified` differs from stored value -> update in CKAN
- **Unchanged** — skip

State file structure:

```json
{
  "last_full_sync": "2026-03-14T23:31:24.474368+00:00",
  "datasets": {
    "Alcock_leafPhenotypingImages_2016": {
      "irods_modify_time": "2020-02-20 15:05:33",
      "ckan_dataset_id": "0ffbe24b-fcaf-407b-b625-51086d4a99ca",
      "last_synced": "2026-03-14T23:28:09.075469+00:00"
    }
  }
}
```

## Scheduling

### Production (Ansible-deployed cron)

The Ansible playbook deploys the sync to `/opt/ckan-sync/` on the CKAN server and installs an hourly cron job:

```bash
flock -n /tmp/ckan-sync.lock \
  /opt/ckan-sync/venv/bin/python -m kando.sync.sync_avu \
  --state-file /opt/ckan-sync/sync_state.json \
  >> /var/log/ckan/sync.log 2>&1
```

- Runs every hour at minute 0
- `flock` prevents overlapping runs
- Logs to `/var/log/ckan/sync.log`
- Only enabled when `ckan_sync_api_key` is set in the Ansible vault

### GitHub Actions (backup)

A weekly workflow (`.github/workflows/sync-avu-metadata.yml`) runs every Monday at 06:00 UTC as a secondary sync. It can also be triggered manually via `workflow_dispatch`. The workflow commits any updated `sync_state.json` back to the repository.

## Running Manually

```bash
cd kando

# Full sync
python -m kando.sync.sync_avu

# Dry run (logs actions without writing to CKAN)
python -m kando.sync.sync_avu --dry-run

# Custom state file location
python -m kando.sync.sync_avu --state-file /path/to/sync_state.json
```

## Environment Variables

Set in `.env` or the deployment environment:

| Variable | Description |
|----------|-------------|
| `CKAN_URL` | CKAN instance URL (e.g. `https://dc.cyverse.org`) |
| `CKAN_API_KEY` | CKAN API key with dataset write permissions |
| `DE_USERNAME` | CyVerse / Terrain username |
| `DE_PASSWORD` | CyVerse / Terrain password |
| `TERRAIN_URL` | Terrain API base URL |

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Missing title AVU | Dataset skipped with warning |
| CKAN API error | Logged, error counter incremented, sync continues |
| Terrain auth failure | Raises error, sync stops |
| Corrupt state file | Starts fresh with empty state |
| Dataset name collision | Retries with DOI suffix appended to name |
| Concurrent cron runs | `flock` silently skips the overlapping run |

## Code Layout

```
kando/sync/
├── sync_avu.py       # Main orchestrator and CKAN API calls
├── irods_client.py   # Terrain API client (auth, directory listing, metadata fetch)
├── mapping.py        # Pure functions: AVU dict -> CKAN dataset dict
├── state.py          # Incremental sync state tracking (JSON persistence)
└── test_mapping.py   # Unit tests for mapping functions
```
