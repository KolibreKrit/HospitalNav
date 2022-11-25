#one-off functions where we save results. performance probably doesn't matter
#trevor roussel
import json
import numpy as np
from PIL import Image
from PIL import ImageDraw
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading

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

# def draw_connections(nodes_path, image_path, length=3):
#     with open(nodes_path, 'r') as file:
#         nodes = json.load(file)
#     print(nodes)
#     for key in nodes:
#         in_path = [key]
#         for i in range()
#         for edge in nodes[key]['connectList']:


# draw_connections('data/testmap_nodes_angles.json', 'data/images/lines')

def fix_connections(path, name):
    with open(path + name + '.json', 'r') as file:
        nodes = json.load(file)
    for node in nodes:
        conns = nodes[node]['connectList']
        conn_list = conns.split(',')
        for adj in conn_list:
            adj = adj.strip()
            print(adj)
        new_conn_list = []
        for adj in conn_list:
            new_conn_list.append({'name': adj, 'angle': 0.0})
        nodes[node]['connectList'] = new_conn_list
    with open(path + name + '_new.json', 'w') as file:
        json.dump(nodes, file)

#fix_connections('data/', 'KYCTestValues')

#draw nodes on map
def display_map(path, name, node_r:int = 10, scale=6):
    line_w = int(node_r/4)
    with open(path + name + '.json', 'r') as file:
        nodes = json.load(file)
    max_coords = [0, 0]
    for node in nodes:
        max_coords[0] = max(max_coords[0], nodes[node]['x_coord'])
        max_coords[1] = max(max_coords[1], nodes[node]['y_coord'])
    blank_map = Image.new("RGB", [scale*(max_coords[0])+5*node_r, scale*(max_coords[1])+5*node_r], (255, 255, 255))
    map_draw = ImageDraw.Draw(blank_map)
    for node in nodes:
        x = nodes[node]['x_coord']
        y = nodes[node]['y_coord']
        for adj_node in nodes[node]['connectList']:
            x_adj = nodes[adj_node['name']]['x_coord']
            y_adj = nodes[adj_node['name']]['y_coord']
            map_draw.line([(scale*x, scale*y), (scale*x_adj, scale*y_adj)], width=line_w, fill=(255, 0, 0))
    for node in nodes:
        x = nodes[node]['x_coord']
        y = nodes[node]['y_coord']
        box = [(scale*x-node_r, scale*y-node_r),(scale*x+node_r, scale*y+node_r)]
        map_draw.ellipse(box, (0, 0, 255))
        map_draw.text((scale*x-(node_r*2), scale*y-(node_r*2)), node, fill=(0,0,0))
    blank_map.show()
    
#display_map('data/', 'KYCTestValues', 8, 3)


def onclick(event):
    x = event.xdata
    print(to_rad(x))

def to_rad(pixel, w=5504):
    return (pixel/w - .5) * 2*np.pi

def find_angles(path, name):
    with open(path + name + '.json', 'r') as file:
        nodes = json.load(file)
    for node in nodes:
        img = mpimg.imread('data/images/' + node + '.jpg')
        imgplot = plt.imshow(img)
        cid = imgplot.figure.canvas.mpl_connect('button_press_event', onclick)
        plt.title(node)
        plt.show()

find_angles('data/', 'KYCTestValues')
        