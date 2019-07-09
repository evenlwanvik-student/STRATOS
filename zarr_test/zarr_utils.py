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
#absstore_object = zarr.convenience.open(absstore_object)
logging.warning(absstore_object)
#create blob from local zarr array
#absstore_zarr.create_blob(ZARR_PATH)


def loop(data, n):
    for i in range(n):
        x = float(data[0,i])

#logging.warning("starting temp loop")



with xr.open_zarr(absstore_object, group='time') as source:   
    logging.warning(source)

