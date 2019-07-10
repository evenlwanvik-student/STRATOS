import zarr
import xarray as xr
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

CONTAINER_NAME  = 'zarr'
BLOB_NAME       = 'Franfjorden32m/time&depth-chunked-consolidated-metadata.zarr'
ACCOUNT_NAME    = 'stratos'
ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='

absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)

chunks = {'time':1, 'zc': 1, 'yc': 294, 'xc': 291}
logging.warning("opening with chunks: %s", chunks)
ds = xr.open_zarr(absstore_object, consolidated=True)

logging.warning(ds)
#logging.warning(xr['temperature'])

logging.warning("creating arrays")
measurements = ds['temperature'][0,0].values
lats = ds['gridLats'].values
lons = ds['gridLons'].values

logging.warning(lats)

ds.close()

