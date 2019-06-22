import xarray as xr
import json
import numpy
import os

# 1. load template as DATA
# 2. load output as output
# 3. load netCDF as source
# 4. run function for inserting source data into the temporary (templated) data file
# 5. dump the data file into outputfile (the geojson file to be used in leaflet)
# create subgrid with indexes:
# (221,19) - (222,20)    -> (221,1), (221,2), (222,1), (222,2)
# these were the 2x2 grid with the largest differences in temperature (about 0.5-1K difference)


# Create geojson with 2x2 grid
def geojson(source, target):
    lats = source['gridLats']
    lons = source['gridLons']
    tmps = source['temperature'][0,0,:]

    lons_list = [] 
    lats_list = []

    # We will iterate over the edges of each square
    edgenode = (221-1,19-1) # -1 since indexing starts at 0 , we actualy want (221,19)

    dim = 2
    dimrange = range(dim)    # the box is 2x2, i.e. dimension of one side is 2
    geojsonIdx = 0           # from 0-3 for correct insertion into the square polygon
    for i in dimrange:       # iterate y
        innerrange = dimrange              
        if i == 1:
            innerrange = reversed(dimrange)     # backward iteration to complete the polygon
        for j in innerrange: # iterate x
            yx = (edgenode[0]+i, edgenode[1]+j) # (y,x) defined as such in the netCDF file
            tmp  = float(tmps[yx])
            lat  = float(lats[yx])
            lon  = float(lons[yx])
            target['features'][0]['geometry']['coordinates'][0][geojsonIdx][0] = lat
            target['features'][0]['geometry']['coordinates'][0][geojsonIdx][1] = lon
            if geojsonIdx == 0: # the last list must always be the same as the first
                target['features'][0]['geometry']['coordinates'][0][4][0] = lat
                target['features'][0]['geometry']['coordinates'][0][4][1] = lon
            geojsonIdx += 1

# define paths to files
template_path = "templates/colorgrid.json"
source_path = "/media/sf_shared/samples_NSEW_2013.03.11.nc"
output_path = "outputs/grid.json"

# open template and load to the dictionary which will be dumped into output when altered
with open(template_path, "r") as template:
    data = json.load(template)

# start writing to output geojson file, remove if exists
output_path = "outputs/grid.json"
if os.path.isfile(output_path):
    os.remove(output_path)

with xr.open_dataset(source_path) as source: # load netCDF file to "source"
    geojson(source, data)                    # run function for copying netcdf data into dictionary

with open(output_path, "w") as output:       # open the final product file as output 
        json.dump(data, output, indent=4)    # dump new data into output json file


