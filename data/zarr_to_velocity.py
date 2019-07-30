import zarr
import logging
import config
import json
import time
import numpy as np
from copy import deepcopy

''' 
Generating a json file containing the wind/ocean velocity vectors. 
The "leaflet-velocity" plugin is tailor-made for this application 
'''

# Create encoder to avoid serialization problem
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        else:
            return super(JsonEncoder, self).default(obj)


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


def get_decompressed_arrays(blobpath, measurementtype, depthIdx=0, timeIdx=0):
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = blobpath.split('/')[0]

    # azure zarr-blob object
    absstore_obj = get_blob_client(blobpath)

    # get correct dimensions and coordinate blob chunk path
    (latalias, lonalias) = get_correct_coord_dimensions(dataset_name)

    # get the shape and datatypes of the datasets
    lat_metadata = json.loads(absstore_obj[f'{latalias}/.zarray'])
    lon_metadata = json.loads(absstore_obj[f'{lonalias}/.zarray'])
    meas_metadata = json.loads(absstore_obj[f'{measurementtype}/.zarray'])
    attributes = json.loads(absstore_obj[f'{measurementtype}/.zattrs'])
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
    # to implement the time and depth indeces, have a look at how it's done in zarr_to_geojson.py
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

    return([lats, lons, measurements, attributes])


def replace_fillval(data):
    ''' replace occurences of fill_val in list '''
    for n, val in enumerate(data):
        if float(val) == -32768.0:
            data[n] = 0.0


def zarr_to_velocity(depthIdx=0,
                    timeIdx=0,
                    blobpath='Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr',
                    wind_flag=True):

    ''' 
    Inserts netCDF data from 'startNode' in a square of size 'nGrids' in positive lat/lon
    index direction into a geojson whose path is described as output. 
    It appends geojson template dictionaries from a given file-path into a 
    temporary data variable, whose data is changed and dumped into output object.
    The datasets have different z dimensions, for instance: depth, thickness, etc.

    Parameters
    ----------
    depthIdx : int
        the depth of the grid to be computed !! NOT IMPLEMENTED YET
    timeIdx : string
        the time index of the grid to be computed !! NOT IMPLEMENTED YET
    dataset : string
        full path to zarr blob 
    wind_flag : boolean
        just to signal if wind (TRUE) velocity or ocean current (FALSE) is to be computed
    '''

    # azure blob storage object
    absstore_obj = get_blob_client(blobpath)
    dataset_name = blobpath.split('/')[0]

    template_path = "data/templates/velocity_template.json"

    with open(template_path, 'r') as f:
        data = json.loads(f.read())
    '''
    eastward_ ... : data[0]
    westward_ ... : data[1]
    '''

    # should have measurement type as input as well, but not enough time to implement..
    if wind_flag:
        # wind velocity
        meas_types = ('w_east', 'w_north')
    else:
        # ocean current
        meas_types = ('u_east', 'v_north')
    
    for idx, meas_type in enumerate(meas_types):
        # check if min and max values for the measure are present in the configuration file
        if not meas_type in config.color_enc[dataset_name]:
            raise ValueError(f"no range registered for '{meas_type}' in config.py")
        # not using the configured min/max values yet, the +- velocities for the layer 
        # is set in the respective fucntion in velocity-demo.js
        logging.warning(f"configured range for {meas_type}: "
                            f"{config.color_enc[dataset_name][meas_type]['min']} to "
                            f"{config.color_enc[dataset_name][meas_type]['max']}")

        # attributes (some metadata) of measurement
        attributes = absstore_obj[f'{meas_type}/.zattrs']

        # decompress data
        [lats, lons, measurements, attributes] = get_decompressed_arrays(blobpath, meas_type)
        
        data[idx]['header']['parameterUnit'] = attributes['units']
        data[idx]['header']['parameterNumberName'] = attributes['standard_name']
        # data[idx]['refTime'] = ... not implemented yet
        # x (lon) and y (lat) resolution in degrees
        data[idx]['header']['dx'] = abs(lons[0,0]-lons[1,0])
        data[idx]['header']['dy'] = abs(lats[0,0]-lats[0,1])
        # number of elements in x-y direction
        data[idx]['header']['nx'] = len(lats[0])
        data[idx]['header']['ny'] = len(lats)
        # start (lon1, lat1) to end (lon2, lat2), creating square perpendicular to lat/lon axis
        data[idx]['header']['la1']  = lats.max() # e.g. 62.8851
        data[idx]['header']['la2']  = lats.min() # e.g. 62.7656
        data[idx]['header']['lo1']  = lons.min() # e.g. 6.96005
        data[idx]['header']['lo2']  = lons.max() # e.g. 7.22188
        # the data is given as one single array
        data[idx]['data'] = measurements.flatten().tolist()
        # replace all fill values with 0.0
        replace_fillval(data[idx]['data'])
        if 'scale_factor' in attributes:
            logging.warning(f"Applying scaling factor of {attributes['scale_factor']}")
            for i,val in enumerate(data[idx]['data']):
                data[idx]['data'][i] = val * attributes['scale_factor']

    logging.warning(f"Wind and ocean current data is now available for {dataset_name}")

    #with open('static/leaflet-velocity/wind-velocity.json', 'w+') as outfile:
    #    json.dump(data, outfile, indent=4, cls=JsonEncoder)

    return json.dumps(data, cls=JsonEncoder)
