import requests
import json

# CKAN instance URL
ckan_url = 'https://ckan.cyverse.rocks/'

# API Key (you need to generate this in your CKAN instance)
api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJid0tfcVU5YUdlQkxScTNuWDRZbkdfRzctRk90bUdzeDh0ZzVwM19GUWJRIiwiaWF0IjoxNzE4MDg0NDcwfQ.f1Zp-LlzrhkqBvBh-bjm7hE0oOJiXKzRutFFjg6ykfo'

url = f'{ckan_url}/api/3/action/organization_list'
headers = {'Authorization': api_key}

response = requests.get(url, headers=headers)
organizations = response.json()

print(organizations)


def create_dataset(data):
    """
    Create a new dataset in CKAN.

    This function sends a POST request to the CKAN API to create a new dataset with the provided metadata.
    The dataset metadata should include information such as name, title, description, owner organization,
    and any additional metadata fields.

    Args:
        data (dict): The dataset metadata dictionary, including keys like 'name', 'title', 'description',
                     'owner_org', and any additional metadata.

    Returns:
        dict: The response from the CKAN API, typically containing the dataset metadata.
    """
    url = f'{ckan_url}/api/3/action/package_create'  # API endpoint for creating a dataset
    headers = {
        'Authorization': api_key,  # API key for authorization
        'Content-Type': 'application/json'  # Content type for the request
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))  # Send POST request to create dataset
    return response.json()  # Return the JSON response from the API


def upload_resource(dataset_id, file_path, name, date_created, date_updated, description=None):
    """
    Upload a resource (file) to a CKAN dataset.

    This function uploads a file to a specified CKAN dataset by sending a POST request to the CKAN API.
    The function attaches the file and metadata such as the resource name and description.

    Args:
        dataset_id (str): The ID of the dataset to add the resource to.
        file_path (str): The local path to the file to upload.
        name (str): The name of the resource.
        description (str, optional): A brief description of the resource.
        date_created (str): The date the resource was created.
        date_updated (str): The date the resource was last updated.

    Returns:
        dict: The response from the CKAN API, typically containing the resource metadata.
    """
    url = f'{ckan_url}/api/3/action/resource_create'  # API endpoint for creating a resource
    headers = {
        'Authorization': api_key  # API key for authorization
    }
    data = {
        'package_id': dataset_id,  # ID of the dataset to add the resource to
        'name': name,  # Name of the resource
        'description': description,  # Description of the resource
        'date_created_de': date_created,  # Date the resource was created
        'date_updated_de': date_updated  # Date the resource was last updated
    }
    files = {
        'upload': open(file_path, 'rb')  # File to upload
    }
    response = requests.post(url, headers=headers, data=data, files=files)  # Send POST request to upload resource
    return response.json()  # Return the JSON response from the API


def add_resource_link(data):
    """
    Add a link to a resource in a CKAN dataset.

    This function adds a URL link to a specified CKAN dataset by sending a POST request to the CKAN API.
    This is the primary way that resources are added to CKAN datasets from the discovery environment.
    The resource metadata should include the dataset ID, URL, name, description, format, and relevant dates.

    Args:
        data (dict): The resource metadata dictionary, including keys like 'package_id', 'name', 'url',
                     'description', 'format', and relevant dates.

    Returns:
        dict: The response from the CKAN API, typically containing the resource metadata.
    """
    resource_url = f'{ckan_url}/api/3/action/resource_create'  # API endpoint for creating a resource
    headers = {
        'Authorization': api_key  # API key for authorization
    }
    # data = {
    #     'package_id': dataset_id,
    #     'name': name,
    #     'description': description,
    #     'url': url,
    #     'format': format,  # or any other format that your link represents
    #     'Date Created in Discovery Environment': date_created_de,
    #     'Date Last Modified in Discovery Environment': date_modified_de
    # }
    response = requests.post(resource_url, headers=headers, json=data)  # Send POST request to add resource link
    return response.json()  # Return the JSON response from the API


def get_dataset_id(dataset_name):
    """
    Get the dataset ID for a given dataset name in CKAN.

    This function retrieves the ID of a dataset by its name. It sends a GET request to the CKAN API
    to fetch the dataset metadata and extract the dataset ID.

    Args:
        dataset_name (str): The name of the dataset.

    Returns:
        str: The dataset ID if found, or None if the dataset does not exist.
    """
    dataset_name = dataset_name.lower().replace(' ', '-').replace('.', '-')  # Format dataset name to match CKAN conventions
    url = f'{ckan_url}/api/3/action/package_show'  # API endpoint for showing dataset details
    headers = {'Authorization': api_key}  # API key for authorization
    params = {'id': dataset_name}  # Parameters for the GET request
    response = requests.get(url, headers=headers, params=params)  # Send GET request to retrieve dataset details
    if response.status_code == 200:
        dataset_metadata = response.json()  # Parse the JSON response
        if dataset_metadata['success']:
            return dataset_metadata['result']['id']  # Return dataset ID if found
        else:
            print(f"Error: {dataset_metadata['error']['message']}")  # Print error message if not successful
            return None
    elif response.status_code == 404:
        print(f"Dataset '{dataset_name}' not found.")  # Print message if dataset not found
        return None
    else:
        print(f"An error occurred: {response.status_code} - {response.text}")  # Print error message for other errors
        return None


def get_dataset_info(dataset_id):
    """
    Get detailed information about a specific dataset in CKAN.

    This function retrieves detailed metadata for a specified dataset by sending a GET request to the CKAN API.
    It is used to fetch information such as the dataset title, description, tags, resources, and other metadata.

    Args:
        dataset_id (str): The ID of the dataset to retrieve information about.

    Returns:
        dict: The response from the CKAN API, containing the dataset metadata.
    """
    url = f'{ckan_url}/api/3/action/package_show'  # API endpoint for showing dataset details
    headers = {'Authorization': api_key}  # API key for authorization
    params = {'id': dataset_id}  # Parameters for the GET request
    response = requests.get(url, headers=headers, params=params)  # Send GET request to retrieve dataset details
    return response.json()  # Return the JSON response from the API


def list_datasets(organization=None, group=None):
    """
    List all datasets in the CKAN instance for a specific organization and/or group.

    This function retrieves a list of all datasets in the CKAN instance, filtered by organization
    or group if specified. It sends a GET request to the CKAN API and returns the dataset metadata.
    This is used in the migration process to check whether a dataset from the discovery environment already exists in CKAN.

    Args:
        organization (str, optional): The name or ID of the organization.
        group (str, optional): The name or ID of the group.

    Returns:
        dict: The response from the CKAN API, containing a list of dataset IDs.
    """
    url = f'{ckan_url}/api/3/action/package_list'  # API endpoint for listing datasets
    headers = {'Authorization': api_key}  # API key for authorization
    output = []

    if organization is not None:
        # If an organization is specified, get the list of datasets for that organization
        url = f'{ckan_url}/api/3/action/organization_show'
        response = requests.get(url, headers=headers, params={'id': organization, 'include_datasets': True})
        response = response.json()
        response = response['result']['packages']
        for dataset in response:
            output.append(get_dataset_info(dataset['id']))
        return output

    elif group is not None:
        # If a group is specified, get the list of datasets for that group
        url = f'{ckan_url}/api/3/action/group_show'
        response = requests.get(url, headers=headers, params={'id': group, 'include_datasets': True})
        response = response.json()
        response = response['result']['packages']
        for dataset in response:
            output.append(get_dataset_info(dataset['id']))
        return output

    else:
        # If neither an organization nor a group is specified, get the list of all datasets
        response = requests.get(url, headers=headers)
        return response.json()


def delete_dataset(dataset_id):
    """
    Delete a dataset in CKAN.

    This function deletes a specified dataset by sending a POST request to the CKAN API.
    This is used in the migration script when a dataset needs to be updated or replaced.

    Args:
        dataset_id (str): The ID of the dataset to delete.

    Returns:
        dict: The response from the CKAN API.
    """
    url = f'{ckan_url}/api/3/action/package_delete'  # API endpoint for deleting a dataset
    headers = {
        'Authorization': api_key,  # API key for authorization
        'Content-Type': 'application/json'  # Content type for the request
    }
    data = {
        'id': dataset_id  # ID of the dataset to delete
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))  # Send POST request to delete dataset
    return response.json()  # Return the JSON response from the API



def delete_all_datasets_in_organization(organization):
    """
    Delete all datasets in a specific organization in CKAN.

    This function deletes all datasets belonging to a specified organization by first listing all datasets
    in the organization and then sending a delete request for each dataset.
    This can be used to clean up existing datasets before migrating new data.

    Args:
        organization (str): The name or ID of the organization.

    Returns:
        None
    """
    datasets = list_datasets(organization=organization)  # List all datasets in the organization
    for dataset in datasets:
        dataset_id = dataset['result']['id']  # Get the dataset ID
        delete_response = delete_dataset(dataset_id)  # Delete the dataset
        print(f'Deleted dataset with ID: {dataset_id}. Response: {delete_response}')  # Print confirmation message



def pretty_print(json_data):
    """
    Format and print JSON data in a readable way.

    This function formats JSON data with indentation and sorted keys to make it more readable
    when printed to the console.

    Args:
        json_data (dict): JSON data to be pretty-printed.
    """
    print(json.dumps(json_data, indent=4, sort_keys=True))


if __name__ == '__main__':
    # pass
    # List all datasets
    # datasets = list_datasets()
    # print(datasets)



    # # Create a new dataset
    extras = [{'key': 'Citation', 'value': 'John Doe (2024). My Dataset. CyVerse Data Commons. DOI 10.12345/abcde'}, {'key': 'DOI', 'value': '10.12345/abcde'}, {'key': 'Publication Year', 'value': '2024'}, {'key': 'Publisher', 'value': 'CyVerse Data Commons'}, {'key': 'resourceType', 'value': 'Example Dataset'}]
    data = {
        'name': 'test_cyverse_dataset',
        'title': 'My Dataset4',
        'notes': 'This is a test dataset',
        # 'owner_org': 'tanmay-s-playground',
        'owner_org': 'cyverse',
        'private': False,
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
        'author': ['John Doe', 'Jane DOe'],
        # "license_id": "notspecified",
        # "license_title": "License not specified",
        # 'author_email': 'john.doe@example.com',
        'tags': [{'name': 'example'}, {'name': 'dataset'}],
        'extras': extras
    }
    dataset_response = create_dataset(data)
    print(f'Dataset creation response: {dataset_response}')


    #
    # # Upload a resource to the new dataset
    # dataset_id = dataset_response['result']['id']
    # file_path = r'C:\Users\tdewa\KEYS2024 Project\CKAN_Testing\testData.csv'
    # resource_response = upload_resource(dataset_id, file_path)
    # print(f'Resource upload response: {resource_response}')



    # # Get the dataset ID for a given dataset name
    # dataset_name = 'ODC PDDL License Testing'
    # dataset_id = get_dataset_id(dataset_name)
    # print(dataset_id)
    # #
    # # upload_resource(dataset_id, r'C:\Users\tdewa\KEYS2024 Project\CKAN_Testing\testData.csv', 'Test Data with dates', 'This is a test resource for testing dates')
    # add_resource_link(dataset_id, 'https://data.cyverse.org/dav-anon/iplant/home/tedgin/public/bms/data-store-fix', 'Test data with dates and url', '', 'Aug 2, 2016 2:36:59 AM', 'Aug 2, 2016 11:52:15 AM', 'This is a test resource for testing dates and url')
    # pretty_print(get_dataset_info(dataset_id))



    # dataset_name = 'U-Nottm_2016_RIPRleaf_images'
    # dataset_id = get_dataset_id(dataset_name)
    # pretty_print(get_dataset_info(dataset_id))





    # {'help': 'https://ckan.cyverse.rocks:443/api/3/action/help_show?name=package_show', 'success': True,
    #  'result': {'author': 'Harel Bacher', 'author_email': '', 'creator_user_id': 'a09d247c-d8ce-4192-8b74-096ebfdc7b48',
    #             'id': '9f952b8d-4865-4aa9-ae94-960ce42d938b', 'isopen': True, 'license_id': 'odc-pddl',
    #             'license_title': 'Open Data Commons Public Domain Dedication and License (PDDL)',
    #             'license_url': 'http://www.opendefinition.org/licenses/odc-pddl', 'maintainer': '',
    #             'maintainer_email': '', 'metadata_created': '2024-06-11T20:41:40.579265',
    #             'metadata_modified': '2024-06-11T20:58:08.112055', 'name': 'wheat_drought-stress-phenomics',
    #             'notes': 'Svevo*Zavitan introgression lines is a sequenced what population harbours wild alleles from the wild emmer wheat (Zavitan) on the genetic background of an elite durum line (Svevo). We screen this population for water stress tolerance and analyzed the image data with PhenoImage GUI software was used for image processing (Zhu et al., 2020). We extracted the key morphological traits derived from RGB images included PSA, plant height and width, plant architecture (convex area), plant density, and water-use efficiency (WUE) on the final day of the experiment. Plant height and plant width were calculated from plant dimensions. Plant architecture (convex area) was calculated to predict plant architecture trajectory. Density was calculated based on the ratio between pixel sum and plant architecture. The relative growth rate (RGR) was calculated by dividing daily pixel accumulation with pixel numbers from the previous day. Daily water-use efficiency (WUEt) was calculated as described by Momen et al. (2019), where (t) represents the day.\r\n',
    #             'num_resources': 2, 'num_tags': 3,
    #             'organization': {'id': '98d859a6-c7b8-4021-baec-9158179a0d2c', 'name': 'cyverse', 'title': 'CyVerse',
    #                              'type': 'organization', 'description': '',
    #                              'image_url': 'https://cyverse.org/sites/default/files/cyverse_logo_1_0.png',
    #                              'created': '2024-06-06T09:22:24.851542', 'is_organization': True,
    #                              'approval_status': 'approved', 'state': 'active'},
    #             'owner_org': '98d859a6-c7b8-4021-baec-9158179a0d2c', 'private': False, 'state': 'active',
    #             'title': 'Wheat_drought stress phenomics', 'type': 'dataset', 'url': '', 'version': '', 'extras': [
    #          {'key': 'Citation',
    #           'value': 'Harel Bacher (2021). Wheat_drought stress phenomics. CyVerse Data Commons. DOI 10.25739/eztp-dj42'},
    #          {'key': 'DOI', 'value': '10.25739/eztp-dj42'}, {'key': 'Publication Year', 'value': '2021'},
    #          {'key': 'Publisher', 'value': 'CyVerse Data Commons'},
    #          {'key': 'resourceType', 'value': 'Wheat phenomics drought tolerance'}], 'resources': [
    #          {'cache_last_updated': None, 'cache_url': None, 'created': '2024-06-11T20:42:35.512658',
    #           'datastore_active': True, 'description': '', 'format': 'CSV', 'hash': '',
    #           'id': 'f040178b-9a9e-422b-9a8a-568346370cc3', 'last_modified': '2024-06-11T20:42:35.478639',
    #           'metadata_modified': '2024-06-11T20:42:35.508082', 'mimetype': 'text/csv', 'mimetype_inner': None,
    #           'name': 'Metadata.csv', 'package_id': '9f952b8d-4865-4aa9-ae94-960ce42d938b', 'position': 0,
    #           'resource_type': None, 'size': 1368, 'state': 'active',
    #           'url': 'https://ckan.cyverse.rocks:443/dataset/9f952b8d-4865-4aa9-ae94-960ce42d938b/resource/f040178b-9a9e-422b-9a8a-568346370cc3/download/metadata.csv',
    #           'url_type': 'upload'},
    #          {'cache_last_updated': None, 'cache_url': None, 'created': '2024-06-11T20:44:04.770456',
    #           'datastore_active': False, 'description': '', 'format': 'TXT', 'hash': '',
    #           'id': '6273b3c3-4f09-40c7-baba-eb802eeebfe5', 'last_modified': '2024-06-11T20:44:04.732241',
    #           'metadata_modified': '2024-06-11T20:44:05.117585', 'mimetype': 'text/plain', 'mimetype_inner': None,
    #           'name': 'ReadMe.txt', 'package_id': '9f952b8d-4865-4aa9-ae94-960ce42d938b', 'position': 1,
    #           'resource_type': None, 'size': 3729, 'state': 'active',
    #           'url': 'https://ckan.cyverse.rocks:443/dataset/9f952b8d-4865-4aa9-ae94-960ce42d938b/resource/6273b3c3-4f09-40c7-baba-eb802eeebfe5/download/readme.txt',
    #           'url_type': 'upload'}], 'tags': [
    #          {'display_name': 'Wheat wild introgression lines', 'id': '518127ea-2041-48d8-956f-c75ce4a068c9',
    #           'name': 'Wheat wild introgression lines', 'state': 'active', 'vocabulary_id': None},
    #          {'display_name': 'wheat phenomics', 'id': '08d517b6-f78c-40fd-a416-3d0ab883f505',
    #           'name': 'wheat phenomics', 'state': 'active', 'vocabulary_id': None},
    #          {'display_name': 'wheat water stress tolerance', 'id': '43bb9759-10f4-4376-b9df-52e0bd164c6a',
    #           'name': 'wheat water stress tolerance', 'state': 'active', 'vocabulary_id': None}], 'groups': [],
    #             'relationships_as_subject': [], 'relationships_as_object': []}}
