# Documentation for data folder

## 1 Modules
### 1.1 zarr_to - _geojson.py, _topojson.py, and _velocity.py
These module creates a azure blob storage ([ABSStore](https://zarr.readthedocs.io/en/stable/api/storage.html#zarr.storage.ABSStore) class) object for the zarray file structure, which is used to create numpy arrays from the compressed zarray chunks containing the measurements of a requested grid. There are templates located in ```./templates/```, which are used to create a output object with a format compatible with [Leaflet](https://leafletjs.com/).

### 1.1 color_encoding.py
Generates the correct color encoding in hexadecimal, which is used as the fill-value of the geojson/topojson polygons. The fill-value is determined by a rgb range (color map) and measurement range.

##### 2.1 [STRAT-17](https://jira.code.sintef.no/browse/STRAT-17) opening local netcdf file and displaying a single polygon in leaflet
This version sucessfully initialized a local netcdf as a [xarray](http://xarray.pydata.org/)'s dataset. It could produce a geojson output which was compatible with Leaflet.

It had a function that simply took the latitudes, longitudes and the edge from which to start traversing the grid plane as input args. It returned a list to be written to the geometry coordinates of the geojson object. To create the polygon it iterates in both y and x direction, but has to reverse the inner loop on the second outer loop iteration, as it has to traverse in a square shape and return back to its original position. This procedure is still used today, however instead of using a "large" function for iterating correctly and allocating memory, it simply inserts the given data into lists in the object. 

Opening a local netcdf file is very fast. Indexing the fourth dimension every time we inserted into the geojson object howeverm, was very tiresome.

##### 2.2 [STRAT-23](https://jira.code.sintef.no/browse/STRAT-23) Copying subsets of the xarray dataframe
The last commit of this branch says it reduced the execution time of creating a geojson output showing 10 grids from 2.1 seconds to 0.6 seconds by creating copies (deepcopy) of subsets of the xarray dataframe. Although it didn't solve the problem of having to initialize the full xarray, it was a small success.

The main issue still was that we were using a local copy of a netcdf file, but we needed to be able to stream data from the cloud. Azure does not have any effective solution to streaming subsets of netcdf data, and it doesn't seem like the community uses anything like this. 

##### 2.3 [STRAT-39](https://jira.code.sintef.no/browse/STRAT-39) Using zarray (zarr) 
With zarray, however, we can initialize a client to a zarray blob, where the data is stored as compressed chunks in a normal file hierarchy structure. More about zarr later in this document. By using the zarray ABSStore class (Azure Blob Storage) created by the zarray project, and a few self produced tools (```tools/azure_utils.py```), we were able to create zarray blobs.

It only takes about about a few microseconds to create the zarray blob client, but we still used xarray to open the datasets, which still took 9-11 seconds. We thought about chunking at this point as well, but since we were still using xarray to open the data, it became a compromise between opening the xarray frame or indexing the data faster.

##### 2.2 [STRAT-51](https://jira.code.sintef.no/browse/STRAT-51) Using metadata consolidation for xarray
Had an idea of opening the xarray with input ```consolidate=True```, where the idea is to reduce overhead for every connection to the cloud storage. By consolidating the metadata before loading datasets, you can reduce the overhead significantly. 

However, at this point I figured out that we could decompress a zarray chunk blob by using using the same compression library used by zarray to create the blob. This buffer could then be opened as a numpy array and shaped based on grid dimensions:
```Python
buffer = zarr.blosc.decompress(absstore_obj[f'temperature/0.0.0.0'])
data = np.frombuffer(buffer, dtype='<f4').reshape(293,290)
```
The time spent opening xarray was reduced from 10 to about 0.3 seconds by accessing the chunk directly and regenerating it as an numpy array. I believe that this is the best solution for accessing cloud data at this point. However, I also believe that the zarr project will open doors to more original and user-friendly approaches.

## 3 zarr
There are a lot of project working towards the best solution for storage of big data (over 50 Gb) in the cloud. The "old" convention is to store data locally, but as cloud storage technology evolves there is a shift to employ cloud storage and access the data using the internet. It is possible to upload the netCDF files as either a [block blob](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs) or , however this was tested and did not give satisfactory results.

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

This tutorial is simple and somewhat deprecated. I would encourage you to have a look at the utilities and their descriptions in ```tools/azure_utils.py```. 
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

## 5 Other issues
### 5.1  Making all datasets (Franfjord, norsok and OSCAR for now) and types of measurements available for the user 
Each model has different measurements, dimensions, coordinate-encoding, fill-values, datatypes etc. Since a lot of code were hard-coded for Franfjord, a lot of changes to make it more receptive was needed. The code changes perceived as trivial will not be mentioned here.

#### 5.1.1 Color encoding
The old code found a new extrema (min/max) for every requested grid, which works whenever a single grid is to be analyzed. However, it would be no changes at all whenever displaying a time series of the model. The current code uses config.py to store the ranges of each datatype. These values were found by going through the full 3 to 4-D datasets for each measurement to find the min and max. Whenever a value exceeds these (in case a new dataset is appended to the zarr blob) it will log a warning and saturate it to be within the given range. This means that this configuration would be changed in the future whenever new datasets are included to the cloud.

#### 5.1.2 Different datatypes


Each of the three models implemented at this time use different fill values: "Franfjorden" - ```NaN```, "norsok" - ```-32768``` and OSCAR - ```3e+38```. The previous method found a new min-max value for the color map with each grid. However, this ruins the visualization of the temperature difference between time and layers. A temporary (?) solution was to create a config file where each min and max of a given dataset and datatype is held. These extrema was found by looking thorugh the full datasets, but in the future there might be some variation between datasets at different times (seasons), and is hence temporary.

The biggest problem that arose from including the OSCAR model was that they use different dimensions and names for coordinates and measurments. 


#### 5.1.3 Problems decompressing norsok measurements
Difficulties decompressing the norsok "<i2" datatypes for the measurements, no clue what the problem is, I've been stuck on this for a couple of hours in the past. I've tested the blosc library compressing and decompressing my own arrays, seems to work just fine for the "<i2" datatypes. The metadata is the same as for Franfjord, the only difference is that norsok use "<i2" datatypes and Franfjord use "<f4":
```Python
{
    "chunks": [
        635,
        1019
    ],
    "compressor": {
        "blocksize": 0,
        "clevel": 5,
        "cname": "lz4",
        "id": "blosc",
        "shuffle": 1
    },
    "dtype": "<i2",
    "fill_value": "NaN",
    "filters": null,
    "order": "C",
    "shape": [
        635,
        1019
    ],
    "zarr_format": 2
}
```
This problem has been saved for later, as this should be solvable in the future. Our focus should be with researching existing and new methods for the project.

The range for the norsok measurements given in config.py should be:
```Python
"norsok": {
    "temperature": {
        Should be: "min": 271, modified to: 21000
        Should be: "max": 285  modified to: 27000
    },
    "salinity": {
        Should be: "min": 11.00, modified to: -25000
        Should be: "max": 38.00  modified to: -9000
    }
}
```
This have not been given too much thought, the limits might be flipped due to the clash of data types.


#### 5.1.4 Modularization and compatability
One problem when dealing with three different datasets (models) is to make one module compatible with them all. It is probably worth it in the beginning of such a project. For instance, if you there are a lot of optimizations to be done, you would have to change all the modules etc. However, it is probably much cleaner and faster to have the microservice call different modules/functions whenever a certain dataset is chosen.

## 6 Velocity vectors
Found a wonderful plugin called ```leaflet-velocity```. As most leaflet applications, it also uses a json object as input. However, it is a much smaller format, as you only need to define direction, start and end of grid, a dataset of all the velocities. The object is an list of two datasets, one for eastward and one for northward velocity. 
``` Python
[{
    "header": { EASTWARD VELOCITY }
    "data": [...]
    }, {
    "header": { NORTHWARD VELOCITY }
    "data": [...]
}]
```
The data needs to be a signle flattened array, which will be turned into the correct velocity vectors as you define the start and end of grid, number of elements in x and y direction, and the resolution of x and y.

For the current build, it is possible to visualize wind velocity and ocean current vectors for Norsok and Franfjorden. They render the correct vectors (haven't had enough time to analyze it properly), although the orientation of the grid is skewed by 45 degrees. That is, the netcdf grids are all skewed by 45 degrees on a globe surface, while the leaflet-velocity convention is perpendicular with the lat/lon axis of a non-tilted earth.
