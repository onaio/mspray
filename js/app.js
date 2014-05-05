var MYAPP = {};

MYAPP.sprayData = null;
MYAPP.hhData = null;

MYAPP.day = 0;
MYAPP.hh_sprayed = 0;
MYAPP.hh_cnt = 0;
MYAPP.spray_perc = 0;

var geojson;
var sprayLayer;  // buffer area

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
                sprayLayer = L.geoJson(json,  {
      			style: getStyle,
      			onEachFeature: onEachFeature
			}).addTo(map);
        });

    }
};



// Load 



// load household points

var map = L.map('map').setView([-15.2164,28.2315], 15);

var legend = L.control({position: 'bottomright'});
L.control.locate().addTo(map);
map.addLayer(new L.Google);


L.mapbox.tileLayer('ona.q7gphkt9').addTo(map);

loadSprayData();
loadHH();
buildLegend();
loadDay();


function loadDay() {
  for (var i=1; i<=MYAPP.day; i++) {
    loadSprayPoints(i);
  }
};



drawCircle();
 

function drawCircle() {


Circles.create({
    id:         'circles-1',
    percentage: 32,
    radius:     60,
    width:      15,
    number:     32,
    text:       '%',
    colors:     ['#AAAAAA', '#2ECC40'],
    duration:   300
});
}


var hhOptions = {
    radius: 4,
    fillColor: "#FFDC00",
    color: "#222",
    weight: 1,
    opacity: 1,
    fillOpacity: 1.
};

var sprayOptions = {
    radius: 4,
    fillColor: "#2ECC40",
    color: "#222",
    weight: 1,
    opacity: 1,
    fillOpacity: 1.
};


// add info controller 
var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
};


info.update = function (props) {
        if (props) {
          var sprayed = sprayCount(MYAPP.day,props)
        //var sprayed = props['day1-cnt'] + props['day2-cnt'] + props['day3-cnt'] + props['day4-cnt'];
        var spray_percent = Math.round((sprayed / props['hh-cnt'])*100);
        var hh_sprayed = spray_percent + '% (' + sprayed + '/' + props['hh-cnt'] +') HH sprayed';
        }
        this._div.innerHTML = (props ?
        '<b>'+ hh_sprayed +'</b>'
        : '');
        
};

info.addTo(map);

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 3,
        color: '#fff',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera) {
        layer.bringToFront();
    }
    info.update(layer.feature.properties);
};

function resetHighlight(e) {
    sprayLayer.resetStyle(e.target);
    info.update();
};


 function zoomToFeature(e) {
      map.fitBounds(e.target.getBounds());
  }


function onEachFeature(feature, layer) {
      layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
      });
}



function getStyle(feature) {
      return {
          weight: 2,
          opacity: 0.1,
          color: 'black',
          fillOpacity: 0.4,
          fillColor: getColor(feature.properties)
      };
 
}


function buildLegend () {
    if(legend.getContainer() !== undefined) {
        legend.removeFrom(map);    
    }
    
    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend'),
            labels = [];
            labels.push('<i style="background:#2ECC40"></i> 100%');
            labels.push('<i style="background:#FFDC00"></i> 66-99% ');
            labels.push('<i style="background:#FF851B"></i> 33-66% ');
            labels.push('<i style="background:#FF4136"></i> 1-33% ');
            labels.push('<i style="background:#CCCCCC"></i> 0%');
        div.innerHTML = labels.join('<br><br>');
        return div;
    };

    legend.addTo(map);
};

function getColor(d) {
    	
      MYAPP.hh_sprayed = MYAPP.hh_sprayed + sprayCount(MYAPP.day,d)
      MYAPP.hh_cnt = MYAPP.hh_cnt + d['hh-cnt']
      //console.log(MYAPP.spray_perc = MYAPP.hh_sprayed / MYAPP.hh_cnt);
     
   

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









