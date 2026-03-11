"""
Main orchestrator for syncing iRODS AVU metadata to CKAN.

Usage:
    python -m kando.sync.sync_avu              # normal run
    python -m kando.sync.sync_avu --dry-run    # preview without CKAN writes
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
from kando.sync.state import SyncState

load_dotenv()

logger = logging.getLogger(__name__)

CKAN_URL = os.getenv("CKAN_URL")
CKAN_API_KEY = os.getenv("CKAN_API_KEY")


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
        resp = self.session.post(url, data=json.dumps(data), timeout=15)
        return resp.json()

    def update_dataset(self, dataset_id: str, data: dict) -> dict:
        data["id"] = dataset_id
        url = f"{self.base_url}/api/3/action/package_update"
        resp = self.session.post(url, data=json.dumps(data), timeout=15)
        return resp.json()


def sync(dry_run: bool = False, state_path: str = None):
    """Run a full sync cycle."""
    if not CKAN_URL or not CKAN_API_KEY:
        logger.error("CKAN_URL and CKAN_API_KEY must be set")
        sys.exit(1)

    state = SyncState.load(state_path)
    irods = IRODSClient()
    ckan = CKANSyncClient(CKAN_URL, CKAN_API_KEY)

    logger.info("Listing curated directories from iRODS...")
    dirs = irods.list_curated_directories()
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
            # Fetch AVU metadata (pass folder_info to avoid extra stat call)
            avus = irods.get_collection_metadata(path, folder_info=entry)

            # Check required fields
            try:
                get_title(avus)
            except KeyError:
                logger.warning("Skipping %s: no title in metadata", dirname)
                stats["skipped"] += 1
                continue

            # Map to CKAN fields
            mapped = map_avus_to_ckan(avus)

            if dry_run:
                logger.info("[DRY-RUN] Would %s: %s (name=%s)", action, dirname, mapped["name"])
                stats["created" if action == "create" else "updated"] += 1
                continue

            # Create or update in CKAN
            ckan_id = None
            if action == "create":
                # Check if already exists (e.g. from a previous partial sync)
                existing = ckan.get_dataset_by_name(mapped["name"])
                if existing:
                    logger.info("Dataset %s already exists in CKAN, updating", mapped["name"])
                    result = ckan.update_dataset(existing["id"], mapped)
                    ckan_id = existing["id"]
                else:
                    result = ckan.create_dataset(mapped)
                    if result.get("success"):
                        ckan_id = result["result"]["id"]
                        logger.info("Created: %s -> %s", dirname, ckan_id)
                    elif "already in use" in str(result.get("error", "")):
                        # Name collision -- append DOI suffix
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
                    result = ckan.update_dataset(ckan_id, mapped)
                    if not result.get("success"):
                        logger.error("Failed to update %s: %s", dirname, result.get("error"))
                        stats["errors"] += 1
                        continue
                    logger.info("Updated: %s", dirname)
                else:
                    # Lost track of ckan_id, try by name
                    existing = ckan.get_dataset_by_name(mapped["name"])
                    if existing:
                        ckan_id = existing["id"]
                        result = ckan.update_dataset(ckan_id, mapped)
                    else:
                        result = ckan.create_dataset(mapped)
                        if result.get("success"):
                            ckan_id = result["result"]["id"]
                stats["updated"] += 1

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
        "Sync complete: created=%d, updated=%d, skipped=%d, errors=%d",
        stats["created"], stats["updated"], stats["skipped"], stats["errors"],
    )
    return stats


def main():
    parser = argparse.ArgumentParser(description="Sync iRODS AVU metadata to CKAN")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to CKAN")
    parser.add_argument("--state-file", default=None, help="Path to sync state JSON file")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    )

    sync(dry_run=args.dry_run, state_path=args.state_file)


if __name__ == "__main__":
    main()
