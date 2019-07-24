# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify, request, redirect, flash, \
    get_flashed_messages, url_for
from netCDF4 import Dataset
import numpy as np
import json
import sys
import logging

from data.getZoom import returnZoom
from data.zarr_to_geojson import zarr_to_geojson
from data.zarr_to_topo import zarr_to_topo

# If running outside container use this instead:
# from .data.getZoom import returnZoom
# from .data.zarr_to_geojson import zarr_to_geojson
# from .data.zarr_to_topo import zarr_to_topo

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.secret_key = "superduper secret key"

@app.route('/')
def login():
	return redirect('/home')

@app.route('/home')
def home():
    return render_template('README.html')

@app.route('/index')
def index(error=""):
    logging.warning("redirected to index")
    return render_template('index.html', lat = 20, long = 2, zoom = 2)

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
    jsondata = zarr_to_geojson(startEdge=startEdge, nGrids=gridcells, depthIdx=depth)
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
    zarr_to_geojson(startEdge=startEdge, nGrids=grid, depthIdx=depth)

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
    depth = request.args.get('depth', 0, type=int)
    time = request.args.get('time', 0, type=int)

    # get the dataset and measurement type
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, depthIdx=depth, timeIdx=time, dataset=dataset_dict),
                        zoom=returnZoom(), lat=62.8133, lon=7.0035)

@app.route('/timelapse')
def timelapse():
    print("::::: redirected to timelapse")
    time = request.args.get('time', 1, type=int)
    #Hardcoding for now
    startEdge=(0,0)
    depth = 1
    gridcells = 290

    jsondata = zarr_to_geojson(startEdge=startEdge, nGrids=gridcells, depthIdx=depth, timeIdx=time)
    return jsonify(geojson=jsondata, time=time) 


@app.route('/depthSeries')
def depthSeries():
    print("::::: redirected to depthSeries")
    depth = request.args.get('depth', 1, type=int)

    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}

    #Hardcoding for now
    startEdge=(0,0)
    time = 1
    gridcells = 180

    jsondata = zarr_to_geojson(dataset=dataset_dict, startEdge=startEdge, nGrids=gridcells, depthIdx=depth, timeIdx=time)
    return jsonify(geojson=jsondata, depthIdx=depth) 


@app.route('/topoJSON')
def topoJSON():
    with open ('data/outputs/topoData.json') as inf:
        jsondata = inf.read() #Not sure if its necessary to read, maybe possible to just dump
        print("::::: topoJSON file was read")
    return jsonify(jsondata)

@app.route('/getGeo')
def getGeo():
    jsondata=zarr_to_geojson(startEdge=(0, 0), nGrids=290)
    return jsondata

@app.route('/makeTopo')
def makeTopo():
    jsondata=zarr_to_topo(startEdge=(0, 0), nGrids=290)
    return jsondata

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

