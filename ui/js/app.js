var App = {
    SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    BUFFER_URI: "http://api.mspray.onalabs.org/households.json?buffer=true",
    TARGET_AREA_URI: "http://api.mspray.onalabs.org/targetareas.json",
    HOUSEHOLD_URI: "http://api.mspray.onalabs.org/households.json",
    DISTRICT_URI: "http://api.mspray.onalabs.org/districts.json",
    hhOptions: {
        radius: 4,
        fillColor: "#FFDC00",
        color: "#222",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    },
    bufferOptions: {
        weight: 3,
        color: '#fff',
        dashArray: '',
        fillOpacity: 0.3
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

    getHouseholdsFor: function (layer) {
        var uri = this.HOUSEHOLD_URI;
        post_data = {in_bbox: layer.getBounds().toBBoxString()};
        $.getJSON(uri, post_data, function(data){
            console.log(data);
        });
    },
    
    getDistricts: function(){
        var uri = this.DISTRICT_URI;
        
        $.ajax({
            url: uri,
            type: 'GET', 
            success: function(data){
                var d_list = $('#districts_list');

                for(var d=0; d<data.length; d++){
                    var list_data = data[d],
                        dist_name = list_data.district_name,
                        num_targets = list_data.num_target_areas,
                        
                        dist_data = '<li><a href="#'+ dist_name +'">'+ dist_name +'</a></li>';
                    
                    d_list.append(dist_data);
                }
                
                var district = d_list.find('li a');
            
                district.click(function(e){
                    var dist_name = $(this).attr('href'),
                        dist_label = $('.dist_label'),
                        target_label = $('.target_label');
                        
                    dist_name = dist_name.slice(1, dist_name.length);
                    dist_label.text(dist_name);
                    target_label.text('Target Areas');
                    
                    App.getTargetAreas(dist_name);
                    //App.loadAreaData(map, dist_name);
                });
            }
        });
    },
    getTargetAreas: function(district_name){
        var uri = this.DISTRICT_URI + "?district=" + district_name;
        
        $.ajax({
            url: uri,
            type: 'GET', 
            success: function(data){
                var t_list = $('#target_areas_list');
                t_list.empty();

                for(var d=0; d<data.length; d++){
                    var list_data = data[d],
                        target_id = list_data.targetid,
                        ranks = list_data.ranks,
                        housess = list_data.houses,
                        
                    target_area = '<li><a href="#'+ target_id +'">'+ target_id +'</a></li>';
                    t_list.append(target_area);
                }
            }
        });
    },
    getSprayCount: function (day){
        var counter = 0, i =0;
        for (; i < points.features.length; i++){
            if(points.features[i].properties.day === day) {
                counter+=1;
            }
        }
        return counter;
    },
    loadHouseholds: function(map, targetid) {
        var households = L.mapbox.featureLayer()
            .loadURL(App.HOUSEHOLD_URI + "?target_area=" + targetid);
        
        households.bringToFront();
        
        households.on('ready', function(){
            var geojson = households.getGeoJSON();

            L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                onEachFeature: function(feature, layer){
                    var content = '<h4>'+ feature.properties.orig_fid +'</h4>' +
                        'HH_type: '+ feature.properties.hh_type;
                    layer.bindPopup(content, { closeButton:false });
                    
                    layer.on({
                        mouseover: function(e){
                            e.layer.openPopup();
                        },
                        mouseout: function(e){
                            e.layer.closePopup();
                        }
                    });
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
            
            var areaLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                style: App.bufferOptions,
                onEachFeature: function(feature, layer){
                    
                    var content = '<h4>'+ feature.coordinates.length +' households</h4>';
                    layer.bindPopup(content, { closeButton:false });
                    
                    layer.on({
                        mouseover: function(e){
                            var layer = e.target;
                            k = layer;
                            layer.setStyle( {fillOpacity: 0.7} );
                        },
                        mouseout: function(e){
                            areaLayer.setStyle(App.bufferOptions);
                        }
                    });
                }
            }).addTo(map);
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

    loadTargetArea: function(map, targetid) {
        var target_area = L.mapbox.featureLayer()
            .loadURL(App.TARGET_AREA_URI + "?target_area=" + targetid);
        
        target_area.on('ready', function(){
            var bounds = target_area.getBounds();
            map.fitBounds(bounds);
        }).addTo(map);
    },
    
    loadAreaData: function(map, targetid){
        this.loadTargetArea(map, targetid);
        this.loadHouseholds(map, targetid);
        this.loadBufferAreas(map, targetid);
    },

    init: function (){
        var map = L.mapbox.map('map', 'examples.map-i86nkdio');
            //.setView([-14.2164, 29.2315], 10);

        var target_id = this.getTargetAreaId();

        if (target_id === undefined){
            target_id = 4;
        }

        //this.loadAreaData(map, target_id); //Default data load
        this.getDistricts();
        
        // carry on with map loading functions
        $(document).ajaxComplete(function(){
            
            var target_area = $('#target_areas_list li a');
    
            target_area.click(function(e){
                var target_id = $(this).attr('href'),
                    target_label = $('.target_label');
                    
                target_id = target_id.slice(1, target_id.length);
                target_label.text(target_id);
                
                App.loadAreaData(map, target_id);
            });
        });
    }
};

App.init();
