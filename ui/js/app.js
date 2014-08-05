var App = {
    // SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    BUFFER_URI: "http://api.mspray.onalabs.org/buffers.json",
    TARGET_AREA_URI: "http://api.mspray.onalabs.org/targetareas.json",
    HOUSEHOLD_URI: "http://api.mspray.onalabs.org/households.json",
    DISTRICT_URI: "http://api.mspray.onalabs.org/districts.json",

    defaultDistrict: 'Chienge',
    defaultTargetArea: 848,
    sprayLayer: [],
    targetLayer: [],
    hhLayer: [],
    bufferLayer: [],
    housesCount: 0,
    sprayCount: 0,

    targetOptions: {
        fillColor: '#999999',
        color: '#FFFFFF',
        weight: 3,
        fillOpacity: 0.4
    },
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

        $.ajax({
            url: uri,
            type: 'GET',
            success: function(data){
                var d_list = $('#districts_list, #search_autocomplete'), c;

                for(c = 0; c < data.length; c++){
                    var list_data = data[c],
                        dist_name = list_data.district_name,
                        num_targets = list_data.num_target_areas,

                        dist_data = '<li><a href="#!'+ dist_name +'">'+ dist_name +'</a></li>';

                    d_list.append(dist_data);
                }

                var district = d_list.find('li a');

                district.click(function(e){
                    var dist_name = $(this).attr('href');

                    dist_name = dist_name.slice(2, dist_name.length);
                    $('.dist_label').text('District : ' + dist_name);

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
                var target_list = $('#target_areas_list'), c;
                target_list.empty();

                // on selection of a district, show data for first target area
                // App.loadAreaData(map, data[0].targetid);

                App.defaultTargetArea = data[0].targetid;

                for(c = 0; c < data.length; c++){
                    var list_data = data[c],
                        target_id = list_data.targetid,
                        ranks = list_data.ranks,
                        houses = list_data.houses;

                    target_list.append(
                        '<li><a href="#!'+ district_name + "/" +
                            target_id + '">'+ target_id +'</a></li>'
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

        if(url.length === 0){
            return App.defaultDistrict;
        }

        var fragment = url.split('/')[0];

        return fragment.substring(2, fragment.length);

    },

    getCurrentTargetArea: function(){
        var url = document.location.hash;
        var target_id = url.split('/')[1];

        if(target_id === undefined){
            target_id = App.defaultTargetArea;
        }

        return target_id;
    },

    loadTargetArea: function(map, targetid) {
        if(targetid === undefined){
            return;
        }
        var target_area = L.mapbox.featureLayer().
            loadURL(App.TARGET_AREA_URI + "?target_area=" + targetid);

        console.log('TARGET_AREA_URI: ' + App.TARGET_AREA_URI + "?target_area=" + targetid);

        target_area.on('ready', function(){
            var bounds = target_area.getBounds();
            map.fitBounds(bounds);
            var geojson = target_area.getGeoJSON();

            this.targetLayer = [];

            this.targetLayer = L.geoJson(geojson, {
                onEachFeature: function(feature, layer){
                    var props = feature.properties;
                    var content = '<h4>Target Area: ' + props.targetid + '</h4>' +
                                  'Houses: ' + props.houses;

                    layer.bindPopup(content, { closeButton:true });

                    console.log('Spray Data: ' + props.houses);
                    //Create a table
                    // target_table.append(
                        // '<tr>'+
                            // '<td class="c1"><a href="#!'+ district_name + "/" + target_id + '">'+ target_id +'</a></td>' +
                            // '<td class="c2">' + houses + '</td>' +
                            // '<td class="c3"></td>' +
                            // '<td class="c4"></td>' +
                        // '</tr>'
                    // );
                }
            });
            this.targetLayer.setZIndex(50);

            target_area.setStyle(App.targetOptions);

        }).addTo(map);
    },

    loadBufferAreas: function(map, targetid) {
        if(targetid === undefined){
            return;
        }
        var hh_buffers = L.mapbox.featureLayer()
            .loadURL(App.BUFFER_URI + "?target_area=" + targetid);

        console.log('BUFFER_URI: ' + App.BUFFER_URI + "?target_area=" + targetid);

        this.bufferLayer = [];

        hh_buffers.on('ready', function(){
            var geojson = hh_buffers.getGeoJSON();

            this.bufferLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                style: App.bufferOptions,
                onEachFeature: function(feature, layer){
                    var content = '<h4>'+ feature.properties.num_households +' households</h4>';
                    content += '<h4>'+ feature.properties.spray_points +' spray points</h4>';
                    content += '<h4>'+ feature.properties.percentage_sprayed +'% sprayed</h4>';
                    layer.bindPopup(content, { closeButton:true });

                    layer.on({
                        mouseover: function(e){
                            var layer = e.target;
                            k = layer;
                            layer.setStyle( {fillOpacity: 0.7} );
                        },
                        mouseout: function(e){
                            e.target.setStyle(App.bufferOptions);
                        }
                    });
                }
            }).addTo(map);

            this.bufferLayer.setZIndex(60);
        });
    },

    loadHouseholds: function(map, targetid) {
        if(targetid === undefined){
            return;
        }
        var households = L.mapbox.featureLayer()
            .loadURL(App.HOUSEHOLD_URI + "?target_area=" + targetid);

        console.log('HOUSEHOLD_URI: ' + App.HOUSEHOLD_URI + "?target_area=" + targetid);

        this.hhLayer = []; //reset layer

        households.on('ready', function(){
            var geojson = households.getGeoJSON();

            this.hhLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                onEachFeature: function(feature, layer){
                    // increment no. of households
                    App.housesCount++;

                    var content = '<h4>'+ feature.properties.orig_fid +'</h4>' +
                        'HH_type: '+ feature.properties.hh_type;
                    layer.bindPopup(content, { closeButton:true });

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

            this.hhLayer.setZIndex(70);
        });
    },

    loadSprayPoints: function (map, day, targetid) {
        if(targetid === undefined){
            return;
        }
        var url = App.SPRAY_DAYS_URI;
        if(day !== undefined){
            url = url += "?day=" + day + "&target_area=" + targetid;
        }
        var sprayed = L.mapbox.featureLayer()
            .loadURL(url);

        console.log('SPRAYPOINT_URI: ' + url);

        this.sprayLayer = []; // reset layer

        sprayed.on('ready', function(){
            var geojson = sprayed.getGeoJSON();
            App.sprayCount = 0; // reset counter

            this.sprayLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.sprayOptions);
                },
                onEachFeature: function(){
                    App.sprayCount++;
                }
            })
            .addTo(map);

            this.sprayLayer.setZIndex(80);

            $('.perc_label').text(App.sprayCount);

            // update circle with this data
            var percentage = 0;
            percentage = (App.sprayCount / App.housesCount) * 100;

            console.log('SPRAY: ' + App.sprayCount + ' / HOUSE: '+ App.housesCount +
                        ' = ' + percentage);

            App.drawCircle(Math.round(percentage));
        });
    },

    loadAreaData: function(map, targetid){
        this.loadTargetArea(map, targetid);
        this.loadBufferAreas(map, targetid);
        this.loadHouseholds(map, targetid);
    },

    drawCircle: function(percent) {
        var fillColor;

        if(percent < 30){
            fillColor = 'orange';
        }
        else if(percent < 30){
            fillColor = '#FFFFCC';
        }
        else if(percent < 40){
            fillColor = '#C2E699';
        }
        else if(percent < 80){
            fillColor = '#78C679';
        }
        else if(percent >= 80){
            fillColor = '#31A354';
        }

        Circles.create({
            id: 'spray-circle',
            percentage: percent,
            radius: 60,
            width: 15,
            number: percent,
            text: '%',
            colors: ['#AAAAAA', fillColor],
            duration: 200
        });
    },

    filterByOperator: function(){
        // filter according to spray operator
    },

    searchInit: function(){

        $(".target_filter").keyup(function(){
            var filterText = $(this).val();

            if(filterText != ""){
                $("#search_autocomplete li").hide();
                $("#search_autocomplete li a").filter(function(){
                    return $(this).text().toLowerCase().indexOf(filterText) >-1;
                }).parent("li").show();
            }
            else if(filterText == ""){
                $("#search_autocomplete li").hide();
            }
            else{
                $("#search_autocomplete li").show();
            }
        });
    },

    getPageState: function(){
        var current_district = this.getCurrentDistrict();
        var current_target_area = this.getCurrentTargetArea();

        console.log("District", current_district.length);
        console.log("TA", current_target_area);
        this.getTargetAreas(current_district);

        $('.dist_label').text('District : ' + current_district);
        $('.target_label').text('Target Area : ' + current_target_area);

        App.loadAreaData(map, current_target_area);
    },

    init: function (){
        window.map = L.mapbox.map('map'); //.setView([-14.2164, 29.2315], 13);
        map.addLayer(new L.Google);
        L.control.locate().addTo(map);

        // load page info
        this.getDistricts();
        this.getPageState();
        this.drawCircle(0);
        this.searchInit();

        $(document).ajaxComplete(function(){
            var target_area = $('#target_areas_list li a');

            App.drawCircle(0);

            target_area.click(function(e){
                var target_id = $(this).attr('href');

                target_id = target_id.split('/')[1];
                $('.target_label').text('Target Area : ' + target_id);

               App.loadAreaData(map, target_id);
            });
        });

        $(document).ready(function(){

            // load spraydays
            $('#spraydays_list li a').click(function(e){
                var sprayday = $(this).attr('href');
                sprayday = sprayday.slice(4, sprayday.length);

                App.loadSprayPoints(map, sprayday, App.getCurrentTargetArea());
                $('.sprayday_label').text('Date: Day ' + sprayday);
                $('.day_label').text('Day ' + sprayday);

                e.preventDefault();
            });

            // sidebar toggle
            $(".info-toggle").click(function(){
                var infopanel = $(".info-panel"),
                    infotoggle = $('.info-toggle'),
                    panelbtn = $('.panel-state');

                if(infopanel.hasClass('open')){
                    infotoggle.removeClass('open');
                    panelbtn.html('<span class="glyphicon glyphicon-chevron-left"> </span> &nbsp; View Table');
                    infopanel.hide();
                }
                else{
                    infotoggle.addClass('open');
                    panelbtn.html('<span class="glyphicon glyphicon-remove"> </span>');
                    infopanel.show();
                }

                infopanel.toggleClass('open');
            });
        });
    }
};

App.init();
