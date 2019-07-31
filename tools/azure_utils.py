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


''' 
Just a recipe how one can use these functions, or at least 
implement something alike in a new and automatized build:

--- 1. download netcdf blob to local file
download_netcdf_blob()

--- 2. figure out what chunk dimensions to use
list_local_netcdf_dimensions()

--- 2. choose chunks..
norsok_chunks = {'time':1, 'zc': 1, 'yc': 635, 'xc': 1019}

--- 4. create a zarr blob with the given chunks
create_zarr_blob_from_local_netcdf(OSCAR_chunks_shoreline_and_sediment)

--- 5. remove zarr blob
remove_zarr_blob()
'''

# Prepare blob access
zr_container_name   = 'zarr'
nc_container_name   = 'netcdf'
zr_blob_name        = 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr'
nc_blob_name        = 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.nc'
account_name     = 'stratos'
account_key      = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
local_zr_path      = '/home/even/data/zarr/'
local_nc_path      = '/home/even/data/netCDFdata/'
local_nc_full = local_nc_path + nc_blob_name


#---------------------- a few azure (not zarr) blob functions ----------------------

def list_blobs():
    ''' List the blobs in the container '''
    block_blob_service = BlockBlobService(account_name, account_key)
    print("\nList blobs in the container")
    generator = block_blob_service.list_blobs(container_name)
    for blob in generator:
        print("\t Blob name: " + blob.name)

def download_netcdf_blob():
    ''' creates local netcdf file, should be able to create a streaming object
    and copy directly over to the zarr store blob object '''
    if os.path.isfile(local_nc_full):
        logging.warning("netcdf blob exists")
    else:
        block_blob_service = BlockBlobService(account_name, account_key)
        block_blob_service.get_blob_to_path(nc_container_name, nc_blob_name, local_nc_full, 'w+')

def list_local_netcdf_dimensions():
    ''' Opens local netcdf file and lists its dimensions.
    Use this to create the chunk sizes, don't have time to automatize the 
    chunk size selection based on metadata... '''
    with xr.open_dataset(local_nc_full) as ds:
        print(ds.variables)
        logging.warning("the chunk sizes are: %s", ds.sizes)

def list_local_netcdf_dimensions():
    ''' Opens azure netcdf and lists its dimensions.
    Use this to create the chunk sizes, don't have time to automatize the 
    chunk size selection based on metadata... '''
    with xr.open_dataset(local_nc_full) as ds:
        print(ds.variables)
        logging.warning("the chunk sizes are: %s", ds.sizes)

#---------------------- a few zarr blob functions ----------------------

def create_zarr_blob_from_local_netcdf(chunks):
    ''' absstore_obj - Azure Blob Service _ zarr storage '''
    download_netcdf_blob()
    absstore_obj  = zarr.storage.ABSStore(zr_container_name, zr_blob_name, account_name, account_key)
    with xr.open_dataset(local_nc_full, chunks=chunks) as ds:
        # remove (if) existing zarr first
        absstore_obj.rmdir()
        ds.to_zarr(absstore_obj)

def create_zarr_blob_from_netcdf_blob(chunks):
    ''' Supposed to stream netcdf blob directly to zarr blob.
    Only use this if you know the chunk sizes on beforehand '''
    download_netcdf_blob()
    absstore_obj = zarr.storage.ABSStore(zr_container_name, zarr_blob_name,account_name, account_key)
    with xr.open_dataset(netcdf_path, chunks=chunks) as ds: 
        ds.to_zarr(absstore_obj)

def remove_zarr_blob():
    ''' simply deletes the zarr blob given by the global strings '''
    absstore_obj = zarr.storage.ABSStore(zr_container_name, zr_blob_name, account_name, account_key)
    absstore_obj.rmdir()
      


