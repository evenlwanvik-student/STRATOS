import xarray as xr
import logging
import time
import numpy as np
from zarr.storage import ABSStore
#from zarr import blosc
import blosc

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

CONTAINER_NAME  = 'zarr'
BLOB_NAME       = 'Franfjorden32m/time&depth-chunked-consolidated-metadata.zarr'
ACCOUNT_NAME    = 'stratos'
ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='

start = time.time()
absstore_object = ABSStore(CONTAINER_NAME, BLOB_NAME, ACCOUNT_NAME, ACCOUNT_KEY)
end = time.time()
logging.warning(end-start)

start = time.time()
decom_temps = blosc.decompress(absstore_object['temperature/0.0.0.0'])
decom_lats = blosc.decompress(absstore_object['gridLons/0.0'])
decom_lons = blosc.decompress(absstore_object['gridLats/0.0'])
end = time.time()
logging.warning(end-start)


start = time.time()
temps = np.frombuffer(decom_temps, dtype='<f4')
lons = np.frombuffer(decom_lats, dtype='<f4')
lats = np.frombuffer(decom_lons, dtype='<f4')
end = time.time()
logging.warning(end-start)


logging.warning(lons)
logging.warning(len(temps))
logging.warning(len(lons))
logging.warning(len(lats))

'''
chunks = {'time':1, 'zc': 1, 'yc': 294, 'xc': 291}
logging.warning("opening with chunks: %s", chunks)
start = time.time()
ds = xr.open_zarr(absstore_object, consolidated=True)
end = time.time()
logging.warning(end-start)
logging.warning("size: %d", ds.nbytes)
#logging.warning(xr['temperature'])
logging.warning("creating arrays")
start = time.time()
measurements = ds['temperature'][0,0].values
end = time.time()
logging.warning(end-start)
start = time.time()
lats = ds['gridLats'].values
end = time.time()
logging.warning(end-start)
start = time.time()
lons = ds['gridLons'].values
end = time.time()
logging.warning(end-start)
ds.close()
'''