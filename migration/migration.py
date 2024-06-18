from CKAN_Testing import main as ckan
from DE_API_Testing import main3 as de
import json

def clean_dataset_metadata(dataset_metadata: dict):
    """
    Clean the dataset metadata by removing tabs from the values in the dictionary.
    Args:
        dataset_metadata (dict): The dataset metadata dictionary.

    Returns:
        dict: The cleaned dataset metadata dictionary.
    """
    for key, value in dataset_metadata.items():
        if isinstance(value, str):
            dataset_metadata[key] = value.replace('\t', '')
        elif isinstance(value, list):
            dataset_metadata[key] = [v.replace('\t', '') for v in value]
    return dataset_metadata

def create_citation(dataset_metadata: dict):
    """
    Create a citation for the dataset using the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The citation for the dataset.
    """

    # Check if the dataset is a datacite dataset
    is_datacite = 'datacite.creator' in dataset_metadata
    citation = ''

    # Add the author, publication year, title, and CyVerse Data Commons to the citation

    citation += get_author(dataset_metadata) + " "

    citation += get_publication_year(dataset_metadata) + ". "

    citation += get_title(dataset_metadata) + ". "

    citation += "CyVerse Data Commons. "

    # Add the DOI identifier to the citation
    try:
        # Check if the dataset's identifier key is a string or a list
        if isinstance(dataset_metadata['Identifier'], str):
            # If the identifier is a string, add it to the citation
            citation += f"DOI {dataset_metadata['Identifier']}"
        # If the identifier is a list, check if the second element is an empty string. If it is, add only the first element to the citation. Otherwise, add both elements to the citation.
        elif dataset_metadata['Identifier'][1] == '':
            citation += f"DOI {dataset_metadata['Identifier'][0]}"
        else:
            citation += f"DOI {dataset_metadata['Identifier'][0]}, {dataset_metadata['Identifier'][1]}"
    # If the dataset does not have an 'Identifier' key, check the 'identifier' key instead
    except KeyError:
        if isinstance(dataset_metadata['identifier'], str):
            citation += f"DOI {dataset_metadata['identifier']}"
        elif dataset_metadata['identifier'][1] == '':
            citation += f"DOI {dataset_metadata['identifier'][0]}"
        else:
            citation += f"DOI {dataset_metadata['identifier'][0]}, {dataset_metadata['identifier'][1]}"

    return citation



def get_title(dataset_metadata: dict):
    """
    Get the title of the dataset from the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The title of the dataset.
    """

    # Check if the dataset is a datacite dataset
    is_datacite = 'datacite.creator' in dataset_metadata

    # Check if the dataset has a 'datacite.title' key. If it does, use that as the title. Otherwise, use the 'title' key.
    if is_datacite:
        try:
            return dataset_metadata['datacite.title']
        except KeyError:
            return dataset_metadata['title']
    ## If the dataset does not have a 'datacite.title' key, use the 'title' key or 'Title' key.
    else:
        try:
            return dataset_metadata['title']
        except KeyError:
            return dataset_metadata['Title']


def get_author(dataset_metadata: dict):
    """
    Get the author(s) of the dataset from the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The author(s) of the dataset.
    """

    # Check if the dataset is a datacite dataset
    is_datacite = 'datacite.creator' in dataset_metadata

    # Check if the dataset has a 'datacite.creator' key. If it does, use that as the author.
    if is_datacite:
        # If the author is a string, return the author. Otherwise, join the authors with a comma.
        if isinstance(dataset_metadata['datacite.creator'], str):
            return dataset_metadata['datacite.creator']
        else:
            return ', '.join(dataset_metadata['datacite.creator'])

    # If the dataset does not have a 'datacite.creator' key...
    else:
        # If the author is a string, return the author. Otherwise, join the authors with a comma.
        try:
            if isinstance(dataset_metadata['creator'], str):
                return dataset_metadata['creator']
            else:
                return ', '.join(dataset_metadata['creator'])
        # If the dataset does not have a 'creator' key, return the 'Creator' key.
        except KeyError:
            return dataset_metadata['Creator']


def get_publication_year(dataset_metadata: dict):
    """
    Get the publication year of the dataset from the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The publication year of the dataset.
    """

    # Check if the dataset is a datacite dataset
    is_datacite = 'datacite.creator' in dataset_metadata

    # Check if the dataset has a 'datacite.publicationyear' key. If it does, use that as the publication year.
    if is_datacite:
        # If the publication year is a string, return the first four characters of the string.
        if isinstance(dataset_metadata['datacite.publicationyear'], str):
            return dataset_metadata['datacite.publicationyear'][:4]
        # If the publication year is a list, return the first four characters of the first element in the list since the second element is empty
        else:
            return dataset_metadata['datacite.publicationyear'][0][:4]

    # If the dataset does not have a 'datacite.publicationyear' key, use the 'publicationYear' key.
    else:
        # If the publication year is a string, return the publication year.
        if isinstance(dataset_metadata['publicationYear'], str):
            return dataset_metadata['publicationYear']
        else:
            return dataset_metadata['publicationYear'][0][:4]


def get_extras(dataset_metadata: dict):
    """
    Get the extras list for the dataset from the dataset metadata.
    These are the metadata fields that are not part of the main dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        list: The extras list for the dataset.
    """

    # Initialize the extras list
    extras = []

    # List of keys to exclude from the extras list
    dont_include = ['title', 'description', 'creator', 'subject', 'rights', 'identifier', 'date_created',
                    'date_modified', 'de_path', 'datacite.creator', 'datacite.title', 'datacite.publicationyear',
                    'publicationYear', 'Creator', 'Title', 'Identifier', 'version']

    # Add the citation to the extras list
    extras.append({'key': 'Citation', 'value': create_citation(dataset_metadata)})
    extras.append({'key': 'Date created in discovery environment', 'value': dataset_metadata['date_created']})
    extras.append({'key': 'Date last modified in discovery environment', 'value': dataset_metadata['date_modified']})

    # If any of the keys in the dataset metadata are not in the 'dont_include' list, add them to the extras list
    # If the values are lists, join them with a comma
    for key, value in dataset_metadata.items():
        if key not in dont_include:
            if isinstance(value, list):
                extras.append({'key': key, 'value': ', '.join(value)})
            else:
                extras.append({'key': key, 'value': value})


    return extras


def migrate_dataset_and_files(dataset_metadata: dict):
    dataset_metadata = clean_dataset_metadata(dataset_metadata)
    # pretty_print(dataset_metadata)
    # print("\n\n\n")
    #
    # is_datacite = 'datacite.creator' in dataset_metadata
    # print(f"Is DataCite: {is_datacite}")


    data = {
        # 'name': get_title(dataset_metadata).lower().replace(' ', '-').replace('(', '').replace(')', ''),
        # 'title': get_title(dataset_metadata),
        # 'notes': dataset_metadata['description'],
        'owner_org': 'tanmay-s-playground',
        'private': False,
        # 'author': dataset_metadata['creator'],
        # 'author_email': 'john.doe@example.com', # DONT FORGET TO ADD EMAIL FOR THAT ONE DATASET
        # 'tags': [{'name': 'example'}, {'name': 'dataset'}],
        'groups': [
            {
                "description": "All data that have been given a permanent identifier (DOI or ARK) by CyVerse. These data are stable and contents will not change.",
                "display_name": "CyVerse Curated",
                "id": "881288fa-e1bf-4ee8-8894-d97976043e4f",
                "image_display_url": "",
                "name": "cyverse-curated",
                "title": "CyVerse Curated"
            }
        ],
        'extras': get_extras(dataset_metadata)
    }

    # Get the title of the dataset
    title = get_title(dataset_metadata).strip()
    ## Set the 'name' key to the title of the dataset with spaces replaced by hyphens and parentheses removed
    data['name'] = title.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '-').replace('"', '').replace('/', '-')
    ## Set the 'title' key to the title of the dataset
    data['title'] = title


    # Set the 'notes' key to the description of the dataset depending on whether the description is stored in the 'description' key or 'Description' key
    try:
        data['notes'] = dataset_metadata['description']
    except KeyError:
        data['notes'] = dataset_metadata['Description']


    # Set the 'author' key to the creator of the dataset
    data['author'] = get_author(dataset_metadata)

    # Set the keys for the license depending on the license specified in the dataset metadata
    if "ODC PDDL" in dataset_metadata['rights']:
        data['license_id'] = "odc-pddl"
        data['license_title'] = "Open Data Commons Public Domain Dedication and License (PDDL)"
        data['license_url'] = "http://www.opendefinition.org/licenses/odc-pddl"
    elif "CC0" in dataset_metadata['rights']:
        data['license_id'] = "cc-zero"
        data['license_title'] = "Creative Commons CCZero"
        data['license_url'] = "http://www.opendefinition.org/licenses/cc-zero"
    else:
        data['license_id'] = "notspecified"
        data['license_title'] = "License not specified"

    # If there is a 'subject' key in the dataset metadata, add it to the tags depending on whether its a string or a list
    if 'subject' in dataset_metadata:
        if isinstance(dataset_metadata['subject'], str):
            subjects = dataset_metadata['subject'].split(',')
            data['tags'] = [{'name': subject} for subject in subjects]
        else:
            data['tags'] = [{'name': subject} for subject in dataset_metadata['subject']]

    # If there is a 'version' or 'Version' key in the dataset metadata, add it to the data dictionary
    if 'version' in dataset_metadata:
        data['version'] = dataset_metadata['version']
    elif 'Version' in dataset_metadata:
        data['version'] = dataset_metadata['Version']

    # Print the data dictionary
    # print("Data Dictionary: ")
    # pretty_print(data)

    # Create the dataset
    dataset_response = ckan.create_dataset(data)
    print(f'Dataset creation response: {dataset_response}')

    # Get the dataset ID
    dataset_id = dataset_response['result']['id']
    print(f'Dataset ID: {dataset_id}')
    print('\n')


    # --------------------------------- FILES ---------------------------------


    # Get the list of files in the dataset
    files = de.get_files(dataset_metadata['de_path'])
    # print('\n\n\nFiles without metadata: ')
    # pretty_print(files)

    # print("\n\n\nFiles with Metadata: \n")
    # print("Files")
    for file in files['files']:
        file_metadata = de.get_all_metadata_file(file)
        # pretty_print(file_metadata)

        data = {
            'package_id': dataset_id,
            'name': file_metadata['file_name'],
            'description': None,
            'url': file_metadata['web_dav_location'],
            'format': file_metadata['file_type'],
            'Date created in discovery environment': file_metadata['date_created'],
            'Date last modified in discovery environment': file_metadata['date_modified']
        }
        response = ckan.add_resource_link(data)
        # print(f'Resource creation response: {response}')
        # print("\n\n")

    # print("Folders")
    for folder in files['folders']:
        folder_metadata = de.get_all_metadata_file(folder)
        # pretty_print(folder_metadata)

        data = {
            'package_id': dataset_id,
            'name': folder_metadata['file_name'],
            'description': None,
            'url': folder_metadata['web_dav_location'],
            'format': 'folder',
            'Date Created in Discovery Environment': folder_metadata['date_created'],
            'Date Last Modified in Discovery Environment': folder_metadata['date_modified']
        }
        response = ckan.add_resource_link(data)
        # print(f'Resource creation response: {response}')
        #
        # print("\n\n")

def pretty_print(json_data):
    """
    Format and print JSON data in a readable way.

    Parameters:
    json_data (dict): JSON data to be pretty-printed.
    """
    print(json.dumps(json_data, indent=4, sort_keys=True))

if __name__ == '__main__':

    # ckan.delete_all_datasets_in_organization('tanmay-s-playground')

    de_datasets: list[dict] = de.get_datasets()
    # pretty_print(de_datasets)

    # print("\n\n\n")
    # ckan_datasets = ckan.list_datasets(group='cyverse-curated')
    ckan_datasets = ckan.list_datasets(organization='tanmay-s-playground')
    # for dataset in ckan_datasets:
    #     pretty_print(dataset)
    # print("\n\n\n")

    count = 0

    # Iterate through each dataset in the discovery environment to see if they exist in CKAN and whether they need to be updated
    for de_dataset in de_datasets:
        if 3 < count < 10:
            # Get the metadata for the dataset in the discovery environment
            de_dataset_metadata = de.get_all_metadata_dataset(de_dataset)
            ## print("Discovery Environment Dataset Metadata")
            ## pretty_print(de_dataset_metadata)

            # Get the title of the dataset in the discovery environment
            de_dataset_title = get_title(de_dataset_metadata).strip()
            # print(f"Discovery Environment Dataset Title: {de_dataset_title}")

            # Iterate through each dataset in CKAN to see if the titles match
            for ckan_dataset in ckan_datasets:
                # pretty_print(ckan_dataset)
                # Get the title of the dataset in CKAN
                ckan_dataset_title = ckan_dataset['result']['title'].strip()
                # print(f"CKAN Dataset Title: {ckan_dataset_title}")
                if de_dataset_title == ckan_dataset_title:
                    print(f"Matched: {de_dataset_title}")

                    # Get the last modified date for the dataset in the discovery environment
                    last_modified_de = de_dataset_metadata['date_modified']

                    # Get the last modified date for the dataset in CKAN
                    for extra in ckan_dataset['result']['extras']:
                        if extra['key'] == 'Date last modified in discovery environment':
                            last_modified_ckan = extra['value']

                    # If the dataset in the discovery environment has been modified update the dataset in CKAN
                    # by deleting the old dataset and creating a new one with the updated metadata and files
                    if last_modified_de != last_modified_ckan:
                        ckan_dataset_id = ckan_dataset['result']['id']
                        print("Rewriting")
                        ckan.delete_dataset(ckan_dataset_id)
                        migrate_dataset_and_files(de_dataset_metadata)

                    # Break out of the loop if the dataset is found in CKAN
                    break



            # If the dataset does not exist in CKAN, create a new dataset
            else:
                print(f"Creating New Dataset in CKAN: {de_dataset_title}")
                migrate_dataset_and_files(de_dataset_metadata)

            print("\n")
        count += 1









    # migrate_dataset_and_files(de.get_all_metadata_dataset(de_datasets[18]))


