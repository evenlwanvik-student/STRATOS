# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify, request, redirect, flash, \
    get_flashed_messages, url_for, make_response
import numpy as np
import json
import sys
import logging

from data.zarr_to_geojson import zarr_to_geojson
from data.zarr_to_topo import zarr_to_topo
from data.get_cloud_json import get_json_blob
from data.zarr_to_velocity import zarr_to_velocity

'''
# If running outside container use this instead:
from .data.zarr_to_geojson import zarr_to_geojson
from .data.zarr_to_topo import zarr_to_topo
from .data.get_cloud_json import get_json_blob
from .data.zarr_to_velocity import zarr_to_velocity
'''

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

@app.route('/readme')
def readme():
	return render_template('README.html')

@app.route('/loadGeojson')
def loadGeojson():
    logging.warning("redirected to loadGeojson")
    
    gridcells = request.args.get('gridcells', 1, type=int)
    depth = request.args.get('depth', 0, type=int)
    time = request.args.get('time', 0, type=int)
    startVertex = (request.args.get('lat_idx', 0 , type=int), request.args.get('long_idx', 0 , type=int)) 

    logging.warning('start node: %s', startVertex)

    # get the dataset and measurement type
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}
    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        if dataset_dict['blobpath']=='Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr':
            return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, depthIdx=depth, timeIdx=time, dataset=dataset_dict, startNode=startVertex),
                        zoom = 12, lat = 62.828181, lon = 7.130122)
        elif dataset_dict['blobpath']=='norsok/samples_NSEW.nc_201301_nc4.zarr':
            return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, depthIdx=depth, timeIdx=time, dataset=dataset_dict, startNode=startVertex),
                        zoom = 5, lat = 56.676736, lon = 3.529368)
        else:
            return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, depthIdx=depth, timeIdx=time, dataset=dataset_dict,startNode=startVertex),
                        zoom = 7, lat = 68.014998, lon = 12.075042)

        


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


@app.route('/timelapse')
def timelapse():
    print("::::: redirected to timelapse")
    time = request.args.get('time', 0, type=int)
    dataset_dict = {'blobpath': request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str), 
                    'measurementtype': request.args.get('datatype', "temperature", type=str)}

    #Hardcoding for now
    startNode=(0,0)
    depth = 0
    gridcells = 240

    if not all(dataset_dict.values()):
        error = f'one or more arguments are missing: {dataset_dict},  gridcells: {gridcells}, depth: {depth}, , time: {time}'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a geojson object for {dataset_dict}')
        return jsonify(geojson=zarr_to_geojson(nGrids=gridcells, startNode=startNode, depthIdx=depth, timeIdx=time, dataset=dataset_dict),
                        timeIdx=time)



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
    logging.warning('redirected to preMadeJSON')
    depth = request.args.get('depth', type=int)
    blob_name = 'topojson_d'+str(depth)+'.json'
    return get_json_blob(blob_name)


@app.route('/velocitydemo')
def velocitydemo():
    ''' render velocity-demo template '''

    logging.warning('redirected to "velocity-demo"')
    return render_template("velocity-demo.html")


@app.route('/getWindVelocityVectors')
def getWindVelocityVector():
    ''' calls function to generate a velocity json object and returns json obj layer'''

    logging.warning('redirected to "getWindVelocityVector"')

    blobpath = request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str)
    if not blobpath:
        error = f'blobpath: {blobpath} missing'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a wind velocity object for {blobpath}')
        return make_response( zarr_to_velocity(blobpath = blobpath, wind_flag=True) )

@app.route('/getOceanCurrentVectors')
def getOceanCurrentVectors():
    ''' calls function to generate a velocity json object and returns json obj layer'''

    logging.warning('redirected to "getOceanCurrentVectors"')

    blobpath = request.args.get('blobpath', 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', type=str)
    if not blobpath:
        error = f'blobpath: {blobpath} missing'
        raise ValueError(error)
    else:
        logging.warning(f'trying to generate a ocean current object for {blobpath}')
        return make_response( zarr_to_velocity(blobpath = blobpath, wind_flag=False) )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

