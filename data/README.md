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
geojson_grid_coord(lats, lons, startNode):
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

For this project, one of the main assignments was to find a viable way to display large datasets in a cloud environment. This also ment researching new methods for storage and access. Although zarr i still a very young project, it has been covered as the best of many newcomers in the field and enjoys a broad popularity within the [Unidata](https://www.unidata.ucar.edu/blogs/news/entry/netcdf-and-native-cloud-storage) community. In  short zarr is a python package providing an implementation of chunked, compressed, N-dimensional arrays. A zarr array is stored in any system that provides a key/value interface, for instance a directory in a normal file system, where keys are file names, values are file contents, and files can be read, written or deleted via the operating system.

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

## 4  Decapitating bottlenecks
### 4.1 Generating geojson object
Before we started this mission (15/07/2019), the average execution time (100 samples) for generating a geojson output object with 250 grids specified took about 6.32 seconds.

#### 4.1.1 testing deepcopy
After a lot of testing and averaging with over 10 runs at 250 grid size, it seems like deepcopy occupies about **2.11/5.51 ~ 38.3%** of the execution time. By replacing the deepcopy call
```python
jsonData['features'].append(deepcopy(feature_template))
```
by 
```python
jsonData['features'].append(json.loads(json.dumps(x)))
```
the fraction was reduced to **1.86/5.06 ~ 36,7%**. Not a significant reduction, but i guess every little helps. 
The next test was rather to open the ```features``` template once, and dump/load or deepcopy the template every time, maybe it is faster to just open the template every time it is to be appended?
```python
def get_feature_template():
    with open(feature_template_path) as feature_json_template:
        return json.load(feature_json_template)
jsonData['features'].append(get_feature_template())
```
With this I managed to reduce the average execution time to 4.97 seconds, where appending the feature used **1.41/4.97 ~ 28%** of the total execution time, which is a almost a 10% reduction!
Opening a file every time for n^2 grids seems a bit tedious, so the next thing on the menu was to simply have a function where the template ```feature``` dictionary is simply static code:
```python
def get_feature_template():
    return {"type": "Feature",
            "properties": {"fill": "#00aa22"},
            "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[ 0.0,0.0], [ 0.0,0.0], [ 0.0,0.0], [ 0.0,0.0], [ 0.0,0.0] ]]}}
```
This seemed to be the most effective solution by far, as it further reduced the time spent on appending the template dictionary by **0.080/3.38 ~ 2.37%**. No clue why I didn't come to this simple conclusion initially..
Anywow, with the temlate appending only occupying 2.3% of the execution time, which is a ~36% reduction from when we appended a deepcopy of a dictionary object, we can further investigate other bottlenecks.

#### 4.1.2 appending list vs using nested loop
The original algorithm used a nested loop which traveled in a square formation with a area of 1 geospacial index in lat/lon direction. This square makes up a polygon which is inserted into the geo


Tested two different methods: 
1. Nested loop for inserting polygon coordinates into the list returned to the geojson feature the algorithm is working on. **Average execution time with 100 samples: 6.32s**. The algorithm would do something like this:
```python
for y in range(n)
    for x in range(n)
    list = []
        for i in range(2)
            for j in range(2)
                list.append([lat[i,j],lon[i,j]]) 
    feature['geometry']['coordinates'][0] = list
```

2. Simply inserting a list with the given indexing for a polygon directly into the coordinates of the feature. **Average execution time with 100 samples: 5.98s**
```python
for y in range(n)
    for x in range(n)
        feature['geometry']['coordinates'].append([
            [lats[y,x], lons[y,x]],
            [lats[y+1,x], lons[y+1,x]],
            ... )]
```

As thought, there is no significant time difference. However, it is much more readable and spends less memory, so the new method (nr. 2) is preferred.

#### 4.1.3 Reduce size of geojson object
When we have a grid of about 200x200 measurements, the geojson object is about 8-9Mb. Since we have to define 5 edges for Leaflet to create the given polygon, and each latitude and longitude is encoded as 64 bit floats (16 decimals and 1-3 integer), each polygon spends about 20 * 5 * 2 (20 characters * 5 edges * 2 lat/lon coordinates) = 200 characters for each polygon. Let's say we have a 200x200 grid, the original size spent on defining the coordinates of the polygons would then be at 8,000,000b - 8.0Mb. When testing a 250x250 grid, the generated output file with full precision (16 decimals) was ```19.1 Mb``` and with rounding (4 decimals) it was at ```17.0 Mb```. It is not a very powerful reduction, but considering that about half of the measurements were on land, and hence won't be included in the geojson object, i believe that this will scale and have some significance for larger datasets..