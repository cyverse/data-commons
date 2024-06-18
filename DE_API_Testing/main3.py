import requests
import json
from datetime import datetime

# Base URL for the Discovery Environment API
base_url = 'https://de.cyverse.org/terrain'

# API Key (replace with your actual API key)
api_key = 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUMUdaWW9IRzJYVUc0NG5NRFpQc3d3V3QzZ0xWUElmcEl2Qm82VGxVQmUwIn0.eyJleHAiOjE3MTg2NzcwOTMsImlhdCI6MTcxODY0ODI5MywianRpIjoiNjRjMDkwZjktZGM4NS00MDc2LWExNzktYTZkNmMxOTRlNmNkIiwiaXNzIjoiaHR0cHM6Ly9rYy5jeXZlcnNlLm9yZy9hdXRoL3JlYWxtcy9DeVZlcnNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5YjM5YTMxLTQzMmQtNDRiMi1iYzMzLTEyOTY4NTUxMzE4ZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImRlLXByb2QiLCJzZXNzaW9uX3N0YXRlIjoiZGQ2ZjE2NWUtNTRjNi00ZGJjLWFkMzUtNzg1OWI1ZDdjMjdiIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2RlLmN5dmVyc2Uub3JnIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsIm9mZmxpbmVfYWNjZXNzIiwiaXBsYW50LWV2ZXJ5b25lIiwidW1hX2F1dGhvcml6YXRpb24iLCJjb21tdW5pdHkiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJUYW5tYXkgRGV3YW5nYW4iLCJlbnRpdGxlbWVudCI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsImlwbGFudC1ldmVyeW9uZSIsImNvbW11bml0eSJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0ZGV3YW5nYW4iLCJnaXZlbl9uYW1lIjoiVGFubWF5IiwiZmFtaWx5X25hbWUiOiJEZXdhbmdhbiIsImVtYWlsIjoidGRld2FuZ2FuQGFyaXpvbmEuZWR1In0.kGjtyfuGJ4aGZm_I7Cx5ORKjXltmgqpZx3UDALv2vTE8rAPQfdyhxnFCMViv42lIdSOKb9T8zbgel8s1yt7LmQHgKm0qz5U2AphRXsBEkr0lDIejeYmHtXPKZtgLbeajY2o5Gl0J7anrgLsuyzgIkY1m11mO8S0_Y_Fyo0y2bJSdKYMt5nl8VHkf84TNM31oCWMhBhHCtlL5t65VoXCPC_CXqRmvsAREiw3GFl1OT6up_kZH-p9keqSY4X9vT0LqeMLSuLBPL_N02eRVnL_qt2spQuV1nMPOFd7MJsntxXirgdiAj_AdwONFQrS-xipmMMcQhzYXm7RedTH-hF26Tg'
# Headers for the requests
headers = {
    'Authorization': api_key
}

def pretty_print(json_data):
    """
    Format and print JSON data in a readable way.

    This function takes JSON data and prints it in a formatted, easy-to-read manner.
    Useful for debugging and ensuring the correct data structure is being used.

    Args:
        json_data (dict): JSON data to be pretty-printed.
    """
    print(json.dumps(json_data, indent=4, sort_keys=True))

def convert_to_date(milliseconds):
    """
    Convert milliseconds since epoch to a human-readable date and time.

    This function converts a timestamp in milliseconds to a human-readable date and time string.
    This is used to convert the milliseconds since epoch of the date created and date updated fields to a more readable format

    Args:
        milliseconds (int): Milliseconds since epoch.

    Returns:
        str: Human-readable date and time.
    """
    seconds = milliseconds / 1000  # Convert milliseconds to seconds
    date_obj = datetime.fromtimestamp(seconds)  # Create a datetime object from the timestamp
    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')  # Format the datetime object as a string
    return date_str

def get_metadata(data_id):
    """
    Get metadata for a specific data ID.

    This function retrieves metadata for a specified dataset by its ID.
    It sends a GET request to the Discovery Environment API.

    Args:
        data_id (str): The ID of the data item.

    Returns:
        dict: The metadata for the specified data ID.
    """
    url = f'{base_url}/filesystem/{data_id}/metadata'  # Construct the API URL for the metadata endpoint
    response = requests.get(url, headers=headers)  # Send a GET request to the API
    if response.status_code == 200:
        metadata = response.json()  # Parse the JSON response
        return metadata
    else:
        print(f"Error getting metadata: {response.status_code} - {response.text}")  # Print error message if the request fails
        return None

def get_all_metadata_dataset(dataset):
    """
    Get all metadata for a dataset.

    This function collects all metadata for a given dataset, including creation and modification dates,
    and detailed attributes from the Discovery Environment API. Used to migrate the datasets and their metadata
    to CKAN.

    Args:
        dataset (dict): The dataset dictionary.

    Returns:
        dict: A dictionary containing all metadata for the dataset.
    """
    metadata_dict = {}

    # Convert and store creation and modification dates
    date_created = convert_to_date(int(dataset['date-created']))  # Convert creation date to readable format
    metadata_dict['date_created'] = date_created

    date_modified = convert_to_date(int(dataset['date-modified']))  # Convert modification date to readable format
    metadata_dict['date_modified'] = date_modified

    metadata_dict['de_path'] = dataset['path']  # Store the dataset path

    dataset_id = dataset['id']  # Get the dataset ID

    # Get detailed metadata from the API
    metadata_return = get_metadata(dataset_id)
    avus = metadata_return['avus']  # Get attribute-value units (AVUs)

    # Loop through each AVU and add it to the metadata dictionary
    for avu in avus:
        key = avu['attr']
        value = avu['value']
        if key in metadata_dict:
            try:
                metadata_dict[key].append(value)
            except AttributeError:
                metadata_dict[key] = [metadata_dict[key], value]
        else:
            metadata_dict[key] = value

    return metadata_dict

def get_all_metadata_file(file):
    """
    Get metadata for a specific file.

    This function collects all metadata for a given file, including creation and modification dates,
    file type, and WebDAV location. Used for migrating files to CKAN.

    Args:
        file (dict): The file dictionary.

    Returns:
        dict: A dictionary containing all metadata for the file.
    """
    metadata_dict = {}

    # Convert and store creation and modification dates
    date_created = convert_to_date(int(file['date-created']))  # Convert creation date to readable format
    metadata_dict['date_created'] = date_created

    date_modified = convert_to_date(int(file['date-modified']))  # Convert modification date to readable format
    metadata_dict['date_modified'] = date_modified

    metadata_dict['de_path'] = file['path']  # Store the file path

    file_name = file['label']  # Get the file name
    metadata_dict['file_name'] = file_name

    # Get the file type from the label
    file_type = file_name.split('.')[-1]
    if file_type == file_name:
        file_type = ''
    metadata_dict['file_type'] = file_type

    # Construct the WebDAV location URL
    web_dav_location = "https://data.cyverse.org/dav-anon/iplant/commons/cyverse_curated/" + file['path'].replace('/iplant/home/shared/commons_repo/curated/', '')
    metadata_dict['web_dav_location'] = web_dav_location

    return metadata_dict


def get_files(path, limit=10):
    """
    Get the list of files in a specified directory.

    This function retrieves a list of files in a specified directory from the Discovery Environment API.
    Useful for migrating files from a directory to CKAN.

    Args:
        path (str): The path to the directory.
        limit (int): The maximum number of files to retrieve.

    Returns:
        dict: A dictionary containing the list of files.
    """
    url = f'{base_url}/secured/filesystem/paged-directory'  # Construct the API URL for the directory endpoint
    params = {'limit': limit, 'path': path}  # Set the request parameters
    response = requests.get(url, headers=headers, params=params)  # Send a GET request to the API
    if response.status_code == 200:
        files = response.json()  # Parse the JSON response
        return files
    else:
        print(f"Error getting files: {response.status_code} - {response.text}")  # Print error message if the request fails
        return None

def get_datasets():
    """
    Get a list of all datasets with some of their metadata. The rest of the metadata can be retrieved using the get_metadata function.

    This function retrieves a list of all datasets in a specified path from the Discovery Environment API.
    Used in conjunction with get_all_metadata_dataset function to migrate datasets and their metadata
    to CKAN.

    Args:
        None

    Returns:
        list: A list of dictionaries, each representing a dataset with its metadata.
    """
    path = '/iplant/home/shared/commons_repo/curated/'  # Define the path to the datasets
    url = f'{base_url}/secured/filesystem/directory'  # Construct the API URL for the directory endpoint
    params = {'path': path}  # Set the request parameters
    response = requests.get(url, headers=headers, params=params)  # Send a GET request to the API
    if response.status_code == 200:
        directories = response.json()  # Parse the JSON response
        datasets = directories['folders']  # Extract the list of datasets
        return datasets
    else:
        print(f"Error getting directories: {response.status_code} - {response.text}")  # Print error message if the request fails
        return None


if __name__ == '__main__':
    file_directory_path = '/iplant/home/shared/commons_repo/curated/Carolyn_Lawrence_Dill_GOMAP_Banana_NCBI_ASM31385v2_February_2021.r1/0_GOMAP-input'

    # get_files(file_directory_path)
    datasets = get_datasets()
    # print(datasets)

    # for dataset in datasets:
    #     dataset_metadata = get_all_metadata_dataset(dataset)
    #     pretty_print(dataset_metadata)

    pretty_print(get_all_metadata_dataset((datasets[18])))

    get_all_metadata_file(get_files(get_all_metadata_dataset((datasets[18]))['de_path'])['folders'][0])
