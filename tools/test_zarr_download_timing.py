import time
import os
import zarr
import xarray as xr
from copy import deepcopy
from sys import getsizeof
import sys

# temporary hardcoded blob
CONTAINER_NAME  = 'zarr'
#BLOB_NAME       = 'Franfjorden32m/samples_NSEW_2013.03.11_chunk-test-2.zarr'
BLOB_NAME       = 'Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr'
ACCOUNT_NAME    = 'stratos'
ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='

# Test client initialization
start = time.time()
absstore_zarr = zarr.storage.ABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)
end = time.time()
print("::::: size of client:",sys.getsizeof(absstore_zarr))
print("::::: initializing client time:", end-start)

# Test zarray to xarray dataset
start = time.time()
ds = xr.open_zarr(absstore_zarr)#, decode_cf=False)
end = time.time()
print("::::: going from azure blob zarr object to x-array:", end-start)
print("::::: size of x-array:", ds.nbytes)

# test temperature subdataset and extraction of value
temps = ds['temperature'][0,0].values
print("::::: size of temps:", temps.nbytes)
start = time.time()
temp = float(temps[220,20])
print(temp)
print("::::: fetching a temperature element from xarray: ", end-start)

ds.close()

'''
#Test with average time

logging.warning("testing blob: %s", BLOB_NAME)
n = 10
start = time.time()
for i in range(n):
    absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)
end = time.time()
logging.warning("downloading ABS client: %f", (end-start)/n)

n = 10
start = time.time()
for i in range(n):
    x = xr.open_zarr(absstore_object)    
    x.close()   
end = time.time()
logging.warning("creating xarray: %f", (end-start)/n)
'''