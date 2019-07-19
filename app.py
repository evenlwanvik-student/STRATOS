# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify, request, redirect
from netCDF4 import Dataset
import numpy as np
import json
import sys
import logging
from data.getZoom import returnZoom
from data.azure_to_json import azure_to_json

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)

@app.route('/')
def login():
	return redirect('/home')

@app.route('/home')
def home():
    return render_template('README.html')

@app.route('/index')
def index():
    logging.warning("redirected to index")
    return render_template('index.html',        
    name = 'World Map',
    lat = 20,
    long = 2,
    zoom = 2)

@app.route('/location')
def location():
    logging.warning("redirected to location")
    zoom = returnZoom()  # this function needs to depend on number of grids
    return render_template('index.html', 
        name = 'Franfjorden', #Hardcoded, get from form maybe?
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom)


@app.route('/geojson')
def geojson():
    logging.warning("redirected to geojson")
    gridcells = 0
    depth = 0
    startEdge=(0,0)
    jsondata = azure_to_json(startEdge=startEdge, nGrids=gridcells, depthIdx=depth)
    zoom = returnZoom()
    return render_template('index.html', 
        name = 'Temperature data',  #Hardcoded, get from form maybe?
        geoData = jsondata, 
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom)

#Nothing routes to this for the time being... should be removed eventually?
'''
@app.route('/inputgrid', methods = ['POST', 'GET'])
def result():
    logging.warning("redirected to inputgrid")
 # todo: grid and startEdge should be moved inside if request==post when figured out
    post = request.form
    grid = 1
    grid = int(post['nGrids'])
    depth = int(post['depth'])
    startEdge = (0,0)

    # set zoom, todo: make this dynamic depending on start and end grid?
    zoom = returnZoom()
    azure_to_json(startEdge=startEdge, nGrids=grid, depthIdx=depth)

    with open ('data/outputs/surface_temp.json') as inf:
        jsondata = inf.read() #Not sure if its necessary to read, maybe possible to just dump
    return render_template('index.html', 
        name = 'Customized grid', 
        geoData = jsondata, 
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom)
'''

@app.route('/loadGeojson')
def loadGeojson():
    logging.warning("redirected to loadGeojson")
    gridcells = request.args.get('gridcells', 1, type=int)
    depth = request.args.get('depth', 1, type=int)

    # get the dataset and measurement type
    dataset_dict = {'dataset': request.args.get('dataset', 'Franfjorden32m', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}

    logging.warning(dataset_dict)

    startEdge=(0,0)
    jsondata = azure_to_json(startEdge=startEdge, nGrids=gridcells, depthIdx=depth, dataset=dataset_dict)
    zoom = returnZoom()
    lat = 62.8133    #Hardcoded at the moment, should be easy to read
    lon = 7.0035
    return jsonify(geojson=jsondata, zoom=zoom, lat=lat, lon=lon)

@app.route('/timelapse')
def timelapse():
    print("::::: redirected to timelapse")
    time = request.args.get('time', 1, type=int)
    #Hardcoding for now
    startEdge=(0,0)
    depth = 1
    gridcells = 290

    jsondata = azure_to_json(startEdge=startEdge, nGrids=gridcells, depthIdx=depth, timeIdx=time)
    return jsonify(geojson=jsondata, time=time) 


@app.route('/depthSeries')
def depthSeries():
    print("::::: redirected to depthSeries")
    depth = request.args.get('depth', 1, type=int)
    #Hardcoding for now
    startEdge=(0,0)
    time = 1
    gridcells = 290

    jsondata = azure_to_json(startEdge=startEdge, nGrids=gridcells, depthIdx=depth, timeIdx=time)
    return jsonify(geojson=jsondata, depthIdx=depth) 


@app.route('/topoJSON')
def topoJSON():
    with open ('data/outputs/topoData.json') as inf:
        jsondata = inf.read() #Not sure if its necessary to read, maybe possible to just dump
        print("::::: topoJSON file was read")
    return jsonify(jsondata)

@app.route('/getGeo')
def getGeo():
    with open ('data/outputs/geojson.json') as inf:
        jsondata = inf.read()
    return jsonify(jsondata)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

