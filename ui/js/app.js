var App = {
    // SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    SPRAY_DAYS_URI: "http://localhost:8000/spraydays.json",
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
    getSprayCount: function (day){
        var counter = 0, i =0;
        for (; i < points.features.length; i++){
            if(points.features[i].properties.day === day) {
                counter+=1;
            }
        }
        return counter;
    },
    
    getDistricts: function(){
        var uri = this.DISTRICT_URI;
        
        console.log('Fetching districts...');
        
        $.ajax({
            url: uri,
            type: 'GET', 
            success: function(data){
                var d_list = $('#districts_list');

                for(var d=0; d<data.length; d++){
                    var list_data = data[d],
                        dist_name = list_data.district_name,
                        num_targets = list_data.num_target_areas,
                        
                        dist_data = '<li><a href="#!'+ dist_name +'">'+ dist_name +'</a></li>';
                    
                    d_list.append(dist_data);
                }
                
                var district = d_list.find('li a');
            
                district.click(function(e){
                    
                    var dist_name = $(this).attr('href');
                        
                    dist_name = dist_name.slice(2, dist_name.length);
                    $('.dist_label').text(dist_name);
                    
                    App.getTargetAreas(dist_name);
                });
            },
            error: function(){
                console.log('Sorry, could not retrieve districts');
            }
        });
    },
    
    getTargetAreas: function(district_name){
        var uri = this.DISTRICT_URI + "?district=" + district_name;
        
        $.ajax({
            url: uri,
            type: 'GET', 
            success: function(data){
                var target_table = $('.target_table tbody');
                target_table.empty();
                
                // on selection of a district, show data for first target area
                $('.target_label').text(data[0].targetid);
                
                for(var d=0; d<data.length; d++){
                    var list_data = data[d],
                        target_id = list_data.targetid,
                        ranks = list_data.ranks,
                        houses = list_data.houses;
                    
                    //Create a table
                    target_table.append(
                        '<tr>'+ 
                            '<td><a href="#!'+ district_name + "/" + target_id + '">'+ target_id +'</a></td>' +
                            '<td>' + houses + '</td>' +
                            '<td></td>' +
                            '<td></td>' +
                        '</tr>'
                    );
                }
            },
            error: function(){
                console.log('Sorry, could not retrieve target areas');
            }
        });
    },
    
    getCurrentDistrict: function(){
        var url = document.location.hash;
        var fragment = url.split('/')[0];  
        
        return fragment.substring(2, fragment.length);
    },
    
    getCurrentTargetArea: function(){
        var url = document.location.hash;
        // var target_id = url.substring(url.indexOf('#') + 1, url.length);
        
        return url.split('/')[1];
    },

    loadHouseholds: function(map, targetid) {
        var households = L.mapbox.featureLayer()
            .loadURL(App.HOUSEHOLD_URI + "?target_area=" + targetid);

        households.on('ready', function(){
            var geojson = households.getGeoJSON();
            
            var hh_Layer = L.geoJson(geojson, {
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
            var count = 0;
            
            var sprayPointLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.sprayOptions);
                },
                onEachFeature: function(){
                    count++;
                    $('.perc_label').text(count);
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
            console.dir(map);
          
            map.fitBounds(bounds);
           
        }).addTo(map);
    },
    
    loadAreaData: function(map, targetid){
        var targetid = this.getCurrentTargetArea();
        
        if(isNaN(targetid) || targetid == undefined){
            targetid=4;
        }
        
        this.loadTargetArea(map, targetid);
        this.loadHouseholds(map, targetid);
        this.loadBufferAreas(map, targetid);
    },
    
    restorePageState: function(){
        // if the page is reloaded, restore same page state
        var current_district = this.getCurrentDistrict();
        var current_target_area = this.getCurrentTargetArea();
        
        this.getTargetAreas(current_district);
        
        $('.dist_label').text(current_district);
        $('.target_label').text(current_target_area);
    },

    init: function (){
        window.map = L.mapbox.map('map'); //'examples.map-i86nkdio'//.setView([-14.2164, 29.2315], 10);
        map.addLayer(new L.Google);
        L.control.locate().addTo(map);
        
        //Counters
        var houseHolds = 0;
        
        this.restorePageState();
        this.getDistricts();
        
        var default_target_id = App.getCurrentTargetArea();
        App.current_target_area = null;
        
        App.loadAreaData(map, default_target_id);
        
        $(document).ajaxComplete(function(){
            
            var target_area = $('.target_table a');
            
            target_area.click(function(e){
                var target_id = $(this).attr('href');
                
                target_id = target_id.split('/')[1];
                $('.target_label').text(target_id);
                
               App.loadAreaData(map, target_id);
            });
        });
        
        $(document).ready(function(){
            
            // load target-buffer areas
            $(".target_filter").keyup(function(){
                var filterText = $(this).val();
                if(filterText != ""){
                    
                    $(".target_table tbody>tr").hide();
                    $(".target_table td").filter(function(){
                        return $(this).text().toLowerCase().indexOf(filterText) >-1; 
                    }).parent("tr").show();
                }
                else{
                    $(".target_table tbody>tr").show();
                }
            });
            
            // load spraydays
            $('#spraydays_list li a').click(function(e){
                var sprayday = $(this).attr('href');
                sprayday = sprayday.slice(4, sprayday.length);
                
                App.loadSprayPoints(map, sprayday);
                $('.day_label').text('Day ' + sprayday);
                
                e.preventDefault();
            });
            
            // sidebar
            $("a.toggle-infopanel").click(function(){
                
                $(".info-panel").toggle();
                e.preventDefault();
            });
        });
    }
};

App.init();