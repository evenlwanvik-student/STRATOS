import json
import numpy as np
import os
from copy import deepcopy
import time
import math
import zarr
import sys
import logging
import warnings
from data.color_encoding import temp_to_rgb, set_colormap_range

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

'''
 1. load template geojson file as DATA
 2. load output geojson file as output
 3. using data loaded by the dataset module
 4. run function for inserting source data into the temporary (templated) data file
 5. dump the data file into outputfile (the geojson file to be used in leaflet)
 create subgrid with indexes:
 (221,19) - (222,20) -> polygon "route" becomes (221,19), (221,20), (222,20), (222,19), (221,19)
 
     *(221,19) -> (221,2)
         ^          |
      (221,20) <- (222,20)                         
'''

# define paths to files
initial_template_path = "data/templates/initial_template.json"
feature_template_path = "data/templates/feature_template.json"


#TODO: Old method of creating the polygon, remove before pull?
def geojson_grid_coord(lats, lons, startEdge):
    '''
    takes a xarray object of a netCDF file as source and variable loaded
    with a geojson dictionary template as target. 
    gridDim is the size of the square grid to be rendered, default is 2 (2x2)
    To show differences in temperature, the temperature is encoded into 
    rgb hexadecimal and inserted into the "fill" under "properties" of the 
    polygon. The polygon itself is inserted into the "coordinates" key under "geometry"
     
    nested loop:
    1. for each square within a given size
    2. y-direction 
    3. x-direction 
    always iterate over polygonedges and squares in the same convention as in moduledescription
    TODO: research multipolygon instead of simply using polygon, maybe we don't need to define every edge
    '''
    coords = []
    # the box is 2x2, this will be made dynamic in the future
    xyRange = range(2)              
    for y in xyRange: # iterate y
        innerRange = xyRange              
        if y == 1:
            innerRange = reversed(xyRange)     # backward iteration to complete the polygon
        for x in innerRange: # iterate x
            yx = (startEdge[0]+y, startEdge[1]+x) # (y,x) defined as such in the netCDF file
            lat  = float(lats[yx])
            lon  = float(lons[yx])
            # OBS! The GIS lat/lon is different from geojson standard, so these are "flipped"
            coords.append([lon, lat])
    # the last list must always be the same as the first 
    coords.append(coords[0])     
    return coords
  

def get_initial_template():
    with open(initial_template_path, "r") as template:
        return json.load(template)


def get_feature_template():
    return {"type": "Feature",
            "properties": {"fill": "#00aa22"},
            "geometry": {   "type": "Polygon",
                            "coordinates": []}}


#azure_to_json should just return the json object instead of writing it to file.
#TODO: remove if deemed unecesarry in future, keeping it in case we decide to roll back
def write_output(data):
    output_path = "data/outputs/geojson.json"
    # open and dump data to output geojson file, remove if exists
    if os.path.isfile(output_path):
        os.remove(output_path)
    # open the final product file as output 
    with open(output_path, "w+") as output: 
        # dump new data into output json file 
        json.dump(data, output, indent=4)  

def create_blob_client(dataset):
    ''' TODO: This should be made to properly react to user input, for now we only
    switch between one measurement per norsok and franfjorden. 
    It should also be able to react to type of measurement, e.g. temperature, wind..'''

    CONTAINER_NAME  = 'zarr'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
    absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, dataset, ACCOUNT_NAME, ACCOUNT_KEY)
    return absstore_object


def set_colormap_encoding_range(measurements, fill_value):
    # finding min/max for color encoding for this grid, this should
    if fill_value == np.NaN:
        set_colormap_range({'min': measurements.nanmin(), 'max': measurements.nanmax()})
    elif fill_value == -32768:
        # omit fillvalues for finding minimum..
        x = measurements[measurements > -32768]
        set_colormap_range({'min': x.min(), 'max': x.max()})
    else:
        warnings.warn("unknown encoding of fill_value, insert in this if-else-section")

def get_correct_dimensions(dataset):
    ''' Different names of latitude/longitude. Most likely a multitude of metadata will
    vary in the future, this should be properly managed. Currently this function takes 
    ataset name as argument and returns the correct lat/(lon encoding'''

    if (dataset.split('/')[0] == 'OSCAR'):
        return ("latitude_bounds", "longitude_bounds")
    else:
        return ("gridLats", "gridLons")

# TODO: Problems with shape, just run it...

def get_decompressed_arrays(dataset, depthIdx=0, timeIdx=0):
    # azure zarr-blob object
    absstore_obj = create_blob_client(dataset['dataset'])
    (latalias, lonalias) = get_correct_dimensions(dataset['dataset'])
    datatype = dataset['measurementtype']
    print(latalias)
    section_start = time.time()
    decom_meas = zarr.blosc.decompress(absstore_obj['{}/{}.{}.0.0'.format(datatype,timeIdx,depthIdx)])
    decom_lats = zarr.blosc.decompress(absstore_obj['{}/0.0'.format(latalias)])
    decom_lons = zarr.blosc.decompress(absstore_obj['{}/0.0'.format(lonalias)])
    end = time.time()
    logging.warning("decompressing azure blob chunks execution time: %f",end-section_start)

    #The metadata for coodinates might be different from the measurement
    coord_metadata = json.loads(absstore_obj['{}/.zarray'.format(latalias)])
    meas_metadata = json.loads(absstore_obj['{}/.zarray'.format(datatype)])
    coord_shape = tuple(coord_metadata['chunks'])
    meas_shape = coord_shape
    coord_datatype = coord_metadata['dtype']
    meas_datatype = meas_metadata['dtype']

    # create numpy arrays from the decompressed buffers and give it our grid shape
    section_start = time.time()
    lons = np.frombuffer(decom_lats, dtype=coord_datatype).reshape(coord_shape)
    lats = np.frombuffer(decom_lons, dtype=coord_datatype).reshape(coord_shape)
    measurements = np.array(np.frombuffer(decom_meas, dtype=meas_datatype).reshape(meas_shape))
    end = time.time()
    logging.warning("creating numpy arrays of decompresed arrays execution time: %f",end-section_start)

    return([lons, lats, measurements, meas_metadata['fill_value']])

def azure_to_json(startEdge=(0,0), 
                    nGrids=10, 
                    gridSize=1, 
                    depthIdx=0,
                    timeIdx=0,
                    dataset={'dataset':'Franfjorden32m', 'measurementtype':'temperature'}):
    ''' 
    Inserts netCDF data from 'startEdge' in a square of size 'nGrids' in positive lat/lon
    index direction into a geojson whose path is described as output. 
    It appends geojson template dictionaries from a given file-path into a 
    temporary data variable, whose data is changed and dumped into output object.

    Parameters
    ----------
    depthIdx : int
        the depth of the grid to be computed
    timeIdx : string
        the time index of the grid to be computed
    filetype : dict
        dictionary containing what dataset and measurement type to be computed
    '''
    start = time.time() 

    # Get the initial template
    jsonData = get_initial_template() 
    # Get the feature template, this will be appended to jsonData for each feature inserted

    # download z-arrays from azure cloud and decompress requested chunks
    [lons, lats, measurements, fill_value] = get_decompressed_arrays(dataset, timeIdx, depthIdx)

    # find min and max and set the color encoding for displaying change on map
    set_colormap_encoding_range(measurements, fill_value)

    # featureIdx counts what feature we are working on = 0,1,2,3, ... 
    featureIdx = 0
    for y in range(nGrids):                 
        for x in range(nGrids):   
            measurement = measurements[(y,x)]
            # if temp=nan: skip grid -> else: insert lat/lon and temp into data
            if np.isnan(measurement) or measurement == -32768:
                continue
            else:
                # add a copy of the feature dictionary template to features
                jsonData['features'].append(get_feature_template())
                # create a reference to the current feature we are working on
                feature = jsonData['features'][featureIdx]
                # insert hex into fill
                feature['properties']['fill'] = temp_to_rgb(measurement) 
 
                # insert lat/lon data. each line is a grid coordinate in a polygon sequence.
                # i.e. (0,0) -> (0,1) -> (1,1) -> (1,0) -> (0,0)
                # rounding from 16 (64bit) to 4 decimals, convert to string for json serialization
                feature['geometry']['coordinates'].append( [
                    [str(round(lons[y,x],4)), str(round(lats[y,x],4))],
                    [str(round(lons[y,x+1],4)), str(round(lats[y,x+1],4))],
                    [str(round(lons[y+1,x+1],4)), str(round(lats[y+1,x+1],4))],
                    [str(round(lons[y+1,x],4)), str(round(lats[y+1,x],4))],
                    [str(round(lons[y,x],4)), str(round(lats[y,x],4))]
                ] )
                
                featureIdx = featureIdx + 1

    logging.warning("showing %s for %s", dataset['measurementtype'], dataset['dataset'])
    logging.warning("startEdge: %s, nGrids: %d, depthIdx: %d, timeIdx: %d",startEdge,nGrids,depthIdx,timeIdx)

    end = time.time()
    logging.warning("total execution time of azure to json function: %f",end-start)
    #write_output(jsonData)
    return jsonData


# TODO: Keep this for quick-testing of both algorithm and execution time..
'''
dataset={'dataset':'Franfjorden32m', 'measurementtype':'temperature'}
#dataset={'dataset':'Franfjorden32m', 'measurementtype':'salinity'}
#dataset={'dataset':'norsok', 'measurementtype':'temperature'}

N = 5
start = time.time()
for i in range(N):
    azure_to_json(nGrids=200, 
                        depthIdx=0,
                        timeIdx=0,
                        dataset=dataset)
end = time.time()
logging.warning("average execution time: %f", (end-start)/N)
'''