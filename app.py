# app.py - minimal flask API for rendering a single netCDF file

from flask import Flask, render_template, jsonify
from netCDF4 import Dataset
import numpy as np
import json
import os

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

@app.route('/getgeojson')
def getegeojson():
    return render_template('geojson.html')

#@app.route('/keys')
#def read_nc_data():
#    nc = Dataset('/home/even/netCDFdata/samples_NSEW_2013.03.11.nc')
#    keys = list(nc.variables.keys())
#    return render_template("keys.html", len = len(keys), keys = keys)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
