from azure.storage.blob import BlockBlobService
from azure import *
from azure.storage import *
import zarr
import xarray as xr
import shutil
import time
from copy import deepcopy
import logging


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')


#logger = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
#                                datefmt='%Y-%m-%d %H:%M:%S')

class zarrABSStore():
    '''
    Utilities for using zarr arrays and interface with the Azure Blob Service.
    This is basically a wrapper for the ABSStore class within the storage.py module
    of the zarr project

    Parameters
    ----------
    container : string
        The name of the ABS container to use.
    zarr_prefix : string
        Location of the root "directory" of the storage hierarchy within the container.
    account_name : string
        The Azure blob storage account name.
    account_key : string
        The Azure blob storage account access key.

    '''

    def __init__(self, container, zarr_prefix, account_name=None, account_key=None):
        self.container = container
        self.prefix = zarr_prefix
        self.account_name = account_name
        self.account_key = account_key
        ''' abs_zarray (below) is the ABS class object on which zarray mapping
        can be performed, e.g. abs_zarray['temperature/0.0...']'''
        self.abs_zarray  = zarr.storage.ABSStore(container, zarr_prefix, account_name, account_key)
        self.abs_client = BlockBlobService(self.account_name, self.account_key)

    def list_blobs(self):
        print("\nList blobs in the container " + self.container + ":")
        generator = self.abs_client.list_blobs(self.container)
        for blob in generator:
            print("\t Blob name: " + blob.name)

    def create_container(self,container_name):
        self.abs_client.create_container(container_name)

    def create_zarr_blob(self, local_zarr_path):
        ''' Using the copy_store function to simply copy a local zarr storage to 
        our ABS storage object, and boom, we have a zarr blob.
        '''
        local_zarr = zarr.DirectoryStore(local_zarr_path)
        zarr.convenience.copy_store(local_zarr, self.abs_zarr)

    def rmdir(self, path=None):
        self.abs_zarr.rmdir(path)

    #def get_zarray_blob(self, sub_blob = ''):
        ''' Function for extracting a subfolder (sub-blob) from the the z-array we are 
        currently working on, it creates a 
        e.g. get_zarray_blob('temperature') gets the temperature z-array (blob) '''
        


def create_zarr(netCDF_path=None, zarr_path='./default.zarr', 
                    chunks={'time':36, 'xc': 291, 'yc': 294, 'zc': 15}):
    with xr.open_dataset(netCDF_path, chunks=chunks) as nc:
        try:
            shutil.rmtree(zarr_path)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        return nc.to_zarr(zarr_path)




#netCDF_test_path    = "/home/even/netCDFdata/tos_O1_2001-2002.nc"
netCDF_path     = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
CONTAINER_NAME  = 'zarr'
BLOB_NAME       = 'Franfjorden32m/samples_NSEW_2013.03.11_chunk-test-1.zarr'
ACCOUNT_NAME    = 'stratos'
ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
ZARR_PATH       = 'zarr/Franfjorden32m/larger_chunks.zarr'
#LOCAL_ZARR2     = 'zarr/2Franfjorden32m/test.zarr'
NETCDF_PATH     = 'netcdf/Franfjorden32m/samples_NSEW_2013.03.11-chunked_coordinates.nc'



# "None" chunks along the full dimension
#chunks = {'time': 10, 'zc': 5, 'xc': 5, 'yc': 5}
#create_zarr(netCDF_path, ZARR_PATH, chunks)

logging.warning("creating azure zarray-blob object")
absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)
#create blob from local zarr array
#absstore_zarr.create_blob(ZARR_PATH)

#chunks = {'time': None, 'zc': None, 'xc': 1, 'yc': 1}
with xr.open_zarr(absstore_object) as source:   
    logging.warning("re-chunking")
    #source.chunk(chunks)                                                                                                                                                                                  
    # Fetching larger grids took way longer, as it probably has to do it element-by-element
    logging.warning("copying latitude data")
    #temps = deepcopy(source['temperature'][0,0])#[::gridSize,::gridSize])
    logging.warning("copying latitude data")
    #lats = deepcopy(source['gridLats'])#[::gridSize,::gridSize])
    logging.warning("copying latitude data")
    #lons = deepcopy(source['gridLons'])#[::gridSize,::gridSize])

    def loop(data, n):
        for i in range(n):
            x = float(data[0,i])

    logging.warning("starting temp loop")
    loop(source['temperature'][0,0], 10)
    logging.warning("starting lat loop")
    loop(source['gridLats'], 10)
    logging.warning("loop ended")

#chunks = {'time': 72, 'zc': 30,'xc': 294, 'yc': 291}
#with xr.open_zarr(absstore_object) as ds:
    #print(ds)
    #x = ds.chunk(chunks=chunks)
    #print(x)


'''     
The Python global interpreter lock (GIL) is released for both compression and 
decompression operations, so Zarr will not block other Python threads from running.

To give a simple example, consider a 1-dimensional array of length 60, z, divided 
into three chunks of 20 elements each. If three workers are running and each attempts 
to write to a 20 element region (i.e., z[0:20], z[20:40] and z[40:60]) then each 
worker will be writing to a separate chunk and no synchronization is required. 
However, if two workers are running and each attempts to write to a 30 element 
region (i.e., z[0:30] and z[30:60]) then it is possible both workers will attempt to 
modify the middle chunk at the same time, and synchronization is required to prevent 
data loss.
'''