#one-off functions where we save results. performance probably doesn't matter
#trevor roussel
import json
import numpy as np
from PIL import Image

#want edges defined by both name of connected node and angle between from perspective of camera
#since test_map was made with constant camera orientations, we can use the 2D vector to find this
#rewrites edges with just names to new json_file with edge names and angles
def write_angles(path, name):
    with open(path+name, 'r') as file:
        nodes = json.load(file)
    #print(type(nodes))
    for node in nodes:
        nodes[node]['connectList2'] = []
        #print(nodes[node]['connectList'])
        for connected_node in nodes[node]['connectList']:
            #vector between connected nodes
            vector = (nodes[connected_node]['x_coord']-nodes[node]['x_coord'], -(nodes[connected_node]['y_coord']-nodes[node]['y_coord']))
            if(vector[1]) != 0:
                angle = np.arctan(vector[0]/vector[1])
                #only maps to -pi/2 to pi/2. fix for full 2pi arc:
                if(vector[1] < 0):
                    if(vector[0] <= 0):
                        angle = angle - np.pi
                    else:
                        angle = angle + np.pi
            else:
                if(vector[0]>=0):
                    angle = np.pi/2
                else: 
                    angle = -np.pi/2
            nodes[node]['connectList2'].append({"name": connected_node, "angle": angle})
            #print(node, connected_node, vector, angle)
        nodes[node]['connectList'] = nodes[node]['connectList2']
        nodes[node].pop('connectList2', None)
    name2 = name.split('.')[0] + '_angles.json'
    with open(path+name2, 'w') as file:
        file.write(json.dumps(nodes))

def rewrite_images(nodes_path, image_path):
    with open(nodes_path, 'r') as file:
        nodes = json.load(file)
    for node in nodes:
        image_name = nodes[node]['photosphere']
        image = Image.open(image_path+image_name)
        im2 = image.convert('RGB')
        im2.save(image_path+'images_test2/'+node+'.jpg')
    print('Done')

#rewrite_images('data/testmap_nodes_angles.json', 'data/')

def draw_connections(nodes_path, image_path):
    with open(nodes_path, 'r') as file:
        nodes = json.load(file)
    print(nodes)
    # for node in nodes:
    #     for 

draw_connections('data/testmap_nodes_angles.json', 'data/images/lines')