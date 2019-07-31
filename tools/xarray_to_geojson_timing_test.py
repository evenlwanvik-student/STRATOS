import xarray as xr
import json
import numpy
import os
from copy import deepcopy
import time # for execution time testing
import math
import sys
import zarr
from ..data import zarr_to_geojson

# ******* Initialize test ***************

# Get the initial template, the data variable will hold all temporary data
data = zarr_to_geojson.get_initial_template() 
# Get the feature template, this will be appended to data for each feature inserted
feature_template = zarr_to_geojson.get_feature_template()

timeIdx  = 0
depthIdx = 1


# Create local xarrays by copying subsets of the zarr
# Xarray is "lazy loading" so printing elements is to ensure 
# that the zarr downloading happens before the timer starts
startOpen=time.time()
with xr.open_zarr(zarr_to_geojson.absstore_zarr) as source: 
    end =time.time()
    print ('**********Time spent opening zarr as xarray', end-startOpen)
    startCopy=time.time()
    print("::::: copying temperature data")
    temps = deepcopy(source['temperature'][timeIdx,depthIdx])
    print("Last temp item: ", temps[-1])

    print("::::: copying latitude data")
    lats = deepcopy(source['gridLats'])
    print("Last latitude item: ", lats[-1])

    print("::::: copying longitude data")
    lons = deepcopy(source['gridLons'])
    print("Last longitude item: ", lons[-1])
end=time.time()
print('*********** Total deepcopy time: ', end-startCopy)

#************  Initializing done   ********************************

# DEFINE TESTING PARAMETERS
latitude_elements = 1
longitude_elements = 1

startEdge = (220,20)

startTest = time.time()
# featureIdx counts what feature we are working on = 0,1,2,3, ... 
featureIdx = 0
for y in range(latitude_elements):                 
    for x in range(longitude_elements): 
        print("********* making grid ", featureIdx) 
        # get the start edge of the next polygon to be inserted into dictionary
        edge = (startEdge[0]+y, startEdge[1]+x)       
        # if temp=nan: skip grid -> else: insert lat/lon and temp into data
        start =time.time()
        temp = float(temps[edge]) 
        end = time.time()
        print ('*********** extracting tempature from array: ', end-start)
        if math.isnan(temp):
            continue
        else:
            # add a copy of the feature dictionary template to features
            start =time.time()
            data['features'].append(deepcopy(feature_template))  
            end = time.time()
            print ('************* add a copy of the feature dictionary template to features: ', end-start)

            # create a reference to the current feature we are working on
            start =time.time()
            feature = data['features'][featureIdx]
            end = time.time()
            print ('************ create a reference to the current feature we are working on: ', end-start)

            # insert hex into fill
            start =time.time()
            feature['properties']['fill'] = zarr_to_geojson.geojson_grid_temp(temp) 
            end = time.time()
            print ('************ insert hex into fill: ', end-start)
           
            # copying netcdf data into the given feature position
            start =time.time()
            feature['geometry']['coordinates'][0] = zarr_to_geojson.geojson_grid_coord(lats, lons, edge) 
            end = time.time()
            print ('********** copying netcdf data into the given feature position: ', end-start)
                            
        
            featureIdx = featureIdx + 1
end = time.time()
print("********** Conversion time:",end-startTest)


start = time.time()
zarr_to_geojson.write_output(data)
end = time.time()
print("*********** Time spent writing to ouput file:",end-start)






