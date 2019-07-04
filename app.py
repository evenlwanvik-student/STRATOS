# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify, request
from netCDF4 import Dataset
import numpy as np
import json
import sys
from data.getZoom import returnZoom
from data.netcdf_to_json import netcdf_to_json

app = Flask(__name__)

@app.route('/')
def login():
	return '<h1>Login</h1>'

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html', 
    name = 'World Map',
    lat = 20,
    long = 2,
    zoom = 2,
    menu = "dropMenuLocation")

@app.route('/location')
def location():
    zoom = returnZoom()  # this function needs to depend on number of grids
    return render_template('index.html', 
        name = 'Franfjorden', #Hardcoded, get from form maybe?
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom,
        menu = "dropMenuData")


@app.route('/geojson')
def geojson():
    zoom = returnZoom()
    netcdf_to_json(startEdge=(215,16), 
                            nGrids=60, 
                            gridSize=1, 
                            layerIdx=0,
                            timeIdx=0)

    with open ('data/outputs/surface_temp.json') as inf:
        jsondata = inf.read() #Not sure if its necessary to read, maybe possible to just dump
    return render_template('index.html', 
        name = 'Temperature data',  #Hardcoded, get from form maybe?
        geoData = jsondata, 
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom,
        menu = "inputField")


@app.route('/inputgrid', methods = ['POST', 'GET'])
def result():
 # todo: grid and startEdge should be moved inside if request==post when figured out
    post = request.form
    grid = 1
    grid = int(post['nGrids'])
    depth = int(post['depth'])
    startEdge = (219,19)
    #x = post[startEdge]
    #startEdge = x
    #print(x)
    #print(tuple (x))

    ''' DOES NOT WORK YET
        # if received request
        if request=='POST': # request==post doesn't always work, maybe it can't get post if stays on same route
            # set a new grid from user request
            grid = int(request.form['nGrids'])
    ''' 
    # set zoom, todo: make this dynamic depending on start and end grid?
    zoom = returnZoom()
    netcdf_to_json(startEdge=startEdge, nGrids=grid, layerIdx=depth)

    with open ('data/outputs/surface_temp.json') as inf:
        jsondata = inf.read() #Not sure if its necessary to read, maybe possible to just dump
    return render_template('index.html', 
        name = 'Customized grid', 
        geoData = jsondata, 
        lat = 62.8133,    #Hardcoded at the moment, should be easy to read
        long = 7.0035,
        zoom = zoom,
        menu = "inputField")
  

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

