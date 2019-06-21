import xarray as xr
import json
import numpy
import os

# Create geojson with 2x2 grid
def geojson(source, target):
    lats = source['gridLats']
    lons = source['gridLons']
    tmps = source['temperature'][0,0,:]
    #print(lats)
    #print(tmp)
    lons_list = [] 
    lats_list = []

    #print tmps[293,1]

    for i in range(19-1,20):
        for j in range(222, 221-1, -1): # +1 since the arrays has index 0 as well
            tmp = float(tmps[j,i]) # (yc: 294, xc: 291), i.e. i and j is swapped
            #print float(lats[i,j])
            #print float(lons[i,j])
            print tmp



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