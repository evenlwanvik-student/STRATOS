import xarray as xr
import zarr   as  zr
import logging
from data.color_encoding import set_colormap_range

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

class data_instance():
    '''
    This class instantiates and holds usefull static variables for a given 
    blob whenever the user specifies what type of data to access.

    Parameters
    ----------
    blob_path : string
        The name (path) of the blob the user wants to access
    measurement_type : string
        What type of measurement to display (e.g. 'temperature', 'salinity', etc)

    '''
    def __init__(self, blob_path, measurement_type):
        logging.warning("generating dataset for blob: %s and measurement type %s", blob_path, measurement_type)
        self.container_name   = "zarr"
        self.account_name     = "stratos"
        self.account_key      = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
        self.blob_name        = blob_path
        self.measurement_type = measurement_type
        self.abs_zr_obj       = zr.storage.ABSStore(self.container_name, 
                                                  self.blob_name, 
                                                  self.account_name, 
                                                  self.account_key)
        
        logging.warning("creating x-array dataset")
        with xr.open_zarr(self.abs_zr_obj) as xr_data:
            self.measurements = xr_data[measurement_type]
            self.lats = xr_data['gridLats']
            self.lons = xr_data['gridLons']


        ''' tried to set the measurement range for the colormap, but then we have to 
        read the whole array and it's not worth it, as we are working with references
        until someone actually wants to access the data, which we do in azure_to_json
        when we know what subset of data we want.
        We can create a kind of index library with custom ranges for whichever type
        of measurement the user wants to access.
        '''
        '''
        logging.warning("setting extrema of the %s measurement", measurement_type)
        # find the extrema of the given measurement type for creating a color map illustrating changes
        measurement_min = self.measurements.min()
        logging.warning(float(measurement_min))
        measurement_max = self.measurements.max()
        self.measurement_range = {'min': measurement_min, 'max': measurement_max}
        # set the range in in color_encoding.py
        #logging.warning("dataset measurement range %s", self.measurement_range)
        set_colormap_range(self.measurement_range)
        '''

    def __del__(self):
        logging.warning("dataset class destructor")
        # not sure if this is necessary