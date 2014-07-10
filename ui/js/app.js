var App = {
    SPRAY_DAYS_URI: "http://127.0.0.1:8000/spraydays.json",
    BUFFER_URI: "http://127.0.0.1:8000/households.json?buffer=true",
    TARGET_AREA_URI: "http://127.0.0.1:8000/targetareas.json",
    HOUSEHOLD_URI: "http://127.0.0.1:8000/households.json",
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
    getTargetAreaId: function(){
        return this.locationParams().target_area;
    },
    loadHouseholds: function(map, targetid) {
        var households = L.mapbox.featureLayer()
            .loadURL(App.HOUSEHOLD_URI + "?target_area=" + targetid);

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
    loadBufferAreas: function(map, targetid) {
        var hh_buffers = L.mapbox.featureLayer()
            .loadURL(App.BUFFER_URI + "&target_area=" + targetid);

        hh_buffers.on('ready', function(){
            var geojson = hh_buffers.getGeoJSON();

            L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                onEachFeature: function(feature, layer){
                    layer.on({
                        mouseover: function(e){
                            var layer = e.target;
                            k = layer;
                            App.getHouseholdsFor(layer);
                            layer.setStyle({
                                weight: 3,
                                color: '#fff',
                                dashArray: '',
                                fillOpacity: 0.7
                            });
                        },
                        mouseout: function(e){
                            // console.log(e.target);
                        }
                    });
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

    getHouseholdsFor: function (layer) {
        var uri = this.HOUSEHOLD_URI;
        post_data = {in_bbox: layer.getBounds().toBBoxString()};
        $.getJSON(uri, post_data, function(data){
            console.log(data);
        });
    },

    loadTargetArea: function(map, targetid) {
        var target_area = L.mapbox.featureLayer()
            .loadURL(App.TARGET_AREA_URI + "?target_area=" + targetid);
        target_area.on('ready', function(){
            var bounds = target_area.getBounds();
            map.fitBounds(bounds);
        }).addTo(map);
    },

    init: function (){
        var map = L.mapbox.map('map', 'examples.map-i86nkdio')
            ;//.setView([-14.2164, 29.2315], 10);

        var targetid = this.getTargetAreaId();

        if (targetid === undefined){
            targetid = 1;
        }

        this.loadTargetArea(map, targetid);
        this.loadHouseholds(map, targetid);
        this.loadBufferAreas(map,targetid);
    }
};

App.init();
