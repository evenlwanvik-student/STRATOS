import json
from netCDF4 import Dataset, num2date
import numpy
import os

def parsesson(root, target):
    xc = root.variables['xc']
    yc = root.variables['yc']

    lats = root.variables['gridLats']
    lons = root.variables['gridLons']
    times = root.variables['time']
    tmp = root.variables['temperature'][:]

    for j in range(len(xc)):
    #for j in range(100,110):

        for i in range(len(yc)):
        #for i in range(100,110):
            la = lats[i,j]
            lo = lons[i,j]

            json.dump({
                'latitude':  float(la),
                'longitude': float(lo),
                'tmp':       float(tmp[1,1,i,j])   # first elements (1,1) means we'll stay on first timestamp at the first layer
            }, target)
            target.write('\n')

def create_single_polygon(root, target):
    lats = root.variables['gridLats']
    lons = root.variables['gridLons']
    times = root.variables['time']
    tmp = root.variables['temperature'][:]

os.remove("test.json")
target = open("test.json", 'w')
source = Dataset("/home/even/netCDFdata/samples_NSEW_2013.03.11.nc", "r", format="NETCDF4")
#print("Number of timestamps: " +str(len(source.variables['time'])))
#print("Number of layers: " + str(len(source.variables['depth']))) 
#print("Number of latitude samples: " + str(len(source.variables['gridLats'][:,1])))
print(len(source.variables['xc']))
print(len(source.variables['yc']))

print(len(source.variables['gridLats'][:,1]))
print(len(source.variables['gridLats'][1,:]))
print(source.variables['gridLons'])
#print("Number of longitude samples: " + str(len(source.variables['gridLons'])))
#print("Number of temperature samples: " + str(len(source.variables['temperature'][1,1])))
#print(source.variables.keys())
#print(source.variables['temperature'])
#parsesson(source, target)
source.close()
target.close()




