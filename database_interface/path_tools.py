#Trevor Roussel
#additional tools and information for the path: string directions, line drawing, etc

import numpy as np
import PIL
from PIL import ImageDraw
from PIL import Image

#get next n nodes on current map
def get_next_n(path, current_ind, n=3):
    next = [path[current_ind]]
    floor = path[current_ind]['floor']
    for i in range(1, n+1):
        if len(path) <= current_ind+i or floor != path[current_ind+i]['floor']:
            return next
        next.append(path[current_ind+i])
    return next

#set angles outside range (-pi, pi) to valid range
def reg_angle(angle):
    while(angle > np.pi):
        angle -= 2*np.pi
    while(angle < -np.pi):
        angle += 2*np.pi
    return angle

#get angle of 2d vector from north vector
def angle_to(vec):
    #in the case of a zero vector, assume we always consider the path taken as straight
    if all(components == 0 for components in vec):
        return 0.0
    b = vec_dist(vec)
    #north vector is (0, -1) for top-left coorinate system
    c = vec_dist((vec[0], vec[1]+1)) 
    angle = law_cosines(1, b, c)
    #arccos has range 0, pi. adjust for -pi, pi:
    if vec[0] < 0:
        angle = -angle
    return angle

#get length of vector
def vec_dist(vec, norm=2):
    sum = 0
    for component in vec:
        sum += component**norm
    return (sum**(1/norm))

#get angle from triangle side lengths
def law_cosines(a, b, c):
    return (np.arccos((a**2 + b**2 - c**2)/(2*a*b)))

#given a path, find from-north angle using trig, offset is what to add to north angle to get real angle
def find_offset(vec, real_angle):
    north_angle = angle_to(vec)
    return reg_angle(real_angle-north_angle)

#given an equirectangular image projection, get location of endpoint of a polar vector on floor. assume flat ground and camera at height cam_height
#distance is in feet (which only matters if passing cam_height argument)
#w & h define size of image
def pixel_coords(h_angle, dist, x_buff, w=1920, h=1080, cam_height=6):
    #equirectangular linearly spaces angles from -pi to pi. map to pixel coord:
    x = int((h_angle/(2*np.pi) + .5) * w + x_buff)
    b = (cam_height**2 + dist**2)**(1/2)
    v_angle = law_cosines(cam_height, b, dist) #angle of elevation to endpoint
    #coordinates are from top-left, subtract from height for real coords
    y = h-int(h/np.pi * v_angle)
    return (x, y)

#for photospheres, may want to wrap the line around sides of the image if it's closer than going across 
def wrap_line(coords, im: Image, linew):
    w = im.width
    w_adj = w - 2*linew
    path = []
    segment = [(coords[0][0], coords[0][1])]
    for i in range(len(coords)-1):
        x_dist_straight = np.abs(coords[i][0] - coords[i+1][0])
        x_dist_wrap = w_adj - x_dist_straight
        if(x_dist_straight > x_dist_wrap):
            #linear intercept of edge of screen and y coord
            if coords[i][0] < w_adj/2:
                y_int = int(coords[i][1] + ((coords[i+1][1]-coords[i][1])/x_dist_wrap)*(coords[i][0]-linew))
                segment.append((linew, y_int))
                path.append(segment)
                segment = [(w-linew, y_int)]
            else:
                y_int = int(coords[i][1] + ((coords[i+1][1]-coords[i][1])/x_dist_wrap)*(w-linew-coords[i][0]))
                segment.append((w-linew, y_int))
                path.append(segment)
                segment = [(linew, y_int)]
        segment.append((coords[i+1][0], coords[i+1][1]))
    path.append(segment)
    return path

#for proper display of lines around the image seam, need to combine the information on the "gutters"
#combine by taking max color of pixel
def max_merge_gutters(im: Image, gutw):
    w = im.width
    h = im.height
    left = im.crop((0, 0, gutw, h))
    right = im.crop((w-gutw, 0, w, h))
    im = max_merge_offset(im, left, (w-2*gutw,0))
    im = max_merge_offset(im, right, (gutw, 0))
    return im

#take a big image and merge colors to take maximum value for overlay image at given top-left offset
def max_merge_offset(imBig: Image, overlay: Image, offset):
    pixelsB = imBig.load()
    pixelsO = overlay.load()
    o_w = overlay.width
    o_h = overlay.height
    for x in range(o_w):
        for y in range(o_h):
            pixelsB[x+offset[0], y+offset[1]] = ( \
                max(pixelsB[x+offset[0], y+offset[1]][0], pixelsO[x,y][0]), \
                max(pixelsB[x+offset[0], y+offset[1]][1], pixelsO[x,y][1]), \
                max(pixelsB[x+offset[0], y+offset[1]][2], pixelsO[x,y][2]), \
                max(pixelsB[x+offset[0], y+offset[1]][3], pixelsO[x,y][3]))
    return imBig

#draw a line overlay given a node and partial path of next connections and size of overlay image
def draw_line(ppath, save_path, w=1920, h=1080, cam_height=6, linew=25):
    #no path to draw:
    if(len(ppath)) <= 1:
        return

    name = "line"
    for node in ppath:
        name += "_" + node["name"]

    #new transparent image: expand width to deal with line wrapping problem
    line_image = Image.new("RGBA", [w+2*linew, h], (0,0,0,0))
    curr_pos = (ppath[0]["x_coord"], ppath[0]["y_coord"])
    vec = (ppath[1]["x_coord"]-curr_pos[0], ppath[1]["y_coord"]-curr_pos[1])
    angle_offset = find_offset(vec, ppath[0]["angle"])
    #pixel coordinates for first connection: angle already known
    pix_coords = [(int((ppath[0]["angle"]/(2*np.pi) + .5) * w + linew), h)]
    pix_coords.append(pixel_coords(ppath[0]["angle"], vec_dist(vec), linew, w, h, cam_height))
    #get pixel coordinates for all following connections
    for i in range(2, len(ppath)):
        vec = (ppath[i]["x_coord"]-curr_pos[0], ppath[i]["y_coord"]-curr_pos[1])
        angle = reg_angle(angle_to(vec) + angle_offset)
        pix_coords.append(pixel_coords(angle, vec_dist(vec), linew, w, h, cam_height))

    pix_path = wrap_line(pix_coords, line_image, linew)
    imdraw = ImageDraw.Draw(line_image)
    for segment in pix_path:
        imdraw.line(segment, width=linew, fill=(0, 0, 255), joint='curve')
        xy = segment[-1]
        box = [(xy[0]-linew/2, xy[1]-linew/2), (xy[0]+linew/2, xy[1]+linew/2)]
        imdraw.ellipse(box, fill=(0, 0, 255))

    #merge the extra information in the image "gutters" to deal with weird behavior around the seams. keep lines at normal thickness
    line_image = max_merge_gutters(line_image, linew)
    save_image = line_image.crop((linew, 0, w+linew, h))
    save_image.save(save_path+name+'.png')


# ppath = [{"name":"roada2_F1", "x_coord":21.1, "y_coord":46.9, "angle":2.51}, \
#     {"name":"roada3_F1", "x_coord":33.3, "y_coord":47.5, "angle":-3.114}, \
#     {"name":"roadc1_F1", "x_coord":33.1, "y_coord":54.8, "angle":-3.061}, \
#     {"name":"roadc2_F1", "x_coord":32.1, "y_coord":67.2, "angle":-1.4644}, \
#     {"name":"roadg1_F1", "x_coord":21.8, "y_coord":66.1, "angle":-1.5707}, \
#     {"name":"roadg2_F1", "x_coord":9.7, "y_coord":65.7, "angle":-1.5707}]

# draw_line(ppath, "data/images/lines/")

