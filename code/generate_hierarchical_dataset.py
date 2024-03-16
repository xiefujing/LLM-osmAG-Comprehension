import process_osm
import utility_map
import xml.etree.ElementTree as ET
import map_loader
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
    # Generate n prefix strings
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

def random_hier_prompt_in_test(test_file):
    new_prompts = [
    "I'm using an OpenStreetMap (XML) campus map with 'ways' that have IDs, names, types, and area categories (rooms or structures) defined by tags. I need to find a person by their room ownership and map hierarchy.",
    "Seeking to locate a person using an XML campus map from OpenStreetMap, focusing on 'ways' with unique IDs and tags for room names, types, and areas, including ownership and hierarchical structure.",
    "Navigating an OpenStreetMap (XML) with 'ways' labeled with IDs, names, and specific tags for type and area (room/structure), including owner and parent tags, to track down a person’s room and its building.",
    "On a quest to find someone using an OpenStreetMap (XML) campus layout. It utilizes 'ways' with IDs and tags detailing names, types, and area classifications, plus ownership and hierarchical links.",
    "Using an XML formatted OpenStreetMap of a campus to identify a person’s location. It involves 'ways' with unique IDs and tags for names, types, area (room or structure), ownership, and structure hierarchy.",
    "Employing an OpenStreetMap (XML) of a campus featuring 'ways' with IDs, names, types, and area tags to discern someone’s room by ownership and map hierarchy.",
    "Exploring an OpenStreetMap (XML) campus guide with 'ways' marked by IDs, names, type, and area tags (indicating rooms or structures), to locate a person through ownership and parent-child map relationships.",
    "Utilizing a campus map in OpenStreetMap (XML) format, which categorizes 'ways' by ID, name, type, and area (room/structure), to track a person via room ownership and hierarchical connections.",
    "On a mission to locate an individual via an OpenStreetMap (XML) campus chart, examining 'ways' with specific IDs, names, types, areas, including ownership and the hierarchy for rooms and buildings.",
    "Seeking an individual using a detailed OpenStreetMap (XML) of a campus, with 'ways' defined by unique IDs, tags for names, types, and areas, plus information on ownership and structure hierarchy."
    ]
    replacement_keyword ="I have a map of a campus, the map is in OpenStreetMap(XML) format. It contains a series of elements called 'ways', each of which has a unique ID and is associated with a set of tags that describe its properties. Each way has several tags: 'name' specifies the name of the room, such as \"1d-204\"; 'osmAG:type' specifies the category of the way. If the attribute 'osmAG:Type' is set to 'area', it indicates the way is either a room or a structure with a defined area. Furthermore, the 'osmAG:areaType' tag details the area's category. When set to 'room,' it signifies that the way is a room or corridor possessing a defined area. Conversely, if 'osmAG:areaType' is 'structure,' it suggests the way encompasses several areas or structures within it. Additionally, the 'owner' tag identifies the room's proprietor, while the 'parent' tag points to the ID of the parent entity, which could be either a room or a structure, thereby establishing a hierarchical relationship within the map's elements. To locate someone, I must identify the room owned by the individual in question and then trace its hierarchical structure up to the corresponding building."
    str_length=len(replacement_keyword)
    with open(test_file, 'r') as file:
        data = json.load(file)
        for entry in data:
            split_position = entry['instruction'].rfind(replacement_keyword)
            if split_position != -1:
            # Select a random prompt
                new_prompt_part = random.choice(new_prompts)
                # Concatenate the new prompt with the unchanged part of the original instruction
                entry['instruction'] = new_prompt_part + entry['instruction'][str_length:]
    modified_file_path = test_file[0:-5] + "_randomprompt.json"         
    with open(modified_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def generate_hierarchy_train_test_json():
    output_file_folder='./osmAG_template/hierarchical/generated_random_name/'
    for filename in os.listdir(output_file_folder):
        file_path = os.path.join(output_file_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                pass
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    input_file_list=['./osmAG_template/topological/template_a.osm','./osmAG_template/topological/template_a.osm','./osmAG_template/topological/template_a.osm']
    for input_file in input_file_list:
        path_parts = input_file.split('/')
        output_file_path=output_file_folder+path_parts[-1]
        process_osm.del_all_node(input_file, output_file_path)
        process_osm.cleanup_way(output_file_path, output_file_path)
        process_osm.double_passages(output_file_path, output_file_path)
        prefixes=generate_random_prefixes(2)
        for prefix in prefixes:
            process_osm.generate_new_xml_with_shuffled_roomno(output_file_path,output_file_path+'_randomNo.osm',prefix)
    all_files = os.listdir(output_file_folder)
    pattern = r"-.\.osm$"
    filtered_files = [file for file in all_files if re.search(pattern, file)]
    for osm_file in filtered_files:
        file_path = os.path.join(output_file_folder, osm_file)
        utility_map.osm2area_connected_by_passage(file_path,file_path[0:-4]+'_no_passages_directly.osm')
    prompt_infos=pd.DataFrame()
    all_files = os.listdir(output_file_folder)
    pattern = r"-.\_no_passages_directly.osm$"
    filtered_files = [file for file in all_files if re.search(pattern, file)]
    train_size=60
    for i in range(train_size):
        picked_files = random.sample(filtered_files, 2)
        picked_df,map_str=hierarchy_two_files(output_file_folder+picked_files[0],output_file_folder+picked_files[1])
        prompt_info=prompt_generator.generate_simple_hier_prompt(picked_df,map_str)
        prompt_infos=prompt_infos._append(prompt_info)
    train_df, test_df = train_test_split(prompt_infos, test_size=0.2, random_state=42)
    train_json_data = []
    test_json_data = []
    convert_to_json(train_df, train_json_data)
    convert_to_json(test_df, test_json_data)
    train_json_file='./generated_dataset/hierarchical/hierarchical_train_dataset.json'
    test_json_file='./generated_dataset/hierarchical/hierarchical_test_dataset.json'
    with open(train_json_file, "w") as train_json_file:
        json.dump(train_json_data, train_json_file, indent=4)
    with open(test_json_file, "w") as test_json_file:
        json.dump(test_json_data, test_json_file, indent=4)

# Helper function to ensure unique IDs
def get_next_id(root,file1_ids=[]):
    existing_ids = [int(way.get('id')) for way in root.findall('way')]+file1_ids
    return min(existing_ids) - 1 if existing_ids else -1

# Function to add or find a hierarchy level
def add_or_find_hierarchy(root, name, areaType, type, parent=None,file1_ids=[]):
    for way in root.findall('way'):
        if way.find("./tag[@k='name']").get('v') == name:
            return  # Already exists
    id_value = get_next_id(root,file1_ids)
    way = ET.SubElement(root, 'way', {'id': str(id_value)})
    ET.SubElement(way, 'tag', {'k': 'name', 'v': name})
    ET.SubElement(way, 'tag', {'k': 'osmAG:areaType', 'v': areaType})
    ET.SubElement(way, 'tag', {'k': 'osmAG:type', 'v': type})
    if parent:
        ET.SubElement(way, 'tag', {'k': 'parent', 'v': parent})

def convert_parent2id(root):
    for way in root.findall('way'):
        parent_tag = way.find("./tag[@k='parent']")
        if parent_tag is not None:
            parent_name = parent_tag.get('v')
            for parent_way in root.findall('way'):
                if parent_way.find("./tag[@k='name']").get('v') == parent_name:
                    parent_id = parent_way.get('id')
                    parent_tag.set('v', parent_id)
                    break

def hierarchy_one_file(file_name,building_name,file1_ids=[]):
    osm_data=map_loader.load_map_to_string(file_name)
    root = ET.fromstring(osm_data)
    for way in root.findall('way'):
        for tag in way.findall('tag'):
            k_attr = tag.get('k')
            if k_attr.endswith('directly_connected_area'):
                way.remove(tag)
        room_name_tag = way.find("./tag[@k='name']")
        if room_name_tag is not None:
            room_name = room_name_tag.get('v')
            if len(room_name) >= 5 and room_name[2] == '-':  # Basic validation for room name format
                building = building_name
                wing = f"{room_name[0]}_wing"
                floor = f"{room_name[3]}_floor"
                zone = f"{room_name[1]}_zone"
                hierarchy = [(building, 'structure', 'area',None),
                            (wing, 'structure', 'area', building),
                            (floor, 'structure', 'area', wing),
                            (zone, 'structure', 'area', floor)]
                # Add or find each level in the hierarchy
                for name, areaType, type, parent in hierarchy:
                    add_or_find_hierarchy(root, name, areaType, type, parent,file1_ids=file1_ids)
                # Add parent tag to the room
                ET.SubElement(way, 'tag', {'k': 'parent', 'v': zone})
    convert_parent2id(root)
    tree = ET.ElementTree(root)
    return tree

def hierarchy_two_files(file_name1,file_name2):
    random_owner=['Sören Schwertfeger',"Maydianne Andrade","Brenda Andrews","J. Richard Bond","Allan Borodin","Dan Breznitz",
                  "Jutta Brunnée","Paul Brumer","Tirone David","John Dick","Daniel Drucker","David Dyzenhaus","Elizabeth Edwards",
                  "Richard Florida","Marie-Josée Fortin","John Friedlander","Mary Gospodarowicz","Jack Greenblatt","John Hull",
                  "David Jenkins","Prabhat Jha","Sajeev John","Junjie Liu",'Fei Gao',"Meishan Zhang","Yueheng Sun","Eren Unlu","Gyeongmin Kim",
                  "Shyam Sundar Kannan","Arthur Bucker","Shuang Ma","Luis Figueredo"]
    file1_tree=hierarchy_one_file(file_name1,'SIST_1')
    file1_ids = [int(way.get('id')) for way in file1_tree.getroot().findall('way')]
    file2_tree=hierarchy_one_file(file_name2,'SIST_2',file1_ids)
    df=pd.DataFrame(columns=['name', 'building'])
    df_list=[]
    for way in file1_tree.findall('way'):
        areaType_tag = way.find("./tag[@k='osmAG:areaType']")
        if areaType_tag.get('v') =='room':
            # room_name = room_name_tag.get('v')
            chosen_one = random.choice(random_owner)
            random_owner.remove(chosen_one)
            new_tag = ET.Element('tag', attrib={'k': 'owner', 'v': chosen_one})  # Update 'key' and 'value'
            way.append(new_tag)
            df_list.append((chosen_one,'SIST_1'))
    for way in file2_tree.findall('way'):
        areaType_tag = way.find("./tag[@k='osmAG:areaType']")
        if areaType_tag.get('v') =='room':
            # room_name = room_name_tag.get('v')
            chosen_one = random.choice(random_owner)
            random_owner.remove(chosen_one)
            new_tag = ET.Element('tag', attrib={'k': 'owner', 'v': chosen_one})  # Update 'key' and 'value'
            way.append(new_tag)
            df_list.append((chosen_one,'SIST_2')) 
    root1 = file1_tree.getroot()
    root2 = file2_tree.getroot()
    for name, building in df_list:
        df = df._append({'name': name, 'building': building}, ignore_index=True)
    for child in root2:
        root1.append(child)
    ET.indent(file1_tree, space="  ", level=0)  # For pretty printing, requires Python 3.9+
    root = file1_tree.getroot()
    xml_string = ET.tostring(root, encoding='unicode')
    return df, xml_string

if __name__ == '__main__':
    generate_hierarchy_train_test_json()
    # random_hier_prompt_in_test('./generated_dataset/hierarchical/hierarchical_test_dataset.json')

    

