from azure.storage.blob import BlockBlobService
from azure import *
from azure.storage import *
import zarr
import xarray as xr

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
        # abs_zarr (below) is the ABS class object
        self.abs_zarr  = zarr.storage.ABSStore(container, zarr_prefix, account_name, account_key)
        self.abs_client = BlockBlobService(self.account_name, self.account_key)

    def list_blobs(self):
        print("\nList blobs in the container " + self.container + ":")
        generator = self.abs_client.list_blobs(self.container)
        for blob in generator:
            print("\t Blob name: " + blob.name)

    def create_container(self,container_name):
        self.abs_client.create_container(container_name)

    def create_blob(self, local_zarr_path):
        ''' Using the copy_store function to simply copy a local zarr storage to 
        our ABS storage object, and boom, we have a zarr blob.
        '''
        local_zarr = zarr.DirectoryStore(local_zarr_path)
        zarr.convenience.copy_store(local_zarr, self.abs_zarr)

    def test():
        print self.abs_zarr.keys()

    def rmdir(self, path=None):
        self.abs_zarr.rmdir(path)



def create_zarr(netCDF_path=None, zarr_path=None):
    with xr.open_dataset(netCDF_path) as nc:
        nc.to_zarr(zarr_path)
        #print nc



netCDF_path    = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
CONTAINER_NAME = 'zarr'
BLOB_NAME      = 'Franfjorden32m/samples_NSEW_2013.03.11.zarr'
ACCOUNT_NAME   = 'stratos'
ACCOUNT_KEY    = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
LOCAL_ZARR     = 'data/Franfjorden32m/test.zarr'
LOCAL_ZARR2    = 'data/2Franfjorden32m/test.zarr'


create_zarr(netCDF_path, LOCAL_ZARR2)
#my_zarr = zarrABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)
#xr = xarray.open_zarr(x.my_zarr)



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