"""
Resource (file) sync helpers for the AVU sync module.

Builds CKAN resource_create payloads from iRODS file listings and filters
out files already present in a dataset, following the same field names used
by kando/utils/migrate.py and kando/ckan.py:add_resource_link().
"""

from kando.sync.irods_client import _ms_to_iso


def _file_format(label: str) -> str:
    """Extract file extension from label, matching kando/de.py:get_all_metadata_file()."""
    if "." not in label:
        return ""
    ext = label.split(".")[-1]
    return "" if ext == label else ext


def build_resource_data(
    file_info: dict,
    dataset_id: str,
    webdav_url: str,
    is_folder: bool = False,
) -> dict:
    """
    Build a CKAN resource_create payload from an iRODS file/folder dict.

    Mirrors the resource dicts produced by kando/utils/migrate.py so that
    resources created by the sync are identical in structure to those created
    by the original migration.

    Args:
        file_info:   A file/folder dict from the Terrain paged-directory response.
        dataset_id:  CKAN dataset ID to attach the resource to.
        webdav_url:  Base WebDAV URL (WEB_DAV_URL env var) for constructing the link.
        is_folder:   True when the item is a directory rather than a file.
    """
    label = file_info.get("label", "")
    path = file_info.get("path", "")
    return {
        "package_id": dataset_id,
        "name": label,
        "description": None,
        "url": webdav_url.rstrip("/") + path,
        "format": "folder" if is_folder else _file_format(label),
        "Date created in discovery environment": _ms_to_iso(
            file_info.get("date-created", 0)
        ),
        "Date last modified in discovery environment": _ms_to_iso(
            file_info.get("date-modified", 0)
        ),
    }


def get_resources_to_add(
    irods_listing: dict,
    existing_names: set,
    dataset_id: str,
    webdav_url: str,
) -> list:
    """
    Return resource payloads for files/folders not yet present in the CKAN dataset.

    Args:
        irods_listing:   Response from IRODSClient.list_files() with 'files'
                         and 'folders' keys.
        existing_names:  Set of resource names already registered in CKAN.
        dataset_id:      CKAN dataset ID.
        webdav_url:      Base WebDAV URL for constructing resource links.

    Returns:
        List of dicts ready to pass to CKANSyncClient.add_resource_link().
    """
    to_add = []
    for file_info in irods_listing.get("files", []):
        if file_info.get("label") not in existing_names:
            to_add.append(
                build_resource_data(file_info, dataset_id, webdav_url, is_folder=False)
            )
    for folder_info in irods_listing.get("folders", []):
        if folder_info.get("label") not in existing_names:
            to_add.append(
                build_resource_data(
                    folder_info, dataset_id, webdav_url, is_folder=True
                )
            )
    return to_add
