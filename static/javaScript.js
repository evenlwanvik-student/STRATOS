
var map = L.map('map').setView([20, 0], 3);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', 
                {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}
            ).addTo(map);

var myLines = [{
    "type": "LineString",
    "coordinates": [[-100, 40], [-105, 45], [-110, 55]]
}, {
    "type": "LineString",
    "coordinates": [[-105, 40], [-110, 45], [-115, 55]]
}];

L.geoJSON().addTo(map);
//var myLayer = L.geoJSON().addTo(map);
//myLayer.addData(geojsonFeature);

function msg(){  
    alert("This website needs some more features");  
   }  



/* Code for importing geojson from external file:
    var geojsonLayer = new L.GeoJSON.AJAX("foo.geojson");       
    geojsonLayer.addTo(map);

    and include this in index header: <script src="/js/leaflet-0.7.2/leaflet.ajax.min.js"></script>
*/


/*
    // Trying to visualize some random geoJSON data, but doesn't work
    var states = [{
        "type": "Feature",
        "properties": {"party": "Republican"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-104.05, 48.99],
                [-97.22,  48.98],
                [-96.58,  45.94],
                [-104.03, 45.94],
                [-104.05, 48.99]
            ]]
        }
        }, {
        "type": "Feature",
        "properties": {"party": "Democrat"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-109.05, 41.00],
                [-102.06, 40.99],
                [-102.03, 36.99],
                [-109.04, 36.99],
                [-109.05, 41.00]
            ]]
        }
    }];

    L.geoJSON(states, {
        style: function(feature) {
            switch (feature.properties.party) {
                case 'Republican': return {color: "#ff0000"};
                case 'Democrat':   return {color: "#0000ff"};
            }
        }
    }).addTo(map);
    */