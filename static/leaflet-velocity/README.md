# Leaflet-velocity

Leaflet-velocity is a leaflet plugin for visualizing both water current and wind velocities. The main problem ahead is that the grids used in the velocity json object is a square which is perpendicular with the map, whereas the netcdf datasets are slightly tilted (45 degrees), producing a somewhat skewed projection.