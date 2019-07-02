// Display map
var latitude = document.getElementById("lat").innerHTML;
var longitude = document.getElementById("long").innerHTML;
var zoom = document.getElementById("zoom").innerHTML;
var map = L.map('map').setView([latitude, longitude], zoom);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);

// Add colored grid to map
var grid=[JSON.parse(document.getElementById("geojson").innerHTML)]
new L.geoJson(grid, {style: polystyle}).addTo(map);

// Render the right menu for webpage
// menutype is a string corresponding to a specific template id
/*
function showContent() {
    var menuType = document.getElementById("menu")
    var temp = document.getElementById("menuType");
    var clon = temp.content.cloneNode(true);
    document.body.appendChild(clon);
}
*/


// Redirect-functions for buttonpress
function redirect(){
    location.href = "http://127.0.0.1:5000/geojson";
}
function redirectToResult() {
    location.href = "http://127.0.0.1:5000/result"
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