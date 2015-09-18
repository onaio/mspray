/* global L, $, Circles */
var App = function(buffer, targetAreaData, hhData) {
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
    L.control.locate().addTo(this.map);

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

    this.drawCircle = function(percent, circle_id) {
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
            value: parseInt(" " + percent, 10),
            radius: 50,
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
            "sick": "sick",
            "locked": "locked",
            "funeral": "funeral",
            "refused": "refused",
            "no one home/missed": "no one home/missed",
            "other": "other"
        },
        target_area_stats = "";
        sprayed.on("ready", function(){
            var geojson = sprayed.getGeoJSON();
            app.k = geojson;
            app.sprayCount = 0; // reset counter

            if(geojson.features !== undefined && geojson.features.length > 0) {
                app.sprayLayer = L.geoJson(geojson, {
                    pointToLayer: function (feature, latlng) {
                        if(feature.properties.sprayed === "no"){
                            app.sprayOptions.fillColor = "#D82118";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return L.circleMarker(latlng, app.sprayOptions);
                    },
                    style: function (feature) {
                        if(feature.properties.sprayed === "no"){
                            app.sprayOptions.fillColor = "#D82118";
                        } else{
                            app.sprayOptions.fillColor = "#2ECC40";
                        }
                        return app.sprayOptions;
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
                .addTo(app.map);
                app.map.fitBounds(app.sprayLayer.getBounds());
            }

            $("#target-area-stats-structures").empty().append(
                "<dt class='reason structures'>" + ((app.housesCount === undefined) ? 0 : app.housesCount) + "</dt><dd>Structures</dd>"
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

            $("#target-area-stats-not-sprayed").empty().append(target_area_stats);
            $("#not-sprayed-reasons").show();

            $(".perc_label").text(app.sprayCount);

            var sprayed_percentage = app.calculatePercentage(sprayed_status.yes, app.visitedTotal, false),
                refused_percentage = app.calculatePercentage(reason_obj.refused, app.visitedTotal),
                other_percentage = app.calculatePercentage(total_of_other, app.visitedTotal);

            app.drawCircle(sprayed_percentage, "circle-sprayed");
            if(geojson.features !== undefined && geojson.features.length > 0) {
                $("#sprayed-ratio").text("(" + sprayed_status.yes + "/" + app.visitedTotal + ")");
                $("#circle-refused").text(refused_percentage);
                $("#circle-other").text(other_percentage);
            }

            $("#target-area-stats-item").on("click", function() {
                $(".info-panel").toggle();
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

    this.loadTargetArea = function(data) {
        var app = this,
            geojson = data;
        app.targetLayer = L.geoJson(geojson, {
            onEachFeature: function(feature, layer){
                var props = feature.properties;
                var content = "<h4>Target Area: " + props.targetid + "</h4>" +
                    "Structures: " + props.structures;
                layer.bindPopup(content, {closeButton: true});
                var label = new L.Label({className: "ta-label"});
                label.setContent("" + props.targetid);
                label.setLatLng(layer.getBounds().getCenter());
                app.map.showLabel(label);
            }
        });
        app.targetLayer.setStyle(app.targetOptions);
        app.targetLayer.addTo(app.map);
    };

    this.loadHouseholds = function(data) {
        var app = this,
            geojson = data;
        app.hhLayer = L.geoJson(geojson, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, app.hhOptions);
            },
            onEachFeature: function(feature, layer){
                layer.on({
                    mouseover: function(e){
                        e.layer.openPopup();
                    },
                    mouseout: function(e){
                        e.layer.closePopup();
                    }
                });
            }
        });
        app.hhLayer.setStyle(app.hhOptions);
        app.hhLayer.addTo(app.map);
    };

    if ( targetAreaData !== undefined ) {
        this.loadTargetArea(targetAreaData);
    }
    if ( hhData !== undefined ) {
        this.loadHouseholds(hhData);
    }
};
