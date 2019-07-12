# Documentation for data folder

## 1 Modules
### 1.1 azure_to_json.py
This module creates a zarr azure blob storage ([ABSStore](https://zarr.readthedocs.io/en/stable/api/storage.html#zarr.storage.ABSStore) class) object, which is then used to create numpy arrays containing the measurements of the requested grid. There are [geojson](https://geojson.org/) templates are located in ```./templates/```. These templates are appended to the output object, and the data-arrays are encoded into the output geojson file, which is compatible with [Leaflet](https://leafletjs.com/).

## 2 History
A diverse set of methods for handling the azure blob interface and extraction of relevant grids has been implemented during this project. Most of these would produce an acceptable output, but mostly within unsatisfactory time and size limits. As this is a part of a summer internship, we see it fit to document the preceding iterations such that future developers know a few of the "do's and dont's". The section of code that has been developed the most is how to get a full grid directly from the azure block blob.

A multitude of libraries and methods has been used to try to achieve adequate execution time and memory usage, especially in regards to retreiving the requested grid as a subarray of the blob, e.g. [0, 0, :, :] (time,depth,lat,lon). 

##### 2.1 [STRAT-17](https://jira.code.sintef.no/browse/STRAT-17)-python-script-for-converting-a-simple-netcdf-grid-e.g-2x2-to-geojson-format
This version sucessfully initialized a local netcdf as a [xarray](http://xarray.pydata.org/)'s dataset. It could produce a geojson output which was compatible with Leaflet.
###### 2.1.1 Generating geojson polygons
Takes latitudes, longitudes and the edge from which to start transversing the grid plane as input args. It returns a list which will be written to the ```"features": "geometry": "coordiniates": [[]]```:  dictionary which was in beforehand appended to the output object. To create the polygon it iterates in both y and x direction, but has to reverse the inner loop on the second outer loop iteration, as it has to traverse in a square shape and return back to its original position.
```python
geojson_grid_coord(lats, lons, startEdge):
    ...
    return [[lat,lon],[lat, ...] ...]
```
It was still very verbose, and with a bit too many arguments as input.
###### 2.1.1 Main function
The main function at this moment simply opened a local netcdf file.
```python
azure_to_json(depthIdx, timeIdx):
    with xarray.open_dataset():
        latitude = ...
    ...
    return jsonData
```
##### 2.2 [STRAT-39](https://jira.code.sintef.no/browse/STRAT-39) Use zarr arrays stored in azure for web app
After a lot of research on the use of z-array ([zarr](https://zarr.readthedocs.io/en/stable/)), this seemed like the way to go forward. Although it is still a very young project, it has had a lot of coverage for being one of the 

## 3 zarr
There are a lot of project working towards the best solution for storage of big data (over 50Gb) in the cloud. The "old" convention is to store data locally, but as cloud storage technology evolves there is a shift to employ cloud storage and access the data using the internet. It is possible to upload the netCDF files as either a [block blob](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs) or , however this was tested and did not give satisfactory results.

### 3.1 Background
For this project, one of the main assignments was to find a viable way to display large datasets in a cloud environment. This also ment researching new methods for storage and access. Although zarr i still a very young project, it has been covered as the best of many newcomers in the field and enjoys a broad popularity within the [Unidata](https://www.unidata.ucar.edu/blogs/news/entry/netcdf-and-native-cloud-storage) community. In  short zarr is a python package providing an implementation of chunked, compressed, N-dimensional arrays. A zarr array is stored in any system that provides a key/value interface, for instance a directory in a normal file system, where keys are file names, values are file contents, and files can be read, written or deleted via the operating system. In a zarr dataset, the arrays are divided into chunks and compressed. These individual chunks cna be stored as files on a filesystem or as objects in a cloud storage bucket. The metadata are stored in lightweight .json files (.zarray in hierarchy shown below). 
```bash
root.zarr
    |-- temperature
    |   |-- .zarray
    |   |-- .zattrs
    |   |-- 0.0.0.0
    |   |-- 0.0.0.1
    |   |-- ...
    |
    `-- gridLats
        |-- ...
```
### 3.2 Simple tutorial when working with netcdf and zarr files
The xarray project has a zarr backend that allows for converting to and from xarray to zarr file structure. Since this feature is still young, xarray can only open zarr datasets that have been written by xarray.
##### 3.2.1 opening netCDF/zarr dataset in Xarray
Simply open the netCDF dataset:
```python
import xarray as xr
ds = xr.open_dataset('/path/to/mydataset.nc')
```
One can also open multiple datasets if they comprise a single dataset split into more than one file. If the files are properly formatted and sufficiently homogeneous, you can open them with a single line of xarray code:
```python
import xarray as xr
ds = xr.open_dataset('/path/to/mydataset/*.nc')
```
##### 3.2.2 export to Zarr format
The next step is to export your xarray.Dataset to a Zarr Directory Store:
```python
ds.to_zarr('/path/to/output/mydataset')
```
Xarray and Zarr have many different options for encoding and compression of the datasets. This can be passed to to_zarr via the encoding keyword argument, an example of chunking will be shown in a following step about cloud storage. 
##### 3.2.3 create a azure blob client for zarr files
First we need to create an interface between you, the zarr file format, and the blob storage account. [Zarr's storage module](https://zarr.readthedocs.io/en/stable/api/storage.html#module-zarr.storage) has classes for different distributed storage systems (Azure, Amazon's S3, Google Cloud Storage, ...). It's implementations of the [MutableMapping](https://docs.python.org/3/library/collections.abc.html) interface makes it easy to access the different sets of data like groups, chunks, metadata, etc. Firstly, we create our Azure Blob Client (ABS):
```python
import zarr
abs_client = zarr.storage.ABSStore(container, prefix, account_name, account_key)
```
where ```container``` is The name of the ABS container to use, ```prefix``` the location of the "directory" to use as root of the storage hierarchy, ```account_name``` the storage account name and ```account_key``` the access key to the storage account.
In order to use the Azure Storage clients in python, you'll need to install the [Microsoft Azure Storage SDK for Python](https://github.com/Azure/azure-storage-python). 
##### 3.2.4 Creating/updating blob from local netcdf
For simply creating/uploading a new Zarr blob, as long as no blob exists with the same prefix, you only need to use xarrays ```to_zarr``` function with the azure blob client as argument:
```python
ds.to_zarr(abs_client)
```
If you want to update an existing blob, you'll have to remove the existing file structure before before uploading:
```python
abs_client.rmdir()
ds.to_zarr(abs_client)
```
It is possible to for instance append new groups to an existing blob, but this won't be covered in this tutorial as it's not relevant for this project.
##### 3.2.5 Creating zarr blob directly from netcdf blob
```python
    block_blob_service = BlockBlobService(account_name, account_key)
    #with open(output_path, 'w+') as f:
    block_blob_service.get_blob_to_path(container_name, blob_name, output_path)
with xr.open_dataset(netcdf_path, chunks=chunks) as ds:
```


