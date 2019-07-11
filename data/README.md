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

For this project, one of the main assignments was to find a viable way to display large datasets in a cloud environment. This also ment researching new methods for storage and access. Although zarr i still a very young project, it has been covered as the best of many newcomers in the field and enjoys a broad popularity within the [Unidata](https://www.unidata.ucar.edu/blogs/news/entry/netcdf-and-native-cloud-storage) community. In  short zarr is a python package providing an implementation of chunked, compressed, N-dimensional arrays. A zarr array is stored in any system that provides a key/value interface, for instance a directory in a normal file system, where keys are file names, values are file contents, and files can be read, written or deleted via the operating system.

```
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