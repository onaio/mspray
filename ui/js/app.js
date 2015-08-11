/* global $ L Circles global console */
var k, mp;
(function() {
    "use strict";

    var App = {
        // SPRAY_DAYS_URI: "http://namibia.api.mspray.onalabs.org/spraydays.json",
        SPRAY_DAYS_URI: "http://namibia.api.mspray.onalabs.org/spraydays.json",
        DATES_URI: "http://namibia.api.mspray.onalabs.org/spraydays.json?dates_only=true",
        BUFFER_URI: "http://namibia.api.mspray.onalabs.org/buffers.json",
        TARGET_AREA_URI: "http://namibia.api.mspray.onalabs.org/targetareas.json",
        HOUSEHOLD_URI: "http://namibia.api.mspray.onalabs.org/households.json",
        DISTRICT_URI: "http://namibia.api.mspray.onalabs.org/districts.json",

        defaultDistrict: "Chienge",
        defaultTargetArea: 0,
        sprayLayer: [],
        targetLayer: [],
        hhLayer: [],
        bufferLayer: [],
        allDistricts: [],
        housesCount: 0,
        sprayCount: 0,
        visitedTotal: 0,

        targetOptions: {
            fillColor: "#999999",
            color: "#FFFFFF",
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
            color: "#fff",
            dashArray: "",
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
            color: "#000000",
            fillOpacity: 0.4
        },

        getDistricts: function(){
            var uri = this.DISTRICT_URI;

            $.ajax({
                url: uri,
                type: "GET",
                success: function(data){
                    var d_list = $("#districts_list, #search_autocomplete"), c, dist_name;

                    for(c = 0; c < data.length; c++){
                        var list_data = data[c];
                        dist_name = list_data.district_name;
                        var dist_data = "<li><a href='/#!" + dist_name + "'>" + dist_name + "</a></li>";
                        App.allDistricts.push(dist_name);
                        d_list.append(dist_data);
                    }
                    d_list.prepend("<li><a href='/#!All'>All</a></li>");

                    var district = d_list.find("li a");

                    district.click(function(e){
                        e.preventDefault();
                        $(".info-toggle").hide();
                        $(".info-panel").hide();

                        $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").hide();
                        $("#district_table").show();

                        dist_name = this.href.split("#!")[1];

                        $(".dist_label").text("District : " + dist_name);
                        $(".target_label").text("Target Area: Select");

                        if (dist_name === "All") {
                            App.getTargetAreasAggregate();
                        } else {
                            App.getTargetAreas(dist_name);
                        }

                        //Show districts modal
                        // $('.modal-div').fadeIn(300);
                    });
                },
                error: function(){
                    // console.log("Sorry, could not retrieve districts");
                }
            }).done(function() {

                if (location.hash.indexOf("All") > 0 || location.hash === "") {
                    $(".progress-spinner").hide();
                    App.getTargetAreasAggregate();
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

                for(i = 0; i < data.length; i++){
                    li += "<li><a href='#" + data[i] + "'>" + data[i] + "</a></li>";
                }
                date_list
                    .append(li)
                    .find("li a")
                        .click(App.load_spray_days_by_date);
                App._dates = data;
            });

           return dates;
        },

        calculatePercentage: function(numerator, denominator, include_sign) {
            var _denominator = denominator,
                _numerator = numerator,
                percentage;
            if (_numerator === undefined) {
                _numerator = 0;
            }
            if (_denominator === undefined || _denominator === 0) {
                _denominator = 1;
            }
            percentage = Math.round((_numerator / _denominator) * 100);
            if (include_sign === undefined) {
                return percentage + "%";
            }

            return percentage;
        },

        getTargetAreas: function(district_name){
            if (district_name === "All") {
                return;
            }
            var uri = this.DISTRICT_URI + "?district=" + district_name,
                target_list = $("#target_areas_list"), c,
                target_table = $("#target_table tbody"),
                target_list_content = "",
                target_table_content = "";

                // reset containers
                $("#target_areas thead tr th :first").text("TARGET AREA");
                target_list.empty();
                target_table.empty();

            // console.log('DISTRICT_URI: ' + uri);

            $.ajax({
                url: uri,
                type: "GET",
                beforeSend: function() {
                    $("#table-container").hide();
                    $(".progress-spinner").show();
                },
                success: function(data){
                    $("#table-container").show();
                    $(".progress-spinner").hide();

                    // on selection of a district, show data for first target areas
                    //App.defaultTargetArea = data[0].properties.targetid;

                    //console.log(data.features[0].properties.targetid);
                    // console.log(data);

                    var agg_structures = 0,
                        agg_visited_total = 0,
                        agg_visited_sprayed = 0,
                        agg_visited_not_sprayed = 0,
                        agg_visited_refused = 0,
                        agg_visited_other = 0,
                        agg_not_visited = 0;

                    for(c = 0; c < data.length; c++){
                        var list_data = data[c];
                        var target_id = list_data.targetid,
                            structures = list_data.structures,
                            visited_total = list_data.visited_total,
                            visited_sprayed = list_data.visited_sprayed,
                            visited_not_sprayed = list_data.visited_not_sprayed,
                            visited_refused = list_data.visited_refused,
                            visited_other = list_data.visited_other,
                            not_visited = list_data.not_visited, radix = 10;

                        agg_structures += parseInt(structures, radix);
                        agg_visited_total += parseInt(visited_total, radix);
                        agg_visited_sprayed += parseInt(visited_sprayed, radix);
                        agg_visited_not_sprayed += parseInt(visited_not_sprayed, radix);
                        agg_visited_refused += parseInt(visited_refused, radix);
                        agg_visited_other += parseInt(visited_other, radix);
                        agg_not_visited += parseInt(not_visited, radix);

                        target_list_content += "<li><a href='#!" + district_name + "/" +
                                target_id + "'>" + target_id + "</a></li>";

                        target_table_content += "<tr>" +
                                "<th><a href='#!" + district_name + "/" + target_id + "'>" + target_id + "</a></th>" +
                                "<td class='lime-column'>" + structures + "</td>" +
                                "<td>" + visited_total + " (" + App.calculatePercentage(visited_total, structures) + ")</td>" +
                                "<td class='lime-column'>" + visited_sprayed + " (" + App.calculatePercentage(visited_sprayed, visited_total) + ")</td>" +
                                "<td >" + visited_not_sprayed + " (" + App.calculatePercentage(visited_not_sprayed, visited_total) + ")</td>" +
                                "<td class='lime-column'>" + visited_refused + " (" + App.calculatePercentage(visited_refused, visited_total) + ")</td>" +
                                "<td>" + visited_other + " (" + App.calculatePercentage(visited_other, visited_total) + ")</td>" +
                                "<td class='lime-column'>" + not_visited + " (" + App.calculatePercentage(not_visited, structures) + ")</td>" +
                            "</tr>";
                        //Create a table

                    }
                    target_list.append(target_list_content);
                    target_table.append(target_table_content);
                    $("table#target_areas tbody").empty().append(target_table_content);
                    $("table#target_areas tfoot").empty().append(
                        "<tr><td> Totals </td>" +
                        "<td class='lime-column'><b>" + agg_structures + "</b></td>" +
                        "<td><b>" + agg_visited_total + " (" + App.calculatePercentage(agg_visited_total, agg_structures) + ")</b></td>" +
                        "<td class='lime-column'><b>" + agg_visited_sprayed + " (" + App.calculatePercentage(agg_visited_sprayed, agg_visited_total) + ")</b></td>" +
                        "<td><b>" + agg_visited_not_sprayed + " (" + App.calculatePercentage(agg_visited_not_sprayed, agg_visited_total) + ")</b></td>" +
                        "<td class='lime-column'><b>" + agg_visited_refused + " (" + App.calculatePercentage(agg_visited_refused, agg_visited_total) + ")</b></td>" +
                        "<td><b>" + agg_visited_other + " (" + App.calculatePercentage(agg_visited_other, agg_visited_total) + ")</b></td>" +
                        "<td class='lime-column'><b>" + agg_not_visited + " (" + App.calculatePercentage(agg_not_visited, agg_structures) + ")</b></td>" +
                        "</tr>"
                    );
                    $("table#target_areas").table().data( "table" ).refresh();
                    $("table#target_areas").table().sortable("sortBy", null, "asc");
                    $("h1#district-name").text("District:" + district_name);
                },
                error: function(){
                    // console.log('Sorry, could not retrieve target areas');
                }
            });
        },

        getTargetAreasAggregate: function(){
            $("h1#district-name").text("District: All");
            $("#target_areas thead tr th :first").text("DISTRICT");
            $("table#target_areas tbody, table#target_areas tfoot").empty();
            var total_agg_structures = 0,
                total_agg_visited_total = 0,
                total_agg_visited_sprayed = 0,
                total_agg_visited_not_sprayed = 0,
                total_agg_visited_refused = 0,
                total_agg_visited_other = 0,
                total_agg_not_visited = 0;
            for(var index in App.allDistricts){
                this.districtData(index, total_agg_structures, total_agg_visited_total, total_agg_visited_sprayed,
                                  total_agg_visited_not_sprayed, total_agg_visited_refused, total_agg_visited_other,
                                  total_agg_not_visited);
            }
        },
        districtData: function(index, total_agg_structures, total_agg_visited_total, total_agg_visited_sprayed,
                               total_agg_visited_not_sprayed, total_agg_visited_refused, total_agg_visited_other,
                               total_agg_not_visited) {
            var district_name = App.allDistricts[index],
                uri = App.DISTRICT_URI + "?district=" + district_name;
                $.ajax({
                    method: "get",
                    url: uri,
                    success: function(data) {
                        var agg_structures = 0,
                            agg_visited_total = 0,
                            agg_visited_sprayed = 0,
                            agg_visited_not_sprayed = 0,
                            agg_visited_refused = 0,
                            agg_visited_other = 0,
                            agg_not_visited = 0;

                        for(var c = 0; c < data.length; c++){
                            var list_data = data[c],
                                structures = list_data.structures,
                                visited_total = list_data.visited_total,
                                visited_sprayed = list_data.visited_sprayed,
                                visited_not_sprayed = list_data.visited_not_sprayed,
                                visited_refused = list_data.visited_refused,
                                visited_other = list_data.visited_other,
                                not_visited = list_data.not_visited, radix = 10;

                            agg_structures += parseInt(structures, radix);
                            agg_visited_total += parseInt(visited_total, radix);
                            agg_visited_sprayed += parseInt(visited_sprayed, radix);
                            agg_visited_not_sprayed += parseInt(visited_not_sprayed, radix);
                            agg_visited_refused += parseInt(visited_refused, radix);
                            agg_visited_other += parseInt(visited_other, radix);
                            agg_not_visited += parseInt(not_visited, radix);
                        }

                        total_agg_structures += agg_structures;
                        total_agg_visited_total += agg_visited_total;
                        total_agg_visited_sprayed += agg_visited_sprayed;
                        total_agg_visited_not_sprayed += agg_visited_not_sprayed;
                        total_agg_visited_refused += agg_visited_refused;
                        total_agg_visited_other += agg_visited_other;
                        total_agg_not_visited += agg_not_visited;

                        $("table#target_areas tbody").append(
                            "<tr><td><a href='/#!" + district_name + "' class='distrct-links'>" + district_name + "</a></td>" +
                            "<td class='lime-column'>" + agg_structures + "</td>" +
                            "<td>" + agg_visited_total + " (" + App.calculatePercentage(agg_visited_total, agg_structures) + ")</td>" +
                            "<td class='lime-column'>" + agg_visited_sprayed + " (" + App.calculatePercentage(agg_visited_sprayed, agg_visited_total) + ")</td>" +
                            "<td>" + agg_visited_not_sprayed + " (" + App.calculatePercentage(agg_visited_not_sprayed, agg_visited_total) + ")</td>" +
                            "<td class='lime-column'>" + agg_visited_refused + " (" + App.calculatePercentage(agg_visited_refused, agg_visited_total) + ")</td>" +
                            "<td>" + agg_visited_other + " (" + App.calculatePercentage(agg_visited_other, agg_visited_total) + ")</td>" +
                            "<td class='lime-column'>" + agg_not_visited + " (" + App.calculatePercentage(agg_not_visited, agg_structures) + ")</td>" +
                            "</tr>"
                        );

                        if (index === (App.allDistricts.length - 1)) {
                            $("table#target_areas tfoot").append(
                                "<tr><td><b>Grand Total</b></td>" +
                                "<td class='lime-column'><b>" + total_agg_structures + "</b></td>" +
                                "<td><b>" + total_agg_visited_total + " (" + App.calculatePercentage(total_agg_visited_total, total_agg_structures) + ")</b></td>" +
                                "<td class='lime-column'><b>" + total_agg_visited_sprayed + " (" + App.calculatePercentage(total_agg_visited_sprayed, total_agg_visited_total) + ")</b></td>" +
                                "<td><b>" + total_agg_visited_not_sprayed + " (" + App.calculatePercentage(total_agg_visited_not_sprayed, total_agg_visited_total) + ")</b></td>" +
                                "<td class='lime-column'><b>" + total_agg_visited_refused + " (" + App.calculatePercentage(total_agg_visited_refused, total_agg_visited_total) + ")</b></td>" +
                                "<td><b>" + total_agg_visited_other + " (" + App.calculatePercentage(total_agg_visited_other, total_agg_visited_total) + ")</b></td>" +
                                "<td class='lime-column'><b>" + total_agg_not_visited + " (" + App.calculatePercentage(total_agg_not_visited, total_agg_structures) + ")</b></td>" +
                                "</tr>"
                            );
                            $("table#target_areas").table().data( "table" ).refresh();
                            $("table#target_areas").table().sortable("sortBy", null, "asc");
                            $("h1#district-name").text("District: All");
                        }
                    }
                });
        },
        getResource: function() {
            var url = document.location.hash,
                fragment = url.split("/"),
                district = (url.length === 0) ? App.defaultDistrict : fragment[0].substring(2, fragment[0].length),
                target_id = (fragment[1] === undefined) ? App.defaultTargetArea : fragment[1];
            return {
                "district": district,
                "target_id": target_id
            };
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
            var uri = App.TARGET_AREA_URI + "?target_area=" + targetid;
            $.getJSON(uri, function(data){
                if(data.length > 0){
                    $("#target-area-stats").empty().append(
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
                        "<dt class='reason total-structures'>" + data[0].structures + "</dt>" +
                        "<dd>Structures</dd>"
                    );
                    $("#target-area-label").text("Target Area : " + targetid);

                    App.housesCount = data[0].structures;
                    App.visitedTotal = data[0].visited_total;

                    var bounds = data[0].bounds;
                    if(bounds.length === 4){
                        var minL = L.latLng(bounds[1], bounds[0]),
                            maxL = L.latLng(bounds[3], bounds[2]);
                        var lat_bounds = L.latLngBounds(minL, maxL);
                        map.fitBounds(lat_bounds);
                    }
                }
            });

            if(targetid !== "XXXXX"){
                var target_area = L.mapbox.featureLayer()
                    .loadURL(uri.replace(".json", ".geojson"));

                // console.log('TARGET_AREA_URI: ' + App.TARGET_AREA_URI + "?target_area=" + targetid);

                target_area.on("ready", function(){
                    var bounds = target_area.getBounds();
                    map.fitBounds(bounds);
                    var geojson = target_area.getGeoJSON();

                    this.targetLayer = [];

                    this.targetLayer = L.geoJson(geojson, {
                        onEachFeature: function(feature, layer){
                            var props = feature.properties;
                            var content = "<h4>Target Area: " + props.targetid + "</h4>" +
                                "Structures: " + props.structures;

                            layer.bindPopup(content, {closeButton: true});

                            // console.log("Spray data: " + props.structures);
                            var label = new L.Label({className: "ta-label"});
                            label.setContent("" + props.targetid);
                            label.setLatLng(layer.getBounds().getCenter());
                            map.showLabel(label);
                            k = label;
                        }
                    });

                    target_area.setStyle(App.targetOptions);
                }).addTo(map);
            }

            $("#circle-refused").text("0%");
            $("#circle-other").text("0%");
            App.drawCircle(0, "circle-sprayed");

        },

        loadBufferAreas: function(map, targetid, day) {
            if(targetid === undefined){
                return;
            }
            var url = App.BUFFER_URI + "?target_area=" + targetid;
            if(day !== undefined){
                url += "&spray_date=" + day;
            }
            var hh_buffers = L.mapbox.featureLayer().loadURL(url);

            // console.log(url);

            if (App.bufferLayer !== undefined) {
                App.map.removeLayer(App.bufferLayer); // reset layer
            }

            hh_buffers.on("ready", function(){
                var geojson = hh_buffers.getGeoJSON();
                // bounds = hh_buffers.getBounds();
                // map.fitBounds(bounds);

                App.bufferLayer = L.geoJson(geojson, {
                    pointToLayer: function (feature, latlng) {
                        return L.circleMarker(latlng, App.hhOptions);
                    },
                    style: function(feature) {
                        App.bufferOptions.fillColor = feature.style.fillColor;

                        return App.bufferOptions;
                    },
                    onEachFeature: function(feature, layer){
                        var content = "<h4>" + feature.properties.percentage_sprayed + "% (" + feature.properties.spray_points + "/" + feature.properties.num_households + ") Found </h4>";
                        layer.bindPopup(content, {closeButton: true});

                        layer.on({
                            mouseover: function(e){
                                e.target.setStyle( {fillOpacity: 0.7} );
                            },
                            mouseout: function(e){
                                e.target.setStyle({fillOpacity: 0.4});
                            }
                        });
                    }
                }).addTo(map);

                App.bufferLayer.setZIndex(60);
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
            if(targetid === "909001"){
                var households = L.mapbox.featureLayer().loadURL(uri);

                // console.log('HOUSEHOLD_URI: ' + App.HOUSEHOLD_URI + "?target_area=" + targetid);

                this.hhLayer = []; //reset layer

                households.on("ready", function(){
                    var geojson = households.getGeoJSON();

                    this.hhLayer = L.geoJson(geojson, {
                        pointToLayer: function (feature, latlng) {
                            return L.circleMarker(latlng, App.hhOptions);
                        },
                        onEachFeature: function(feature, layer){
                            // increment no. of households
                            App.housesCount++;

                            // var content = "<h4>" + feature.properties.orig_fid + "</h4>" +
                            //     "HH_type: " + feature.properties.hh_type;
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

        loadSprayPoints: function (map, targetid, day) {
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
                    "sick": "sick",
                    "locked": "locked",
                    "funeral": "funeral",
                    "refused": "refused",
                    "no one home/missed": "no one home/missed",
                    "other": "other"
                },
                // reason_colors = {
                //     "sick": "#800080",
                //     "locked": "#FFA500",
                //     "funeral": "#1B11E1",
                //     "refused": "#D05B5B",
                //     "no one home/missed": "#C27344",
                //     "other": "#6C696B"
                // },
                target_area_stats = "";


            // console.log('SPRAYPOINT_URI: ' + url);

            App.map.removeLayer(App.sprayLayer); // reset layer

            sprayed.on("ready", function(){
                var geojson = sprayed.getGeoJSON();
                App.sprayCount = 0; // reset counter

                App.sprayLayer = L.geoJson(geojson, {
                    pointToLayer: function (feature, latlng) {
                        if(feature.properties.sprayed === "no"){
                            // App.sprayOptions.fillColor = reason_colors[feature.properties.reason];
                            App.sprayOptions.fillColor = "#D82118";
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


                $("#target-area-stats-structures").empty().append(
                    "<dt class='reason structures'>" + ((App.housesCount === undefined) ? 0 : App.housesCount) + "</dt><dd>Structures</dd>"
                );

                target_area_stats += "<dt class='reason reason-sprayed'>" + ((sprayed_status.yes === undefined) ? 0 : sprayed_status.yes) + "</dt><dd>Sprayed</dd>";
                target_area_stats += "<dt class='reason reason-not-sprayed'>" + ((sprayed_status.no === undefined) ? 0 : sprayed_status.no) + "</dt><dd>Not Sprayed</dd>";
                $("#target-area-stats").empty().append(target_area_stats);

                target_area_stats = "";
                var total_of_other = 0;
                $.each(reasons, function(key, value) {
                    target_area_stats += "<dt class='reason reason-" + value.replace(/ /g, "-");
                    if (reason_obj[value]){
                        target_area_stats += "'>" + reason_obj[value] + "</dt><dd>" + value + "</dd>";
                        if (value !== "refused") {
                            total_of_other += reason_obj[value];
                        }
                    } else {
                        target_area_stats += "'>0</dt><dd >" + value + "</dd>";
                    }
                });
                // console.log("target area stats: " + target_area_stats);
                $("#target-area-stats-not-sprayed").empty().append(target_area_stats);
                $("#not-sprayed-reasons").show();

                App.sprayLayer.setZIndex(80);

                $(".perc_label").text(App.sprayCount);

                var sprayed_percentage = App.calculatePercentage(sprayed_status.yes, App.visitedTotal, false),
                    refused_percentage = App.calculatePercentage(reason_obj.refused, App.visitedTotal),
                    other_percentage = App.calculatePercentage(total_of_other, App.visitedTotal);

                // console.log('SPRAY: ' + sprayed_status.yes + ' / VISTED: '+ App.visitedTotal + ' = ' + sprayed_percentage);

                App.drawCircle(sprayed_percentage, "circle-sprayed");
                $("#sprayed-ratio").text("(" + sprayed_status.yes + "/" + App.visitedTotal + ")");
                $("#circle-refused").text(refused_percentage);
                $("#circle-other").text(other_percentage);
            });

        },

        loadAreaData: function(map, targetid){
            this.loadTargetArea(map, targetid);
            this.loadBufferAreas(map, targetid);
            this.loadHouseholds(map, targetid);
            this.loadSprayPoints(map, targetid, "");
        },

        drawCircle: function(percent, circle_id) {
            var fillColor;
            if(percent < 30){
                fillColor = "#FFA500";
            }
            else if(percent >= 30 && percent < 40){
                fillColor = "#FFFFCC";
            }
            else if(percent >= 40 && percent < 80){
                fillColor = "#C2E699";
            }
            else if(percent >= 80 && percent < 90){
                fillColor = "#78C679";
            }
            else if(percent >= 90 && percent <= 100){
                fillColor = "#31A354";
            }

            Circles.create({
                id: circle_id,
                percentage: parseInt(" " + percent, 10),
                radius: 50,
                width: 12,
                number: percent,
                text: "%",
                colors: ["#AAAAAA", fillColor],
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
                        return $(this).text().toLowerCase().indexOf(filterText) >= 1;
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
                bing = new L.BingLayer("AuOGADooQT2MGfigXZmbgIOJ_Jts7glmpRAAWZU9WHYfvPFFZp0lmxqV5T86RVt6"),
                bufferHouseholdsLayer = L.mapbox.tileLayer("ona.j6c49d56");

            App.map = L.mapbox.map("map");
            App.map.locate({ enableHighAccuracy: true });
            App.map.addLayer(google);
            App.map.addLayer(bufferHouseholdsLayer);
            L.control.layers({
                "Google": google,
                "Bing": bing
            }, {
                "buffershouseholds": bufferHouseholdsLayer
            }).addTo(App.map);
            // var locateOptions = {
            //     remainActive: true,
            //     locateOptions: {
            //         enableHighAccuracy: true,
            //         maximumAge: 0,
            //         watch: true
            //     }
            // };
            L.control.locate().addTo(App.map);
            L.control.scale({
                position: "bottomright"
            }).addTo(App.map);
            App.map.options.maxZoom = 19;
            // TODO: show legend optional config
            // App.buildLegend(App.map);
        },

        getPageState: function(){
            var current_district = this.getCurrentDistrict();
            var current_target_area = this.getCurrentTargetArea();

            $("#target-area-label").text("Target Area : " + current_target_area);
            $(".target_label").text("Target Area : " + current_target_area);

            if(current_target_area !== this.defaultTargetArea){
                App.loadMap();
                $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").show();
                App.loadAreaData(App.map, current_target_area);
                // console.log("Loading map for target", current_target_area);
            } else {
                // Check if url has a district name
                if (location.href.indexOf("#!") >= 0) {
                    this.getTargetAreas(current_district);
                }
            }
        },

        buildLegend: function(map) {
            var legend = L.control({
                position: "bottomright"
            });

            if (legend.getContainer() !== undefined) {
                legend.removeFrom(map);
            }

            legend.onAdd = function () {
                var div = L.DomUtil.create("div", "info legend"),
                    labels = [];
                labels.push("<i style='background:#2ECC40'></i> 100%");
                labels.push("<i style='background:#FFDC00'></i> 66-99% ");
                labels.push("<i style='background:#FF851B'></i> 33-66% ");
                labels.push("<i style='background:#FF4136'></i> 1-33% ");
                labels.push("<i style='background:#CCCCCC'></i> 0%");
                div.innerHTML = labels.join("<br><br>");

                return div;
            };

            legend.addTo(map);
        },

        init: function (){
            $(document).ready(function(){
                var set_target_id, fragment, target_id,
                    infopanel = $(".info-panel");

                L.mapbox.accessToken = "pk.eyJ1Ijoib25hIiwiYSI6IlVYbkdyclkifQ.0Bz-QOOXZZK01dq4MuMImQ";
                $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").hide();

                // load page info
                App.getDistricts();
                App.getDates();
                App.getPageState();

                App.drawCircle(0, "circle-sprayed");
                $("#circle-refused").text("0%");
                $("#circle-other").text("0%");

                App.searchInit();

                $(document).ajaxComplete(function(){
                    $("#target_areas_list li a, #target_areas a").click(function(){
                        fragment = this.href.split("#!")[1];

                        // Check if link has a target area segment
                        if (fragment.indexOf("/") > 0) {
                            // If it does, load map
                            target_id = fragment.split("/")[1];

                            $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").show();
                            $("#not-sprayed-reasons").hide();
                            App.loadMap();
                            $("#district_table").hide();

                            if (target_id !== set_target_id) {
                                set_target_id = target_id;
                                $(".target_label").text("Target Area : " + target_id);
                                App.loadAreaData(App.map, target_id);
                                // console.log("Loading map for target", target_id);
                            }
                        } else {
                            // If it doesn't, the link should load a district table based on the district
                            $(".info-toggle").hide();
                            $(".info-panel").hide();

                            $("#map, #spray_date_picker, #map-legend, #target-area-stats-item").hide();
                            $("#district_table").show();

                            $(".dist_label").text("District : " + fragment);
                            $(".target_label").text("Target Area: Select");

                            App.getTargetAreas(fragment);
                        }
                    });

                });
                $("#target-area-stats-item").on("click", function() {
                    infopanel.toggle();
                });

            });
        },

        load_spray_days_by_date: function(event){
            event.preventDefault();
            var sprayday = this.href.split("#")[1], dt, dt_label;

            App.loadSprayPoints(App.map, App.getCurrentTargetArea(), sprayday);
            App.loadBufferAreas(App.map, App.getCurrentTargetArea(), sprayday);

            if (sprayday === "") {
                $(".sprayday_label").text("All");
                $(".day_label").text("All");
            } else {
                dt = new Date(sprayday);
                dt_label = dt.toLocaleDateString();
                $(".sprayday_label").text(dt_label);
                $(".day_label").text(dt_label);
            }
        }
    };

    App.init();
})();
