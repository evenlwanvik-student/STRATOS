import xarray as xr
import json
import numpy
import os
from copy import deepcopy


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

# Create geojson with 2x2 grid
def geojson(source, target, startEdge):
    '''
    takes a xarray object of a netCDF file as soruce and variable loaded
    with a geojson dictionary template as target.
    To show differences in temperature, the temperature is encoded into 
    rgb hexadecimal and inserted into the "fill" under "properties" of the 
    polygon. The polygon itself is inserted into the "coordinates" key under "geometry"
     
    nested loop:
    1. for each square within a given size
    2. y-direction 
    3. x-direction 
    always iterate over polygonedges and squares in the same convention as in moduledescription
    '''
    lats = source['gridLats']
    lons = source['gridLons']
    tmps = source['temperature'][0,0,:]
    tmp = float(tmps[startEdge]) # todo: maybe add interpolation for avg tmp of square 

    gridDim = 2
    xyRange = range(gridDim)    # the box is 2x2, i.e. dimension of one side is 2
    polyEdgeIdx = 0             # The current index of the polygon square
    for y in xyRange:           # iterate y
        innerRange = xyRange              
        if y == 1:
            innerRange = reversed(xyRange)     # backward iteration to complete the polygon
        for x in innerRange: # iterate x
            yx = (startEdge[0]+y, startEdge[1]+x) # (y,x) defined as such in the netCDF file
            lat  = float(lats[yx])
            lon  = float(lons[yx])
            target['geometry']['coordinates'][0][polyEdgeIdx][0] = lat
            target['geometry']['coordinates'][0][polyEdgeIdx][1] = lon
            if polyEdgeIdx == 0: # the last list must always be the same as the first
                target['geometry']['coordinates'][0][4][0] = lat
                target['geometry']['coordinates'][0][4][1] = lon
            polyEdgeIdx += 1


# define paths to files
initial_template_path = "templates/initial_template.json"
feature_template_path = "templates/feature_template.json"
source_path = "/home/even/netCDFdata/samples_NSEW_2013.03.11.nc"
output_path = "outputs/surface_temp.json"

# Dump the initial template only containing the highest level keys (type and features)
with open(initial_template_path, "r") as template:
    data = json.load(template) # we will continue to dump into this dictionary

with open(feature_template_path) as feature_json_template:
    feature_template = json.load(feature_json_template)

with xr.open_dataset(source_path) as source: # load netCDF file to "source"
    startEdge = (221-1,19-1) # -1 since indexing starts at 0, we actualy want (221,19)
    nGrids = 10
    for y in range(nGrids):                 
        for x in range(nGrids):            
            # get the start edge of the next polygon to be inserted into dictionary
            edge = (startEdge[0]+y, startEdge[1]+x)            
            # add a copy of the feature dictionary template to features
            data['features'].append(deepcopy(feature_template)) 
            # index of the appended feature, featureIdx = 0,1,2,3, ...
            featureIdx = nGrids*y + x   
            # copying netcdf data into the goven feature position                      
            geojson(source, data['features'][featureIdx], edge)                 

# open and dump data to output geojson file, remove if exists
if os.path.isfile(output_path):
    os.remove(output_path)

with open(output_path, "w+") as output:  # open the final product file as output 
    json.dump(data, output, indent=4)    # dump new data into output json file


''' 
One example of reducing the load of taking the whole source file as xarray could 
be to nest the opens as such:
with xr.open_dataset(source_pat, drop_variables[...]) as geo_coord:
    with xr.open_dataset(source_path, drop_variables[...]) as tmp:

or just

coord = xr.open_dataset(source_path, drop_variables[...])
tmp = xr.open_dataset(source_path, drop_variables[...])
'''