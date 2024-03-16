

import pandas as pd
import map_loader

def generate_simple_prompt(map_name,map_from_to):
    map_text=map_loader.load_map_to_string(map_name)
    prompts_info=[]
    prompt_template='''I have a map of a campus, the map is in OpenStreetMap(XML) format. It contains a series of elements called 'ways', each of which has a unique ID and is associated with a set of tags that describe its properties. Each way has several tags: 'name' specifies the name of the room, such as "1d-204"; 'osmAG:type' specifies the category of the way. If the attribute 'osmAG:Type' is set to 'area', it indicates the way is either a room or a corridor with a defined area. 'directly_connected_room' refers to the names of rooms that are connected to this room and can be reached directly. 
For example, here is a small snippet of the map: 
   <way id="-134173">
    <tag k="name" v="1d-201" />
    <tag k="osmAG:areaType" v="room" />
    <tag k="osmAG:type" v="area" />
    <tag k="1d-201 directly_connected_room" v="1d-203" />
    <tag k="1d-201 directly_connected_room" v="1d-213" />
    </way>
   <way id="-134166">
    <tag k="name" v="1d-203" />
    <tag k="osmAG:areaType" v="room" />
    <tag k="osmAG:type" v="area" />
    <tag k="1d-203 directly_connected_room" v="1d-201" />
    <tag k="1d-203 directly_connected_room" v="1d-202" />
    </way>
  <way id="-134179">
    <tag k="name" v="1d-213" />
    <tag k="osmAG:areaType" v="room" />
    <tag k="osmAG:type" v="area" />
    <tag k="1d-213 directly_connected_room" v="1d-201" />
    <tag k="1d-213 directly_connected_room" v="1d-209" />
    </way>
  </osm>
  In this example, there is a room with id '-134173', its name is '1d-201'. It has two doors and is directly connected to two rooms '1d-203' and '1d-213'. Consider each room as a node. If it is connected to other room, there is an edge between them. Some rooms may have several doors connected to several other rooms. This means if there are several 'directly_connected_room' tags all connected to this room, you need to choose one 'directly_connected_room' accrording to which one has a shorter path(shorter means fewer rooms to go through and has nothing to do with close or similiar room numbers) to destination. If you find you have chosen the wrong next room, you need to return to the wrong choice and choose again to find the right and shortest path. If a room is not listed the 'directly_connected_room', it means it is not directly connected to current room. So if I want to go from room '1d-201' to room '1d-209', from room '1d-201' there are two doors, I choose room '1d-213' because it is closer to destination room '1d-209'. Thus the answer would be ['1d-201','1d-213','1d-209']. And if I want to go from '1d-201' to '1d-213', since they are directly connnected, the answer would be ['1d-201','1d-213']. Please analyze the topological structure of this map. Then, tell me how to go from {from_} to {to}, please only output all the room names I need to pass through including the start room and the destination room. Here is the map:{map_text}'''
    for _, row_map in map_from_to.iterrows():
        prompt_template_formatted=prompt_template.format(from_=row_map['From'],to=row_map['To'],map_text=map_text)
        # row_map=list(row_map['From'],row_map['To'],row_map['Path'])
        prompts_info.append([prompt_template_formatted,row_map['From'],row_map['To'],row_map['Path']])
    columns_name=['formatted_prompt','from_','to','GT']
    prompts_info=pd.DataFrame(prompts_info,columns=columns_name)
    return prompts_info

def generate_simple_hier_prompt(hier_df,map_string):
    # map_text=map_loader.load_map_to_string(map_name)
    prompts_info=[]
    prompt_template='''I have a map of a campus, the map is in OpenStreetMap(XML) format. It contains a series of elements called 'ways', each of which has a unique ID and is associated with a set of tags that describe its properties. Each way has several tags: 'name' specifies the name of the room, such as "1d-204"; 'osmAG:type' specifies the category of the way. If the attribute 'osmAG:Type' is set to 'area', it indicates the way is either a room or a structure with a defined area. Furthermore, the 'osmAG:areaType' tag details the area's category. When set to 'room,' it signifies that the way is a room or corridor possessing a defined area. Conversely, if 'osmAG:areaType' is 'structure,' it suggests the way encompasses several areas or structures within it. Additionally, the 'owner' tag identifies the room's proprietor, while the 'parent' tag points to the ID of the parent entity, which could be either a room or a structure, thereby establishing a hierarchical relationship within the map's elements. To locate someone, I must identify the room owned by the individual in question and then trace its hierarchical structure up to the corresponding building. Please analyze the hierarchical structure of this map. Then, tell me how to find {person}, should I go to SIST_1 or SIST_2? Please only output the building name. Here is the map:{map_text}'''
    for _, row_map in hier_df.iterrows():
        prompt_template_formatted=prompt_template.format(person=row_map['name'],map_text=map_string)
        # row_map=list(row_map['From'],row_map['To'],row_map['Path'])
        prompts_info.append([prompt_template_formatted,row_map['name'],row_map['building']])
    columns_name=['formatted_prompt','person','GT']
    prompts_info=pd.DataFrame(prompts_info,columns=columns_name)
    return prompts_info
