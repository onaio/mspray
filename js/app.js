var MYAPP = {};

MYAPP.sprayData = null;
MYAPP.hhData = null;

MYAPP.day = 1;
MYAPP.hh_sprayed = 0;
MYAPP.hh_cnt = 0;
MYAPP.spray_perc = 0;

var params = {};

var myDay = location.search.split('day=')[1]

if (myDay) {
  MYAPP.day = parseInt(myDay.replace("\/", ""));

}



function loadHH() {
  d3.json("data/hh-chimbombo-1.geojson", function (json) {
    var hhLayer = L.geoJson(json, {
       pointToLayer: function (feature, latlng) {
         return L.circleMarker(latlng, hhOptions);
       }}).addTo(map);
  });
    
   }

function loadSprayPoints(day) {

  d3.json("data/spray-day-"+day+".geojson", function (json) {
    var hhLayer = L.geoJson(json, {
       pointToLayer: function (feature, latlng) {
         return L.circleMarker(latlng, sprayOptions);
       }}).addTo(map);
  });
    
   }


function loadSprayData() {

    if (MYAPP.sprayData === null) {
        d3.json("data/chimbombo-1-spray.geojson", function (json) {
                var sprayLayer = L.geoJson(json,  {
      			style: getStyle,
      			onEachFeature: onEachFeature
			}).addTo(map);
        });

    }
};



// Load 



// load household points

var map = L.map('map').setView([-15.2164,28.2315], 15);
map.addLayer(new L.Google);

loadSprayData();
loadHH();
loadDay();

function loadDay() {
  for (var i=1; i<=MYAPP.day; i++) {
    loadSprayPoints(i);
  }
  

drawCircle();
};

console.log(MYAPP.hh_sprayed);

 




  

function drawCircle() {

Circles.create({
    id:         'circles-1',
    percentage: Math.round(MYAPP.spray_perc*100),
    radius:     60,
    width:      15,
    number:     Math.round(MYAPP.spray_perc*100),
    text:       '%',
    colors:     ['#AAAAAA', '#2ECC40'],
    duration:   300
});
}


var hhOptions = {
    radius: 3,
    fillColor: "#FFDC00",
    color: "#222",
    weight: 1,
    opacity: 1,
    fillOpacity: 1.
};

var sprayOptions = {
    radius: 3,
    fillColor: "red",
    color: "#222",
    weight: 1,
    opacity: 1,
    fillOpacity: 1.
};





/*
var sprayLayer = L.geoJson(MYAPP.sprayData,  {
      style: getStyle,
      onEachFeature: onEachFeature
}).addTo(map);
*/

function getStyle(feature) {
      return {
          weight: 2,
          opacity: 0.1,
          color: 'black',
          fillOpacity: 0.4,
          fillColor: getColor(feature.properties)
      };
 
}


function getColor(d) {
    	
      MYAPP.hh_sprayed = MYAPP.hh_sprayed + sprayCount(MYAPP.day,d)
      MYAPP.hh_cnt = MYAPP.hh_cnt + d['hh-cnt']
      //MYAPP.spray_perc = MYAPP.hh_sprayed / MYAPP.hh_cnt;
       
      var spray_rate = sprayRate(MYAPP.day,d)
    
        return spray_rate === 1  ? '#2ECC40' :
        	   spray_rate > 0.66 ?	'#FFDC00' : 
               spray_rate > 0.33 ? '#FF851B' :
               spray_rate > 0 ? '#FF4136' :
                '#ccc';
          };




function sprayRate(day,d) {
 
	return day === 1 ? d['day1-cnt'] / d['hh-cnt'] :
	       day === 2 ? (d['day1-cnt']+ d['day2-cnt']) / d['hh-cnt'] :
	       day === 3 ? (d['day1-cnt']+ d['day2-cnt']+ d['day3-cnt']) / d['hh-cnt'] :
	       day === 4 ? (d['day1-cnt']+ d['day2-cnt']+ d['day3-cnt']+ d['day4-cnt']) / d['hh-cnt'] :
		     0;
};


function sprayCount(day,d) {
  
  return day === 1 ? d['day1-cnt'] :
         day === 2 ? (d['day1-cnt']+ d['day2-cnt']):
         day === 3 ? (d['day1-cnt']+ d['day2-cnt']+ d['day3-cnt']) :
         day === 4 ? (d['day1-cnt']+ d['day2-cnt']+ d['day3-cnt']+ d['day4-cnt']) :
       0;
};





/*
L.geoJson(someGeojsonFeature, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, geojsonMarkerOptions);
    }
}).addTo(map);
*/


  function onEachFeature(feature, layer) {
      layer.on({
          //mousemove: mousemove,
          //mouseout: mouseout,
          click: zoomToFeature
      });
  }

 function zoomToFeature(e) {
      map.fitBounds(e.target.getBounds());
  }

