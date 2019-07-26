import json
import zarr

''' Generating a json file containing the wind/ocean velocity vectors. 
The "leaflet-velocity" plugin is tailor-made for this application '''

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

    with open("/home/even/Workspaces/stratos/data/outputs/u-east.json", 'r') as df:
        data = df.read()
        return json.loads(data)

    '''
    start = time.time() 

    measurement_type = dataset['measurementtype']
    # get the dataset name from blobpath "OSCAR/ ..."
    dataset_name = dataset['blobpath'].split('/')[0]
    # check if min and max values for the measure are present in the configuration file
    if not measurement_type in config.color_enc[dataset_name]:
        raise ValueError(f"no range registered for '{measurement_type}' in config.py")
    '''