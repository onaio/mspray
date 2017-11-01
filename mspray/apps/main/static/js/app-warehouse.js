/* global L, $, Circles */
var App = function(buffer, targetAreaData, hhData, notSpraybleValue) {
    "use strict";
    this.targetOptions = {
        fillColor: "#999999",
        color: "#FFFFFF",
        weight: 3,
        fillOpacity: 0.1,
        opacity: 1
    };
    this.hhOptions = {
        radius: 4,
        fillColor: "#FFDC00",
        color: "#222",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    };
    this.bufferOptions = {
        weight: 3,
        color: "#fff",
        dashArray: "",
        fillOpacity: 0.4
    };
    this.sprayOptions = {
        radius: 4,
        fillColor: "#2ECC40",
        color: "#222",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    };
    this.WAS_NOT_SPRAYABLE = notSpraybleValue;

    L.mapbox.accessToken = "pk.eyJ1Ijoib25hIiwiYSI6IlVYbkdyclkifQ.0Bz-QOOXZZK01dq4MuMImQ";
    this.map = L.mapbox.map("map");
    var bufferHouseholdsLayer = L.mapbox.tileLayer("ona.j6c49d56")
        , google = new L.Google()
        , bing = new L.BingLayer("Alt-3s6hwEWPw-f2IKRw3Fg4qsV1BItu4KbylMsVKY7jyWFGkT5D10Qntw9xr6MX", {type: "Aerial"});
    this.map.addLayer(google);
    if(buffer !== undefined) {
        this.map.addLayer(bufferHouseholdsLayer);
        this.map.addControl(new L.control.layers({
            "Google": google,
            "Bing": bing
        }, {
            "Households Buffer": bufferHouseholdsLayer
        }));
    } else {
         this.map.addControl(new L.control.layers({
            "Google": google,
            "Bing": bing
        }));
    }

    this.buildLegend = function() {
        var legend = L.control({
            position: "bottomright"
        });

        if (legend.getContainer() !== undefined) {
            legend.removeFrom(this.map);
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

        legend.addTo(this.map);
    };

    this.calculatePercentage = function(numerator, denominator, include_sign) {
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
    };

    this.getFillColor = function (percent) {
        var fillColor;
        if(percent < 20){
            fillColor = "#FFA500";
        }
        else if(percent >= 20 && percent < 40){
            fillColor = "#FFFFCC";
        }
        else if(percent >= 40 && percent < 75){
            fillColor = "#C2E699";
        }
        else if(percent >= 75 && percent < 85){
            fillColor = "#78C679";
        }
        else if(percent >= 85 && percent <= 100){
            fillColor = "#31A354";
        }
        return fillColor;
    };

    this.drawCircle = function(percent, circle_id, radius) {
        var fillColor = this.getFillColor(percent);
        radius = radius === undefined ? 50 : radius;
        Circles.create({
            id: circle_id,
            value: parseInt(" " + percent, 10),
            radius: radius,
            width: 12,
            maxValue: 100,
            text: function(value){return value + "%"; },
            colors: ["#AAAAAA", fillColor],
            duration: 200
        });
    };

    this.fitBounds = function(bounds) {
        if(bounds.length === 4){
            var minL = L.latLng(bounds[1], bounds[0]),
                maxL = L.latLng(bounds[3], bounds[2]);
            this.map.fitBounds(L.latLngBounds(minL, maxL));
        }
    };

    this.loadSprayPoints = function (url, day) {
        var app = this;
        if(day !== undefined){
            url = url += "&spray_date=" + day;
        }
        var sprayed = L.mapbox.featureLayer().loadURL(url),
            sprayed_status = {}, reason_obj = {},
            reasons = {
            "S": "sick",
            "L": "locked",
            "F": "funeral",
            "R": "refused",
            "M": "no one home/missed",
            "O": "other"
        },
        reasons_keys = ["S", "L", "F", "R", "M", "O"],
        target_area_stats = "";
        app.kk = [];
        sprayed.on("ready", function(){
            var geojson = sprayed.getGeoJSON();
            app.k = geojson;
            app.sprayCount = 0; // reset counter
            app.sprayData = geojson;
            var reasonCounter = function(key, data) {
                return data.filter(function(k, v) {
                    return k.properties.reason !== null && k.properties.sprayed == app.WAS_NOT_SPRAYED_VALUE;
                }) .reduce(function(k, v){
                    return v.properties.reason === key ? k + 1: k;
                }, 0);
            }, key, i;
            for(i = 0; i < reasons_keys.length; ++i) {
                key = reasons_keys[i];
                reason_obj[reasons[key]] = reasonCounter(key, geojson.features);
            }

            // geojson.features.filter(function(k, v){ return k.properties.reason !== null}) .reduce(function(k, v){return v.properties.reason === 'R' ? k + 1: k + 0}, 0)
            if(geojson.features !== undefined && geojson.features.length > 0) {
                app.sprayLayer = L.geoJson(geojson, {
                    pointToLayer: function (feature, latlng) {
                        if(feature.properties.sprayed === app.WAS_SPRAYED_VALUE){
                            app.sprayOptions.fillColor = "#D82118";
                        } else if (feature.properties.sprayed === app.WAS_NOT_SPRAYABLE) {
                            app.sprayOptions.fillColor = "#000000";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return L.circleMarker(latlng, app.sprayOptions);
                    },
                    style: function (feature) {
                        if(feature.properties.sprayed === app.WAS_NOT_SPRAYED_VALUE){
                            app.sprayOptions.fillColor = "#D82118";
                        } else if (feature.properties.sprayed === app.WAS_NOT_SPRAYABLE) {
                            app.sprayOptions.fillColor = "#000000";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return app.sprayOptions;
                    },
                    onEachFeature: function(features){
                        var was_sprayed = features.properties.sprayed;
                        if (sprayed_status[features.properties.sprayed] === undefined) {
                            sprayed_status[features.properties.sprayed] = 1;
                        } else {
                            sprayed_status[features.properties.sprayed]++;
                        }

                    }
                }).addTo(app.map);

                app.map.fitBounds(app.sprayLayer.getBounds());
                app.duplicateLayer = L.geoJson(geojson, {
                    pointToLayer: function (feature, latlng) {
                        if(feature.properties.sprayed === app.WAS_SPRAYED_VALUE){
                            app.sprayOptions.fillColor = "#D82118";
                        } else if (feature.properties.sprayed === app.WAS_NOT_SPRAYABLE) {
                            app.sprayOptions.fillColor = "#000000";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return L.circleMarker(latlng, app.sprayOptions);
                    },
                    style: function (feature) {
                        // console.log(feature.properties.sprayed);
                        if(feature.properties.sprayed === app.WAS_NOT_SPRAYED_VALUE){
                            app.sprayOptions.fillColor = "#D82118";
                        } else if (feature.properties.sprayed === app.WAS_NOT_SPRAYABLE) {
                            app.sprayOptions.fillColor = "#000000";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return app.sprayOptions;
                    },
                    filter: function(feature) {
                        var i, duplicates = app.sprayedDuplicatesData !== undefined ? app.sprayedDuplicatesData : [];

                        for(i =0; i < duplicates.length; i++){
                            if(feature.properties.osmid === duplicates[i].osmid) {
                                return true;
                            }
                        }

                        duplicates = app.notSprayedDuplicatesData !== undefined ? app.notSprayedDuplicatesData : [];

                        for(i =0; i < duplicates.length; i++){
                            if(feature.properties.osmid === duplicates[i].osmid) {
                                return true;
                            }
                        }

                        return false;
                    }
                });
            }

            $("#target-area-stats-structures").empty().append(
                "<dt class='reason structures'>" + ((app.housesCount === undefined) ? 0 : app.housesCount) + "</dt><dd>Structures</dd>"
            );
            target_area_stats += "<dt class='reason reason-sprayed'>" + ((app.visitedSprayed === undefined) ? 0 : app.visitedSprayed) + "</dt><dd>Sprayed</dd>";
            target_area_stats += "<dt class='reason reason-not-sprayed'>" + ((app.visitedNotSprayed === undefined) ? 0 : app.visitedNotSprayed) + "</dt><dd>Not Sprayed</dd>";
            $("#target-area-stats").empty().append(target_area_stats);

            target_area_stats = "";
            var total_of_other = 0;
            $.each(reasons, function(key, value) {
                target_area_stats += "<dt class='reason";  //  reason-" + value.replace(/ /g, "-");
                if (reason_obj[value]){
                    target_area_stats += "'>" + reason_obj[value] + "</dt><dd>" + value + "</dd>";
                    if (value !== "refused") {
                        total_of_other += reason_obj[value];
                    }
                } else {
                    target_area_stats += "'>0</dt><dd >" + value + "</dd>";
                }
            });

            $("#target-area-stats-not-sprayed").empty().append(target_area_stats);
            $("#not-sprayed-reasons").show();

            $(".perc_label").text(app.sprayCount);

            var sprayed_percentage = app.calculatePercentage(app.visitedSprayed, app.visitedTotal, false),
                refused_percentage = app.calculatePercentage(app.visitedRefused, app.visitedTotal),
                other_percentage = app.calculatePercentage(app.visitedOther, app.visitedTotal),
                found_percentage = app.calculatePercentage(app.visitedTotal, app.housesCount, false),
                progress_percentage = app.calculatePercentage(app.visitedSprayed, app.housesCount, false);
            app.drawCircle(sprayed_percentage, "spray-coverage", 40);
            app.drawCircle(found_percentage, "found-coverage", 40);
            app.drawCircle(progress_percentage, "circle-progress", 50);
            if(geojson.features !== undefined && geojson.features.length > 0) {
                $("#sprayed-ratio").text("(" + app.visitedSprayed + "/" + app.visitedTotal + ")");
                $("#found-ratio").text("(" + app.visitedTotal + "/" + app.housesCount + ")");
                $("#progress-ratio").text("(" + app.visitedSprayed + "/" + app.housesCount + ")");
            }

            $("#target-area-stats-item").on("click", function() {
                $(".info-panel").toggle();
            });
            $("#sprayed-duplicates").on("click", function(e) {
                e.preventDefault();
                app.showDupes = app.showDupes !== true;
                if(app.showDupes) {
                    app.map.removeLayer(app.sprayLayer);
                    app.map.addLayer(app.duplicateLayer);
                    $("#sprayed-duplicates").html("Show all");
                } else {
                    app.map.removeLayer(app.duplicateLayer);
                    app.map.addLayer(app.sprayLayer);
                    $("#sprayed-duplicates").html("Show Duplicates");
                }
                return false;
            });
        });
    };

    this.loadBufferAreas = function(url, day, showLegend) {
        var app = this;

        showLegend = showLegend === undefined ? true : showLegend;

        if(day !== undefined){
            url += "&spray_date=" + day;
        }
        var hh_buffers = L.mapbox.featureLayer().loadURL(url);


        if (app.bufferLayer !== undefined) {
            app.map.removeLayer(app.bufferLayer); // reset layer
        }

        hh_buffers.on("ready", function(){
            var geojson = hh_buffers.getGeoJSON();

            app.bufferLayer = L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, app.hhOptions);
                },
                style: function(feature) {
                    app.bufferOptions.fillColor = feature.style.fillColor;

                    return app.bufferOptions;
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
            }).addTo(app.map);

            if(app.sprayLayer !== undefined) {
                app.sprayLayer.bringToFront();
            }

            if(showLegend) {
                app.buildLegend();
            }
        });
    };

    this.drawCircles = function (props) {
        var app = this, structures = props.level == 'ta' ? props.structures : props.total_structures;
        var sprayed_percentage = app.calculatePercentage(props.visited_sprayed, props.visited_total, false),
            found_percentage = app.calculatePercentage(props.visited_total, structures, false),
            progress_percentage = app.calculatePercentage(props.visited_sprayed, structures, false);
        app.drawCircle(sprayed_percentage, "spray-coverage", 40);
        app.drawCircle(found_percentage, "found-coverage", 40);
        app.drawCircle(progress_percentage, "circle-progress", 50);
        $("#sprayed-ratio").text("(" + props.visited_sprayed + "/" + props.visited_total + ")");
        $("#found-ratio").text("(" + props.visited_total + "/" + structures + ")");
        $("#progress-ratio").text("(" + props.visited_sprayed + "/" +structures + ")");
    };

    this.loadTargetArea = function(data) {
        var app = this,
            geojson = data;
        app.targetAreaData = data;
        app.targetLayer = L.geoJson(geojson, {
            onEachFeature: function(feature, layer){
                var props = feature.properties;
                if (props.label) {
                    var this_label = props.label;
                } else {
                    var this_label = props.district_name;
                }
                var content = "<h4>Target Area: " + this_label + "</h4>" +
                    "Structures: " + props.structures;
                layer.bindPopup(content, {closeButton: true});
                var label = new L.Label({className: "ta-label"});
                label.setContent(this_label);
                label.setLatLng(layer.getBounds().getCenter());
                app.map.showLabel(label);
                if (props.level != 'ta') {
                    app.drawCircles(props);
                }
            }
        });
        app.targetLayer.setStyle(app.targetOptions);
        app.targetLayer.addTo(app.map);
        app.map.fitBounds(app.targetLayer.getBounds());
    };

    this.loadHouseholds = function(data) {
        var app = this,
            geojson = data;
        app.hhLayer = L.geoJson(geojson, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, app.hhOptions);
            },
            style: function(feature) {
                var props = feature.properties;
                if(props.visited_total !== undefined && props.visited_total > 0){
                    var percent = app.calculatePercentage(props.visited_sprayed, props.structures, false);
                    app.hhOptions.fillColor = app.getFillColor(percent);
                } else {
                    app.hhOptions.fillColor = '#FFDC00';
                }
                app.hhOptions.fillOpacity = 0.4;
                return app.hhOptions;
            },
            onEachFeature: function(feature, layer){
                var props = feature.properties;
                if(props.level !== undefined) {
                    var content;
                    if (props.label) {
                        var this_label = props.label;
                    } else {
                        var this_label = props.district_name;
                    }
                    if (props.level === 'RHC') {
                        content = this_label + "<br/>" +
                            "Number of spray areas: " + props.total_structures + "<br/>" +
                            "Spray areas Visited: " + props.visited_total + "<br/>" +
                            "Spray areas Sprayed: " + props.visited_sprayed+ "<br/>" +
                            "Spray areas NOT Sprayed: " + props.visited_not_sprayed;
                    } else {
                        content = this_label + "<br/>" +
                            "Structures: " + props.structures + "<br/>" +
                            "Visited Total: " + props.visited_total + "<br/>" +
                            "Sprayed: " + props.visited_sprayed + "<br/>" +
                            "Not Sprayed: " + props.visited_not_sprayed;
                    }

                    layer.bindPopup(content, {closeButton: true});
                    // var label = new L.Label();
                    var label = new L.Label({className: "hh-label"});
                    label.setContent(this_label);
                    label.setLatLng(layer.getBounds().getCenter());
                    app.map.showLabel(label);
                    layer.on({
                        click: function(e) {
                            var uri = props.url;
                            window.location.href = uri;
                        },
                        mouseover: function(e){
                            // e.layer.openPopup();
                        },
                        mouseout: function(e){
                            // e.layer.closePopup();
                        }
                    });
                }
            }
        });
        // app.hhLayer.setStyle(app.hhOptions);
        app.hhLayer.addTo(app.map);
    };

    if ( targetAreaData !== undefined ) {
        this.loadTargetArea(targetAreaData);
    }
    if ( hhData !== undefined ) {
        this.loadHouseholds(hhData);
    }
};