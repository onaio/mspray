var App = {
    SPRAY_DAYS_URI: "http://localhost:8000/spraydays.json",
    TARGET_AREA_URI: "http://localhost:8000/targetareas.json",
    HOUSEHOLD_URI: "http://localhost:8000/households.json",
    hhOptions: {
        radius: 4,
        fillColor: "#FFDC00",
        color: "#222",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    },

    sprayOptions: {
        radius: 4,
        fillColor: "#2ECC40",
        color: "#222",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    },
    sprayAltOptions: {

        weight: 2,
        opacity: 0.1,
        color: 'black',
        fillOpacity: 0.4
    },
    locationParams: function () {
        var i, params = location.search.substring(1).split("&");
        obj = {};

        for(i = 0; i < params.length; i++){
            var param = params[i].split("=");

            if(param.length > 1){
                var key = param[0], val = param[1];

                if(val.length > 1 && val[val.length - 1] == "/"){
                    val = val.slice(0, val.length - 1);
                }
                obj[key] = val;
            }
        }

        return obj;
    },
    getDay: function () {
        return this.locationParams().day;
    },
    loadHouseholds: function(map) {
        var households = L.mapbox.featureLayer()
            .loadURL(App.HOUSEHOLD_URI);

        households.on('ready', function(){
            var geojson = households.getGeoJSON();

            L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                }
            })
            .addTo(map);
        });
    },
    loadSprayPoints: function (map, day) {
        var url = App.SPRAY_DAYS_URI;
        if(day !== undefined){
            url = url += "?day=" + day;
        }
        var sprayed = L.mapbox.featureLayer()
            .loadURL(url);

        sprayed.on('ready', function(){
            var geojson = sprayed.getGeoJSON();

            L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.sprayOptions);
                }
            })
            .addTo(map);
        });
    },

    init: function (){
        var map = L.mapbox.map('map', 'examples.map-i86nkdio')
            .setView([-15.2164, 28.2315], 15);

        var target_area = L.mapbox.featureLayer()
            .loadURL(App.TARGET_AREA_URI)
            .addTo(map);

        this.loadHouseholds(map);
        this.loadSprayPoints(map, this.getDay());
    }
};

App.init();
