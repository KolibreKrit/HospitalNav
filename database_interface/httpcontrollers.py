#!/usr/bin/env python
# encoding: utf-8
import json
import random

from DBTools import simpleLoadDB
from DBTools import simpleShortestPath
from DBTools import loadDB
from DBTools import shortestPath


from DBTools import getEndpoints
from DBTools import getStartpoints
import os
import pyorient
from flask import Flask, request, jsonify, render_template, send_file

print(os.getcwd())
app = Flask(__name__, static_folder = './templates')

# filepath = './data/testmap_nodes_angles.json'
filepath = './data/KYCTestValues.json'
simple = False

# if filepath == './data/KYCTestValues.json':
#     simple = True

if simple:
    simpleLoadDB(filepath)
else:
    loadDB(filepath)

@app.route('/')
def home():
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("172.17.0.2", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    if simple:
        return render_template('simple-main-page.html', 
                            endpoints=getEndpoints(client), 
                            startpoints=getStartpoints(client), 
                            start='NULL', 
                            end='NULL', 
                            path=[], 
                            jsonPath=json.dumps([]))
    else:
        return render_template('main-page.html', 
                            endpoints=getEndpoints(client), 
                            startpoints=getStartpoints(client), 
                            start='NULL', 
                            end='NULL', 
                            path=[], 
                            jsonPath=json.dumps([]))
    
@app.route('/<string:start>&<string:end>', methods=['GET'])
def directions(start, end):
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("172.17.0.2", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    
    path = []
    
    if (start != 'NULL') and (end != 'NULL'):
        if simple:
            path = simpleShortestPath(start, end)
        else:
            path = shortestPath(start, end)
    
    if simple:
        return render_template('simple-main-page.html', 
                            endpoints=getEndpoints(client), 
                            startpoints=getStartpoints(client), 
                            start=start, 
                            end=end, 
                            path=path, 
                            jsonPath=json.dumps(path))
    else:
        return render_template('main-page.html', 
                            endpoints=getEndpoints(client), 
                            startpoints=getStartpoints(client), 
                            start=start, 
                            end=end, 
                            path=path, 
                            jsonPath=json.dumps(path))

@app.route('/get_endpoints', methods=['GET'])
def get_endpoints():
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("172.17.0.2", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    return jsonify(getEndpoints(client))
    
@app.route('/get_image/<string:name>', methods=['GET'])
def get_image(name):
    if simple:
        return send_file('../data/images/' + name + '.JPG', mimetype='image/gif')
    else:
        return send_file('../data/images/' + name + '.JPG', mimetype='image/gif')

@app.route('/reset', methods=['GET'])
def reset():
    loadDB(filepath)
    return jsonify("reset")

@app.route('/shortest_path/<string:start>&<string:end>', methods = ['GET'])
def shortest_path(start, end):
  
    return jsonify(shortestPath(start, end))

app.run(host='0.0.0.0', port=36824, debug=True)
