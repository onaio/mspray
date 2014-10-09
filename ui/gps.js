var watchId, output = document.getElementById("output");


function success(position){
    console.log(position);
    var position_str = "Latitude: " + position.coords.latitude + " Longitude: " + position.coords.longitude + " Altitude: " + position.coords.altitude + " Accuracy: " + position.coords.accuracy.toFixed() + " metres <br />";
    output.innerHTML = position_str;
    var img = new Image();
    img.src = "http://maps.googleapis.com/maps/api/staticmap?center=" + position.coords.latitude + "," + position.coords.longitude + "&zoom=16&size=300x300&sensor=false&markers=colors:blue|label:P|" + position.coords.latitude + "," + position.coords.longitude;
    output.appendChild(img);

    if(position.coords.accuracy < 15){
        navigator.geolocation.clearWatch(watchId);
    }
}


function error(err){
    console.warn('ERROR(' + err.code + '): ' + err.message);
}
if("geolocation" in navigator){
    watchId = navigator.geolocation.watchPosition(success, error, {enableHighAccuracy: true, maximumAge: 0});
    output.innerHTML = "Geolocation is available!";
} else {
    output.innerHTML = "Geolocation is NOT AVAILABLE!";
}
