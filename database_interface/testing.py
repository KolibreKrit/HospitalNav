#Test cases
#Trevor Roussel

import DBTools
import path_tools
from PIL import Image

#test path using blender testmap data
path = [\
    {"name":"roada2_F1", "x_coord":21.1, "y_coord":46.9, "angle":1.59, "angle_back":-1.55, "floor":"1"}, \
    {"name":"roada3_F1", "x_coord":33.3, "y_coord":47.5, "angle":-3.114, "angle_back":-1.522, "floor":"1"}, \
    {"name":"roadc1_F1", "x_coord":33.1, "y_coord":54.8, "angle":-3.061, "angle_back":0.027, "floor":"1"}, \
    {"name":"roadc2_F1", "x_coord":32.1, "y_coord":67.2, "angle":1.825, "angle_back":0.080, "floor":"1"}, \
    {"name":"inside1_F1", "x_coord":43.1, "y_coord":69.9, "angle":1.571, "angle_back":-1.316, "floor":"1"}, \
    {"name":"inside2_F1", "x_coord":56.2, "y_coord":69.8, "angle":1.5707, "angle_back":-1.571, "floor":"1"}, \
    {"name":"inside1_F2", "x_coord":56.2, "y_coord":69.8, "angle":-1.463, "angle_back":1.571, "floor":"2"}, \
    {"name":"Upstairs_Window", "x_coord":42.8, "y_coord":69.8, "angle":-1.571, "angle_back":1.571, "floor":"2"} ]

#same path but with starting angle offset by -pi/4
path_offset = [\
    {"name":"roada2_F1", "x_coord":21.1, "y_coord":46.9, "angle":2.375, "angle_back":-0.767, "floor":"1"}, \
    {"name":"roada3_F1", "x_coord":33.3, "y_coord":47.5, "angle":-3.114, "angle_back":-1.522, "floor":"1"}, \
    {"name":"roadc1_F1", "x_coord":33.1, "y_coord":54.8, "angle":-3.061, "angle_back":0.027, "floor":"1"}, \
    {"name":"roadc2_F1", "x_coord":32.1, "y_coord":67.2, "angle":1.825, "angle_back":0.080, "floor":"1"}, \
    {"name":"inside1_F1", "x_coord":43.1, "y_coord":69.9, "angle":1.571, "angle_back":-1.316, "floor":"1"}, \
    {"name":"inside2_F1", "x_coord":56.2, "y_coord":69.8, "angle":1.5707, "angle_back":-1.571, "floor":"1"}, \
    {"name":"inside1_F2", "x_coord":56.2, "y_coord":69.8, "angle":-1.463, "angle_back":1.571, "floor":"2"}, \
    {"name":"Upstairs_Window", "x_coord":42.8, "y_coord":69.8, "angle":-1.571, "angle_back":1.571, "floor":"2"} ]

#path with 1 node
path_1 = [{"name":"roada2_F1", "x_coord":21.1, "y_coord":46.9, "angle":2.375, "angle_back":-0.767, "floor":"1"}]

print("String Directions Tests")
string_path = path.copy()
string_path2 = path_offset.copy()
string_path3 = path_1.copy()
string_path = DBTools.string_directions(string_path)
string_path2 = DBTools.string_directions(string_path2)
string_path3 = DBTools.string_directions(string_path3)

#String directions tests
#Important: seen by all users, but a confusing result doesn't break the functionality of the app
for i in range(len(string_path)):
    #All should be equal: only angle change is at beginning, but first node is always assumed to be "head straight"
    assert(string_path[i]["string_direction"] == string_path2[i]["string_direction"])
    #I print all the directions for the test path here. The path is visualized in the image "data/map_test_reference.png" 
    #which I figured was the best way to demonstrate the correctness of the directions without making you just take my word for it
    #sorry it's not very convenient
    print(string_path[i]["string_direction"])


#if only one node in path, should say that you arrived
for node in string_path3:
    assert(node["string_direction"] == "You've arrived!")


print("\nLine Drawing Test")
line_path = path_offset.copy()
#Normally you would run this from command line in HospitalNav folder, but for simplicity I moved images to the database_interface
#folder that this testing file should be in

#Most of how I tested this during the project was just manual acceptance testing, so I do that here for our given path
#The first node has an offset different than 0 which shows its ability to handle that
#The path also crosses a floor change, showing how the path will truncate before an elevator
#Illustrates several times the handling of lines drawn around or across the image "seam"
#Also demonstrates the limitation where an occluded line will draw over a wall
#Sorry that this isn't super accessible for easy testing, this is essentially the process I used when doing my own tests during development
#Our expected result draws a line between the next 3 nodes unless that path intersects a floor change or there aren't 3 nodes remaining in the path
#Important: every user will see these lines, and they should be accurate. However, small inconsistencies don't break the functionality.
line_path = DBTools.next_nodes(line_path, segments=3, line_path="data/images/lines/", unit_to_ft=1, cam_height=6)
for node in line_path:
    background = Image.open("data/images/" + node["name"] + ".JPG")
    foreground = Image.open("data/images/lines/" + node["line_name"])
    background.paste(foreground, (0,0), foreground)
    background.show()
