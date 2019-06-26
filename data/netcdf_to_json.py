import xarray as xr
import json
import numpy
import os
from copy import deepcopy
import time # for execution time testing
import math

from color_encoding import temp_to_rgb

'''
 1. load template geojson file as DATA
 2. load output geojson file as output
 3. load netCDF file as source
 4. run function for inserting source data into the temporary (templated) data file
 5. dump the data file into outputfile (the geojson file to be used in leaflet)
 create subgrid with indexes:
 (221,19) - (222,20) -> polygon "route" becomes (221,19), (221,20), (222,20), (222,19), (221,19)
 
     *(221,19) -> (221,2)
         ^          |
      (221,20) <- (222,20)                         
                          
these were the 2x2 grid with the largest differences in temperature (about 0.5-1K difference)

    * We should probably implement some sort of dynamic rendering which makes
        the grids larger depending on how far out the user zoom.
        - Depending on if temperature is called, only create xarray subsets of temperature and coordinates
        - Depending on zoom, only extract every other or 4.th squares and extrapolate from the edge throughout
            the other squares
        - We probably have to change geojson to take geological coordinate and the target unit as seperate arguments
    * Make it compatible with other measurements
        - 

    (24/06/2019): In the first round this can extract a single 2x2 grids.
    (...): It now colors the grid depending on surface temperature# these were the 2x2 grid with the largest differences in temperature (about 0.5-1K difference)
'''

# define paths to files
initial_template_path = "templates/initial_template.json"
feature_template_path = "templates/feature_template.json"
source_path = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
output_path = "outputs/surface_temp.json"


def geojson_grid_coord(target, lats, lons, startEdge):
    '''
    takes a xarray object of a netCDF file as source and variable loaded
    with a geojson dictionary template as target. 
    gridDim is the size of the square grid to be rendered, default is 2 (2x2)
    To show differences in temperature, the temperature is encoded into 
    rgb hexadecimal and inserted into the "fill" under "properties" of the 
    polygon. The polygon itself is inserted into the "coordinates" key under "geometry"
     
    nested loop:
    1. for each square within a given size
    2. y-direction 
    3. x-direction 
    always iterate over polygonedges and squares in the same convention as in moduledescription
    '''
    
    coord_list = []

    xyRange = range(2)    # the box is 2x2, i.e. dimension of one side is 2
    polyEdgeIdx = 0             # The current index of the polygon square
    
    for y in xyRange:           # iterate y
        innerRange = xyRange              
        if y == 1:
            innerRange = reversed(xyRange)     # backward iteration to complete the polygon
        for x in innerRange: # iterate x
            yx = (startEdge[0]+y-1, startEdge[1]+x-1) # (y,x) defined as such in the netCDF file
            lat  = float(lats[yx])
            lon  = float(lons[yx])
            # OBS! The GIS lat/lon is different from geojson standard, so these are "flipped"
            target['geometry']['coordinates'][0][polyEdgeIdx][0] = lon 
            target['geometry']['coordinates'][0][polyEdgeIdx][1] = lat
            if polyEdgeIdx == 4: # the last list must always be the same as the first
                target['geometry']['coordinates'][0][4][0] = lon
                target['geometry']['coordinates'][0][4][1] = lat
            polyEdgeIdx += 1
    
    return coord_list


def geojson_grid_temp(T_in, T0=272, T1=282):
    ''' Get T from T_in if not nan, convert to RGB hex and insert into T_out reference'''
    return temp_to_rgb(T_in,T0,T1)


def get_initial_template():
    with open(initial_template_path, "r") as template:
        return json.load(template)


def get_feature_template():
    with open(feature_template_path) as feature_json_template:
        return json.load(feature_json_template)


def write_output(data):
    # open and dump data to output geojson file, remove if exists
    if os.path.isfile(output_path):
        os.remove(output_path)
    # open the final product file as output 
    with open(output_path, "w+") as output: 
        # dump new data into output json file 
        json.dump(data, output, indent=4)    


def netcdf_to_json(startEdge=(0,0), nGrids=10, gridSize=1, T0=275.8, T1=279.5):
    ''' 
    Inserts netCDF data from 'startEdge' in a square of size 'nGrids' in positive lat/lon
    index direction into a geojson whose path is described as output. 
    It appends geojson template dictionaries from a given file-path into a 
    temporary data variable, whose data is changed and dumped into output file..
    '''

    start = time.time()

    # Get the initial template, the data variable will hold all temporary data
    data = get_initial_template() 
    # Get the feature template, this will be appended to data for each feature inserted
    feature_template = get_feature_template()

    # Create local copies of subsets for further use, much faster to access
    with xr.open_dataset(source_path) as source: 
        temps = deepcopy(source['temperature'][0,0])#[::gridSize,::gridSize])
        lats = deepcopy(source['gridLats'])#[::gridSize,::gridSize])
        lons = deepcopy(source['gridLons'])#[::gridSize,::gridSize])

    # featureIdx counts what feature we are working on = 0,1,2,3, ... 
    featureIdx = 0
    for y in range(nGrids):                 
        for x in range(nGrids):  
            # get the start edge of the next polygon to be inserted into dictionary
            edge = (startEdge[0]+y, startEdge[1]+x)       
            # if temp=nan: skip grid -> else: insert lat/lon and temp into data
            temp = float(temps[edge])
            if math.isnan(temp):
                continue
            else:
                # add a copy of the feature dictionary template to features
                data['features'].append(deepcopy(feature_template))    
                # create a reference to the current feature we are working on
                feature = data['features'][featureIdx]
                # insert hex into fill
                feature['properties']['fill'] = geojson_grid_temp(temp) 
                # copying netcdf data into the goven feature position                     
                geojson_grid_coord(feature, 
                                    lats, 
                                    lons, 
                                    edge)                 
                #coordinates = feature['geometry']['coordinates'][0][polyEdgeIdx][0]

                featureIdx = featureIdx + 1

    write_output(data)    

    end = time.time()       
    print end-start   

''' 
One example of reducing the load of taking the whole source file as xarray could 
be to nest the opens as such:
with xr.open_dataset(source_pat, drop_variables[...]) as geo_coord:
    with xr.open_dataset(source_path, drop_variables[...]) as tmp:

or just

coord = xr.open_dataset(source_path, drop_variables[...])
tmp = xr.open_dataset(source_path, drop_variables[...])

25/06/2019:
    Testing execution time with getting 100 grids:
        - normal operation (x=1) takes about 1e-6
        - appending the 'features' template to the data file takes about 2e-4
        - copying lat/lon data takes about 4e-4
        - fetching the hex RGB from temperature takes about 5e-3
        - the loop for inserting coordinates takes about 1.5e-2 :O

26/06/2019:
    Split data into subset copies for processing, still getting 100 grids:
        - the loop for inserting coordinates now takes about 7e-3
        - full operation takes 0.68815 seconds as before it took
            2.14507 seconds. big improvements.
    takes a total of 206 seconds to get 250^2=62500 grids

Tried to increase number of CPUs to 2 and memory to about 1k. The execution time of 
the insertion loop still took 1.5e-2 seconds. Maybe implement multithreading, spreading
the resource between different grid squares.

'''