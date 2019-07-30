import topojson
from shapely.geometry import shape, Point, MultiPoint
import json
import numpy as np

########### FIGURE OUT LISENCE IF THIS WORKS ###############
def geo2topo(geojson, quant_factor=1e4):
    """Given a geojson dict, returns topojson"""
    assert geojson["type"] == "FeatureCollection"

    geometries = []

    for feature in geojson['features']:
        geometries.append(shape(feature['geometry']))

    x0, y0, x1, y1 = get_bounds(geometries)
    kx, ky = 1 / ((quant_factor - 1) / (x1 - x0)), 1/ ((quant_factor - 1) / (y1 - y0))

    arcs = lines2arcs(geometries, kx, ky, x0, y0)

    return {
        "type" : "Topology",
        "transform" : {
  	  "scale" : [kx, ky],
		  "translate" : [x0, y0]
	    },
        "objects" : {
            "type": "GeometryCollection",
            "geometries": geometries
        },
        "arcs" : arcs
    }

def get_bounds(geometries):
    """Returns bounding box of geometries. Implementation creates a MultiPoint
    from the boxes of all polygons in order to get the result"""
    points = []
    for g in geometries:
        bounds = g.bounds
        points.extend([Point(bounds[:2]), Point(bounds[2:])])
    return MultiPoint(points).bounds


def lines2arcs(geometries, kx, ky, x0, y0):
    """Naive approach to create arcs from lines. TODO: implement detection of
    shared points/arcs"""
    for g in geometries:
        try:
            boundary = g.boundary
        except AttributeError:
            continue

        if boundary.type == 'LineString':
            boundary = [boundary]

        arcs = []
        x = y = 0
        for line in boundary:
            arc = []
            for a, b in line.coords:
                a = int(round((a - x0) / kx - x))
                b = int(round((b - y0) / ky - y))
                x += a
                y += b
                arc.append([a, b])
            arcs.append(arc)
        return arcs

    '''
    start_convert = time.time() 
    topoData=geo2topo(jsonData)
    end = time.time()
    logging.warning("time spent converting: %f",end-start_convert)
    '''