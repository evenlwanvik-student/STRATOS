from netCDF4 import Dataset
import time
import math
import azure
import zarr
import numpy as np

def get_blob_client(dataset):
    ''' create a client for the requested dataset '''

    CONTAINER_NAME  = 'zarr'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
    absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, dataset, ACCOUNT_NAME, ACCOUNT_KEY)
    return absstore_object