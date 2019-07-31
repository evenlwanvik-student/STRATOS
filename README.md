# Stratos

Summer project at SINTEF Ocean where the goal was to extract data from netCDF files from SINMOD, OSCAR and DREAM and display this data on a web page.
We were given netCDF files as azure blobs, and we have pre-processed these files into multiple zarr-blobs which contain chunks of the netCDF data. The zarr blobs are also stored in azure. A flask server hosts a webpage where the client can request different kinds of data to inpsect. The server fetches the appropriate data from the zarr blobs, processes this data, and returns a response that can be interpreted and displayed in the browser. The back-end part of the system is written in python, while the front-end is created with html, css and javaScript code. The app runs in a docker container in the azure cloud and can be accessed here: http://sommeroppgave-stratos.azurewebsites.net/index

Authors: Even Wanvik and Maria Skårdal
***************************************************
## Usage

## Demo web page
* Not all datasets are fully tested and debugged, so some strange behavior might occur depending on input
* Frænfjorden and Oscar_surface datasets have been tested the most and are recommended to use
* Legends are just for show so do not pay attention to them. They are not related to the data as we did not prioritize to make this dynamic.
* Color encoding is not really customized to all the different data types, so don't get caught up in this either.
* The input fields have default values so the only thing that NEEDS to be filled out is dataset and datatype.
* The velocity demo is heavily dependent on plugins and borrowed scripts, but the data that is displayed is still fetched from blob as per usual.

### How to run the server in docker:
* In powershell:
    `Set-NetConnectionProfile -interfacealias "vEthernet (DockerNAT)" -NetworkCategory Private`
* Enable shared C-drive in docker desktop settings
* Run these in terminal:\
    `docker build -t stratos .`\
    `docker run -p 80:80 stratos`

### How to push image to container registry
1. Login to azure registry:
    `az acr login --name stratoscontainers`
2. Tag the image:
    `docker tag <Image_ID> stratoscontainers.azurecr.io/name`
3. Push it to the registry
    `docker push stratoscontainers.azurecr.io/name`

### Convert GeoJSON to TopoJSON
 * `npm install -g topojson` (This requires node.js installed) 
 * `geo2topo -q 1e4 -p -o topo.json -- geo.json` 

*************************************************************
# Brief summary of the whole project:
The back end of the app is written in python, and we chose to use a flask server. 
Initially we extracted data form the netcdf files with the python library [xarray](http://xarray.pydata.org/en/stable/). The data was then converted to the [GeoJSON](https://geojson.org/) format with functions we made from scratch. One of the reasons we wanted to use GeoJSON is that it is very compatible with [Leaflet](https://leafletjs.com/reference-1.5.0.html) which is the javaScript library we use to make the map in the browser and add data to it. Xarray proved to be slow, especially when we started fetching data from netCDF files in the cloud. So we changed gear a little and started using [Zarr](https://zarr.readthedocs.io/en/stable/) instead. Zarr is a python package that allows for convinient chunking of data, so that no more data than necessary can be extracted at a time. We converted netCDF blobs to zarr blobs, and generated GeoJSON from the data retrieved from the cloud. We were successful in generating and showing the GeoJSON data, but it wasnt't as fast as we had hoped. So we looked into using [TopoJSON](https://github.com/topojson/topojson/wiki), which is an extension of GeoJSON. THis format was more lightweight than GeoJSON, but it proved to be very difficult to generate TopoJSON from scratch. We were able to generate somehting that rendered (almost) correctly, but it was not smaller and faster than what we had already managed with geoJSON. We also tried to pregenerate topoJSON data by converting already made geoJSON files. This saves processing time, but the data still needs to be retrieved from azure blob storage, so it's not as fast as we hoped. However, pregenerated topoJSON performs better that pregenerated GeoJSON. Towards the end, we also attempted to display velocity vectors (ocean current and wind) on the map. We had moderate success here; we used a plugin and some borrowed scripts to show the vectors on the map, but this caused the rendered data to be slightly out of place (some of it was on land etc).

For more thorough descriptions of what we have done the past 6 weeks see the `testing.md` file in the 'tools' folder, and the `README.md` file in the 'data'-folder.

*****************************************************************
# JSON format
JSON (JavaScript Object Notation) is a lightweight data-interchange format. It is easy for humans to read and write, and it is easy for machines to parse and generate.

## Alternatives to using GeoJSON
Remarks: An advantage of using geoJSON is that it is very compatible with Leaflet. However, when the geoJSON objects become large, rendering is slow and zooming and dragging functions are very sluggish. 
Alternative approaches:
* Convert NetCDF to Shapefile 
    * need three files: .shp, .dbf, .shx () 
    * Shapefile can be displayed by Leaflet (although some suggest converting it GeoJSON..)
    * Not a good idea according to Petter :)
* Convert NetCDF file to GeoTIFF using GDAL
    * GDAL is a translator library for raster/vector data
    * GeoTIFF is raster data and can be used to generate a tilelayer to display with Leaflet
    * Attempted this briefly, but did not succeed. It might be worth looking into again if there is time, but we are not sure if this will be faster and smaller than geoJSON
* TopoJson
    * Primary advantage: its smaller than GeoJSON
    * the same output is 17 KB with GeoJSON and 5 KB with TopoJSON
    * Downside: more complex file format, has to be converted back to GeoJSON in javaScript
    * Could be beneficial if we are certain that rendering GeoJson data in Leaflet is fast (not sure that this is the case).
* Use Esri's ArcGIS with ArcPy and ArcMap
    * Disadvantage: need to purchase ArcGIS

Useful site for further options: https://gisgeography.com/gis-formats/


## TopoJSON vs GeoJSON performance
Motivation for using TopoJSON:
TopoJSON represents lines and polygons as sequences of arcs rather than sequences of coordinates. For the temperature grid, the polygons have shared borders, but with GeoJSON all these coordinates must be duplicated for each polygon. TopoJSO takes advantage of this redundancy. Additionally TopoJSON can be quantized, where coordinates are represented as integers instead of floating-point values with many decimal places. (We lose some information here, but but typically a small-scale map does not require the full precision of the original geometry). In order to convert the int-coordinates to latitude and longitude, the topology defines a linear transform consisting of a "scale" and "translate". The coordinates in topojson are delta-encoded such that each successive x- and y-value is relative to the previous one.

We converted a locally stored geojson file to a topojson file, and stored both files in stratos/data/outputs.
We then requested the two different local files with jQuery in javaScript and rendered the files with leaflet:

| Format   | File size | Content download | Time  | Total time until rendered |
|----------|-----------|------------------|-------|---------------------------|
| GeoJSON  | 8.5 MB    | 952.92 ms        | 1.0s  | ca 2.5 s                  |
| TopoJSON | 2.0 MB    | 185.50 ms        | 208ms |  ca 1.5 s                 |

This encouraged us to continue exploring TopoJSON, and we attempted to generate a TopoJSON object from zarr-arrays in a similar manner as the GeoJSON data was produced. The recurring "JSON-serlialization" problem was solved by adding an encoder class which is called in `json.dumps()`. 
Here is a comparison of the performance when we generated the json files upon a jQuery request:

| GridCells | Function        | Generated file   | Time   | Comment                    |
|-----------|-----------------|------------------|--------|----------------------------|
| 290x290   |zarr_to_geojson()| 7.4 MB (Geojson) | 3.71 s |                            |
| 290x290   | zarr_to_topo()  | 15.6 MB (Topo)   | 9.90 s | Generating all arcs        |
| 290x290   | zarr_to_topo()  | 6.7 MB (Topo)    | 7.30 s | Disregarding NaN-temp-arcs |

Unfortunately topoJSON took longer to generate than GeoJSON. It was difficult to come up with an efficient algorithm that generated topoJSON data from the zarr-arrays retrieved from azure (For specifics of the algorithms we used, see zarr_to_topo.py and read the explaining comments). We tried and failed a lot here. We did succeed at making a topojson file from scratch. However, it rendered triangles insetad of polygons for some reason, except for at the top left border, so we did something wrong in there. We did not try to fix this bug though, because the output file was larger and slower than its geoJSON counterpart. Some of the main problems were that when we generated all the arcs in the entire layer, we didn't exploit the fact that some of the gridcells were on shore and would not be rendered. This consumed both time and memory, so this solution was far from optimal. The tricky part was to keep track of which gridcell-polygons corresponded to which indeces in the comprehensive 'arcs' list. The algorithm we came up with for pairing the polygons with the correct arcs, relied on a "full" arcs list. 

To avoid the unnecessary work of generating arcs that would never be used, we tried to disregard the polygons with NaN-temps when generating the TopoJSON arcs, and simply put `None` at these particular indeces in the arcs list. But this introduced another problem which was that some of the arcs between a temperature-polygon and a NaN-temp polygon were never generated. This caused an error on the client side and Leaflet complained about `Uncaught TypeError: Cannot read property 'length' of undefined`. So in order to deal with this, we tried to check if the four adjacent polygons had temperatures that were real numbers, and generate the arcs if any of them did. This type of checking caused zarr_to_topo to run even slower than if we just generated ALL the arcs.

Furthermore, we were not able to figure out how to utilize the "scale" and "translate" members of the linear transform that contributes to compressing topoJSON, and how to connect this with the logic of the arc indeces. Most of the topojson examples from the internet were concerned with converting geojson data to topojson. Since we wanted to skip the geojson-making all together, this was not very helpful. All in all, the topoJSON format is more complex than GeoJSON. We did not succeed at generating output that would help us achieve faster dynamics, probably because our algorithms aren't optimal. So we abandoned the idea of making topoJSON from scratch, and stared looking into pregenerating the data instead. 

NOTE: even if we did not succeed at generating topoJSON sufficietly fast in real time, there is certainly room for improvement in our (somewhat verbose) algorithms, and the topoJSON file format might still have potential.

MAJOR PROBLEM:
Things are incredibly slow when the app runs in the cloud. The same image was used both places, and the time was found by examining the F12 network tab.

| GridCells | Type     | Generated file | Execution in local container | Execution in cloud |
|-----------|----------|----------------|------------------------------|--------------------|
| 290x290   | GeoJSON  | 7.4 MB         | 4.9 s                        |   ~ 23 sec         |
| 290x290   | TopoJSON | 15.6 MB        | 10.5 s                       |   ~ 90 sec         |

The whole idea of being able to generate something fast enough in the cloud seems to be out of reach at this point since the project is coming to a close soon.

## Pre-generating JSON files and storing them as blobs
Since the real-time making of both GeoJSON and TopoJSON files was too slow in the cloud, we looked into pregenerating these files and accessing them directly from azure blob storage. Unfortunately this also takes a while..

Initially a 290x290 Frænfjorden polygon GeoJSON grid was generated and stored in a local file. Then the GeoJSON-file was uploaded to azure along with the converted TopoJSON equivalent. Both blobs were fetched with the get_json_blob function in flask, and returned to the javaScript and then rendered with Leaflet. We retrieved the blob with `block_blob_service.get_blob_to_text(CONTAINER_NAME, BLOB_NAME)`, but we did not have time to research if there are faster ways of getting the json blob from the cloud.

| Type     | Size   | Local server time | Local container time | App Service time |
|----------|--------|-------------------|----------------------|------------------|
| GeoJSON  | 7.8 MB |      7.99 s       |        7.63 s        |      7.62 s      |
| TopoJSON | 3.5 MB |      3.63 s       |        3.54 s        |      3.43 s      |


Fortunately, things were now running faster in the cloud, but it was still a little sluggish. TopoJSON is clearly better than geoJSON for this purpose, if pre-generating data is a path we want to continue down. However, it should also be mentioned that it takes about 2 seconds from the package is received and downloaded on the client side until the data is rendered on the Leaflet map, so the user experience still isn't great. Also, when the json-files get too large, Leaflet struggles and hangs a lot.

We did not make a python script that converts geojson to topojson, but instead we converted the files manually in the terminal. However, if conversion is to be done on a larger scale with multiple files, using a python script would certainly be the best approach.
We ran the following commands in the directory of where the geojson files were stored:\
 `npm install -g topojson` (This requires node.js installed) \
 `geo2topo -q 1e4 -p -o topo.json -- geo.json` \
 The `geo2topo` command produces the topo.json file that stores the same data as the geo.json file. We quantize the data with 1*10^4 resolution (`-q 1e4`), and this is a way of reducing the size of the TopoJSON file.


The summer project is now at its conclusion, and although our system is not as fast and agile as we wanted it to be, we hope that our code and research might still be of use if anyone wants to pick up where we left off. In retrospective, we may have written too much of the code from scratch instead of using premade plugins (ref displaying velocity data) etc. 
