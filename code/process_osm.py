import xml.etree.ElementTree as ET
from utility_map import *
import random

def cleanup_way(input_file,output_file):
    # delete all ref node in way 
    tree = ET.parse(input_file)
    root = tree.getroot()
    for way in root.findall('way'):
        del way.attrib['action']
        del way.attrib['visible']
        for tag in way.findall('tag'):
            if(tag.attrib['k']=='height' or tag.attrib['k']=='indoor' or tag.attrib['k']=='level'):
                way.remove(tag)
            if tag.attrib['k']=='name' and any(tag.get('v') == 'passage' for tag in way.findall('tag')):
                way.remove(tag)
        for nd in way.findall('nd'):
            way.remove(nd)
    tree.write(output_file,encoding='utf-8', xml_declaration=True)

def del_all_node(input_file,output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    for node in root.findall('node'):
        root.remove(node)
    tree.write(output_file,encoding='utf-8', xml_declaration=True)

def double_passages(input_file, output_file):
    with open(input_file, 'r') as file:
        xml_data = file.read()
    root = ET.fromstring(xml_data)
    xml_str = ET.tostring(root, encoding='unicode')
    highest_id = max([int(way.get('id')) for way in root.findall('way')], default=0)
    new_way_strings = []
    for way_element in root.findall('way'):
        highest_id += 1
        way_id = str(highest_id)
        new_way_str = f'  <way id="{way_id}">\n'
        tags_dict = {}
        for tag in way_element.findall('tag'):
            tags_dict[tag.get('k')] = tag.get('v')
        if 'osmAG:' in tags_dict and 'osmAG:' in tags_dict:
            new_way_str += f'    <tag k="osmAG:from" v="{tags_dict["osmAG:to"]}" />\n'
            if 'osmAG:type' in tags_dict:
                new_way_str += f'    <tag k="osmAG:type" v="{tags_dict["osmAG:type"]}" />\n'
            new_way_str += f'    <tag k="osmAG:to" v="{tags_dict["osmAG:from"]}" />\n'
        else:
            continue  # Skip this 'way' if it doesn't have both 'from' and 'to'
        new_way_str += '  </way>'
        new_way_strings.append(new_way_str)
    final_xml = '<osm>\n' + xml_str[0:-6]+'\n'.join(new_way_strings) + '\n</osm>'
    final_xml =  xml_str[0:-6]+'\n'.join(new_way_strings) + '\n</osm>'
    with open(output_file, 'w') as file:
        file.write(final_xml)

def generate_new_xml_with_shuffled_roomno(input_file,output_file,prefix):
    with open(input_file, 'r') as file:
        xml_data = file.read()
    root = ET.fromstring(xml_data)
    room_names = set()
    existing_ids = set()
    for way in root.findall('way'):
        existing_ids.add(int(way.get('id')))
        for tag in way.findall('tag'):
            if tag.get('k') == 'osmAG:areaType' and tag.get('v') == 'room':
                name_tag = way.find("tag[@k='name']")
                if name_tag is not None:
                    room_names.add(name_tag.get('v'))
    num_rooms = len(room_names)
    random_num=random.randint(1, 20)
    new_room_ids = [f"{prefix}{str((random_num + i) % 100).zfill(2)}" for i in range(num_rooms)]
    random.shuffle(new_room_ids)  # Randomize the sequence
    room_mapping = dict(zip(room_names, new_room_ids))
    max_existing_id = max(existing_ids) if existing_ids else 0
    new_way_ids = list(range(max_existing_id + 1, max_existing_id + 1 + len(root.findall('way'))))
    random.shuffle(new_way_ids)  # Ensure IDs are randomized
    for way, new_id in zip(root.findall('way'), new_way_ids):
        way.set('id', str(new_id))  # Update way ID
        for tag in way.findall('tag'):
            if tag.get('k') == 'name' and tag.get('v') in room_mapping:
                # Update room names
                tag.set('v', room_mapping[tag.get('v')])
            elif tag.get('k') in ['osmAG:from', 'osmAG:to'] and tag.get('v') in room_mapping:
                # Update passage references to rooms
                tag.set('v', room_mapping[tag.get('v')])
    updated_xml = ET.tostring(root, encoding='unicode')
    with open(output_file[0:-4]+'_'+prefix+'.osm', 'w') as file:
        file.write(updated_xml)
    return updated_xml