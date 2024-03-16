import json

def load_map_to_string(file_path:str)->str:
    """
    Load an OSM map file and convert it to a string.

    Args:
    file_path (str): The file path of the OSM map file.

    Returns:
    str: A string representation of the OSM map file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            map_data = file.read()
            return map_data
    except FileNotFoundError:
        return file_path+"OSM File not found"
    except Exception as e:
        return f"An error occurred: {e}"

