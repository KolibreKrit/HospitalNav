import pyorient
import json
import re
import numpy as np
import path_tools
from os.path import exists


def reset_db(client, name):

   # Remove Old Database
   if client.db_exists(name):
    client.db_drop(name)

   # Create New Database
   client.db_create(name,
      pyorient.DB_TYPE_GRAPH,
      pyorient.STORAGE_TYPE_PLOCAL)

def getrid(client,name):
    nodeId = client.query("SELECT FROM Location WHERE name = '" + str(name) + "'")
    return str(nodeId[0]._rid)
    
def getname(client, rid):
    name = client.query("SELECT name FROM " + rid.get_hash())
    return name[0].__getattr__('name')

#get several attributes needed by web client
def getattr(client, rid):
    attr = client.query("SELECT name, x_coord, y_coord, floor FROM " + rid.get_hash())
    return {"name": attr[0].name, "x_coord": attr[0].x_coord, "y_coord": attr[0].y_coord, "floor": attr[0].floor}

def getangle_out(client, ridout, ridin):
    angle = client.query("SELECT angle FROM Connection WHERE out = " + ridout.get_hash() + " AND in = " + ridin.get_hash())
    return angle[0].angle

def getangle_back(client, ridout, ridin):
    angle = client.query("SELECT angle FROM Connection WHERE out = " + ridin.get_hash() + " AND in = " + ridout.get_hash())
    return angle[0].angle

def getEndpoints(client):
    endpoints = client.query("SELECT name FROM Location WHERE is_endpoint = TRUE")
    return [endpoint.__getattr__('name') for endpoint in endpoints]
    
def getStartpoints(client):
    startpoints = client.query("SELECT name FROM Location WHERE is_startpoint = TRUE")
    return [startpoint.__getattr__('name') for startpoint in startpoints]

#def getphoto(client, name):
#    photosphere = client.query("SELECT photosphere FROM Location WHERE name = '" + str(name) + "'")
#    return photosphere[0].__getattr__('photosphere')

def loadDB(filepath):

    #database name
    dbname = "locations"
    #database login is root by default
    login = "root"
    #database password, set by docker param
    password = "rootpwd"

    #create client to connect to local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    #remove old database and create new one
    reset_db(client,dbname)

    #open the database we are interested in
    client.db_open(dbname, login, password)

    client.command("CREATE CLASS Location EXTENDS V")
    client.command("CREATE PROPERTY Location.name String")
    client.command("CREATE PROPERTY Location.is_startpoint Boolean")
    client.command("CREATE PROPERTY Location.is_endpoint Boolean")
    client.command("CREATE PROPERTY Location.x_coord Double")
    client.command("CREATE PROPERTY Location.y_coord Double")
    client.command("CREATE PROPERTY Location.building String")
    client.command("CREATE PROPERTY Location.map String")
    client.command("CREATE PROPERTY Location.floor String")
    #client.command("CREATE PROPERTY Location.metric Integer")

    client.command("CREATE CLASS Connection EXTENDS E")
    client.command("CREATE PROPERTY Connection.angle Double")

    #open and parse local json file
    with open(filepath) as f:
        data = json.load(f)

    #loop through each key in the json database and create a new vertex, V with the id in the database
    # for key in data:
    #     client.command("CREATE VERTEX Location SET name = '" + key
    #     + "', is_startpoint = '" + str(data.get(key).get("is_startpoint"))
    #     + "', is_endpoint = " + str(data.get(key).get("is_endpoint"))
    #     + ", x_coord = " + str(data.get(key).get("x_coord"))
    #     + ", y_coord = " + str(data.get(key).get("y_coord"))
    #     + ", building = " + data.get(key).get("building")
    #     + ", map = " + data.get(key).get("map"))
    
    for key in data:
        client.command("CREATE VERTEX Location SET name = '" + key
        + "', is_startpoint = '" + str(data[key]["is_startpoint"])
        + "', is_endpoint = " + str(data[key]["is_endpoint"])
        + ", x_coord = " + str(data[key]["x_coord"])
        + ", y_coord = " + str(data[key]["y_coord"])
        + ", building = " + data[key]["building"]
        + ", floor = " + data[key]["floor"]
        + ", map = " + data[key]["map"])

    #loop through each key creating edges from location to location
    for key in data:
        location1ID = str(getrid(client,key))
        for connection in data.get(key)["connectList"]:
            location2 = connection["name"]
            angle = connection["angle"]
            location2ID = str(getrid(client,location2))
            client.command("CREATE EDGE Connection FROM " + location1ID + " TO " + location2ID + "SET angle = " + str(angle))

    client.close()

def shortestPath(locationA, locationB):
    dbname = "locations"
    login = "root"
    password = "rootpwd"
    path = list()

    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)

    #get the RID of the two people
    locationAID = getrid(client,locationA)
    locationBID = getrid(client,locationB)

    #determine the shortest path
    pathlist = client.command("SELECT shortestPath(" + locationAID + ", " + locationBID +")")
    #print(pathlist[0].__getattr__('shortestPath'))

    #get distance
    distance = len(pathlist[0].__getattr__('shortestPath'))
    raw_path = pathlist[0].__getattr__('shortestPath')

    print(raw_path)
    for i in range(distance):
        path.append(getattr(client, raw_path[i]))
    for i in range(distance-1):
        path[i]["angle"] = getangle_out(client, raw_path[i], raw_path[i+1])
        path[i+1]["angle_back"] = getangle_back(client, raw_path[i], raw_path[i+1])
    if len(path) >= 2:
        path[-1]["angle"] = path[-2]["angle"] #last node has no out edge: just use angle of second-to-last node
        path[0]["angle_back"] = path[1]["angle_back"]
    else:
        path[-1]["angle"] = 0.0 # 1 node path edge case
        path[0]["angle_back"] = 0.0

    client.close()

    path_string = string_directions(path)
    path_string = next_nodes(path_string, 3)

    return path_string


#take back angle and out angle to find left/right/straight turns
#angles are in range -pi, pi
#trevor roussel
def string_directions(path):
    for i in range(len(path)-1):
        next_floor = path[i+1]['floor']
        if(path[i]['floor'] != next_floor):
            path[i]['string_direction'] = f'Take the elevator to floor {next_floor}'
            #next iteration, first vector will be zero vector. will always display direction as straight, avoids unintended behavior with different coords on diff maps
        else:
            #find angle of out angle from perspective of back angle
            angle = path[i]["angle"] - path[i]["angle_back"] + np.pi
            angle = path_tools.reg_angle(angle) #set to range -pi, pi
            #3pi/4 and pi/4 constants are precomputed because python is iffy about folding constants
            if (angle > -2.3562 and angle < -0.7854):
                path[i]['string_direction'] = 'Turn left'
            elif (angle < 0.7854):
                path[i]['string_direction'] = 'Head straight'
            elif (angle < 2.3562):
                path[i]['string_direction'] = 'Turn right'
            else:
                path[i]['string_direction'] = 'Turn backwards' #probably an error case but maybe there are weird directions
    path[-1]['string_direction'] = 'You\'ve arrived!'
    return path

#for each node in path, get the next 3 nodes and add name of overlay image
#trevor roussel
def next_nodes(path, segments=3, line_path='data/images/lines/'):
    connections = []
    for i in range(len(path)):
        connections.append(path_tools.get_next_n(path, i, segments))
        name = 'line'
        for j in range(len(connections[i])):
            name += '_' + connections[i][j]['name']
        name += '.png'
        if not exists(line_path+name):
            path_tools.draw_line(connections[i], line_path)
        path[i]['line_name'] = name
    return path

# def angle_between(vec1, vec2):
#     #in the case of a zero vector, assume we always consider the path taken as straight
#     if all(components == 0 for components in vec1):
#         return np.pi
#     v1_norm = vec1 / np.linalg.norm(vec1)
#     v2_norm = vec2 / np.linalg.norm(vec2)
#     angle = np.arccos(np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0))
#     #angle in 2D plane: angle measures from a left turn, with 0 being a reverse, pi/2 being 90 deg left, 3pi/2 90 deg right, etc.
#     #arccos has range [0, pi]. Checking sign of cross product lets us adjust to full 2pi radius
#     if (np.cross(v1_norm, v2_norm) > 0):
#         angle = angle + np.pi
#     return angle

