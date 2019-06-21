# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify
from netCDF4 import Dataset
import numpy as np
import json

app = Flask(__name__)

@app.route('/')
def login():
	return '<h1>Login</h1>'

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')


#@app.route('/getgeojson')
#def get_geojson():
    # use a netcdf to json script (e.g. "netcdf2geojson.py") which will
    # decode the netcdf file and insert the data into a template html file
    # return the HTML file for rendering 
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
