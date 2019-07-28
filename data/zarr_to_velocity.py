import zarr
import logging
import config
import json
import time
import numpy as np

''' 
Generating a json file containing the wind/ocean velocity vectors. 
The "leaflet-velocity" plugin is tailor-made for this application 
'''


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

    return([lats, lons, measurements, json.loads(absstore_obj['grid_mapping/.zattrs'])])


def zarr_to_velocity(depthIdx=0,
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

    measurement_type = dataset['measurementtype']
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]
    # check if min and max values for the measure are present in the configuration file
    if not measurement_type in config.color_enc[dataset_name]:
        raise ValueError(f"no range registered for '{measurement_type}' in config.py")

    # download z-arrays from azure cloud and decompress requested chunks
    [lons, lats, measurements, grid_mapping] = get_decompressed_arrays(dataset, timeIdx=timeIdx, depthIdx=depthIdx)

    logging.warning(f"configured range for {measurement_type}: "
                        f"{config.color_enc[dataset_name][measurement_type]['min']} to "
                        f"{config.color_enc[dataset_name][measurement_type]['max']}")


    template_path = "data/templates/velocity_template.json"

    with open(template_path) as f:
        data = json.loads(f.read())

    '''
    eastward_wind: data[0]
    westward_wind: data[1]
    '''

    # resolution
    data[0]["dx"] = 1.0
    data[0]["dy"] = 1.0

    xgrids = len(lats[0])
    ygrids = len(lats[0])
    # This gives lat1: 7.105113983154297, lat2: 7.078174591064453
    # i.e. Not sure if correct direction
    data[0]["la1"] = lats[0,0]
    data[0]["la2"] = lats[xgrids-1,ygrids-1]
    data[0]["lo1"] = lons[0,0]
    data[0]["lo2"] = lons[xgrids-1,ygrids-1]

    



zarr_to_velocity(depthIdx=0,
    timeIdx=0,
    dataset={'blobpath':'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr', 'measurementtype':'u_east'})
