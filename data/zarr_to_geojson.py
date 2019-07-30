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

#from .color_encoding import temp_to_rgb
#from .. import config
from data.color_encoding import temp_to_rgb
import config


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

# Create encoder to avoid serialization problem
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        else:
            return super(JsonEncoder, self).default(obj)


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
    #Inside container:
    # output_path = "data/outputs/written_geojson.json"
    #Locally running:
    output_path = "C:/Users/marias/Documents/Git/stratos/data/outputs/written_geojson.json"
    # open and dump data to output geojson file, remove if exists
    if os.path.isfile(output_path):
        os.remove(output_path)
    # open the final product file as output 
    with open(output_path, "w+") as output: 
        output.write(data) 
  

def get_blob_client(dataset):
    ''' create a client for the requested dataset '''

    CONTAINER_NAME  = 'zarr'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
    absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, dataset, ACCOUNT_NAME, ACCOUNT_KEY)
    return absstore_object


def get_correct_coord_dimensions(dataset_name):
    ''' Different names of latitude/longitude. Most likely a multitude of metadata will
    vary in the future, this should be properly managed. Currently this function takes 
    dataset name as argument and returns the correct lat/lon encoding'''

    if (dataset_name == 'OSCAR'):
        return ('latitude', 'longitude')
    else:
        return ('gridLats', 'gridLons')


def get_chunk_blob_encoding(blob_chunks, time):
    ''' get the correct string for extracting correct blob, e.g. the "0.0.0.0" in 
    client['temperature'/0.0.0.0]. The coordinates and the '''
    def switch(x): return [f'',2,3,4][x]
    string = switch(dim)


def get_decompressed_arrays(dataset, depthIdx=0, timeIdx=0):
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]

    # azure zarr-blob object
    absstore_obj = get_blob_client(dataset['blobpath'])

    # get correct dimensions and coordinate blob chunk path
    (latalias, lonalias) = get_correct_coord_dimensions(dataset_name)
    measurementtype = dataset['measurementtype']

    # get the shape and datatypes of the datasets
    lat_metadata = json.loads(absstore_obj[f'{latalias}/.zarray'])
    lon_metadata = json.loads(absstore_obj[f'{lonalias}/.zarray'])
    meas_metadata = json.loads(absstore_obj[f'{measurementtype}/.zarray'])
    lat_dims= lat_metadata['chunks']
    lon_dims = lon_metadata['chunks']
    meas_dims = meas_metadata['chunks']
    coord_datatype = lat_metadata['dtype']
    meas_datatype = meas_metadata['dtype']
    
    # if lat/lon is 2d, e.g. lat/lon is are grid coordniates, different paths for extracting
    # chunk, and different ways of creating a reshaping tuple for the measurements
    if len(lat_dims)==2:  
        meas_shape = tuple(lat_dims)
        lat_shape = meas_shape
        lon_shape = meas_shape
        coord_chunks = '0.0'
    else:                   
        meas_shape = (lat_dims[0],lon_dims[0])
        lat_shape = lat_dims[0]
        lon_shape = lon_dims[0]
        coord_chunks = '0'

    # if z dimension is present
    if len(meas_dims)==4: meas_chunks = f'{timeIdx}.{depthIdx}.0.0'
    else:                 meas_chunks = f'{timeIdx}.0.0' 

    section_start = time.time()
    # insert conditional check for time, depth and possible other dimensions..
    decom_meas = zarr.blosc.decompress(absstore_obj[f'{measurementtype}/{meas_chunks}'])
    decom_lats = zarr.blosc.decompress(absstore_obj[f'{latalias}/{coord_chunks}'])
    decom_lons = zarr.blosc.decompress(absstore_obj[f'{lonalias}/{coord_chunks}'])
    end = time.time()
    logging.warning("decompressing zarr blob chunk execution time: %f",end-section_start)

    # create numpy arrays from the decompressed buffers and give it our grid shape
    section_start = time.time()
    lats = np.frombuffer(decom_lats, dtype=coord_datatype).reshape(lat_shape)
    lons = np.frombuffer(decom_lons, dtype=coord_datatype).reshape(lon_shape)
    measurements = np.frombuffer(decom_meas, dtype=meas_datatype).reshape(meas_shape)
    
    end = time.time()
    logging.warning("creating numpy arrays of decompresed arrays execution time: %f",end-section_start)

    return([lats, lons, measurements, meas_metadata['fill_value'], len(lat_dims)])



def zarr_to_geojson(startNode=(0,0), 
                    nGrids=10, 
                    gridSize=1, 
                    depthIdx=0,
                    timeIdx=0,
                    dataset={'blobpath':'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', 'measurementtype':'temperature'}):
    # TODO: check default value here  dataset={'dataset':'', 'measurementtype':''}):
    ''' 
    Inserts netCDF data from 'startNode' in a square of size 'nGrids' in positive lat/lon
    index direction into a geojson whose path is described as output. 
    It appends geojson template dictionaries from a given file-path into a 
    temporary data variable, whose data is changed and dumped into output object.
    The datasets have different z dimensions, for instance: depth, thickness, etc.

    Parameters
    ----------
    depthIdx : int
        the depth of the grid to be computed
    timeIdx : string
        the time index of the grid to be computed
    dataset : dict
        dictionary containing what dataset and measurement type to be computed
    '''



    start = time.time() 

    
    measurement_type = dataset['measurementtype']
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]
    # check if min and max values for the measure are present in the configuration file
    if not measurement_type in config.color_enc[dataset_name]:
        raise ValueError(f"no range registered for '{measurement_type}' in config.py")

    # Get the initial template
    jsonData = get_initial_template() 
    # Get the feature template, this will be appended to jsonData for each feature inserted

    # download z-arrays from azure cloud and decompress requested chunks
    [lons, lats, measurements, fill_value, coord_dims] = get_decompressed_arrays(dataset, timeIdx=timeIdx, depthIdx=depthIdx)

    logging.warning(f"configured range for {measurement_type}: "
                        f"{config.color_enc[dataset_name][measurement_type]['min']} to "
                        f"{config.color_enc[dataset_name][measurement_type]['max']}")

    # featureIdx counts what feature we are working on = 0,1,2,3, ... 
    featureIdx = 0
    geojson_start = time.time()
    for y in range(nGrids):                 
        for x in range(nGrids):   
            node = (startNode[0]+y, startNode[1]+x)  
            measurement = measurements[node]
            # if current square is fill value: skip grid -> else: insert lat/lon and temp into data
            if measurement in config.fill_values:
                continue
            else:
                # add a copy of the feature dictionary template to features
                jsonData['features'].append(get_feature_template())
                # create a reference to the current feature we are working on
                feature = jsonData['features'][featureIdx]
                # insert hex into fill
                feature['properties']['fill'] = temp_to_rgb(measurement, measurement_type, dataset_name) 
 
                # insert lat/lon data. each line is a grid coordinate in a polygon sequence.
                # i.e. (0,0) -> (0,1) -> (1,1) -> (1,0) -> (0,0)
                # rounding from 16 (64bit) to 4 decimals, convert to string for json serialization
                counter_start = time.time() 
                # if lat/lon is a 2d array (grid coordinates)
                
                if coord_dims==2:
                    feature['geometry']['coordinates'].append( [
                        [round(lats[node],4), round(lons[node],4)],
                        [round(lats[node[0],node[1]+1],4), round(lons[node[0],node[1]+1],4)],
                        [round(lats[node[0]+1,node[1]+1],4), round(lons[node[0]+1,node[1]+1],4)],
                        [round(lats[node[0]+1,node[1]],4), round(lons[node[0]+1,node[1]],4)],
                        [round(lats[node[0],node[1]],4), round(lons[node[0],node[1]],4)]
                    ])
                else:
                    feature['geometry']['coordinates'].append( [
                        [round(lats[node[0]],4), round(lons[node[1]],4)],
                        [round(lats[node[0]],4), round(lons[node[1]+1],4)],
                        [round(lats[node[0]+1],4), round(lons[node[1]+1],4)],
                        [round(lats[node[0]+1],4), round(lons[node[1]],4)],
                        [round(lats[node[0]],4), round(lons[node[1]],4)]
                    ])
                featureIdx = featureIdx + 1
    end =time.time
    logging.warning("number of generated polygons: %d", len(jsonData['features']))
    logging.warning("showing %s for %s", dataset['measurementtype'], dataset['blobpath'])
    logging.warning("startEdge: %s, nGrids: %d, depthIdx: %d, timeIdx: %d",startNode,nGrids,depthIdx,timeIdx)

    end = time.time()
    logging.warning("total execution time of azure to json function: %f",end-start)
    
    return json.dumps(jsonData, cls=JsonEncoder)

    

'''
# TODO: Keep this for quick-testing of both algorithm and execution time..

#dataset={'dataset':'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', 'measurementtype':'temperature'}
dataset={'dataset':'norsok/samples_NSEW.nc_201301_nc4.zarr', 'measurementtype':'salinity'}
#dataset={'dataset':'norsok', 'measurementtype':'temperature'}

N = 1
start = time.time()
for i in range(N):
    zarr_to_geojson(nGrids=200, 
                        depthIdx=0,
                        timeIdx=0,
                        dataset=dataset)
end = time.time()
logging.warning("average execution time: %f", (end-start)/N)
'''