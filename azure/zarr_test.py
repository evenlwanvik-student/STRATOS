import xarray as xr
import numpy as np
import pandas as pd
import shutil
import dask
import zarr


def get_encoding(name):
    '''Get encodings from a Zarr archive.
    Arguments:
        - name: the name of the archive.
    Returns:
        - encoding: the encodings of the variables.
    '''
    ds = xr.open_zarr(name)
    encoding = {name: ds[name].encoding for name in list(ds.variables)}
    print encoding
    return encoding


def create_zarr(ds, name, encoding=None):
    '''Create a Zarr archive from an Xarray Dataset.
    Arguments:
        - ds: the Dataset to store.
        - name: the name of the Zarr archive.
        - encoding: the encoding to use for each variable.
    Returns:
        - encoding: the encoding used for each variable.
    '''
    shutil.rmtree(name, ignore_errors=True)
    
    ds = ds.chunk({name: ds[name].shape for name in list(ds.dims)})
    
    ds.to_zarr(name, encoding=encoding)
    
    if encoding is None:
        encoding = get_encoding(name)
    return encoding


ACCOUNT_NAME = 'stratos'
ACCOUNT_KEY = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
CONTAINER_NAME = 'netcdf'
BLOB_NAME = "Franfjorden32m/samples_NSEW_2013.03.11.zarr"

# Create the BlockBlockService that is used to call the Blob service for the storage account.
blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

netCDF_path = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
with xr.open_dataset(netCDF_path) as data:

    x = create_zarr(data, "test")
    # zarr Azure Blob Storage (ABS)
    zarr.storage.ABSStore(container, blob_name, accound_name, account_key)

    '''
    zarr_path = "/home/even/netCDFdata/test.zarr"
    # open and dump data to output geojson file, remove if exists
    try:
      shutil.rmtree(zarr_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    data.to_zarr(zarr_path)
    '''