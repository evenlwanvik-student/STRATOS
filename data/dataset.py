import xarray as xr
import zarr   as  zr

class init_dataset():
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
        self.container_name   = "zarr"
        self.account_name     = "stratos"
        self.account_key      = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
        self.blob_name        = blob_path
        self.measurement_type = measurement_type
        self.abs_zr_obj       = zr.storage.ABSStore(self.container_name, 
                                                  self.blob_name, 
                                                  self.account_name, 
                                                  self.account_key)
        self.xr_data  = xr.open_zarr(self.abs_zr_obj)

        self.measurement = self.xr_data[measurement_type]
        self.lats = self.xr_data['lats']
        self.lons = self.xr_data['lons']

        # locate min/max for creating a color map for displaying the changes in the measurement
        self.measurement_min = self.measurement.min()
        self.measurement_max = self.measurement.max()

    def get_measurement_extrema()
        return [self.]

    def 

    def __del__(self):
        # not sure if this is necessary
        self.xr_data.close()
