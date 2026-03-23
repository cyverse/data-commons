"""
iRODS data access via the CyVerse Terrain API.

Uses the same Terrain API as kando/de.py but with a focused, decoupled interface
for the sync module. Requires DE credentials for authenticated access.

Verified AVU response format (from live MCP tool calls 2026-03-11):
  { "avus": [{"attr": "title", "value": "..."}, {"attr": "contributor", "value": "Smith J"}, ...] }

Directory listing format (from Terrain secured/filesystem/directory):
  { "folders": [{"id": "...", "path": "...", "label": "...", "date-created": ms, "date-modified": ms}, ...] }
"""

import os
import logging
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TERRAIN_URL = os.getenv("TERRAIN_URL", "https://de.cyverse.org/terrain")
WEBDAV_URL = os.getenv("WEBDAV_URL", "https://data.cyverse.org/dav")
CURATED_PATH = "/iplant/home/shared/commons_repo/curated"


def _ms_to_iso(ms) -> str:
    """Convert milliseconds since epoch to ISO datetime string."""
    try:
        return datetime.fromtimestamp(int(ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return str(ms)


class IRODSClient:
    def __init__(self, username: str = None, password: str = None):
        self.base_url = TERRAIN_URL.rstrip("/")
        self.session = requests.Session()

        # Authenticate
        username = username or os.getenv("DE_USERNAME")
        password = password or os.getenv("DE_PASSWORD")
        if not username or not password:
            raise ValueError("DE_USERNAME and DE_PASSWORD must be set for Terrain API access")

        token = self._get_token(username, password)
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })

    def _get_token(self, username: str, password: str) -> str:
        url = f"{self.base_url}/token/keycloak"
        resp = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Terrain auth failed: {resp.status_code} {resp.text[:200]}")
        return resp.json()["access_token"]

    def is_publicly_readable(self, path: str) -> bool:
        """
        Check if an iRODS path is publicly readable via anonymous WebDAV.

        Makes an unauthenticated HEAD request to the CyVerse WebDAV endpoint
        using the 'anonymous' user (empty password). Returns True if the server
        responds with 200 or 207 (WebDAV Multi-Status), which mirrors the iRODS
        ACL: public folders are accessible to the anonymous user.
        """
        url = f"{WEBDAV_URL}{path}"
        try:
            resp = requests.head(
                url,
                auth=HTTPBasicAuth("anonymous", ""),
                timeout=10,
                allow_redirects=True,
            )
            return resp.status_code in (200, 207)
        except requests.RequestException as e:
            logger.warning("Public access check failed for %s: %s", path, e)
            return False

    def list_project_directories(self, base_path: str) -> list[dict]:
        """
        List subdirectories under any iRODS collection path.

        Returns:
            List of dicts with keys: 'name', 'path', 'modify_time', 'create_time', 'id'
        """
        url = f"{self.base_url}/secured/filesystem/directory"
        params = {"path": base_path}
        resp = self.session.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        dirs = []
        for folder in data.get("folders", []):
            dirs.append({
                "name": folder.get("label", ""),
                "path": folder.get("path", ""),
                "modify_time": _ms_to_iso(folder.get("date-modified", 0)),
                "create_time": _ms_to_iso(folder.get("date-created", 0)),
                "id": folder.get("id", ""),
            })
        return dirs

    def list_curated_directories(self) -> list[dict]:
        """List subdirectories under the curated collection."""
        return self.list_project_directories(CURATED_PATH)

    def get_collection_metadata(self, path: str, folder_info: dict = None) -> dict:
        """
        Get AVU metadata for a collection, returned as a dict
        matching the format from de.get_all_metadata_dataset().

        Multi-value attrs are stored as lists.
        """
        metadata_dict = {"de_path": path}

        # Get dates from folder_info if provided, otherwise fetch
        if folder_info:
            metadata_dict["date_created"] = folder_info.get("create_time", "")
            metadata_dict["date_modified"] = folder_info.get("modify_time", "")
            folder_id = folder_info.get("id", "")
        else:
            info = self.get_collection_info(path)
            metadata_dict["date_created"] = info.get("create_time", "")
            metadata_dict["date_modified"] = info.get("modify_time", "")
            folder_id = info.get("id", "")

        # Fetch AVUs via Terrain metadata endpoint
        if folder_id:
            url = f"{self.base_url}/filesystem/{folder_id}/metadata"
        else:
            # Fallback: stat to get ID first
            info = self.get_collection_info(path)
            folder_id = info.get("id", "")
            if not folder_id:
                logger.warning("Cannot get metadata for %s: no folder ID", path)
                return metadata_dict
            url = f"{self.base_url}/filesystem/{folder_id}/metadata"

        resp = self.session.get(url, timeout=30)
        if resp.status_code != 200:
            logger.warning("Metadata fetch failed for %s: %s", path, resp.status_code)
            return metadata_dict

        data = resp.json()

        for avu in data.get("avus", []):
            key = avu.get("attr", "")
            value = avu.get("value", "")
            if not key:
                continue
            if key in metadata_dict:
                existing = metadata_dict[key]
                if isinstance(existing, list):
                    existing.append(value)
                else:
                    metadata_dict[key] = [existing, value]
            else:
                metadata_dict[key] = value

        return metadata_dict

    def list_collection_contents(self, path: str) -> dict:
        """
        List files and subfolders in a collection via the paged-directory endpoint.

        Returns:
            Dict with 'files' and 'folders' lists. Each entry has:
            'name', 'path', 'modify_time', 'create_time', 'type' ('file' or 'folder').
        """
        url = f"{self.base_url}/secured/filesystem/paged-directory"
        params = {"path": path, "limit": 1000}
        resp = self.session.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        files = []
        for f in data.get("files", []):
            label = f.get("label", "")
            ext = label.rsplit(".", 1)[-1] if "." in label else ""
            files.append({
                "name": label,
                "path": f.get("path", ""),
                "modify_time": _ms_to_iso(f.get("date-modified", 0)),
                "create_time": _ms_to_iso(f.get("date-created", 0)),
                "type": "file",
                "format": ext,
            })

        folders = []
        for f in data.get("folders", []):
            folders.append({
                "name": f.get("label", ""),
                "path": f.get("path", ""),
                "modify_time": _ms_to_iso(f.get("date-modified", 0)),
                "create_time": _ms_to_iso(f.get("date-created", 0)),
                "type": "folder",
                "format": "folder",
            })

        return {"files": files, "folders": folders}

    def get_collection_info(self, path: str) -> dict:
        """Get stat info for a collection path."""
        url = f"{self.base_url}/secured/filesystem/stat"
        params = {"paths": path}
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Response: {"paths": {"/path/...": {"id": "...", "date-created": ms, "date-modified": ms, ...}}}
        path_info = data.get("paths", {}).get(path, {})
        return {
            "modify_time": _ms_to_iso(path_info.get("date-modified", 0)),
            "create_time": _ms_to_iso(path_info.get("date-created", 0)),
            "id": path_info.get("id", ""),
        }
