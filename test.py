import json
import numpy as np
import os
from copy import deepcopy
import time
import math
import zarr
import sys
import logging
import warnings
import xarray as xr

CONTAINER_NAME  = 'zarr'
ACCOUNT_NAME    = 'stratos'
ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
dataset = "samples_NSEW_2013.03.11_chunked-time&depth.zarr"



bin_data = b"\x1a\x2b\x3c\x4d"
measurements = np.frombuffer(bin_data, ">i2")
print(measurements)

'''

#franfjord = zarr.storage.ABSStore(CONTAINER_NAME, "Franfjorden32m/samples_NSEW_2013.03.11_chunked-time&depth.zarr", ACCOUNT_NAME, ACCOUNT_KEY)
#norsok = zarr.storage.ABSStore(CONTAINER_NAME, "norsok/samples_NSEW.nc_201301_nc4.zarr", ACCOUNT_NAME, ACCOUNT_KEY)

#absstore_object['salinity']
with xr.open_zarr(franfjord) as franfjord_ds:
    with xr.open_zarr(norsok) as norsok_ds:
        print(franfjord_ds['salinity'])
        print(norsok_ds['salinity'])
'''