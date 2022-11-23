#!/usr/bin/env python
# encoding: utf-8
import json
import random
from DBTools import loadDB
from DBTools import shortestPath
from DBTools import getEndpoints
from DBTools import getStartpoints
import os
import pyorient
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__, static_folder = './templates')

filepath = './data/testmap_nodes_angles.json'
loadDB(filepath)
shortestPath("roada1_F1", "Upstairs_Window")

@app.route('/')
def home():
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    return render_template('main-page.html', endpoints=getEndpoints(client), startpoints=getStartpoints(client), start='NULL', end='NULL', path=[], jsonPath=json.dumps([]))
    
@app.route('/<string:start>&<string:end>', methods=['GET'])
def directions(start, end):
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    
    path = []
    
    if (start != 'NULL') and (end != 'NULL'):
        path=shortestPath(start, end)
    
    return render_template('main-page.html', endpoints=getEndpoints(client), startpoints=getStartpoints(client), start=start, end=end, path=path, jsonPath=json.dumps(path))

@app.route('/get_endpoints', methods=['GET'])
def get_endpoints():
    dbname = "locations"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)
    return jsonify(getEndpoints(client))
    
@app.route('/get_image/<string:name>', methods=['GET'])
def get_image(name):
    return send_file('../data/images/' + name + '.jpg', mimetype='image/gif')

@app.route('/get_line_image/<string:name>', methods=['GET'])
def get_line_image(name):
    return send_file('../data/images/lines/' + name, mimetype='image/gif')

@app.route('/reset', methods=['GET'])
def reset():
    filepath = './data/KYCTestValues.json'
    loadDB(filepath)
    return jsonify("reset")

@app.route('/shortest_path/<string:start>&<string:end>', methods = ['GET'])
def shortest_path(start, end):
  
    return jsonify(shortestPath(start, end))

app.run(debug=True)
