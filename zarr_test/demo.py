import shutil
from azure.storage.blob import BlockBlobService
from azure import *
from azure.storage import *
import zarr
import xarray as xr


netcdf_path = "data/example.nc"
zarr_path   = "data/example.zarr"


'''
# Create local z-array from netcdf data
with xr.open_dataset(netcdf_path) as data:
    try:
        shutil.rmtree(zarr_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    data.to_zarr(zarr_path)
'''



''' Open zarr as xarray again, when we open it we can see that zarr
automatically chose chunk sizes'''
'''
with xr.open_zarr(zarr_path) as data:
    print(data)
'''


'''
We can also choose the shape of the compressed array by choosing chunk sizes depending
on what fields we want to extract, e.g. every time sample.
Using smaller chunk sizes will use more space for metadata as it has e.g. 1-byte
metadata per timestamp instead of one for the whole 24 elements.
'''
'''
chunk = {'lat': 170, 'lon': 180, 'time': 1}
with xr.open_dataset(netcdf_path, chunks=chunk) as data:
    print("netCDF dataset: ", data)
    try:
        shutil.rmtree(zarr_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    data.to_zarr(zarr_path)
'''
#tree data/ -s
#du -hs data/*




container  = 'zarr'
blob       = 'Franfjorden32m/samples_NSEW_2013.03.11-chunked_time.zarr'
account    = 'stratos'
key        = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='


# Create a Azure Blob Service object to the z-array stored in azure

abs_object = zarr.storage.ABSStore(container, blob, account, key)
'''
with xr.open_zarr(zarr_path) as zr:
    abs_object = zr
'''

'''
with xr.open_zarr(abs_object) as abs_zr:
    print abs_zr
'''