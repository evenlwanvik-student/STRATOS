# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify, request, redirect, flash, \
    get_flashed_messages, url_for
import numpy as np
import json
import sys
import logging

# from data.zarr_to_geojson import zarr_to_geojson
# from data.zarr_to_topo import zarr_to_topo
# from data.get_cloud_json import get_json_blob

# If running outside container use this instead:
from data.zarr_to_geojson import zarr_to_geojson
from data.zarr_to_topo import zarr_to_topo
from data.get_cloud_json import get_json_blob
from data.zarr_to_velocity import zarr_to_velocity

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.secret_key = "superduper secret key"

@app.route('/')
def login():
	return redirect('/index')

@app.route('/index')
def index(error=""):
    logging.warning("redirected to index")
    return render_template('index.html', lat = 20, long = 2, zoom = 2)

@app.route('/location')
def location():
    logging.warning("redirected to location")
    return render_template('index.html', 
        name = 'Franfjorden', #Hardcoded, get from form maybe?
        zoom = 12,
        lat = 62.828181,    #Hardcoded at the moment, should be easy to read
        long = 7.130122)

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
                        zoom=6, lat=68.17184, lon=11.56522)


@app.route('/depthSeries')
def depthSeries():
    print("::::: redirected to depthSeries")
    depth = request.args.get('depth', 1, type=int)

    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}

    #Hardcoding for now
    startNode=(0,0)
    time = 1
    gridcells = 180

    # get the dataset and measurement type
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, , time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, startNode=startNode, depthIdx=depth, timeIdx=time, dataset=dataset_dict),
                        depthIdx=depth)

# Temporary routes used for testing purposes
@app.route('/getGeo')
def getGeo():
    '''
    # get the dataset and measurement type
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, , time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        return zarr_to_geojson(startNode=(0,0), nGrids=290, dataset=dataset_dict)
    '''
    return zarr_to_geojson(startNode=(0,0), nGrids=290)

@app.route('/makeTopo')
def makeTopo():
    # get the dataset and measurement type
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, , time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        return zarr_to_topo(startNode=(0,0), nGrids=290)

@app.route('/preMadeJSON')
def preMadeJSON():
    blob_name = request.args.get('blob_name', type=str)
    return jsonify(json=get_json_blob(blob_name), blob=blob_name)


@app.route('/getVelocityVector')
def getVelocityVector():
    ''' calls function to generate a velocity json object and returns to js for rendering'''
    logging.warning('redirected to "getVelocityVector"')

    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
 
    logging.warning(f'trying to generate a velocity vector object for {dataset_dict}')
    return jsonify(json=zarr_to_velocity())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

