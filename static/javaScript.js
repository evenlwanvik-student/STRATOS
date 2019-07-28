// Display map
var latitude = document.getElementById("lat").innerHTML;
var longitude = document.getElementById("long").innerHTML;
var zoom = document.getElementById("zoom").innerHTML;
var map = L.map('map').setView([latitude, longitude], zoom);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);


// Adding legend to map
var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
    grades = [0, 1, 2, 3],
    labels = [];
    var degrees = 1;
    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            degrees + grades[i] + '<br>';
}

return div;
};

legend.addTo(map);

function getColor(d) {
  return d > 3   ? '#0779f2' :
         d > 2   ? '#24aeed' :
         d > 1   ? '#5ec7f7' :
                    '#87e1fa';
}


function loadJSON() {
  // create XRMLHttpRequest instance
  var datasets = new XMLHttpRequest(); 
  // synchronous load json object
  datasets.open("GET", "templates/datasets.json", false); 
  datasets.onreadystatechange = func
}


/* Populates the drop-down menu for selecting dataset, names and values are held in datasets.json */ 
function populateDatasetMenu() {
  let dsMenu = $('#datasetMenu');
  // empty dropdown, then initialize and opulate dropdown with dataset names
  dsMenu.empty();
  dsMenu.append('<option selected="true" value="norsok" disabled>-- Select --</option>');
  dsMenu.prop('selectedIndex', 0);
  $.getJSON('static/datasets.json', function (datasets) {
    $.each(datasets, function (name, content) {
      // for each dataset in json config file, populate:
      dsMenu.append($('<option></option>').attr('value', content.blobpath).text(name));
    });
  });
}

// blobpath is for holding the full path to the blob of the model, e.g. OSCAR/TEST3MEMWX.XNordlandVI_evap.zarr
var blobpath = ""
/* Populates the drop-down menu for selecting datatype, names and values are held in datasets.json. 
The content of the menu depends on the chosen dataset */
function populateDatatypeMenu() {
  // get name of current dataset
  var dsMenu = document.getElementById("datasetMenu");
  var dsStr = dsMenu.options[dsMenu.selectedIndex].text;
  let dtMenu = $('#datatypeMenu');
  // empty dropdown, then initialize and populate dropdown with measurement types of dataset
  dtMenu.empty();
  dtMenu.append('<option selected="true" value="temperature" disabled>-- Select --</option>');
  dtMenu.prop('selectedIndex', 0);
  $.getJSON('static/datasets.json', function (datasets) {
    // for each type of the dataset, populate:
    $.each(datasets[dsStr].typename, function (key, datatype) {
      dtMenu.append($('<option></option>').attr('value', datatype).text(datatype));
    }) 
  });
}


// Loading topoJSON to Leaflet map

// Loading topoJSON to Leaflet map
function loadTOPO(){
  map.setView([62.828181, 7.130122], 12);
   $.getJSON('/makeTopo')
   .done(addTopoData);
}

function addTopoData(topoData) {
  var geojsonLayer = new L.GeoJSON(topojson.feature(topoData, topoData.objects),{style: polystyle}).addTo(map);
  /*  topojson.feature(topology, object) <> translates a topojson-object to a geojson-object.
      It returns a FeatureCollection if the object is of type GeometryCollection and maps each Geometry to a Feature
      The returned feature is a shallow copy of the source object: they may share identifiers, bounding boxes, properties and coordinates. */
}

function addPreMadeTopo(topoData) {
  var geojsonLayer = new L.GeoJSON(topojson.feature(topoData, topoData.objects.written_geojson),{style: polystyle}).addTo(map);
}

//Loading GeoJSON for testing
function loadGEO(){
  map.setView([62.828181, 7.130122], 12);
  $.getJSON('/getGeo')
  .done(addGeoData);
}

function loadPreMadeJSON(jsonType){
  map.setView([62.828181, 7.130122], 12);
  $.getJSON('/preMadeJSON',
    {
    blob_name: jsonType
    },
    function(flask_response){
      if (flask_response.blob == 'written_geojson.json'){
        addGeoData(JSON.parse(flask_response.json))
      } else {
        addPreMadeTopo(JSON.parse(flask_response.json))
      }
    });
}

function addGeoData(GeoData) {  
  new L.GeoJSON(GeoData, {style: polystyle}).addTo(map);
}

// Reloading geojson with input fields, getting new geojson with ajax, fixing html with jQuery
$(function() {
    $('#reload').bind('click', function() {
      $.getJSON('/loadGeojson', 
                {
                  blobpath: $('select[name="dataset"]').val(),
                  datatype: $('select[name="datatype"]').val(),
                  gridcells: $('input[name="gridcells"]').val(),
                  depth: $('input[name="depth"]').val(), 
                  time: $('input[name="time"]').val() 
                },
                function(flask_response) 
                {
                    map.setView([flask_response.lat, flask_response.lon], 
                                flask_response.zoom);
                    new L.GeoJSON(JSON.parse(flask_response.geojson),{style: polystyle}).addTo(map);
                });
      return false;
    });
  });


var depthLayerArray = new Array(20);
 // Depth series with ajax/jQuery
 $(function() {
  $('#depthseries').bind('click', function() {
    map.setView([62.828181, 7.130122], 13);
    var depthIndex; 
    for (depthIndex = 0; depthIndex <2; depthIndex++){  //request first two
      $.getJSON('/depthSeries', {
          depth: depthIndex
        }, function(flask_response) {
          // organize geojson layers in array
            depthLayerArray[flask_response.depthIdx]=new L.GeoJSON(JSON.parse(flask_response.geojson), {style: polystyle})
        });
    }
    return false;
  });
});

window.setInterval(drawDepthLayer, 600); // calls drawDepthLayers every 600 millisecond
depthIndex = 0;
function drawDepthLayer(){
  if (depthLayerArray[depthIndex] == null){   
    return;                                      
  } // only moves past this if the next layer to be displayed has arrived
  if (depthIndex!=0){
    depthLayerArray[depthIndex-1].clearLayers(); //removes old layer from map
  }
  depthLayerArray[depthIndex].addTo(map); // adds new layer from current depth
  depthIndex++;
  
  if (depthIndex < 20){
    $.getJSON('/depthSeries', {   //requests next layer
      depth: depthIndex + 1 
    }, function(flask_response) {
      // puts geojson layer in array
      depthLayerArray[flask_response.depthIdx]=new L.geoJSON(JSON.parse(flask_response.geojson), {style: polystyle})
    });
  }
}

// Function to style the grid accoring to each geojson feature data
function polystyle(feature) {
    return {
        "color" : feature.properties.fill,
        "weight": 0.1,
        "opacity": 0.6,
        "fillColor": feature.properties.fill,
        "fillOpacity": 0.6
    };
}
