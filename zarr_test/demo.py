import shutil
from azure.storage.blob import BlockBlobService
from azure import *
from azure.storage import *
import zarr
import xarray


netcdf_path = "data/example.nc"
zarr_path   = "data/example.zarr"
'''
# Create local z-array from netcdf data
with xarray.open_dataset(netcdf_path) as data:
    try:
        shutil.rmtree(zarr_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    data.to_zarr(zarr_path)
'''
# hver gruppe er gitt en metadata fil og en eller flere komprimerte binaere filer ut fra hvordan vi har valgt aa chunke dataen
#tree data/ -s
#du -hs data/*


'''
We can also choose the shape of the compressed array by choosing chunk sizes depending
on what fields we want to extract, e.g. every time sample.
Using smaller chunk sizes will use more space for metadata as it has e.g. 1-byte
metadata per timestamp instead of one for the whole 24 elements.
'''

'''
chunk = {'lat': 10, 'lon': 10, 'time': 5}

encoding = {'my_variable': {'dtype': 'int16', 'scale_factor': 0.1,
                               'zlib': True}}

with xarray.open_dataset(netcdf_path, chunks=chunk) as data:
    try:
        shutil.rmtree(zarr_path)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    data.to_zarr(zarr_path)
'''


container  = 'zarr'
blob       = 'Franfjorden32m/samples_NSEW_2013.03.11-chunked_time.zarr'
account    = 'stratos'
key        = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='


# Create a Azure Blob Service object to the z-array stored in azure

abs_object = zarr.storage.ABSStore(container, blob, account, key)

# copy local zarr to azure cloud
my_zarr = zarr.DirectoryStore("path/to/zarr")
zarr.convenience.copy_store(my_zarr, abs_object)

'''
with xr.open_zarr(abs_object) as abs_zr:
    print abs_zr
'''