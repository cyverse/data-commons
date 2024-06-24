import ckan
import de
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

        # If the identifier is a list, check if the second element is an empty string.
        # If it is, add only the first element to the citation. Otherwise, add both elements to the citation.
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

    # Keep trying to get the title from different keys in the dataset metadata
    try:
        title = dataset_metadata['title']
    except KeyError:
        pass

    try:
        title = dataset_metadata['Title']
    except KeyError:
        pass

    try:
        title = dataset_metadata['datacite.title']
    except KeyError:
        pass

    # If the title is a list, join the elements with a comma
    if isinstance(title, list):
        return ", ".join(title)

    # Return the title
    return title


def get_author(dataset_metadata: dict):
    """
    Get the author(s) of the dataset from the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The author(s) of the dataset.
    """

    # Check if the dataset has a 'datacite.creator' key. If it does, use that as the author.
    try:
        # If the author is a string, return the author. Otherwise, join the authors with a comma.
        if isinstance(dataset_metadata['datacite.creator'], str):
            return dataset_metadata['datacite.creator']
        else:
            return ', '.join(dataset_metadata['datacite.creator'])

    # If the dataset does not have a 'datacite.creator' key...
    except KeyError:
        # If the author is a string, return the author. Otherwise, join the authors with a comma.
        try:
            if isinstance(dataset_metadata['creator'], str):
                return dataset_metadata['creator']
            else:
                return ', '.join(dataset_metadata['creator'])
        # If the dataset does not have a 'creator' key, return the 'Creator' key.
        except KeyError:
            if isinstance(dataset_metadata['Creator'], str):
                return dataset_metadata['Creator']
            else:
                return ', '.join(dataset_metadata['Creator'])


def get_publication_year(dataset_metadata: dict):
    """
    Get the publication year of the dataset from the dataset metadata.
    Args:
        dataset_metadata: The dataset metadata dictionary.

    Returns:
        str: The publication year of the dataset.
    """

    # Check if the dataset has a 'datacite.publicationyear' key. If it does, use that as the publication year.
    try:
        # If the publication year is a string, return the first four characters of the string.
        if isinstance(dataset_metadata['datacite.publicationyear'], str):
            return dataset_metadata['datacite.publicationyear'][:4]
        # If the publication year is a list, return the first four characters
        # of the first element in the list since the second element is empty
        else:
            return dataset_metadata['datacite.publicationyear'][0][:4]

    # If the dataset does not have a 'datacite.publicationyear' key, use the 'publicationYear' key.
    except KeyError:
        try:
            # If the publication year is a string, return the publication year.
            if isinstance(dataset_metadata['publicationYear'], str):
                return dataset_metadata['publicationYear']
            else:
                return dataset_metadata['publicationYear'][0][:4]

        # If the dataset does not have a 'publicationYear' key, use the 'PublicationYear' key.
        except KeyError:
            # If the publication year is a string, return the publication year.
            if isinstance(dataset_metadata['PublicationYear'], str):
                return dataset_metadata['PublicationYear']
            else:
                return dataset_metadata['PublicationYear'][0][:4]


def get_extras(dataset_metadata: dict, curated=True):
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
    if curated:
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


def migrate_dataset_and_files(dataset_metadata: dict, title=None, organization='cyverse', curated=True):
    dataset_metadata = clean_dataset_metadata(dataset_metadata)
    # pretty_print(dataset_metadata)

    data = {
        'owner_org': organization,
        'private': False,
        'extras': get_extras(dataset_metadata, curated=curated)
    }

    # Only add the 'groups' key if the dataset is curated
    if curated:
        data['groups'] = [{
                "description": "All data that have been given a permanent identifier (DOI or ARK) by CyVerse. "
                               "These data are stable and contents will not change.",
                "display_name": "CyVerse Curated",
                "id": "881288fa-e1bf-4ee8-8894-d97976043e4f",
                "image_display_url": "",
                "name": "cyverse-curated",
                "title": "CyVerse Curated"
            }]

    # Get the title of the dataset
    if title is None:
        title = get_title(dataset_metadata).strip()
    # Set the 'name' key to the title of the dataset with unallowed characters replaced
    name = (title.lower().replace(' ', '-').replace('(', '').replace(')', '')
            .replace('.', '-').replace('"', '').replace('/', '-')
            .replace(',', '').replace(':', '').replace("*", "-")
            .replace("'", "-").replace('&', '-').replace("’", "-"))
    # If the length of the name is greater than 100, truncate it to 100 characters
    if len(name) > 100:
        name = name[:100]
    data['name'] = name

    # Set the 'title' key to the title of the dataset
    data['title'] = title

    # Set the 'notes' key to the description of the dataset depending on
    # whether the description is stored in the 'description' key or 'Description' key
    try:
        data['notes'] = dataset_metadata['description']
    except KeyError:
        data['notes'] = dataset_metadata['Description']

    # Set the 'author' key to the creator of the dataset
    data['author'] = get_author(dataset_metadata)

    # Try-Except block to check whether the key is 'rights' or 'Rights' in the dataset metadata
    try:
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
    except KeyError:
        # Set the keys for the license depending on the license specified in the dataset metadata
        if "ODC PDDL" in dataset_metadata['Rights']:
            data['license_id'] = "odc-pddl"
            data['license_title'] = "Open Data Commons Public Domain Dedication and License (PDDL)"
            data['license_url'] = "http://www.opendefinition.org/licenses/odc-pddl"
        elif "CC0" in dataset_metadata['Rights']:
            data['license_id'] = "cc-zero"
            data['license_title'] = "Creative Commons CCZero"
            data['license_url'] = "http://www.opendefinition.org/licenses/cc-zero"
        else:
            data['license_id'] = "notspecified"
            data['license_title'] = "License not specified"

    # If there is a 'subject' key in the dataset metadata,
    # add it to the tags depending on whether it's a string or a list
    if 'subject' in dataset_metadata:
        if isinstance(dataset_metadata['subject'], str):
            subjects = dataset_metadata['subject'].replace("(", "").replace(")", "").replace("&", "-").split(',')
            data['tags'] = [{'name': subject} for subject in subjects]
        else:
            data['tags'] = [{'name': subject.replace("(", "").replace(")", "").replace("&", "-").replace("#", "-")} for
                            subject in dataset_metadata['subject']]
            # Go through each tag in the tags list and check if any of them are separated by a comma.
            # If they are, split them into separate tags
            for tag in data['tags']:
                if ', ' in tag['name']:
                    data['tags'].remove(tag)
                    data['tags'] += [{'name': t.strip()} for t in tag['name'].split(',')]

    # If there is a 'version' or 'Version' key in the dataset metadata, add it to the data dictionary
    if 'version' in dataset_metadata:
        data['version'] = dataset_metadata['version']
    elif 'Version' in dataset_metadata:
        data['version'] = dataset_metadata['Version']

    # Create the dataset
    dataset_response = ckan.create_dataset(data)
    print(f'Dataset creation response: {dataset_response["success"]}')
    if not dataset_response["success"]:
        print(dataset_response)

    # Get the dataset ID
    dataset_id = dataset_response['result']['id']
    print(f'Dataset ID: {dataset_id}')

    # --------------------------------- FILES ---------------------------------

    print("\nMigrating Files...")

    # Get the list of files in the dataset
    files = de.get_files(dataset_metadata['de_path'])
    # Get the total number of files in the dataset
    num_files = files['total']
    print(f"Number of Files: {num_files}")

    # check if num_files is none and return if it is
    if num_files is None:
        return

    # Pass the number of files to the get_files function to get all the files
    files = de.get_files(dataset_metadata['de_path'], limit=num_files)

    # Iterate through each file in the dataset and create a resource for it in CKAN
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

    # Iterate through each folder in the dataset and create a resource for it in CKAN
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


def pretty_print(json_data):
    """
    Format and print JSON data in a readable way.

    Parameters:
    json_data (dict): JSON data to be pretty-printed.
    """
    print(json.dumps(json_data, indent=4, sort_keys=True))


# Function to check whether all the files/resources transferred from DE to CKAN
# If not, then transfer the remaining files
def check_files_transferred(de_files, ckan_resources):
    """
    Check if all files from DE have been transferred to CKAN.

    Args:
        de_files (list): List of files in DE.
        ckan_resources (list): List of resources in CKAN.

    Returns:
        list: List of files that have not been transferred to CKAN.
    """
    # Get the names of the files in DE
    de_file_names = [file['file_name'] for file in de_files]

    # Get the names of the resources in CKAN
    ckan_resource_names = [resource['name'] for resource in ckan_resources]

    # Find the files that have not been transferred
    files_not_transferred = [file for file in de_file_names if file not in ckan_resource_names]

    # transfer the remaining files
    for file in files_not_transferred:
        file_metadata = de.get_all_metadata_file(file)
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
        print(f'Resource creation response: {response}')


if __name__ == '__main__':
    # Create a .txt script that will be used to log the output of the script
    file = open("migration_log.txt", "w")

    # Get the list of datasets in the discovery environment
    de_datasets = de.get_datasets()

    # Get the list of datasets in CKAN by group or organization
    # ckan_datasets = ckan.list_datasets(group='cyverse-curated')
    ckan_datasets = ckan.list_datasets(organization='cyverse')

    # Initialize a counter to keep track of the number of datasets processed
    count = 0

    # Iterate through each dataset in the discovery environment to see
    # if they exist in CKAN and whether they need to be updated
    for de_dataset in de_datasets:
        new_ckan_title = None
        if count == 205:
            print("Skipping #205: No metadata dataset\n")
            file.write("Skipping #205: No metadata dataset\n")
            count += 1
            continue
        else:
            # Get the metadata for the dataset in the discovery environment
            de_dataset_metadata = de.get_all_metadata_dataset(de_dataset)

            # Get the title of the dataset in the discovery environment
            de_dataset_title = get_title(de_dataset_metadata).strip()
            # print(f"Discovery Environment Dataset Title: {de_dataset_title}")

            # Iterate through each dataset in CKAN to see if the titles match
            for ckan_dataset in ckan_datasets:
                # pretty_print(ckan_dataset)
                # Get the title of the dataset in CKAN
                ckan_dataset_title = ckan_dataset['title'].strip()
                # print(f"CKAN Dataset Title: {ckan_dataset_title}")
                if de_dataset_title == ckan_dataset_title:
                    print(f"{count} - Matched: {de_dataset_title}")
                    file.write(f"{count} - Matched: {de_dataset_title}\n")

                    # Get the last modified date for the dataset in the discovery environment
                    last_modified_de = de_dataset_metadata['date_modified']

                    # Get the last modified date for the dataset in CKAN
                    for extra in ckan_dataset['extras']:
                        if extra['key'] == 'Date last modified in discovery environment':
                            last_modified_ckan = extra['value']

                    print(f"Last Modified DE: {last_modified_de}")
                    file.write(f"Last Modified DE: {last_modified_de}\n")
                    print(f"Last Modified CKAN: {last_modified_ckan}")
                    file.write(f"Last Modified CKAN: {last_modified_ckan}\n")

                    # If the dataset in the discovery environment has been modified update the dataset in CKAN
                    # by deleting the old dataset and creating a new one with the updated metadata and files
                    if last_modified_de != last_modified_ckan:
                        # Check if the last_modified date in CKAN is exactly 7 hours ahead
                        # of the last_modified date in DE because of timezone difference.
                        # If it is not, then rewrite the dataset in CKAN
                        if not (int(last_modified_ckan[11:13]) == int(last_modified_de[11:13]) + 7
                                and last_modified_ckan[14:] == last_modified_de[14:]):
                            ckan_dataset_id = ckan_dataset['id']
                            print("Rewriting")
                            file.write("Rewriting\n\n")
                            ckan.delete_dataset(ckan_dataset_id)
                            migrate_dataset_and_files(de_dataset_metadata, new_ckan_title)
                    else:
                        print("\tNo Changes Made. Skipping...")
                        file.write("\tNo Changes Made. Skipping...\n")

                    # Break out of the loop if the dataset is found in CKAN
                    break

            # If the dataset does not exist in CKAN, create a new dataset
            else:
                print(f"{count} - Creating New Dataset in CKAN: {de_dataset_title}")
                file.write(f"{count} - Creating New Dataset in CKAN: {de_dataset_title}\n")
                migrate_dataset_and_files(de_dataset_metadata, new_ckan_title)
                print("Creation Complete.")
                file.write("Creation Complete.\n")

            print("\n")
            file.write("\n\n")
        count += 1

    file.close()

    # migrate_dataset_and_files(de.get_all_metadata_dataset(de_datasets[18]))
