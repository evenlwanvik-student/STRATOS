# Testing

## Conversion time from xarray to geojson
The testing script is designed to time how long it takes to convert the downloaded xarray into a geojson file. The script imports a zarr blob from azure. The blob is specified by the 'BLOB_NAME' variable in zarr_to_geojson. The testing parameters are the number of latitude-elements and longitude-elements that will be used in generating the color grid (aka the size of the rectangle). Layer index may also be specified, but the performance should be approximately the same for all layers (depending on number of nan-grids of course). Start vertex can also be specified (0,0) - (291, 291), and will affect number of NaN vs color grids, and thereby also the total conversion time.

Procedure for test 1
1. Fill in desired test parameters
2. Build a docker image
3. Run an iterative docker container 
4. Run "python xarray_to_geojson_test.py" inside the container

### Test 1 results:
| Lat_elements | Long_elements | Conversion time |      Zarr file     | Comment                              |
|:------------:|:-------------:|:---------------:|:------------------:|--------------------------------------|
|      290     |      290      |    24+ hours    | chunked-time&depth | Approximation obviously              |
|       5      |       5       |      6.35 s     | chunked-time&depth | Only nan-grids (start edge: [0,0])   |
|       5      |       5       |      55.4 s     | chunked-time&depth | Colored grids (start edge: [200,20]) |
|       5      |       5       |      41.9 s     |    chunk-test-1    | Colored grids                        |
|       5      |       5       |      5.2 s      |    chunk-test-1    | Nan-grids                            |
|       5      |       5       |      434 s      |    auto-chunked    | Colored grids                        |
|       5      |       5       |       13 s      |    auto-chunked    | Nan-grids                            |


In conclusion, the chunking affects the performance. However, it is likely that even optimal chunking will result in a slow system when producing a large amount of color gridcells. The test only covers the conversion of a tiny bit of data, and it still takes more than half a minute to produce the geojson file.


### Test 2 results
A second test was performed, where only one geojson polygon (gridcell) was generated. The purpose was to identify the bottleneck of the xarray-to-geojson conversion.

| Zarr file          | Open zarr | Deep- copy | Extracting single  temperature | Add copy of feature template | Create reference to feature  | Insert hex into "fill" | Get coordinates  into geojson | Write to  outFile | Total conversion time |
|--------------------|:---------:|------------|:------------------------------:|:----------------------------:|:----------------------------:|:----------------------:|:-----------------------------:|:-----------------:|:---------------------:|
| chunk-test-1       |   7.50 s  | <0.1s      |             0.21 s             |             <1 ms            |             <1 ms            |          <1 ms         |             1.63 s            |        <1ms       |         1.84 s        |
| auto-chunked       |   7.43 s  | <0.1s      |             16.7 s             |             <1 ms            |             <1 ms            |          <1 ms         |             2.0 s             |        <1ms       |         18.7 s        |
| chunked-Time&Depth |   7.9 s   | <0.1s      |             0.26 s             |             <1 ms            |             <1 ms            |          <1 ms         |             1.89 s            |       <1 ms       |         2.15 s        |

REMARKS: simply opening the zarr file as an xarray takes over 7 seconds. This is only done once, regardless of how many gridcells is produced, but it is still a significant amount of time. From the table it is clear that there are two steps in the conversion process that are time consuming, namely extracting a temperature corresponding to coordinates and getting the correct coordinates of each geojson polygon. The extraction step can be optimized by choosing an appropriate chunking. The "coordinate-step" is harder to redeem, and considering this has to be done for every single geojson-gridcell that is being generated, it is safe to say that this is the bottleneck of the conversion. Note that the geojson_grid_coord function is called here, and since the function extracts lat/long data from the xarrays, chunking might also affect how fast/slow this step is. 

************************

## Time-lapse testing 11.07.2019
Tested with 10 timesteps, and the webpage is still a bit slow. 
Once the "start time-lapse" button is pressed:
* 10 requests are sent to flask
* When the javaScript receives a response, the geojson from flask is stored in an array under the corresponding timeindex
* A periodic function (runs every 1 second) adds the geojson layers to the map sequentially (removing the preceding layer in the process)

Results:
* The responses from flask does not arrive in a strictly ascending order
* The first response (time index 3) came after 8.6 s
* The last response (time index 9) came after 23.4 s
* The response tied to time index 0 came after 14.1 s

So the whole time-lapse takes a while, and since the temperatures are very similar at each time step it is very hard to see any change. Might want to change the color spectrum in order to visualize the difference better.

***********************

## Depth series testing 12.07.2019

We requested 20 depth layers in order to actually see that new layers were produced continuously. The same image was used in both a locally running container and in the app service in azure. The interval function for drawing depth layer was called every 600 ms for all the tests.

Test 1: A request for layer with index 0 is sent once "start depth series"-button is pushed. When response is received from flask, the layer is stored in geoJsonLayerArray. drawDepthLayer (the interval function) adds layer to map and send a request for the next layer. So in this test the layers are fetched sequentially one at a time.

| Request one-by-one | Total time | Slowest package | Fastest package |
|--------------------|------------|-----------------|-----------------|
| local container    |  1min 4s   | ~3 sec          | ~1.1 sec        |
| app service        | 3min 28s   | ~14 sec         | ~3.1 sec        |

Test 2: A request for the first two layers (index 0 and 1) is sent once "start depth series"-button is pushed. When response for the first layer is received from flask, the layer is added to the map and a request for the third layer (index 2) is sent to flask. Upon arrival of the second layer (index 1) response, the fourth layer (index 3) is requested and so on. So in this test we request the two next layers in an efficient manner.

| Request one + next | Total time | Slowest package | Fastest package |
|--------------------|------------|-----------------|-----------------|
| local container    |  48 s      | ~5.46 sec       | ~1.1 sec        |
| app service        | 1min 58s   | ~20 sec         | ~2.1 sec        |

Test 3: All 20 depth layers are requested at once. The repsonses from flask does not arrive in a strictly ascending order. The layers are rendered once the index in order has returned a response.

| Request all at once | Total time | Slowest package | Fastest package |
|---------------------|------------|-----------------|-----------------|
| local container     |  1min 2s   | ~54 sec         | ~14 sec         |
| app service         | 1min 35s   | ~1min 30 sec    | ~35 sec         |

NOTE: The process is much slower in the cloud regardless of how the layer requests are sent. Requesting one layer plus the next seems to be the best option, if the server is running in a local container. But requesting all the layers at once is actually the fastest option in the cloud. We have not recorded the results using different intervals for the drawDepthLayer function, but we tried some values in the range 50ms-900ms. Seemingly there was no significant difference in performance. Choosing a very small value will lead to many redundant calls and this caused the web page to lag slightly.

We logged the execution time of the different operations included retrieving the geoJSON layers. Here are some findings:
* Decompressing the azure blobs: range [0.1s , 1.2s]
* Get the shape of the array using meta data: ~ 0.1s
* Creating numpy arrays: ~ 0.1ms
* set color map range: ~ 1ms
* Double for loop generating grid: 2-3 seconds

So the `azure-to-json` function takes a couple of seconds for each layer, but there might be other things either on the clint or the server side that slows things down.