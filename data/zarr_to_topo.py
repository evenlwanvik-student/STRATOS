import json
import numpy as np
import os
from copy import deepcopy
import time
import math
import azure
import zarr
import sys
import logging
import warnings
from data.color_encoding import temp_to_rgb
#from .color_encoding import temp_to_rgb

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

# define paths to files (inside container)
initial_template_path = "data/templates/initial_topo_template.json"
geometry_template_path = "data/templates/geometry_template.json"

def get_initial_template():
    with open(initial_template_path, "r") as template:
        return json.load(template)

def get_geometry_template():
    with open(geometry_template_path, "r") as template:
        return json.load(template)

def set_colormap_encoding_range(measurements, fill_value):
    # finding min/max for color encoding for this grid, this should
    if fill_value == np.NaN:
        set_colormap_range({'min': measurements.nanmin(), 'max': measurements.nanmax()})
    elif fill_value == -32768:
        # omit fillvalues for finding minimum..
        x = measurements[measurements > -32768]
        set_colormap_range({'min': x.min(), 'max': x.max()})
    else:
        warnings.warn("unknown encoding of fill_value, insert in this if-else-section")

# Create encoder to avoid serialization problem
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        else:
            return super(JsonEncoder, self).default(obj)

def get_blob_client(dataset):
    ''' create a client for the requested dataset '''

    CONTAINER_NAME  = 'zarr'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
    absstore_object = zarr.storage.ABSStore(CONTAINER_NAME, dataset, ACCOUNT_NAME, ACCOUNT_KEY)
    return absstore_object

def get_decompressed_arrays(dataset, depthIdx=0, timeIdx=0):
    # azure zarr-blob object
    absstore_obj = get_blob_client(dataset)

    datatype = dataset['type']

    section_start = time.time()
    decom_meas = zarr.blosc.decompress(absstore_obj['{}/{}.{}.0.0'.format(datatype,timeIdx,depthIdx)])
    decom_lats = zarr.blosc.decompress(absstore_obj['gridLons/0.0'])
    decom_lons = zarr.blosc.decompress(absstore_obj['gridLats/0.0'])
    end = time.time()
    logging.warning("decompressing azure blob chunks execution time: %f",end-section_start)

    #The metadata for coodinates might be different from the measurement
    coord_metadata = json.loads(absstore_obj['gridLats/.zarray'])
    meas_metadata = json.loads(absstore_obj['{}/.zarray'.format(datatype)])
    coord_shape = tuple(coord_metadata['chunks'])
    meas_shape = coord_shape
    coord_datatype = coord_metadata['dtype']
    meas_datatype = meas_metadata['dtype']

    # create numpy arrays from the decompressed buffers and give it our grid shape
    section_start = time.time()
    lons = np.frombuffer(decom_lats, dtype=coord_datatype).reshape(coord_shape)
    lats = np.frombuffer(decom_lons, dtype=coord_datatype).reshape(coord_shape)
    measurements = np.array(np.frombuffer(decom_meas, dtype=meas_datatype).reshape(meas_shape))
    end = time.time()
    logging.warning("creating numpy arrays of decompresed arrays execution time: %f",end-section_start)

    return([lons, lats, measurements, meas_metadata['fill_value']])


def write_output(data):
    '''Function used mainly for inspection the output when testing'''
    # Path outside container
    #output_path = "C:/Users/marias/Documents/Git/stratos/data/outputs/written_topojson.json"
    
    # Path inside container
    output_path = "data/outputs/written_topojson.json"

    # open and dump data to output geojson file, remove if exists
    if os.path.isfile(output_path):
        os.remove(output_path)
    # open the final product file as output 
    with open(output_path, "w+") as output: 
        output.write(data)  


def create_arcs(nGrids, measurements, lats, lons, startNode, json):
    '''
    This function creates the edges (or "arcs") of all the polygons and stores them in a large set. 
    The arcs must be stored systematically in order to know which arcs belong to which polygon.
    The motivation for using arcs is that we can exploit that the polygons share borders and 
    thereby remove some of the redundancy that exists in the GeoJSON format.
    Consider a two by two grid with four polygons (nGrids=2).
        ____ ____
        |_1_|_2_|    
        |_3_|_4_|  

    We start at polygon 1 (x=0, y=0) and generate the vertical left arc and the top arc. 
    Then we do the same for polygon 2 (x=1, y=0). Next we arrive the edgecase (x=2=nGrids, y=0),
    where we only generate a vertical arc, which is the right border of polygon 2.
    The same procedure is followed for polygons 3 and 4, [(x=0,y=1), (x=1,y=1), (x=2=nGrids,y=1)].
    Finally we arrive at the bottom border of the large square, and in loop iterations (x=0,y=2=nGrids) 
    and (x=1,y=2=nGrids) we only generate the horizontal arcs. In loop iteration x==y==nGrids we do nothing.
    '''
    start_arc= time.time()
    logging.warning("Making arcs...")
    arc_collection = []
    for y in range(nGrids+1):                 
        for x in range(nGrids+1):
            if x == nGrids and y == nGrids:
                # Edge case where we are at the right bottom corner of entire grid
                break
            elif x == nGrids:
                # Edge case where we are at the vertical right border of entire grid
                arc_collection.append([[round(lons[startNode[0]+y+1,startNode[1]+x],4), round(lats[startNode[0]+y+1,startNode[1]+x],4)],
                                       [round(lons[startNode[0]+y,startNode[1]+x],4), round(lats[startNode[0]+y,startNode[1]+x],4)]])
            elif y == nGrids:
                # Edge case where we are at bottom border of entire grid
                arc_collection.append([[round(lons[startNode[0]+y,startNode[1]+x],4), round(lats[startNode[0]+y,startNode[1]+x],4)],
                                       [round(lons[startNode[0]+y,startNode[1]+x+1],4), round(lats[startNode[0]+y,startNode[1]+x+1],4)]])
            else:
                arc_collection.append([[round(lons[startNode[0]+y+1,startNode[1]+x],4), round(lats[startNode[0]+y+1,startNode[1]+x],4)],
                                       [round(lons[startNode[0]+y,startNode[1]+x],4), round(lats[startNode[0]+y,startNode[1]+x],4)]])
                arc_collection.append([[round(lons[startNode[0]+y,startNode[1]+x],4), round(lats[startNode[0]+y,startNode[1]+x],4)],
                                       [round(lons[startNode[0]+y,startNode[1]+x+1],4), round(lats[startNode[0]+y,startNode[1]+x+1],4)]])

    json["arcs"] = arc_collection
    end=time.time()
    logging.warning("Finished making arcs in: %f", end-start_arc,)
    logging.warning("length of arc list: %d", len(arc_collection))  


def zarr_to_topo(startNode=(0,0), 
                    nGrids=10, 
                    gridSize=1, 
                    depthIdx=0,
                    timeIdx=0,
                    dataset={'dataset':'nordfjord32m', 'type':'temperature'}):

    ''' 
    This function makes the polygons and stores them as objects in the "geomtries" key in the TopoJSON dictionary.
    We "draw" the polygon by starting in its lower left corner and moving clockwise:
        o----->o   
        ^      |          
        |      v
        S<-----o   

    The arc set for a grid with only one polygon will look like this:
    [ ↑ ,-→ , ↑ ,-→ ], which corresponds to the following borders respectively: left, top, right, bottom.

    Because of how the arcs are added to the set (see create_arcs), each polygon will have arcs-indeces corresponding to the following structure:
        [a, a+1, -(a+2), -function(a, nGrids)]
    Here "a" is an index which points to the arc that is the vertical left border of the polygon.
    The minus signs in the index set are due to the fact that we are drawing those arcs in the opposite direction of how they were defined.
    The last index corresponds to the lower edge of the polygon, which is also the "----->" top arc of the polygon that will be beneath the one we are currently drawing.
    In the double foor loop in this function, consider y as the number of rows of polygons that are being generated, and x is the number of polygons in each row
    
    '''
    start = time.time() 

    # ---------- Initializing --------------#
    
    jsonData = get_initial_template()

    # download z-arrays from azure cloud and decompress requested chunks
    [lons, lats, measurements, fill_value] = get_decompressed_arrays(dataset, timeIdx, depthIdx)

    #create the arcs for the topoJSON
    create_arcs(nGrids, measurements, lats, lons, startNode, jsonData)

    logging.warning(f"configured range for {dataset['measurementtype']}: "
                        f"{config.color_enc[dataset['measurementtype']]['min']} to "
                        f"{config.color_enc[dataset['measurementtype']]['max']}")

    # PolygonIdx tells us which polygon we are working on = 0,1,2,3, ... 
    polygonIdx = 0

    start_topo=time.time()
    logging.warning("Making topojson elements...")
    
    for y in range(nGrids):                 
        for x in range(nGrids):
            edge = (startNode[0]+y, startNode[1]+x)  
            measurement = measurements[edge]
            # if temp=nan: skip grid -> else: make polygon
            if np.isnan(measurement) or measurement == -32768:
                continue
            else:
                # add a copy of the geometry dictionary template to the topoJSON
                jsonData["objects"]["geometries"].append(get_geometry_template())
                # create a reference to the current polygon we are working on
                polygon = jsonData["objects"]["geometries"][polygonIdx]
                # insert hex into fill
                polygon["properties"]["fill"] = temp_to_rgb(measurement)

                # Below we find the correct arc indeces for the specific polygon
                # Note: "a" corresponds to the vertical left border of the polygon
                # The arcs are stored systematically, and the arc-set belonging to each polygon is a function of x, y and nGrids 
                if y==nGrids-1 and x ==0: 
                    # Edge case: first polygon of bottom row
                    a = y*(2* int(nGrids) + 1)
                    poly_arcs = [[a, a+1, -(a+2), -(int(nGrids)*(2*int(nGrids)+1)+x)]]
                elif y==nGrids-1:
                    # Edge case: entire bottom row of polygons
                    a = y*(2* int(nGrids) + 1)+2*x
                    poly_arcs = [[a, a+1, -(a+2), -(int(nGrids)*(2*int(nGrids)+1)+x)]]
                elif x==0:
                    # Edge case: first polygon in a new row
                    a = y*(2 * int(nGrids) + 1)
                    poly_arcs = [[a, a+1, -(a+2), -(a+(2*int(nGrids)+2))]]
                else:
                    # All other polygons
                    a = y*(2* int(nGrids) + 1) +2*x
                    poly_arcs = [[a, a+1, -(a+2), -(a+(2*int(nGrids)+2))]]
                
                polygon["arcs"]=poly_arcs
                polygonIdx = polygonIdx + 1

    end = time.time()            
    logging.warning("Execution time making geometries:%f", end-start_topo)
    logging.warning("number of generated polygons: %d", len(jsonData['objects']['geometries']))
    logging.warning("showing %s for %s", dataset['type'], dataset['dataset'])
    logging.warning("startNode: %s, nGrids: %d, depthIdx: %d, timeIdx: %d",startNode,nGrids,depthIdx,timeIdx)

    end = time.time()
    logging.warning("total execution time of zarr_to_topo function: %f",end-start)
    return json.dumps(jsonData, cls=JsonEncoder)
