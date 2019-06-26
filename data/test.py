import xarray as xr
import json
import numpy
import time
from copy import deepcopy

# define paths to files
initial_template_path = "templates/initial_template.json"
feature_template_path = "templates/feature_template.json"
source_path = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
output_path = "outputs/surface_temp.json"


with xr.open_dataset(source_path) as source: # load netCDF file to "source" 

    gridSize = 10
    temps = deepcopy(source['temperature'][0,0][::gridSize,::gridSize])
    lats = deepcopy(source['gridLats'][::gridSize,::gridSize])
    lons = deepcopy(source['gridLons'][::gridSize,::gridSize])
    print temps
    print lats
    print lons


'''
nGrids = 1
y=1
x=1
start = time.time()
for i in range(100):
    featureIdx = nGrids*y + x 
end = time.time()    
print end-start


start = time.time()
featureIdx = 0
for i in range(100):
    featureIdx = featureIdx + 1
end = time.time()
print end-start





'''