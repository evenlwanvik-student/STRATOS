// Displaying map initially
var latitude = document.getElementById("lat").innerHTML;
var longitude = document.getElementById("long").innerHTML;
var zoom = document.getElementById("zoom").innerHTML;
var map = L.map('map').setView([latitude, longitude], zoom);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);

// Creating legends for demo purposes
// NOTE: these are not customized to fit all the different types of data
var temp_legend = L.control({position: 'bottomright'});
var oscar_legend = L.control({position: 'bottomright'});

temp_legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
    grades = [0, 5, 10, 15, 20],
    labels = [];
    var degrees = 1;
    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
      div.innerHTML +=
          '<i style="background:' + getTemperatureColor(grades[i] + 1) + '"></i> ' +
          grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
  }
  return div;
};

function getTemperatureColor(d) {
  return d > 20   ? '#5cfdd0' :
         d > 15   ? '#5cf1fd' :
         d > 10   ? '#58b4f6' :
         d > 5    ? '#3b9ee5' :
                    '#1686d6' ;
}

oscar_legend.onAdd =  function (map) {
  var div = L.DomUtil.create('div', 'info legend'),
      grades = [0, 10, 20, 50, 100, 200, 500, 1000],
      labels = [];
  for (var i = 0; i < grades.length; i++) {
      div.innerHTML +=
          '<i style="background:' + getOscarColor(grades[i] + 1) + '"></i> ' +
          grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
  }
  return div;
};

function getOscarColor(d) {
  return d > 1000 ? '#800026' :
         d > 500  ? '#BD0026' :
         d > 200  ? '#E31A1C' :
         d > 100  ? '#FC4E2A' :
         d > 50   ? '#FD8D3C' :
         d > 20   ? '#FEB24C' :
         d > 10   ? '#FED976' :
                    '#FFEDA0';
}

// Function that toggles the input field for the pregenereated topoJSON
$("#norsok").bind('click', function() {
  $("#preMade").toggle();
});

function loadJSON() {
  // create XRMLHttpRequest instance
  var datasets = new XMLHttpRequest(); 
  // synchronous load json object
  datasets.open("GET", "templates/datasets.json", false); 
  datasets.onreadystatechange = func
}

// Populates the drop-down menu for selecting dataset
// names and values are held in datasets.json
function populateDatasetMenu() {
  let dsMenu = $('#datasetMenu');
  // empty dropdown, then initialize and fill the dropdown with dataset names
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
var blobpath = "";
// Populates the drop-down menu for selecting datatype
// The content of the menu depends on the chosen dataset
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

// Function to add selfmade topoJSON to Leaflet map
// Currently not in use
function loadTOPO(){
  map.setView([62.828181, 7.130122], 12);
  temp_legend.addTo(map);
  $.getJSON('/makeTopo')
  .done(addTopoData);
}

function addTopoData(topoData) {
  var geojsonLayer = new L.GeoJSON(topojson.feature(topoData, topoData.objects),{style: polystyle}).addTo(map);
  temp_legend.addTo(map);
  /*  topojson.feature(topology, object) <> translates a topojson-object to a geojson-object.
      It returns a FeatureCollection if the object is of type GeometryCollection and maps each Geometry to a Feature
  */
}

// Reloading geojson with input fields, getting new geojson with ajax, fixing html with jQuery
$(function() {
    $('#reload').bind('click', function() {
      $.getJSON('/loadGeojson', 
                {
                  blobpath: $('select[name="dataset"]').val(),
                  datatype: $('select[name="datatype"]').val(),
                  gridcells: $('input[name="gridcells"]').val(),
                  lat_idx: $('input[name="lat_idx"]').val(),
                  long_idx: $('input[name="long_idx"]').val(),
                  depth: $('input[name="depth"]').val(), 
                  time: $('input[name="time"]').val() 
                },
                function(flask_response) 
                {
                    map.setView([flask_response.lat, flask_response.lon], 
                                flask_response.zoom);
                    new L.GeoJSON(JSON.parse(flask_response.geojson),{style: polystyle}).addTo(map);
                    temp_legend.addTo(map);
                });
      return false;
    });
});

// Function to get pregenerated salinity NORSOK topojson data
$(function() {
  $('#reloadPremade').bind('click', function() {
    map.setView([59.973424, 5.567064], 7);
    $.getJSON('/preMadeJSON', 
              {
                depth: $('input[name="depth2"]').val()
              },
              function(flask_response) 
              {
                new L.GeoJSON(topojson.feature(flask_response, flask_response.objects.geojson),{style: polystyle}).addTo(map);
                oscar_legend.addTo(map);
              });
    return false;
  });
});


// Timelapse of OSCAR data
var timelapseArray = new Array(100);

$(function() {
  $('#timelapse').bind('click', function() {
    map.setView([68.014998, 12.075042], 7);
    var timeIndex; 
    for (timeIndex = 0; timeIndex <7; timeIndex+=3){  //request first two
      $.getJSON('/timelapse', {
          time: timeIndex,
          blobpath: 'OSCAR/TEST3MEMWX.XNordlandVI_surface.zarr',
          datatype: 'water_content'
        }, function(flask_response) {
          // organize geojson layers in array
            timelapseArray[(flask_response.timeIdx)/3]=new L.GeoJSON(JSON.parse(flask_response.geojson), {style: polystyle})
            oscar_legend.addTo(map);
        });
    }
    return false;
  });
});

window.setInterval(drawTimelapse, 100); // calls drawTimelapse every 100 millisecond
timeIndex = 0;
function drawTimelapse(){
  if (timelapseArray[timeIndex/3] == null){   
    return;                                      
  } // only moves past this point if the next layer to be displayed has been returned from flask
  if (timeIndex!=0){
    timelapseArray[(timeIndex/3)-1].clearLayers(); //removes old layer from map
  }
  timelapseArray[timeIndex/3].addTo(map); // adds new layer from current timestep
  timeIndex = timeIndex + 3;
  
  if (timeIndex < 301){
    $.getJSON('/timelapse', {   //requests next layer
      time: timeIndex,
      blobpath: 'OSCAR/TEST3MEMWX.XNordlandVI_surface.zarr',
      datatype: 'water_content'
    }, function(flask_response) {
      // puts geojson layer in array
      timelapseArray[(flask_response.timeIdx)/3]=new L.geoJSON(JSON.parse(flask_response.geojson), {style: polystyle})
    });
  }
}

 // Depth series Frænfjorden with ajax/jQuery
 // Not used currently
 var depthLayerArray = new Array(20);
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
            temp_legend.addTo(map);
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

// Function to style the gridcells
function polystyle(feature) {
    return {
        "color" : feature.properties.fill,
        "weight": 0.1,
        "opacity": 0.6,
        "fillColor": feature.properties.fill,
        "fillOpacity": 0.6
    };
}
