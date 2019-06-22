import xarray as xr
import json
import numpy
import os

# Create geojson with 2x2 grid
def geojson(source, target):
    lats = source['gridLats']
    lons = source['gridLons']
    tmps = source['temperature'][0,0,:]

    lons_list = [] 
    lats_list = []

    # We will iterate over the edges of each square
    edgenode = (221-1,19-1) # -1 since indexing starts at 0 , we actualy want (221,19)

    squaresize = 2
    squarerange = range(squaresize)
    for i in squarerange:
        innerrange = squarerange
        if i == 1:
            innerrange = reversed(squarerange)
        for j in innerrange:
            xy = (edgenode[0]+i, edgenode[1]+j)
            tmp  = float(tmps[xy])
            lat  = float(lats[xy])
            lon  = float(lons[xy])
            print [lat, lon]




json_file = "grid.json"
source = "/media/sf_shared/samples_NSEW_2013.03.11.nc"

# remove exisiting json file if exists and create new
if os.path.isfile(json_file):
    os.remove(json_file)
target = open(json_file, 'w')

# open dataset and create dataframe
data = xr.open_dataset(source)
#dataframe = data.to_dataframe()

geojson(data, json_file)

# close files
data.close()
target.close()



# create subgrid with indexes:
# (221,19) - (222,20)    -> (221,1), (221,2), (222,1), (222,2)