from azure.storage.blob import BlockBlobService
from azure import *
from azure.storage import *

import zarr
import xarray as xr
import shutil
import time
import json
import os
import numpy
import logging
import numpy as np

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')


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

    def create_zarr_blob_from_local(self, local_zarr_store):
        ''' Using the copy_store function to simply copy a local zarr storage to 
        our ABS storage object, and boom, we have a zarr blob.
        '''
        local_zarr = zarr.DirectoryStore(local_zarr_store)
        zarr.convenience.copy_store(local_zarr, self.abs_zarr)

    def rmdir(self, path=None):
        self.abs_zarray.rmdir()

    def create_zarr_blob_from_local_netcdf(self, netcdf_path=None, chunks=None):
        with xr.open_dataset(netcdf_path, chunks=chunks) as ds:
            # remove existing zarr first
            self.rmdir()
            ds.to_zarr(self.abs_zarray)
            
    def download_zarr(self, target='data/zarr/target.zarr'):
        ''' creates local zarr file to the target location '''
        zarr.save(target, self.abs_zarray)
        #fw = zarr.open(target, mode='w')# as fw:
        #zarr.convenience.copy_store(self.abs_zarray, fw)

    #def get_zarr_blob(self, sub_blob = ''):
        ''' Function for extracting a subfolder (sub-blob) from the the z-array we are 
        currently working on, it creates a 
        e.g. get_zarray_blob('temperature') gets the temperature z-array (blob) '''


# Prepare blob access
zarr_container_name   = 'zarr'
netcdf_container_name   = 'netcdf'
zarr_blob_name        = 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr'
netcdf_blob_name = 'norsok/samples_NSEW.nc_201301_nc4.nc'
account_name     = 'stratos'
account_key      = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
zarr_path        = 'zarr/Franfjorden32m/chunked_coordinates.zarr'

#---------------------- a few azure (not zarr) blob functions ----------------------

def list_blobs(output_path=None, account_name=account_name, account_key=account_key):
    ''' List the blobs in the container '''
    block_blob_service = BlockBlobService(account_name, account_key)
    print("\nList blobs in the container")
    generator = block_blob_service.list_blobs(container_name)
    for blob in generator:
        print("\t Blob name: " + blob.name)

def download_netcdf_blob(output_path=None, 
                         account_name=account_name, 
                         account_key=account_key,
                         container_name=netcdf_container_name,
                         blob_name=netcdf_blob_name):
    ''' creates local netcdf file, should be able to create a streaming object
    and copy directly over to the zarr store blob object '''
    block_blob_service = BlockBlobService(account_name, account_key)
    #with open(output_path, 'w+') as f:
    block_blob_service.get_blob_to_path(container_name, blob_name, output_path)
    
netcdf_path = "/home/even/data/netCDFdata/norsok/samples_NSEW.nc_201301_nc4.nc"
zarr_blob_name = 'norsok/samples_NSEW.nc_201301_nc4.zarr'

#encoding = {'temperature': {'_FillValue':NaN, 'chunks':chunks}}
chunks = {'time':1, 'zc': 1, 'yc': 635, 'xc': 1019}
encoding={'temperature':{'_FillValue':np.NaN}}

my_zarr_obj = zarrABSStore(zarr_container_name, zarr_blob_name,account_name, account_key)
my_zarr_obj.create_zarr_blob_from_local_netcdf(netcdf_path, chunks)


my_zarr_obj = zarr.storage.ABSStore(zarr_container_name, zarr_blob_name,account_name, account_key)
#my_zarr_obj = zarr.storage.ABSStore(zarr_container_name, zarr_blob_name,account_name, account_key)
#with xr.open_dataset(netcdf_path, chunks=chunks) as ds:
#    ds.to_zarr(my_zarr_obj)
    #zarr.convenience.copy_store(ds.to_zarr(), my_zarr_obj)


#local_path = os.path.join("/home/even/data/netCDFdata/", netcdf_blob_name)
#download_netcdf_blob(output_path = local_path)



#zarr_blob_name = 'Franfjorden32m/samples_NSEW_2013.03.11_chunk-test-3.zarr'
#abs_obj = zarr.storage.ABSStore(netcdf_container_name, zarr_blob_name, account_name, account_key)
#abs_obj.rmdir(zarr_blob_name)