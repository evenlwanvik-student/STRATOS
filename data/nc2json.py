import json
from netCDF4 import Dataset, num2date
import numpy
import os


def create_polygons(root, geojson):

    xlen = len(root.variables['xc'])
    ylen = len(root.variables['yc'])
    lats = root.variables['gridLats']
    lons = root.variables['gridLons']
    times = root.variables['time']
    tmp = root.variables['temperature'][:]

    geojson["features"] = {
		"type": "Feature",
		"properties": {
			"stroke": "#555555",
			"stroke-width": 2,
			"stroke-opacity": 1,
			"fill": "#00aa22",
			"fill-opacity": 0.5
		},
		"geometry": {
			"type": "Polygon",
			"coordinates": [
				[
					[float(lats[1,1]),
						float(lons[1,1])
					],
                    [float(lats[2,2]),
						float(lons[1,1])
					],
					[float(lats[2,2]),
						float(lons[2,2])
					],
					[float(lats[1,1]),
						float(lons[2,2])
					], 
					[float(lats[1,1]),
                        float(lons[1,1])
					]
				]
			]
		},
        "type": "Feature",
		"properties": {
			"stroke": "#555555",
			"stroke-width": 2,
			"stroke-opacity": 1,
			"fill": "#00ff22",
			"fill-opacity": 0.5
		},
		"geometry": {
			"type": "Polygon",
			"coordinates": [
				[
					[float(lats[2,2]),
						float(lons[2,2])
					],
                    [float(lats[3,3]),
						float(lons[2,2])
					],
					[float(lats[3,3]),
						float(lons[3,3])
					],
					[float(lats[2,2]),
						float(lons[3,3])
					], 
					[float(lats[2,2]),
                        float(lons[2,2])
					]
				]
			]
		}
	}

    for i in range(xlen):
        for j in range(ylen):
            target["features"] = 
            lat = float(lats[i,j])
            lon = float(lons[i,j])
            innerlist.append([float(lat), [float(lat)])

geojson = {
	"type": "FeatureCollection",
	"features": []
}

my_file = "grid.json"
netcdfpath = "/media/sf_shared/netCDFdata/samples_NSEW_2013.03.11.nc"

if os.path.isfile(my_file):
    os.remove(my_file)
target = open(my_file, 'w')
source = Dataset(netcdfpath, "r", format="NETCDF4")

create_polygons(source, geojson)
json.dump(geojson, target)

source.close()
target.close()


