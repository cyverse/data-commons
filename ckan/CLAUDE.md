# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CKAN 2.11 deployment for CyVerse Data Commons (`dc.cyverse.org`). Two deployment modes:

- **Production**: Ansible playbook deploys CKAN on bare-metal Ubuntu with PostgreSQL, Solr 9.5, Nginx (HTTPS), Supervisor, and Keycloak OIDC authentication
- **Local dev**: Docker Compose stack with CKAN dev server, PostgreSQL, Solr, and Redis

## Commands

### Local Development (Docker Compose)

```bash
# Start the full stack (CKAN on port 5000)
docker compose up -d

# Rebuild after Dockerfile.dev changes
docker compose up -d --build

# View logs
docker compose logs -f ckan

# Create admin user inside running container
docker compose exec ckan ckan -c $CKAN_INI sysadmin add admin email=admin@example.com password=admin123

# Generate API token for a user
docker compose exec ckan ckan -c $CKAN_INI user token add admin api_token

# Restart
docker compose restart

# Tear down (volumes persist)
docker compose down

# Tear down and destroy all data
docker compose down -v
```

### Production Deployment (Ansible)

```bash
# Requires: inventory.ini and group_vars/vault.yml (both gitignored)
ansible-playbook ansible_script.yml --ask-vault-pass

# Check CKAN status on production server
sudo supervisorctl status ckan
sudo systemctl status solr
sudo systemctl status nginx
sudo tail -f /var/log/ckan/ckan.log
```

### AVU Metadata Sync (from kando/sync/)

```bash
# Dry run against local CKAN
cd ../kando && python -m kando.sync.sync_avu --dry-run

# Full sync against local CKAN
cd ../kando && python -m kando.sync.sync_avu

# Custom state file
python -m kando.sync.sync_avu --state-file /path/to/sync_state.json
```

## Architecture

### Docker Compose Stack (Local Dev)

`Dockerfile.dev` builds from `ckan/ckan-dev:2.11` and patches `ckan.ini` at build time via `ckan config-tool`. This is necessary because the CKAN `envvars` plugin and environment variables like `CKAN_SQLALCHEMY_URL` are only applied at runtime — but `prerun.py` and `ckan db init` read the ini file directly during container startup, before envvars are processed. The `docker-entrypoint.d/00-patch-config.sh` script provides additional runtime patching but is secondary to the build-time config.

Services: `ckan` (port 5000) → `db` (PostgreSQL 15) + `solr` (Solr 9 with CKAN schema) + `redis` (Redis 7). A `solr-init` container runs first as root to fix volume permissions (`chown 8983:8983`) since Solr refuses to run as root.

The `ckan_style.css` file is bind-mounted as `/srv/app/src/ckan/ckan/public/base/css/custom.css` for CyVerse branding (blue color scheme).

### Ansible Playbook (Production)

`ansible_script.yml` is a single-play playbook targeting `ckan_servers` hosts. Provisions the full stack in order: system packages → PostgreSQL (user + DB) → Solr (download, systemd service, CKAN schema) → CKAN (.deb package, ini config, db init, admin user) → Supervisor → Nginx (HTTPS with existing SSL certs) → AVU sync cron job.

Key configuration:
- CKAN venv: `/usr/lib/ckan/default`
- Config: `/etc/ckan/default/ckan.ini`
- Storage: `/var/lib/ckan/default/storage`
- Solr: `/opt/solr` (install), `/var/solr` (data)
- Logs: `/var/log/ckan/`
- AVU sync: `/opt/ckan-sync/` (hourly cron via `flock`)

Authentication: Keycloak OIDC via `ckanext-oidc-pkce` plugin against `kc.cyverse.org/auth` realm `CyVerse`.

### Vault Variables (group_vars/vault.yml)

Required: `ckan_db_user`, `ckan_db_password`, `ckan_db_name`, `oidc_client_id`, `oidc_client_secret`. Optional: `ckan_admin_user`, `ckan_admin_email`, `ckan_admin_password`, `ckan_sync_api_key`, `de_sync_username`, `de_sync_password`.

## Known Gotchas

- **CKAN envvars plugin limitation**: Environment variables like `CKAN_SQLALCHEMY_URL` are NOT available during `prerun.py`/`ckan db init`. Config must be patched in the Dockerfile or via `ckan config-tool` before the entrypoint runs.
- **Solr volume permissions**: The `solr-init` service is required because the Docker Solr image runs as UID 8983 but Docker volumes are created as root.
- **Datastore plugin**: Not enabled in local dev. Enabling it requires a separate PostgreSQL database and connection string; without it, CKAN falls back to localhost and fails.
- **CSRF in dev**: `WTF_CSRF_ENABLED = false` is set in `Dockerfile.dev` to allow API calls and browser access without CSRF tokens. Do not use in production.
- **Templates directory**: `templates/ckan.ini.j2` is a legacy/minimal template. The authoritative CKAN config is generated inline in `ansible_script.yml`.
