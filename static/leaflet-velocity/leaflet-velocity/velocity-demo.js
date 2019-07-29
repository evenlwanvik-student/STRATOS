/* 
  Most of this code is copied and altered from :
  https://github.com/danwild/leaflet-velocity 
*/

/* Populates the drop-down menu for selecting dataset, names and values are held in datasets.json */ 
function populateDatasetMenu() {
  let dsMenu = $('#datasetMenu');
  // empty dropdown, then initialize and populate dropdown with dataset names
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

function initDemoMap() {
  var Esri_WorldImagery = L.tileLayer(
    "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, " +
        "AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    }
  );

  var Esri_DarkGreyCanvas = L.tileLayer(
    "http://{s}.sm.mapstack.stamen.com/" +
      "(toner-lite,$fff[difference],$fff[@23],$fff[hsl-saturation@20])/" +
      "{z}/{x}/{y}.png",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, " +
        "NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community"
    }
  );

  var baseLayers = {
    Satellite: Esri_WorldImagery,
    "Grey Canvas": Esri_DarkGreyCanvas
  };

  var map = L.map("map", {
    layers: [Esri_WorldImagery]
  });

  var layerControl = L.control.layers(baseLayers);
  layerControl.addTo(map);

  return {
    map: map,
    layerControl: layerControl
  };
}

// demo map
var mapStuff = initDemoMap();
var map = mapStuff.map;
var layerControl = mapStuff.layerControl;

// load data (u, v grids) 
$.getJSON("static/leaflet-velocity/barrier-reef.json", function(data) {
  var velocityLayer = L.velocityLayer({
    displayValues: true,
    displayOptions: {
      velocityType: "GBR Wind",
      displayPosition: "bottomleft",
      displayEmptyString: "No wind data"
    },
    data: data,
    maxVelocity: 10
  });
  map.setView([-22, 150], 5);
  console.log(data)
  // add possibility to add the layer to map
  layerControl.addOverlay(velocityLayer, "Wind - Great Barrier Reef");
});


// when dataset is choosen, create option to render wind/ocean velocities
function addDatasetOptions() {

  // load data (u, v grids)  static/leaflet-velocity/wind-velocity.json
  $.getJSON("/getWindVelocityVector", 
    //{ blobpath: $('select[name="dataset"]').val() },
    function(data) {
      var velocityLayer = L.velocityLayer({
        displayValues: true,
        displayOptions: {
          velocityType: "GBR Wind",
          displayPosition: "bottomleft",
          displayEmptyString: "No wind data"
        },
        data: data,
        maxVelocity: 10
      });
      map.setView([data[0]['header']["lo1"], data[0]['header']["la1"]], 12);
      // 
      // map.setView([62.828181, 7.130122], 12);
      // add possibility to add the layer to map
      console.log(data)
      layerControl.addOverlay(velocityLayer, "Wind velocity - Franfjorden");
      });

  /*
  $.getJSON("data/outputs/ocean-current.json", function(data) {
    var velocityLayer = L.velocityLayer({
      displayValues: true,
      displayOptions: {
        velocityType: "Ocean current",
        displayPosition: "bottomleft",
        displayEmptyString: "No ocean data"
      },
      data: data,
      maxVelocity: 0.6,
      velocityScale: 0.1 // arbitrary default 0.005
    });

    layerControl.addOverlay(velocityLayer, "Ocean current - Franfjorden");
  });
  */
}

