import json
from netCDF4 import Dataset, num2date
import numpy

def parsesson(root, target):
    lats = root.variables['lat']
    lons = root.variables['lon']
    times = root.variables['time']
    tmp = root.variables['tos'][:]

    for j in range(len(lats)):
        la = lats[j]

        for i in range(len(lons)):
            lo = lons[i]

            #print(tmp[j,i].tolist())

            json.dump({
                'latitude': float(la),
                'longitude': float(lo),
                : tmp[1,j,i].tolist()   # 1 indicates 1/24 hours
            }, target)
            target.write('\n')

target = open("test.json", 'w')
source = Dataset("/home/even/netCDFdata/tos_O1_2001-2002.nc", "r", format="NETCDF4")
#print("length of latitudes: " + str(len(source.variables['lat'])))
#print("length of longitudes: " + str(len(source.variables['lon'])))
#print("number of temperatures: " + str(len(source.variables['tos'][1,1])))
print(source.variables.keys())
parsesson(source, target)
source.close()
target.close()




