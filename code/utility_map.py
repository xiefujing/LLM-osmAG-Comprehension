import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
import networkx as nx

def osm2area_connected_by_passage(input_file, output_file):
    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()
    G = nx.Graph()
    # build graph
    for way in root.findall('way'):
        way_tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
        # print(f'way_tags= {way_tags}')
        if way_tags.get('osmAG:type') == 'passage':
            G.add_edge(way_tags['osmAG:from'], way_tags['osmAG:to'])
    # find all connected area in  all areas
    for way in root.findall('way'):
        way_tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
        if way_tags.get('osmAG:type') == 'area':
            area_name=way_tags['name']
            connected_areas = G.neighbors(area_name)
            for connected_area in connected_areas:
                ET.SubElement(way, 'tag', {'k': area_name+'_directly_connected_area', 'v': connected_area})
        #  remove all passages
        else:
            root.remove(way)
    tree.write(output_file, "UTF-8",short_empty_elements=True)
