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
# from color_encoding import temp_to_rgb
from color_encoding import temp_to_rgb
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
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)


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
    output_path = "data/outputs/written_geojson.json"
    # open and dump data to output geojson file, remove if exists
    if os.path.isfile(output_path):
        os.remove(output_path)
    # open the final product file as output 
    with open(output_path, "w+") as output: 
        # dump new data into output json file 
        json.dump(data, output, indent=4)  

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
    def switch(x): return [2,3,4][x]
    string = switch(dim)


def get_decompressed_arrays(dataset, depthIdx=0, timeIdx=0):

    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]

    # azure zarr-blob object
    absstore_obj = get_blob_client(dataset['blobpath'])

   

  
    import xarray as xr
    #print(absstore_obj())
    #absstore_object['salinity']
    with xr.open_zarr(absstore_obj) as ds:
        print(dataset['blobpath'])
        print(dataset['measurementtype'])
        min = float(ds[dataset['measurementtype']].min())
        print(f"{dataset['measurementtype']} min: {min}")
        max = float(ds[dataset['measurementtype']].max())
        print(f"{dataset['measurementtype']} max: {max}")

    exit()

  
    
    import xarray as xr
    import blosc

    CONTAINER_NAME  = 'zarr'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='

    absstore_obj = zarr.storage.ABSStore(CONTAINER_NAME, "norsok/samples_NSEW.nc_201301_nc4.zarr", ACCOUNT_NAME, ACCOUNT_KEY)


    decom_meas = blosc.decompress(absstore_obj['salinity/0.0.0.0'])
    measurements = np.frombuffer(decom_meas, "<i2").reshape((635, 1019))

    measurements=measurements[measurements>-20000]
    measurements=measurements[measurements<-9500]
    print(float(measurements.min()))
    print(measurements.max())
    exit()
    #absstore_object['salinity']
    with xr.open_zarr(franfjord) as franfjord_ds:
        with xr.open_zarr(norsok) as norsok_ds:
            print(float(franfjord_ds['temperature'][0,220,0,0]))
            print(float(norsok_ds['temperature'][0,0,220,20]))
 
    
    







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

    section_start = time.time()
    # append strings to create the correct zr blob path

    end = time.time()
    logging.warning("decompressing azure blob chunks execution time: %f",end-section_start)
    # if lat/lon is 2d, e.g. lat/lon is are grid coordniates, different paths for extracting
    # chunk, and different ways of creating a reshaping tuple for the measurements
    if len(lat_dims)==2:  
        meas_shape = tuple(lat_dims)
        coord_chunks = '0.0'
    else:                   
        meas_shape = (lat_dims[0],lon_dims[0])
        coord_chunks = '0'

    # insert conditional check for time, depth and possible other dimensions..
    decom_meas = zarr.blosc.decompress(absstore_obj[f'{measurementtype}/{timeIdx}.{depthIdx}.0.0'])
    decom_lats = zarr.blosc.decompress(absstore_obj[f'{latalias}/{coord_chunks}'])
    decom_lons = zarr.blosc.decompress(absstore_obj[f'{lonalias}/{coord_chunks}'])

    # create numpy arrays from the decompressed buffers and give it our grid shape
    section_start = time.time()
    lats = np.frombuffer(decom_lats, dtype=coord_datatype).reshape(meas_shape)
    lons = np.frombuffer(decom_lons, dtype=coord_datatype).reshape(meas_shape)
    measurements = np.array(np.frombuffer(decom_meas, dtype=meas_datatype).reshape(meas_shape))
    end = time.time()
    logging.warning("creating numpy arrays of decompresed arrays execution time: %f",end-section_start)

    return([lats, lons, measurements, meas_metadata['fill_value']])

def zarr_to_geojson(startEdge=(0,0), 
                    nGrids=10, 
                    gridSize=1, 
                    depthIdx=0,
                    timeIdx=0,
                    dataset={'dataset':'', 'measurementtype':''}):
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
    dataset : dict
        dictionary containing what dataset and measurement type to be computed
    '''


    start = time.time() 

    measurement_type = dataset['measurementtype']
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]

    # Get the initial template
    jsonData = get_initial_template() 
    # Get the feature template, this will be appended to jsonData for each feature inserted

    # download z-arrays from azure cloud and decompress requested chunks
    [lats, lons, measurements, fill_value] = get_decompressed_arrays(dataset, timeIdx=timeIdx, depthIdx=depthIdx)

    logging.warning(f"configured range for {measurement_type}: "
                        f"{config.color_enc[dataset_name][measurement_type]['min']} to "
                        f"{config.color_enc[dataset_name][measurement_type]['max']}")

    # featureIdx counts what feature we are working on = 0,1,2,3, ... 
    featureIdx = 0
    geojson_start = time.time()
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
                print(float(measurement))
                feature['properties']['fill'] = temp_to_rgb(measurement, measurement_type, dataset_name) 
 
                # insert lat/lon data. each line is a grid coordinate in a polygon sequence.
                # i.e. (0,0) -> (0,1) -> (1,1) -> (1,0) -> (0,0)
                # rounding from 16 (64bit) to 4 decimals, convert to string for json serialization
                counter_start = time.time() 
                feature['geometry']['coordinates'].append( [
                    [round(lons[y,x],4), round(lats[y,x],4)],
                    [round(lons[y,x+1],4), round(lats[y,x+1],4)],
                    [round(lons[y+1,x+1],4), round(lats[y+1,x+1],4)],
                    [round(lons[y+1,x],4), round(lats[y+1,x],4)],
                    [round(lons[y,x],4), round(lats[y,x],4)]
                ])
                '''
                feature['geometry']['coordinates'].append( [
                    [str(round(lons[y,x],4)), str(round(lats[y,x],4))],
                    [str(round(lons[y,x+1],4)), str(round(lats[y,x+1],4))],
                    [str(round(lons[y+1,x+1],4)), str(round(lats[y+1,x+1],4))],
                    [str(round(lons[y+1,x],4)), str(round(lats[y+1,x],4))],
                    [str(round(lons[y,x],4)), str(round(lats[y,x],4))]
                ] )
                '''

                featureIdx = featureIdx + 1

    logging.warning("creating geojson object execution time: %f",time.time()-geojson_start)

    logging.warning("showing %s for %s", dataset['measurementtype'], dataset['blobpath'])
    logging.warning("startEdge: %s, nGrids: %d, depthIdx: %d, timeIdx: %d",startEdge,nGrids,depthIdx,timeIdx)

    end = time.time()
    logging.warning("total execution time of azure to json function: %f",start-end)
    
    #start_write = time.time() 
    #write_output(json.dumps(jsonData, cls=JsonEncoder))
    #end = time.time()
    #logging.warning("time spent writing to file: %f",end-start_write)

    return json.dumps(jsonData, cls=JsonEncoder)

# TODO: Keep this for quick-testing of both algorithm and execution time..

#dataset={'blobpath':'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', 'measurementtype':'temperature'}
dataset={'blobpath':'norsok/samples_NSEW.nc_201301_nc4.zarr', 'measurementtype':'v_north'}
#dataset={'blobpath':'norsok', 'measurementtype':'temperature'}
#dataset={'blobpath':'OSCAR/TEST3MEMWX.XNordlandVI_concentration.zarr', 'measurementtype':'total_concentration'}
#dataset={'blobpath':'OSCAR/TEST3MEMWX.XNordlandVI_surface.zarr', 'measurementtype':'surface_avg_asphaltene_fraction_distribution_by_thickness'}

 

N = 1
start = time.time()
for i in range(N):
    zarr_to_geojson(nGrids=200, 
                        depthIdx=20,
                        timeIdx=0,
                        dataset=dataset)
end = time.time()
logging.warning("average execution time: %f", (end-start)/N)
