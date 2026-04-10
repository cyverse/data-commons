"""
Main orchestrator for syncing iRODS AVU metadata to CKAN.

Usage:
    python -m kando.sync.sync_avu                        # curated (default)
    python -m kando.sync.sync_avu --source esiil         # esiil public folders
    python -m kando.sync.sync_avu --source ncems         # ncems public folders
    python -m kando.sync.sync_avu --source all           # all sources
    python -m kando.sync.sync_avu --dry-run              # preview without CKAN writes
"""

import os
import sys
import json
import logging
import argparse

import requests
from dotenv import load_dotenv

from kando.sync.irods_client import IRODSClient
from kando.sync.mapping import map_avus_to_ckan, get_title
from kando.sync.resources import get_resources_to_add
from kando.sync.state import SyncState

load_dotenv()

logger = logging.getLogger(__name__)

CKAN_URL = os.getenv("CKAN_URL")
CKAN_API_KEY = os.getenv("CKAN_API_KEY")
WEB_DAV_URL = os.getenv("WEB_DAV_URL")

# Source definitions: base_path, owner_org, ckan groups, state file, filter_public
SOURCES = {
    "curated": {
        "base_path": "/iplant/home/shared/commons_repo/curated",
        "owner_org": "cyverse",
        "groups": None,  # uses default cyverse-curated group
        "state_file": "sync_state_curated.json",
        "filter_public": False,
    },
    "esiil": {
        "base_path": "/iplant/home/shared/esiil",
        "owner_org": "esiil",
        "groups": [{"name": "esiil"}],
        "state_file": "sync_state_esiil.json",
        "filter_public": True,
    },
    "ncems": {
        "base_path": "/iplant/home/shared/NCEMS/working-groups",
        "owner_org": "ncems",
        "groups": [{"name": "ncems"}],
        "state_file": "sync_state_ncems.json",
        "filter_public": True,
    },
}

# Directory containing the sync package — used as default state file location
_SYNC_DIR = os.path.dirname(__file__)


class CKANSyncClient:
    """Thin CKAN API wrapper for sync operations."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        })

    def get_dataset_by_name(self, name: str) -> dict | None:
        url = f"{self.base_url}/api/3/action/package_show"
        resp = self.session.get(url, params={"id": name}, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("success"):
                return result["result"]
        return None

    def create_dataset(self, data: dict) -> dict:
        url = f"{self.base_url}/api/3/action/package_create"
        timeout = 300 if data.get("resources") else 15
        resp = self.session.post(url, data=json.dumps(data), timeout=timeout)
        if not resp.text:
            return {"success": False, "error": f"Empty response (HTTP {resp.status_code})"}
        return resp.json()

    def update_dataset(self, dataset_id: str, data: dict) -> dict:
        data["id"] = dataset_id
        url = f"{self.base_url}/api/3/action/package_update"
        timeout = 300 if data.get("resources") else 15
        resp = self.session.post(url, data=json.dumps(data), timeout=timeout)
        if not resp.text:
            return {"success": False, "error": f"Empty response (HTTP {resp.status_code})"}
        return resp.json()


def build_resources_for_dataset(
    irods: IRODSClient,
    dataset_id: str,
    de_path: str,
    existing_resources: list | None = None,
) -> list | None:
    """
    Build the full resources list for a dataset (existing + new).

    Returns the combined list to embed in package_create/package_update,
    or None if WEB_DAV_URL is not set or listing fails.
    """
    if not WEB_DAV_URL:
        logger.warning("WEB_DAV_URL not set — skipping resource sync")
        return None

    existing = existing_resources or []
    existing_names = {r["name"] for r in existing}

    try:
        listing = irods.list_files(de_path)
    except Exception as e:
        logger.error("Failed to list files at %s: %s", de_path, e)
        return None

    to_add = get_resources_to_add(listing, existing_names, dataset_id, WEB_DAV_URL)
    if to_add:
        for r in to_add:
            logger.info("  + resource: %s", r["name"])

    return existing + to_add


def sync_source(
    irods: IRODSClient,
    ckan: CKANSyncClient,
    base_path: str,
    owner_org: str,
    groups: list,
    state_path: str,
    filter_public: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Sync one iRODS source path to CKAN.

    Args:
        irods: authenticated IRODSClient
        ckan: CKANSyncClient
        base_path: iRODS collection to scan
        owner_org: CKAN organization slug
        groups: CKAN group list (or None for default)
        state_path: path to the per-source state JSON file
        filter_public: if True, skip folders that are not publicly readable
        dry_run: preview without writing to CKAN

    Returns:
        Stats dict with keys: created, updated, skipped, errors
    """
    state = SyncState.load(state_path)

    logger.info("Listing directories under %s ...", base_path)
    dirs = irods.list_project_directories(base_path)
    logger.info("Found %d directories", len(dirs))

    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for entry in dirs:
        dirname = entry["name"]
        path = entry["path"]

        # Skip deprecated datasets
        if dirname.startswith("_deprecated_"):
            logger.debug("Skipping deprecated: %s", dirname)
            stats["skipped"] += 1
            continue

        # For project folders, skip private collections
        if filter_public:
            if not irods.is_publicly_readable(path):
                logger.info("Skipping private folder: %s", dirname)
                stats["skipped"] += 1
                continue

        # Determine action
        modify_time = entry.get("modify_time", "")
        if state.is_new(dirname):
            action = "create"
        elif state.is_modified(dirname, modify_time):
            action = "update"
        else:
            stats["skipped"] += 1
            continue

        try:
            avus = irods.get_collection_metadata(path, folder_info=entry)

            try:
                get_title(avus)
            except KeyError:
                logger.info("No title in metadata for %s, using directory name", dirname)
                avus["title"] = dirname

            mapped = map_avus_to_ckan(avus, owner_org=owner_org, groups=groups)

            if dry_run:
                logger.info("[DRY-RUN] Would %s: %s (name=%s)", action, dirname, mapped["name"])
                stats["created" if action == "create" else "updated"] += 1
                continue

            ckan_id = None
            if action == "create":
                existing = ckan.get_dataset_by_name(mapped["name"])
                if existing:
                    logger.info("Dataset %s already exists in CKAN, updating", mapped["name"])
                    # Build resources: keep existing + add new
                    resources = build_resources_for_dataset(
                        irods, existing["id"], path,
                        existing_resources=existing.get("resources", []),
                    )
                    if resources is not None:
                        mapped["resources"] = resources
                    result = ckan.update_dataset(existing["id"], mapped)
                    ckan_id = existing["id"]
                else:
                    # Build resources for new dataset (no existing ones)
                    resources = build_resources_for_dataset(
                        irods, "new", path,
                    )
                    if resources is not None:
                        mapped["resources"] = resources
                    result = ckan.create_dataset(mapped)
                    if result.get("success"):
                        ckan_id = result["result"]["id"]
                        logger.info("Created: %s -> %s", dirname, ckan_id)
                    elif "already in use" in str(result.get("error", "")):
                        doi = avus.get("identifier", "")
                        if isinstance(doi, list):
                            doi = doi[0]
                        suffix = doi.replace("/", "-").replace(".", "-") if doi else dirname[:20]
                        mapped["name"] = mapped["name"][:80] + "_" + suffix[:19]
                        result = ckan.create_dataset(mapped)
                        if result.get("success"):
                            ckan_id = result["result"]["id"]
                            logger.info("Created (with suffix): %s -> %s", dirname, ckan_id)
                        else:
                            logger.error("Failed to create %s: %s", dirname, result.get("error"))
                            stats["errors"] += 1
                            continue
                    else:
                        logger.error("Failed to create %s: %s", dirname, result.get("error"))
                        stats["errors"] += 1
                        continue
                stats["created"] += 1
            else:
                ckan_id = state.get_ckan_id(dirname)
                if ckan_id:
                    # Build resources: keep existing + add new
                    existing_dataset = ckan.get_dataset_by_name(mapped["name"])
                    existing_res = existing_dataset.get("resources", []) if existing_dataset else []
                    resources = build_resources_for_dataset(
                        irods, ckan_id, path,
                        existing_resources=existing_res,
                    )
                    if resources is not None:
                        mapped["resources"] = resources
                    result = ckan.update_dataset(ckan_id, mapped)
                    if not result.get("success"):
                        logger.error("Failed to update %s: %s", dirname, result.get("error"))
                        stats["errors"] += 1
                        continue
                    logger.info("Updated: %s", dirname)
                else:
                    existing = ckan.get_dataset_by_name(mapped["name"])
                    if existing:
                        ckan_id = existing["id"]
                        existing_res = existing.get("resources", [])
                        resources = build_resources_for_dataset(
                            irods, ckan_id, path,
                            existing_resources=existing_res,
                        )
                        if resources is not None:
                            mapped["resources"] = resources
                        result = ckan.update_dataset(ckan_id, mapped)
                    else:
                        resources = build_resources_for_dataset(
                            irods, "new", path,
                        )
                        if resources is not None:
                            mapped["resources"] = resources
                        result = ckan.create_dataset(mapped)
                        if result.get("success"):
                            ckan_id = result["result"]["id"]
                stats["updated"] += 1

            if mapped.get("resources"):
                logger.info("Resources included: %d total", len(mapped["resources"]))

            # Update state
            irods_info = {"modify_time": modify_time}
            if ckan_id:
                state.mark_synced(dirname, irods_info, ckan_id)

        except Exception as e:
            logger.error("Error processing %s: %s", dirname, e, exc_info=True)
            stats["errors"] += 1

    if not dry_run:
        state.save()

    logger.info(
        "[%s] Sync complete: created=%d, updated=%d, skipped=%d, errors=%d",
        base_path, stats["created"], stats["updated"], stats["skipped"], stats["errors"],
    )
    return stats


def sync(source: str = "curated", dry_run: bool = False, state_path: str = None):
    """Run sync for the given source name (or 'all')."""
    if not CKAN_URL or not CKAN_API_KEY:
        logger.error("CKAN_URL and CKAN_API_KEY must be set")
        sys.exit(1)

    irods = IRODSClient()
    ckan = CKANSyncClient(CKAN_URL, CKAN_API_KEY)

    sources_to_run = list(SOURCES.keys()) if source == "all" else [source]

    totals = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for src_name in sources_to_run:
        cfg = SOURCES[src_name]
        # Allow CLI --state-file override only when running a single source
        effective_state = state_path if (state_path and len(sources_to_run) == 1) else None
        if effective_state is None:
            effective_state = os.path.join(_SYNC_DIR, "..", cfg["state_file"])

        stats = sync_source(
            irods=irods,
            ckan=ckan,
            base_path=cfg["base_path"],
            owner_org=cfg["owner_org"],
            groups=cfg["groups"],
            state_path=effective_state,
            filter_public=cfg["filter_public"],
            dry_run=dry_run,
        )
        for k in totals:
            totals[k] += stats[k]

    if len(sources_to_run) > 1:
        logger.info(
            "All sources complete: created=%d, updated=%d, skipped=%d, errors=%d",
            totals["created"], totals["updated"], totals["skipped"], totals["errors"],
        )
    return totals


def main():
    parser = argparse.ArgumentParser(description="Sync iRODS AVU metadata to CKAN")
    parser.add_argument(
        "--source",
        choices=["curated", "esiil", "ncems", "all"],
        default="curated",
        help="Which source to sync (default: curated)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to CKAN")
    parser.add_argument("--state-file", default=None, help="Path to sync state JSON file (single source only)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    )

    sync(source=args.source, dry_run=args.dry_run, state_path=args.state_file)


if __name__ == "__main__":
    main()
