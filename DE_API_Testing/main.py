import requests
import json
from datetime import datetime

# Base URL for the Discovery Environment API
base_url = 'https://de.cyverse.org/terrain'

# API Key (replace with your actual API key)
api_key = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUMUdaWW9IRzJYVUc0NG5NRFpQc3d3V3QzZ0xWUElmcEl2Qm82VGxVQmUwIn0.eyJleHAiOjE3MTg0MTgxMDUsImlhdCI6MTcxODM4OTMwNSwianRpIjoiNjExZjFjOWMtYjc1Zi00Y2I1LTkwOTktMmI5MjQxOWY3MjhjIiwiaXNzIjoiaHR0cHM6Ly9rYy5jeXZlcnNlLm9yZy9hdXRoL3JlYWxtcy9DeVZlcnNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijg5YjM5YTMxLTQzMmQtNDRiMi1iYzMzLTEyOTY4NTUxMzE4ZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImRlLXByb2QiLCJzZXNzaW9uX3N0YXRlIjoiZDY0OTM4NTQtN2Y1YS00YWM0LWFlYmUtMGRlMWFkZTQ5NTQ2IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2RlLmN5dmVyc2Uub3JnIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsIm9mZmxpbmVfYWNjZXNzIiwiaXBsYW50LWV2ZXJ5b25lIiwidW1hX2F1dGhvcml6YXRpb24iLCJjb21tdW5pdHkiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJUYW5tYXkgRGV3YW5nYW4iLCJlbnRpdGxlbWVudCI6WyJkZS1wcmV2aWV3LWFjY2VzcyIsImlwbGFudC1ldmVyeW9uZSIsImNvbW11bml0eSJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0ZGV3YW5nYW4iLCJnaXZlbl9uYW1lIjoiVGFubWF5IiwiZmFtaWx5X25hbWUiOiJEZXdhbmdhbiIsImVtYWlsIjoidGRld2FuZ2FuQGFyaXpvbmEuZWR1In0.b6QrzRd5yo3lipbVm9q1K7ZQn9ZWfRxGjU-9eRHcSJtwBqTmm-3e90Omxt7Rmo_XdLnlBFgGF4yl-am7q0EBJpZg9Fe8zlYuihT32vyhpJbUKpQMeIcqXQKGW3Qs4Tg1Rng2X5OWXFZ5e_5htPHZXPUN2qkFSwS3qsLb288qbRdVwbeTi0ncUFXqY_MfpVUpSrGHAQiFSRsSbetJnc-ZQZOOVZo1tb_MdCrikulundBqkWPrqhCZObBtGjYA2vlK6I05G0-dv98Q_N6JYNpaE7FbamlZHmR_VfV1ZGOergyhjaEtfshUANDJG5DJQPOZh7OjWcfM3L86jDQs8F6g4A'

# Headers for the requests
headers = {
    'Authorization': api_key
}

# Function to pretty-print JSON responses
def pretty_print_json(json_data):
    print(json.dumps(json_data, indent=4, sort_keys=True))

# Step 1: Get the list of directories in a specified path
def get_datasets():
    path = '/iplant/home/shared/commons_repo/curated/'
    url = f'{base_url}/secured/filesystem/directory'
    params = {'path': path}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        directories = response.json()
        datasets = directories['folders'] # This variable is now a list of dictionaries where each dictionary represents a single dataset
        # get_all_metadata(datasets[0])

        all_identifiers = []

        file = open("metadata_output1.txt", "w")

        for dataset in datasets:
            metadata: dict = get_all_metadata(dataset)
            try:
                print(metadata['title'], ": ", metadata['identifier'])
                try:
                    file.write(metadata['title'] + ": " + metadata['identifier'] + "\n")
                except TypeError:
                    # This means the identifier is a list
                    try:
                        file.write(metadata['title'] + ": " + metadata['identifier'][0] + "\n")
                    except TypeError:
                        file.write(metadata['title'][0] + ": " + metadata['identifier'][0] + "\n")


                all_identifiers.append(metadata['identifier'])
            except KeyError:
                try:
                    print(metadata['title'], ": ", "No identifier found")
                    file.write(metadata['title'] + ": " + "No identifier found" + "\n")
                    all_identifiers.append("No identifier found")
                except KeyError:
                    print("No title found")
                    file.write("No title found" + "\n")
                    all_identifiers.append("No title found")
            pretty_print_json(metadata)
            file.write(json.dumps(metadata, indent=4, sort_keys=True) + "\n")

            print("\n")

        print("\n")
        print("All identifiers:")
        file.write("\nAll identifiers:\n")
        for identifier in all_identifiers:
            print(identifier)
            try:
                file.write(identifier + "\n")
            except TypeError:
                file.write(identifier[0] + "\n")


        file.close()




        # # Print the title of each dataset
        # for dataset in datasets:
        #     print(dataset['label'])

        return datasets
    else:
        print(f"Error getting directories: {response.status_code} - {response.text}")
        return None

# Step 2: Get the list of files in a specified directory
def get_list_of_files(path, limit=10):
    url = f'{base_url}/secured/filesystem/paged-directory'
    params = {'limit': limit, 'path': path}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        files = response.json()
        print("List of files:")
        pretty_print_json(files)
        return files
    else:
        print(f"Error getting files: {response.status_code} - {response.text}")
        return None

# Step 3: Get metadata for a specific data ID
def get_metadata(data_id):
    url = f'{base_url}/filesystem/{data_id}/metadata'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metadata = response.json()
        # print("Metadata:")
        # pretty_print_json(metadata)
        return metadata
    else:
        print(f"Error getting metadata: {response.status_code} - {response.text}")
        return None

def convert_to_date(milliseconds):
    seconds = milliseconds / 1000
    date_obj = datetime.fromtimestamp(seconds)
    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return date_str

def get_all_metadata(dataset: dict):
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





# Example usage
if __name__ == '__main__':
    # Example paths (replace with your actual paths and data IDs)
    file_directory_path = '/iplant/home/shared/commons_repo/curated/Bacher_Wheat_DroughtStress_Dec2016'
    sample_data_id = '78bda920-691e-11ea-910c-90e2ba675364'  # Sample ID for a dataset

    # Get list of datasets
    get_datasets()


    # Get list of files
    # get_list_of_files(file_directory_path)

    # Get metadata for a specific data ID
    # Returns a dictionary with keys of "avus", "irods-avus", and "path"
    # "avus" has a value of a list of dictionaries
    # get_metadata(sample_data_id)
