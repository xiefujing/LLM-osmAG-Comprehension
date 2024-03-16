import process_osm
import utility_map
import xml.etree.ElementTree as ET
import map_loader
import get_from_to_from_osm
import prompt_generator
import pandas as pd
import os
import random
from sklearn.model_selection import train_test_split
import json
import re

def generate_random_prefixes(n):
    # Define the characters to choose from
    chars = 'abcdef'
    prefixes = []
    for _ in range(n):
        char = random.choice(chars)  # Choose a random character
        first_num = random.randint(1, 5)  # Choose a random number from 1 to 15
        second_num = random.randint(1, 9)  # Choose a random number from 1 to 9
        prefix = f"{first_num}{char}-{second_num}"
        prefixes.append(prefix)
    return prefixes

def convert_to_json(df, json_data):
    for index, row in df.iterrows():
        instruction = {
            "instruction": row["formatted_prompt"],
            "input": "",  # You mentioned input is empty in your example
            "output": str(row['GT']),
            "history": []
        }
        json_data.append(instruction)

def random_prompt_in_test(test_file):
    new_prompts = [
    "Using an OpenStreetMap formatted campus map with 'ways', each having unique IDs and tags for properties like room names ('name'), types ('osmAG:type'), and connections ('connected_area'), how can I navigate from",
    "On a campus map in OpenStreetMap format, where 'ways' denote areas with unique IDs and tags for room names ('name') and categories ('osmAG:type'), how do I find the shortest path from",
    "I possess a digital campus map featuring areas called 'ways', each with a unique ID and tags describing room names ('name') and their functions ('osmAG:type'). How can I navigate from",
    "Given an OpenStreetMap-style campus layout, with 'ways' indicating rooms tagged by 'name' and 'osmAG:type', how do I determine the shortest route from",
    "Navigating a campus map with 'ways' marked by unique IDs, room names ('name'), and categories ('osmAG:type'), how can I find the most direct route from",
    "With an OpenStreetMap of a campus where 'ways' are detailed with identifiers and tags for names ('name') and area types ('osmAG:type'), how do I efficiently navigate from",
    "Exploring a campus through an OpenStreetMap format, where 'ways' define spaces with names ('name') and types ('osmAG:type'), how can I plot the shortest path from",
    "On an OpenStreetMap-based campus guide, 'ways' are utilized to represent areas with identifiers and tags for room names ('name') and classifications ('osmAG:type'). How can I proceed from",
    "Employing an OpenStreetMap format for campus navigation, with 'ways' categorized by unique IDs, names ('name'), and types ('osmAG:type'), how do I determine the best path from",
    "Utilizing a campus map in OpenStreetMap format, where 'ways' serve as markers for spaces with specific names ('name') and types ('osmAG:type'), how do I navigate from"
    ]
    replacement_keyword ="I have a map of a campus, the map is in OpenStreetMap(XML) format. It contains a series of elements called 'ways', each of which has a unique ID and is associated with a set of tags that describe its properties. Each way has several tags: 'name' specifies the name of the room, such as \"1d-204\"; 'osmAG:type' specifies the category of the way. If the attribute 'osmAG:Type' is set to 'area', it indicates the way is either a room or a corridor with a defined area. 'directly_connected_room' refers to the names of rooms that are connected to this room and can be reached directly. \nFor example, here is a small snippet of the map: \n   <way id=\"-134173\">\n    <tag k=\"name\" v=\"1d-201\" />\n    <tag k=\"osmAG:areaType\" v=\"room\" />\n    <tag k=\"osmAG:type\" v=\"area\" />\n    <tag k=\"1d-201 directly_connected_room\" v=\"1d-203\" />\n    <tag k=\"1d-201 directly_connected_room\" v=\"1d-213\" />\n    </way>\n   <way id=\"-134166\">\n    <tag k=\"name\" v=\"1d-203\" />\n    <tag k=\"osmAG:areaType\" v=\"room\" />\n    <tag k=\"osmAG:type\" v=\"area\" />\n    <tag k=\"1d-203 directly_connected_room\" v=\"1d-201\" />\n    <tag k=\"1d-203 directly_connected_room\" v=\"1d-202\" />\n    </way>\n  <way id=\"-134179\">\n    <tag k=\"name\" v=\"1d-213\" />\n    <tag k=\"osmAG:areaType\" v=\"room\" />\n    <tag k=\"osmAG:type\" v=\"area\" />\n    <tag k=\"1d-213 directly_connected_room\" v=\"1d-201\" />\n    <tag k=\"1d-213 directly_connected_room\" v=\"1d-209\" />\n    </way>\n  </osm>\n  In this example, there is a room with id '-134173', its name is '1d-201'. It has two doors and is directly connected to two rooms '1d-203' and '1d-213'. Consider each room as a node. If it is connected to other room, there is an edge between them. Some rooms may have several doors connected to several other rooms. This means if there are several 'directly_connected_room' tags all connected to this room, you need to choose one 'directly_connected_room' accrording to which one has a shorter path(shorter means fewer rooms to go through and has nothing to do with close or similiar room numbers) to destination. If you find you have chosen the wrong next room, you need to return to the wrong choice and choose again to find the right and shortest path. If a room is not listed the 'directly_connected_room', it means it is not directly connected to current room. So if I want to go from room '1d-201' to room '1d-209', from room '1d-201' there are two doors, I choose room '1d-213' because it is closer to destination room '1d-209'. Thus the answer would be ['1d-201','1d-213','1d-209']. And if I want to go from '1d-201' to '1d-213', since they are directly connnected, the answer would be ['1d-201','1d-213']. Please analyze the topological structure of this map. Then, tell me how to go from"
    str_length=len(replacement_keyword)
    with open(test_file, 'r') as file:
        data = json.load(file)
        for entry in data:
            split_position = entry['instruction'].rfind(replacement_keyword)
            if split_position != -1:
                new_prompt_part = random.choice(new_prompts)
                entry['instruction'] = new_prompt_part + entry['instruction'][str_length:]
    modified_file_path = test_file[0:-5] + "_random_prompt.json"         
    with open(modified_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def generate_train_test_json():
    input_file_list=['./osmAG_template/topological/template_a.osm','./osmAG_template/topological/template_b.osm','./osmAG_template/topological/template_c.osm']
    output_file_folder='./osmAG_template/topological/generated_random_name/'
    for filename in os.listdir(output_file_folder):
        file_path = os.path.join(output_file_folder, filename)
        try:
            # Check if it is a file and not a directory
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # If you also want to delete directories, uncomment the next line
                # shutil.rmtree(file_path)
                pass
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    for input_file in input_file_list:
        path_parts = input_file.split('/')
        output_file_path=output_file_folder+path_parts[-1]
        process_osm.del_all_node(input_file, output_file_path)
        process_osm.cleanup_way(output_file_path, output_file_path)
        process_osm.double_passages(output_file_path, output_file_path)
        prefixes=generate_random_prefixes(5)
        for prefix in prefixes:
            process_osm.generate_new_xml_with_shuffled_roomno(output_file_path,output_file_path[0:-4]+'_randomNo.osm',prefix)
    all_files = os.listdir(output_file_folder)
    pattern = r"-.\.osm$"
    filtered_files = [file for file in all_files if re.search(pattern, file)]
    for osm_file in filtered_files:
        file_path = os.path.join(output_file_folder, osm_file)
        utility_map.osm2area_connected_by_passage(file_path,file_path[0:-4]+'_no_passages_directly.osm')
    prompt_infos=pd.DataFrame()
    for osm_file in filtered_files:
        osm_data=map_loader.load_map_to_string(os.path.join(output_file_folder, osm_file))
        graph = get_from_to_from_osm.parse_osm_data(osm_data)
        root = ET.fromstring(osm_data)
        paths = get_from_to_from_osm.find_paths(graph)
        csv_file_path = ''
        df=get_from_to_from_osm.save_paths_to_csv(paths, csv_file_path)
        prompt_info=prompt_generator.generate_simple_prompt(os.path.join(output_file_folder, osm_file[0:-4]+'_no_passages_directly.osm'),df)
        prompt_infos=prompt_infos._append(prompt_info)
    train_df, test_df = train_test_split(prompt_infos, test_size=0.2, random_state=42)
    train_json_data = []
    test_json_data = []
    convert_to_json(train_df, train_json_data)
    convert_to_json(test_df, test_json_data)
    train_json_file='./generated_dataset/topological/topological_train_dataset.json'
    test_json_file='./generated_dataset/topological/topological_test_dataset.json'
    with open(train_json_file, "w") as train_json_file:
        json.dump(train_json_data, train_json_file, indent=4)
    with open(test_json_file, "w") as test_json_file:
        json.dump(test_json_data, test_json_file, indent=4)

if __name__ == '__main__':
    generate_train_test_json()
    random_prompt_in_test('./generated_dataset/topological/topological_test_dataset.json')
