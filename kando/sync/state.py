"""
Manages sync state manifest to track which datasets have been synced and when.
"""

import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "sync_state.json")


class SyncState:
    def __init__(self, path: str = None):
        self.path = path or DEFAULT_STATE_PATH
        self.data = {
            "last_full_sync": None,
            "datasets": {},
        }

    @classmethod
    def load(cls, path: str = None) -> "SyncState":
        state = cls(path)
        if os.path.exists(state.path):
            try:
                with open(state.path, "r") as f:
                    state.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Could not load state from %s: %s. Starting fresh.", state.path, e)
        return state

    def save(self):
        self.data["last_full_sync"] = datetime.now(timezone.utc).isoformat()
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)
        logger.info("State saved to %s", self.path)

    def is_new(self, dirname: str) -> bool:
        return dirname not in self.data["datasets"]

    def is_modified(self, dirname: str, modify_time: str) -> bool:
        entry = self.data["datasets"].get(dirname)
        if entry is None:
            return True
        return entry.get("irods_modify_time") != modify_time

    def get_ckan_id(self, dirname: str) -> str | None:
        entry = self.data["datasets"].get(dirname)
        if entry:
            return entry.get("ckan_dataset_id")
        return None

    def mark_synced(self, dirname: str, irods_info: dict, ckan_id: str):
        self.data["datasets"][dirname] = {
            "irods_modify_time": irods_info.get("modify_time", ""),
            "ckan_dataset_id": ckan_id,
            "last_synced": datetime.now(timezone.utc).isoformat(),
        }
