"""
Pure functions to map iRODS AVU metadata to CKAN dataset fields.

Extracted from kando/helpers/migration.py -- no external service imports.
"""


def clean_dataset_metadata(dataset_metadata: dict) -> dict:
    """Remove tabs from all string values in the metadata dict."""
    for key, value in dataset_metadata.items():
        if isinstance(value, str):
            dataset_metadata[key] = value.replace('\t', '')
        elif isinstance(value, list):
            dataset_metadata[key] = [v.replace('\t', '') if isinstance(v, str) else v for v in value]
    return dataset_metadata


def get_title(dataset_metadata: dict) -> str:
    """Extract title from metadata, trying multiple key variants."""
    title = None
    for key in ('title', 'Title', 'datacite.title'):
        if key in dataset_metadata:
            title = dataset_metadata[key]

    if title is None:
        raise KeyError("No title found in metadata (tried 'title', 'Title', 'datacite.title')")

    if isinstance(title, list):
        return (", ".join(title)).strip()
    return title.strip()


def get_author(dataset_metadata: dict) -> str:
    """Extract author/creator from metadata."""
    for key in ('datacite.creator', 'creator', 'Creator'):
        if key in dataset_metadata:
            val = dataset_metadata[key]
            if isinstance(val, str):
                return val
            return ', '.join(val)
    raise KeyError("No creator found in metadata")


def get_publication_year(dataset_metadata: dict) -> str:
    """Extract publication year from metadata."""
    for key in ('datacite.publicationyear', 'publicationYear', 'PublicationYear'):
        if key in dataset_metadata:
            val = dataset_metadata[key]
            if isinstance(val, str):
                return val[:4]
            return val[0][:4]
    raise KeyError("No publication year found in metadata")


def get_description(dataset_metadata: dict) -> str:
    """Extract description from metadata."""
    for key in ('description', 'Description'):
        if key in dataset_metadata:
            val = dataset_metadata[key]
            if isinstance(val, list):
                return ', '.join(val)
            return val
    raise KeyError("No description found in metadata")


def get_license_info(dataset_metadata: dict) -> dict:
    """Map rights AVU to CKAN license fields."""
    rights = None
    for key in ('rights', 'Rights'):
        if key in dataset_metadata:
            rights = dataset_metadata[key]
            if isinstance(rights, list):
                rights = ', '.join(rights)
            break

    if rights and "ODC PDDL" in rights:
        return {
            'license_id': "odc-pddl",
            'license_title': "Open Data Commons Public Domain Dedication and License (PDDL)",
            'license_url': "http://www.opendefinition.org/licenses/odc-pddl",
        }
    elif rights and "CC0" in rights:
        return {
            'license_id': "cc-zero",
            'license_title': "Creative Commons CCZero",
            'license_url': "http://www.opendefinition.org/licenses/cc-zero",
        }
    else:
        return {
            'license_id': "notspecified",
            'license_title': "License not specified",
        }


def get_tags(dataset_metadata: dict) -> list:
    """Extract and normalize subject tags."""
    tags = []
    if 'subject' not in dataset_metadata:
        return tags

    subjects = dataset_metadata['subject']
    if isinstance(subjects, str):
        subjects = subjects.replace("(", "").replace(")", "").replace("&", "-").split(',')
        tags = [{'name': s.strip()} for s in subjects if s.strip()]
    else:
        for subject in subjects:
            cleaned = subject.replace("(", "").replace(")", "").replace("&", "-").replace("#", "-")
            if ', ' in cleaned:
                tags.extend({'name': t.strip()} for t in cleaned.split(',') if t.strip())
            else:
                tags.append({'name': cleaned})
    return tags


def get_name_from_title(title: str) -> str:
    """Normalize title into a CKAN-compatible dataset name."""
    name = ''.join(c if c.isalnum() or c in ('-', '_', ' ') else '' for c in title.lower().replace(' ', '_'))
    return name[:100]


def create_citation(dataset_metadata: dict) -> str:
    """Build a citation string from metadata."""
    citation = ''
    citation += get_author(dataset_metadata) + " "
    citation += get_publication_year(dataset_metadata) + ". "
    citation += get_title(dataset_metadata) + ". "
    citation += "CyVerse Data Commons. "

    identifier = None
    for key in ('Identifier', 'identifier'):
        if key in dataset_metadata:
            identifier = dataset_metadata[key]
            break

    if identifier is not None:
        if isinstance(identifier, str):
            citation += f"DOI {identifier}"
        elif len(identifier) > 1 and identifier[1] != '':
            citation += f"DOI {identifier[0]}, {identifier[1]}"
        else:
            citation += f"DOI {identifier[0]}"

    return citation


def get_extras(dataset_metadata: dict) -> list:
    """Build CKAN extras list from metadata, excluding fields mapped to core CKAN fields."""
    extras = []

    dont_include = {
        'title', 'description', 'creator', 'subject', 'rights', 'identifier',
        'date_created', 'date_modified', 'de_path',
        'datacite.creator', 'datacite.title', 'datacite.publicationyear',
        'publicationYear', 'Creator', 'Title', 'Identifier', 'version',
    }

    extras.append({'key': 'Citation', 'value': create_citation(dataset_metadata)})

    if 'date_created' in dataset_metadata:
        extras.append({'key': 'Date created in discovery environment', 'value': dataset_metadata['date_created']})
    if 'date_modified' in dataset_metadata:
        extras.append({'key': 'Date last modified in discovery environment', 'value': dataset_metadata['date_modified']})

    for key, value in dataset_metadata.items():
        if key not in dont_include:
            if isinstance(value, list):
                extras.append({'key': key, 'value': ', '.join(str(v) for v in value)})
            else:
                extras.append({'key': key, 'value': str(value)})

    return extras


_DEFAULT_GROUPS = [{
    "description": "All data that have been given a permanent identifier (DOI or ARK) by CyVerse. "
                   "These data are stable and contents will not change.",
    "display_name": "CyVerse Curated",
    "name": "cyverse-curated",
    "title": "CyVerse Curated"
}]


def map_avus_to_ckan(
    dataset_metadata: dict,
    owner_org: str = 'cyverse',
    groups: list = None,
) -> dict:
    """
    Map a full AVU metadata dict to a CKAN dataset dict ready for package_create/update.

    Args:
        dataset_metadata: Dict of AVU attrs (multi-value attrs as lists),
                         plus optional 'date_created', 'date_modified', 'de_path'.
        owner_org: CKAN organization slug (default: 'cyverse').
        groups: CKAN group list (default: cyverse-curated group).

    Returns:
        Dict suitable for CKAN package_create or package_update API.
    """
    dataset_metadata = clean_dataset_metadata(dataset_metadata)

    title = get_title(dataset_metadata)

    data = {
        'owner_org': owner_org,
        'private': False,
        'name': get_name_from_title(title),
        'title': title,
        'notes': get_description(dataset_metadata),
        'author': get_author(dataset_metadata),
        'tags': get_tags(dataset_metadata),
        'extras': get_extras(dataset_metadata),
        'groups': groups if groups is not None else _DEFAULT_GROUPS,
    }

    data.update(get_license_info(dataset_metadata))

    if 'version' in dataset_metadata:
        data['version'] = dataset_metadata['version']
    elif 'Version' in dataset_metadata:
        data['version'] = dataset_metadata['Version']

    return data
