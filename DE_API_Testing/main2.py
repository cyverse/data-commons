import requests
import json
from datetime import datetime

# Base URL for the Discovery Environment API
base_url = 'https://de.cyverse.org/terrain'

# API Key (replace with your actual API key)
api_key = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUMUdaWW9IRzJYVUc0NG5NRFpQc3d3V3QzZ0xWUElmcEl2Qm82VGxVQmUwIn0.eyJleHAiOjE3MTgzMjU1ODcsImlhdCI6MTcxODI5Njc4NywianRpIjoiOGNlODU1ZTAtOWJjMi00NjdlLWJiNzctMzJiMzFlNzBjNTA2IiwiaXNzIjoiaHR0cHM6Ly9rYy5jeXZlcnNlLm9yZy9hdXRoL3JlYWxtcy9DeVZlcnNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5YjM5YTMxLTQzMmQtNDRiMi1iYzMzLTEyOTY4NTUxMzE4ZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImRlLXByb2QiLCJzZXNzaW9uX3N0YXRlIjoiMTI1N2RlMTAtM2ZmOS00MjhhLTk5ZGItOGNkOTAwNTQxODA3IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2RlLmN5dmVyc2Uub3JnIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsIm9mZmxpbmVfYWNjZXNzIiwiaXBsYW50LWV2ZXJ5b25lIiwidW1hX2F1dGhvcml6YXRpb24iLCJjb21tdW5pdHkiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJUYW5tYXkgRGV3YW5nYW4iLCJlbnRpdGxlbWVudCI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsImlwbGFudC1ldmVyeW9uZSIsImNvbW11bml0eSJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0ZGV3YW5nYW4iLCJnaXZlbl9uYW1lIjoiVGFubWF5IiwiZmFtaWx5X25hbWUiOiJEZXdhbmdhbiIsImVtYWlsIjoidGRld2FuZ2FuQGFyaXpvbmEuZWR1In0.Ow6r5RnY9DIFkaSSbfscUmXi22F_YlQpbSFZLwL29vII8Zj7Sxy3Ouq-LK3WVlpM1iG7Azifm0QNvF7gt9S3uCDY4n2GFgdBFMtIvqCcuxayyc4lGUW3fjP99v7DuI1pR_mdA1A5WZAjVwPdycAfZiaRa3hw_QjSg4dfkSEg-LVoYWNO9SoIUsr0ycTaLO7HQWkKYi1oI4s3mrQ7PHlieq0PNJl6HDx5frf9KCTW3at9ib4KdmW3qey5GigZzqy4k3NExLScLmKewRO0Li1_AwapJ2TdH54O1J5BBGBo304Al1ATLmeZyb93he7wR-XfPTXZoJdFLdCKMBJcA4jTnA'
# Headers for the requests
headers = {
    'Authorization': api_key
}


# Function to format JSON responses
def pretty_print(json_data):
    print(json.dumps(json_data, indent=4, sort_keys=True))


# Get a list of all the datasets with their metadata
def get_datasets():
    path = '/iplant/home/shared/commons_repo/curated/'
    url = f'{base_url}/secured/filesystem/directory'
    params = {'path': path}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        directories = response.json()
        datasets = directories['folders'] # This variable is now a list of dictionaries where each dictionary represents a single dataset
        # get_all_metadata(datasets[0])

        # PRINT THE TITLE AND IDENTIFIER OF EACH DATASET
        # all_identifiers = []
        #
        # for dataset in datasets:
        #     metadata: dict = get_all_metadata(dataset)
        #     try:
        #         print(metadata['title'], ": ", metadata['identifier'])
        #         all_identifiers.append(metadata['identifier'])
        #     except KeyError:
        #         try:
        #             print(metadata['title'], ": ", "No identifier found")
        #             all_identifiers.append("No identifier found")
        #         except KeyError:
        #             print("No title found")
        #             all_identifiers.append("No title found")
        #     pretty_print_json(metadata)
        #
        #     print("\n")
        #
        # print("\n")
        # print("All identifiers:")
        # for identifier in all_identifiers:
        #     print(identifier)





        # # Print the title of each dataset
        # for dataset in datasets:
        #     print(dataset['label'])

        for dataset in datasets:
            metadata: dict = get_all_metadata_dataset(dataset)
            pretty_print(metadata)
            print("\n")

        return datasets
    else:
        print(f"Error getting directories: {response.status_code} - {response.text}")
        return None

# Get the list of files in a specified directory
def get_list_of_files(path, limit=10):
    url = f'{base_url}/secured/filesystem/paged-directory'
    params = {'limit': limit, 'path': path}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        files = response.json()
        print("List of files:")
        pretty_print(files)
        return files
    else:
        print(f"Error getting files: {response.status_code} - {response.text}")
        return None


# Get metadata for a specific data ID
def get_metadata(data_id):
    url = f'{base_url}/filesystem/{data_id}/metadata'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        print(f"Error getting metadata: {response.status_code} - {response.text}")
        return None

def convert_to_date(milliseconds):
    seconds = milliseconds / 1000
    date_obj = datetime.fromtimestamp(seconds)
    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return date_str

def get_all_metadata_dataset(dataset: dict):
    metadata_dict = {}

    date_created = convert_to_date(int(dataset['date-created']))
    metadata_dict['date_created'] = date_created

    date_modified = convert_to_date(int(dataset['date-modified']))
    metadata_dict['date_modified'] = date_modified

    metadata_dict['de_path'] = dataset['path']

    dataset_id = dataset['id']

    metadata_return = get_metadata(dataset_id)
    # pretty_print_json(metadata_return)
    avus: list = metadata_return['avus']

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

    # pretty_print_json(metadata_dict)
    return metadata_dict


def get_all_metadata_file(file: dict):
    metadata_dict = {}

    date_created = convert_to_date(int(file['date-created']))
    metadata_dict['date_created'] = date_created

    date_modified = convert_to_date(int(file['date-modified']))
    metadata_dict['date_modified'] = date_modified

    metadata_dict['de_path'] = file['path']

    file_name = file['label']
    metadata_dict['file_name'] = file_name

    # Get the file type from the label
    file_type = file_name.split('.')[-1]
    metadata_dict['file_type'] = file_type

    web_dav_location = "https://data.cyverse.org/dav-anon/iplant/commons/cyverse_curated/" + file['path'].replace('/iplant/home/shared/commons_repo/curated/', '')
    metadata_dict['web_dav_location'] = web_dav_location

    # pretty_print_json(metadata_dict)
    return metadata_dict


# Example usage
if __name__ == '__main__':
    # Example paths (replace with your actual paths and data IDs)
    file_directory_path = '/iplant/home/shared/commons_repo/curated/Carolyn_Lawrence_Dill_GOMAP_Banana_NCBI_ASM31385v2_February_2021.r1/0_GOMAP-input'
    sample_data_id = '78bda920-691e-11ea-910c-90e2ba675364'  # Sample ID for a dataset

    # Get list of datasets
    get_datasets()


    # Get list of files
    # files = get_list_of_files(file_directory_path)
    # for file in files['files']:
    #     metadata: dict = get_all_metadata_file(file)
    #     pretty_print(metadata)
    #     print("\n")

    # Get metadata for a specific data ID
    # Returns a dictionary with keys of "avus", "irods-avus", and "path"
    # "avus" has a value of a list of dictionaries
    # get_metadata(sample_data_id)
