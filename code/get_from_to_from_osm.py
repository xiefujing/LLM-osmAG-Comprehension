import xml.etree.ElementTree as ET
import networkx as nx
import csv
import pandas as pd

def parse_osm_data(osm_xml):
    root = ET.fromstring(osm_xml)
    G = nx.Graph()

    # Process each 'way' element
    for way in root.findall('way'):
        tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
        if 'osmAG:areaType' in tags and tags['osmAG:areaType'] == 'room':
            G.add_node(tags['name'])
        elif 'osmAG:type' in tags and tags['osmAG:type'] == 'passage':
            G.add_edge(tags['osmAG:from'], tags['osmAG:to'])

    return G

def find_paths(graph):
    paths=dict(nx.all_pairs_shortest_path(graph))
    for start_room in paths:
        for end_room in paths[start_room]:
            path_list = paths[start_room][end_room]
            if start_room != end_room:
                path = list(nx.all_shortest_paths(graph, source=start_room, target=end_room))
                if len(path)<=1:
                    continue
                else:
                    paths[start_room][end_room]=path
    return paths

def save_paths_to_csv(paths, file_path):
    data_for_df = []
    if bool(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['From', 'To', 'Path'])
            for start_room in paths:
                for end_room in paths[start_room]:
                    path_list = paths[start_room][end_room]
                    if start_room != end_room:
                        writer.writerow([start_room, end_room, path_list])
    else:
        for start_room in paths:
            for end_room in paths[start_room]:
                path_list = paths[start_room][end_room]
                if start_room != end_room:
                    data_for_df.append([start_room, end_room, path_list])
        df = pd.DataFrame(data_for_df, columns=['From', 'To', 'Path'])
    return df
