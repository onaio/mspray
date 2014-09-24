var App = {
    // SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    SPRAY_DAYS_URI: "http://api.mspray.onalabs.org/spraydays.json",
    DATES_URI: "http://api.mspray.onalabs.org/spraydays.json?dates_only=true",
    BUFFER_URI: "http://api.mspray.onalabs.org/buffers.json",
    TARGET_AREA_URI: "http://api.mspray.onalabs.org/targetareas.json",
    HOUSEHOLD_URI: "http://api.mspray.onalabs.org/households.json",
    DISTRICT_URI: "http://api.mspray.onalabs.org/districts.json",

    defaultDistrict: 'Chienge',
    defaultTargetArea: 0,
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
        fillOpacity: 0.1
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
        fillOpacity: 0.4
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
        color: '#000000',
        fillOpacity: 0.4
    },

    getHouseholdsFor: function (layer) {
        var uri = this.HOUSEHOLD_URI,
            post_data = {in_bbox: layer.getBounds().toBBoxString()};
        $.getJSON(uri, post_data, function (data) {
            console.log(data);
        });
    },

    getSprayCount: function (day) {
        var counter = 0, i = 0;
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

                        // dist_data = '<li><a href="#!'+ dist_name +'">'+ dist_name +'</a></li>';
                        dist_data = '<li><a href="/#!' + dist_name +'">'+ dist_name +'</a></li>';

                    d_list.append(dist_data);
                }

                var district = d_list.find('li a');

                district.click(function(e){
                    $('.info-toggle').hide();
                    $('.info-panel').hide();

                    $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").hide();
                    $("#district_table").show();

                    var dist_name = this.href.split('#!')[1];

                    $('.dist_label').text('District : ' + dist_name);
                    $('.target_label').text('Target Area: Select');

                    App.getTargetAreas(dist_name);

                    //Show districts modal
                    // $('.modal-div').fadeIn(300);
                });
            },
            error: function(){
                console.log('Sorry, could not retrieve districts');
            }
        });
    },
    getDates: function() {
        if(App._dates !== undefined){
            return App._dates;
        }
        var dates = [];

        $.getJSON(App.DATES_URI, function(data){
            var i,
                date_list = $("#spraydays_list"),
                li = "<li><a href='#'> All </a></li>";
            date_list.empty();

            for(i=0; i < data.length; i++){
                li += '<li><a href="#' + data[i] + '">' + data[i] + '</a></li>';
            }
            date_list
                .append(li)
                .find('li a')
                    .click(App.load_spray_days_by_date);
            App._dates = data;
        });

       return dates;
    },

    calculatePercentage: function(numerator, denominator, include_sign) {
        if (numerator === undefined) numerator = 0;
        if (denominator === undefined) numerator = 1;
        var percentage = Math.round((numerator/denominator) * 100);
        if (include_sign === undefined) return percentage + "%";
        return percentage;
    },

    getTargetAreas: function(district_name){
        var uri = this.DISTRICT_URI + "?district=" + district_name,
            target_list = $('#target_areas_list'), c,
            target_table = $('table#target_table tbody'),
            target_list_content = "",
            target_table_content = "" ;

            // reset containers
            target_list.empty();
            target_table.empty();

        console.log('DISTRICT_URI: ' + uri);

        $.ajax({
            url: uri,
            type: 'GET',
            beforeSend: function() {
                $('#table-container').hide();
                $('.progress-spinner').show();
            },
            success: function(data){
                $('#table-container').show();
                $('.progress-spinner').hide();

                // on selection of a district, show data for first target areas
                //App.defaultTargetArea = data[0].properties.targetid;

                //console.log(data.features[0].properties.targetid);
                console.log(data);

                var agg_structures = 0,
                    agg_visited_total = 0,
                    agg_visited_sprayed = 0,
                    agg_visited_refused =  0,
                    agg_visited_other = 0,
                    agg_not_visited = 0;

                for(c = 0; c < data.length; c++){
                    var list_data = data[c];
                    var target_id = list_data.targetid,
                        structures = list_data.structures,
                        visited_total = list_data.visited_total,
                        visited_sprayed = list_data.visited_sprayed,
                        visited_refused = list_data.visited_refused,
                        visited_other = list_data.visited_other,
                        not_visited = list_data.not_visited, radix = 10;

                    agg_structures += parseInt(structures, radix);
                    agg_visited_total += parseInt(visited_total, radix);
                    agg_visited_sprayed += parseInt(visited_sprayed, radix);
                    agg_visited_refused += parseInt(visited_refused, radix);
                    agg_visited_other += parseInt(visited_other, radix);
                    agg_not_visited += parseInt(not_visited, radix);

                    target_list_content += '<li><a href="#!'+ district_name + "/" +
                            target_id + '">'+ target_id +'</a></li>';

                    target_table_content += '<tr>'+
                            '<th><a href="#!'+ district_name + "/" + target_id + '">'+ target_id +'</a></th>' +
                            '<td>' +  structures +  '</td>' +
                            '<td>' +  visited_total +  ' (' + App.calculatePercentage(visited_total, structures) + ')</td>' +
                            '<td>' +  visited_sprayed +  ' (' +  App.calculatePercentage(visited_sprayed, structures) + ')</td>' +
                            '<td>' +  visited_refused +  ' (' + App.calculatePercentage(visited_refused, structures) + ')</td>' +
                            '<td>' +  visited_other +  ' (' + App.calculatePercentage(visited_other, structures) + ')</td>' +
                            '<td>' +  not_visited +  ' (' + App.calculatePercentage(not_visited, structures) + ')</td>' +
                        '</tr>';
                }
                target_table_content_total = "<tr><td> Totals </td>" +
                    "<td><b>" + agg_structures + "</b></td>" +
                    "<td><b>" + agg_visited_total + ' (' + App.calculatePercentage(agg_visited_total, agg_structures) + ")</b></td>" +
                    "<td><b>" + agg_visited_sprayed + ' (' + App.calculatePercentage(agg_visited_sprayed, agg_structures) + ")</b></td>" +
                    "<td><b>" + agg_visited_refused + ' (' + App.calculatePercentage(agg_visited_refused, agg_structures) + ")</b></td>" +
                    "<td><b>" + agg_visited_other + ' (' + App.calculatePercentage(agg_visited_other, agg_structures) + ")</b></td>" +
                    "<td><b>" + agg_not_visited + ' (' + App.calculatePercentage(agg_not_visited, agg_structures) + ")</b></td>" +
                    "</tr>";
                target_list.append(target_list_content);

                var promise = new Promise(function(resolve, reject) {
                    $('table#target_areas tbody').empty().prepend(
                        target_table_content
                    )
                    resolve($('table#target_areas tbody'));
                });

                promise.then(function(selector) {
                    selector.prepend(target_table_content_total)
                });

                $('table#target_areas').table().data( "table" ).refresh();
                $('table#target_areas').table().sortable('sortBy', null, 'asc');
                $('h1#district-name').text("District:" + district_name);
            },
            error: function(){
                console.log('Sorry, could not retrieve target areas');
            }
        });
    },

    getResource: function() {
        var url = document.location.hash,
            fragment = url.split('/'),
            district = (url.length === 0) ? App.defaultDistrict : fragment[0].substring(2, fragment[0].length),
            target_id = (fragment[1] === undefined) ? App.defaultTargetArea : fragment[1];
        return {
            "district": district,
            "target_id": target_id
        }
    },

    getCurrentDistrict: function(){
        return App.getResource().district;
    },

    getCurrentTargetArea: function(){
        return App.getResource().target_id;
    },

    loadTargetArea: function(map, targetid) {
        if(targetid === undefined){
            return;
        }
        uri = App.TARGET_AREA_URI + "?target_area=" + targetid;
        $.getJSON(uri, function(data){
            if(data.length > 0){
                $('#target-area-stats').empty().append(
                    "<dt class='reason reason-sprayed'>" + data[0].visited_sprayed + "</dt>" +
                    "<dd>Visited Sprayed</dd>" +
                    "<dt class='reason reason-not-sprayed'>" + data[0].visited_refused + "</dt>" +
                    "<dd>Visited Refused</dd>" +
                    "<dt class='reason reason-other'>" + data[0].visited_other + "</dt>" +
                    "<dd>Visited Other</dd>" +
                    "<dt class='reason reason-total-visited'>" + data[0].visited_total + "</dt>" +
                    "<dd>Visited Total</dd>" +
                    "<dt class='reason reason-not-visited'>" + data[0].not_visited + "</dt>" +
                    "<dd>Not Visited</dd>" +
                    "<dt class='reason total-structures'>" + data[0].structures + "</dt>"+
                    "<dd>Structures</dd>"
                )
                $('#target-area-label').text('Target Area : ' + targetid);

                App.housesCount = data[0].structures;

                App.drawCircle(App.calculatePercentage(data[0].visited_sprayed, App.housesCount, false), 'circle-sprayed');
                $('#circle-refused').text(App.calculatePercentage(data[0].visited_refused, App.housesCount));
                $('#circle-other').text(App.calculatePercentage(data[0].visited_other, App.housesCount));

                var bounds = data[0].bounds;
                if(bounds.length == 4){
                    var minL = L.latLng(bounds[1], bounds[0]),
                        maxL = L.latLng(bounds[3], bounds[2]);
                    var lat_bounds = L.latLngBounds(minL, maxL);
                    map.fitBounds(lat_bounds);
                }
            }
        });

        if(targetid === '909001'){
            var target_area = L.mapbox.featureLayer()
                .loadURL(uri.replace('.json', '.geojson'));

            console.log('TARGET_AREA_URI: ' + App.TARGET_AREA_URI + "?target_area=" + targetid);

            target_area.on('ready', function(){
                bounds = target_area.getBounds();
                map.fitBounds(bounds);
                var geojson = target_area.getGeoJSON();

                this.targetLayer = [];

                this.targetLayer = L.geoJson(geojson, {
                    onEachFeature: function(feature, layer){
                        var props = feature.properties;
                        var content = '<h4>Target Area: ' + props.targetid + '</h4>' +
                                    'Structures: ' + props.structures;

                        layer.bindPopup(content, { closeButton:true });

                        console.log("Spray data: " + props.structures);
                    }
                });

                target_area.setStyle(App.targetOptions);
            }).addTo(map);
        }

        $('#circle-refused').text("0%");
        $('#circle-other').text("0%");
        App.drawCircle(0, 'circle-sprayed');

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
            // bounds = hh_buffers.getBounds();
            // map.fitBounds(bounds);

            this.bufferLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, App.hhOptions);
                },
                style: function(feature) {
                    App.bufferOptions.fillColor = feature.style.fillColor;

                    return App.bufferOptions;
                },
                onEachFeature: function(feature, layer){
                    var content = "<h4>"+ feature.properties.percentage_sprayed + '% (' + feature.properties.spray_points + '/' + feature.properties.num_households + ') Visited </h4>';
                    layer.bindPopup(content, { closeButton:true });

                    layer.on({
                        mouseover: function(e){
                            var layer = e.target;
                            k = layer;
                            layer.setStyle( {fillOpacity: 0.7} );
                        },
                        mouseout: function(e){
                            e.target.setStyle({fillOpacity: 0.4});
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
        var uri = App.HOUSEHOLD_URI + "?target_area=" + targetid;
        // $.getJSON(uri, function(data){
        //     console.log(data);
        // });
        if(targetid === '909001'){
            var households = L.mapbox.featureLayer().loadURL(uri);

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
                        // layer.bindPopup(content, { closeButton:true });

                        layer.on({
                            mouseover: function(e){
                                e.layer.openPopup();
                            },
                            mouseout: function(e){
                                e.layer.closePopup();
                            }
                        });
                    }
                }).addTo(map);

                this.hhLayer.setZIndex(70);
            });
        }
    },

    loadSprayPoints: function (map, day, targetid) {
        if(targetid === undefined){
            return;
        }
        var url = App.SPRAY_DAYS_URI;
        if(day !== undefined){
            url = url += "?spray_date=" + day + "&target_area=" + targetid;
        }
        var sprayed = L.mapbox.featureLayer().loadURL(url),
            sprayed_status = {}, reason_obj = {},
            reasons = {
                '1': 'sick',
                '2': 'locked',
                '3': 'funeral',
                '4': 'refused',
                '5': 'knowone home or missed',
                '6': 'other'
            },
            reason_colors = {
                '1': '#800080',
                '2': '#FFA500',
                '3': '#1B11E1',
                '4': '#D05B5B',
                '5': '#C27344',
                '6': '#6C696B'
            },
            target_area_stats = '';


        console.log('SPRAYPOINT_URI: ' + url);

        App.map.removeLayer(App.sprayLayer); // reset layer

        sprayed.on('ready', function(){
            var geojson = sprayed.getGeoJSON();
            App.sprayCount = 0; // reset counter

            App.sprayLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    if(feature.properties.sprayed === 'no'){
                        App.sprayOptions.fillColor = reason_colors[feature.properties.reason];
                    } else{
                        App.sprayOptions.fillColor = "#2ECC40";
                    }
                    return L.circleMarker(latlng, App.sprayOptions);
                },
                onEachFeature: function(features){
                    if (sprayed_status[features.properties.sprayed] === undefined) {
                        sprayed_status[features.properties.sprayed] = 1;
                    } else {
                        sprayed_status[features.properties.sprayed]++;
                    }

                    if (features.properties.reason !== null) {
                        if (reason_obj[reasons[features.properties.reason]] === undefined) {
                            reason_obj[reasons[features.properties.reason]] = 1;
                        } else {
                            reason_obj[reasons[features.properties.reason]]++;
                        }
                    }
                }
            })
            .addTo(map);

            target_area_stats += "<dt class='reason reason-sprayed'>" + ((sprayed_status.yes === undefined) ? 0 : sprayed_status.yes) + "</dt><dd>Sprayed</dd>";
            target_area_stats += "<dt class='reason reason-not-sprayed'>" + ((sprayed_status.no === undefined) ? 0 : sprayed_status.no) + "</dt><dd>Not Sprayed</dd>";
            $('#target-area-stats').empty().append(target_area_stats);

            target_area_stats = "";
            $.each(reasons, function(key, value) {
                target_area_stats += "<dt class='reason reason-" + value.replace(/ /g, '-');
                if (reason_obj[value])
                     target_area_stats += "'>" + reason_obj[value] + "</dt><dd>" + value + "</dd>";
                else
                    target_area_stats +=  "'>0</dt><dd >" + value + "</dd>";
            });
            console.log("target area stats: " + target_area_stats)
            $('#target-area-stats-not-sprayed').empty().append(target_area_stats);
            $("#not-sprayed-reasons").show();

            App.sprayLayer.setZIndex(80);

            $('.perc_label').text(App.sprayCount);

            var sprayed_percentage = App.calculatePercentage(sprayed_status.yes, App.housesCount, false),
                refused_percentage = App.calculatePercentage(reason_obj.refused, App.housesCount),
                other_percentage = App.calculatePercentage(reason_obj.other, App.housesCount);

            console.log('SPRAY: ' + sprayed_status.yes + ' / HOUSE: '+ App.housesCount + ' = ' + sprayed_percentage);

            App.drawCircle(sprayed_percentage, 'circle-sprayed');
            $('#circle-refused').text(refused_percentage);
            $('#circle-other').text(other_percentage);
        });

    },

    loadAreaData: function(map, targetid){
        this.loadTargetArea(map, targetid);
        this.loadBufferAreas(map, targetid);
        this.loadHouseholds(map, targetid);
    },

    drawCircle: function(percent, circle_id) {
        var fillColor;
        if(percent < 30){
            fillColor = '#FFA500';
        }
        else if(percent >= 30 && percent < 40){
            fillColor = '#FFFFCC';
        }
        else if(percent >= 40 && percent < 80){
            fillColor = '#C2E699';
        }
        else if(percent >= 80 && percent < 90){
            fillColor = '#78C679';
        }
        else if(percent >= 90 && percent <= 100){
            fillColor = '#31A354';
        }

        Circles.create({
            id: circle_id,
            percentage: parseInt(" " + percent, 10),
            radius: 50,
            width: 12,
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
            var targetAreasList = $("#target_areas_list li");

            if(filterText !== ""){
                targetAreasList.hide();
                targetAreasList.children("a").filter(function(){
                    return $(this).text().toLowerCase().indexOf(filterText) >-1;
                }).parent("li").show();
            }
        /*    else if(filterText == ""){
                targetAreasList.hide();
            } */
            else{
                targetAreasList.show();
            }
        });
    },

    loadMap: function(){
        if (App.map !== undefined){
            return;
        }
        var google = new L.Google(),
            bing = new L.BingLayer("AuOGADooQT2MGfigXZmbgIOJ_Jts7glmpRAAWZU9WHYfvPFFZp0lmxqV5T86RVt6");
            bufferHouseholdsLayer = L.mapbox.tileLayer('ona.j6c49d56');

        App.map = L.mapbox.map('map');
        App.map.addLayer(google);
        App.map.addLayer(bufferHouseholdsLayer);
        L.control.layers({
            'Google':google,
            'Bing':bing
        }, {
            'buffershouseholds': bufferHouseholdsLayer
        }).addTo(App.map);
        L.control.locate().addTo(App.map);
        L.control.scale({
            position: 'bottomright'
        }).addTo(App.map);
        App.map.options.maxZoom = 19
        App.buildLegend(App.map);
    },

    getPageState: function(){
        var current_district = this.getCurrentDistrict();
        var current_target_area = this.getCurrentTargetArea();

        $('#target-area-label').text('Target Area : ' + current_target_area);
        $('.target_label').text('Target Area : ' + current_target_area);

        if(current_target_area != this.defaultTargetArea){
            App.loadMap();
            $('#map, #spray_date_picker, #map-legend, #target-area-stats-item').show();
            App.loadAreaData(App.map, current_target_area);
            console.log("Loading map for target", current_target_area);
        } else {
            this.getTargetAreas(current_district);
        }

    },

    buildLegend: function(map) {
        var legend = L.control({
            position: 'bottomright'
        });

        if (legend.getContainer() !== undefined) {
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
    },

    init: function (){
        $(document).ready(function(){
            var set_target_id, fragment, target_id,
                infopanel = $(".info-panel");

            L.mapbox.accessToken = 'pk.eyJ1Ijoib25hIiwiYSI6IlVYbkdyclkifQ.0Bz-QOOXZZK01dq4MuMImQ';
            $('#map, #spray_date_picker, #map-legend, #target-area-stats-item').hide();

            // load page info
            App.getDistricts();
            App.getDates();
            App.getPageState();

            App.drawCircle(0, 'circle-sprayed');
            $('#circle-refused').text("0%");
            $('#circle-other').text("0%");

            App.searchInit();

            $(document).ajaxComplete(function(){
                $('#target_areas_list li a, #target_areas a').click(function(e){
                    fragment = this.href.split('#!')[1];
                    target_id = fragment.split('/')[1];

                    $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").show();
                    $("#not-sprayed-reasons").hide();
                    App.loadMap();
                    $("#district_table").hide();

                    if (target_id !== set_target_id) {
                        set_target_id = target_id;
                        $('.target_label').text('Target Area : ' + target_id);
                        App.loadAreaData(App.map, target_id);
                        console.log("Loading map for target", target_id);
                    }
                });

            });
            $('#target-area-stats-item').on('click', function() {
                infopanel.toggle();
            })

        });
    },

    load_spray_days_by_date: function(event){
        event.preventDefault();
        var sprayday = this.href.split('#')[1], dt, dt_label;
        App.loadSprayPoints(App.map, sprayday, App.getCurrentTargetArea());
        if (sprayday === "") {
            $('.sprayday_label').text("All");
            $('.day_label').text("All");
        } else {
            dt = new Date(sprayday);
            dt_label = dt.toLocaleDateString();
            $('.sprayday_label').text(dt_label);
            $('.day_label').text(dt_label);
        }
    }
};

App.init();
