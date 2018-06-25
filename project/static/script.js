// Google Map
var map;

// markers for map
var markers = [];
var endmark=null;

// info window
var info = new google.maps.InfoWindow();



$(document).ready(()=>{
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        $('#map-canvas').prepend('<p>Geolocation is not supported by this browser.</p>');
    }
});


function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            $('#map-canvas').prepend('<p>User denied the request for Geolocation.</p>');
            break;
        case error.POSITION_UNAVAILABLE:
            $('#map-canvas').prepend('<p>Location information is unavailable.</p>');
            break;
        case error.TIMEOUT:
            $('#map-canvas').prepend('<p>The request to get user location timed out.</p>');
            break;
        case error.UNKNOWN_ERROR:
            $('#map-canvas').prepend('<p>An unknown error occurred.</p>');
            break;
    }
}

// execute when the DOM is fully loaded
function showPosition(position) {
    // styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    var styles = [

        {
    elementType: "geometry",
    stylers: [
      {
        color: "#ebe3cd"
      }
    ]
  },
  {
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#523735"
      }
    ]
  },
  {
    elementType: "labels.text.stroke",
    stylers: [
      {
        color: "#f5f1e6"
      }
    ]
  },
  {
    featureType: "administrative",
    elementType: "geometry.stroke",
    stylers: [
      {
        color: "#c9b2a6"
      }
    ]
  },
  {
    featureType: "administrative.land_parcel",
    elementType: "geometry.stroke",
    stylers: [
      {
        color: "#dcd2be"
      }
    ]
  },
  {
    featureType: "administrative.land_parcel",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#ae9e90"
      }
    ]
  },
  {
    featureType: "landscape.natural",
    elementType: "geometry",
    stylers: [
      {
        color: "#dfd2ae"
      }
    ]
  },
  {
    featureType: "poi",
    elementType: "geometry",
    stylers: [
      {
        color: "#dfd2ae"
      }
    ]
  },
  {
    featureType: "poi",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#93817c"
      }
    ]
  },
  {
    featureType: "poi.park",
    elementType: "geometry.fill",
    stylers: [
      {
        color: "#a5b076"
      }
    ]
  },
  {
    featureType: "poi.park",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#447530"
      }
    ]
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [
      {
        color: "#f5f1e6"
      }
    ]
  },
  {
    featureType: "road.arterial",
    elementType: "geometry",
    stylers: [
      {
        color: "#fdfcf8"
      }
    ]
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [
      {
        color: "#f8c967"
      }
    ]
  },
  {
    featureType: "road.highway",
    elementType: "geometry.stroke",
    stylers: [
      {
        color: "#e9bc62"
      }
    ]
  },
  {
    featureType: "road.highway.controlled_access",
    elementType: "geometry",
    stylers: [
      {
        color: "#e98d58"
      }
    ]
  },
  {
    featureType: "road.highway.controlled_access",
    elementType: "geometry.stroke",
    stylers: [
      {
        color: "#db8555"
      }
    ]
  },
  {
    featureType: "road.local",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#806b63"
      }
    ]
  },
  {
    featureType: "transit.line",
    elementType: "geometry",
    stylers: [
      {
        color: "#dfd2ae"
      }
    ]
  },
  {
    featureType: "transit.line",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#8f7d77"
      }
    ]
  },
  {
    featureType: "transit.line",
    elementType: "labels.text.stroke",
    stylers: [
      {
        color: "#ebe3cd"
      }
    ]
  },
  {
    featureType: "transit.station",
    elementType: "geometry",
    stylers: [
      {
        color: "#dfd2ae"
      }
    ]
  },
  {
    featureType: "water",
    elementType: "geometry.fill",
    stylers: [
      {
        color: "#b9d3c2"
      }
    ]
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [
      {
        color: "#92998d"
      }
    ]
  }

    ];

    // options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    var options = {
        center: {lat:position.coords.latitude, lng: position.coords.longitude},
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 14,
        panControl: true,
        gestureHandling: 'greedy',
        styles: styles,
        zoom: 13,
        zoomControl: false,
        streetViewControl: false,
    };

    // get DOM node in which map will be instantiated
    var canvas = $("#map-canvas").get(0);

    // instantiate map
    map = new google.maps.Map(canvas, options);

    // configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);

}



/**
 * Configures application.
 */
function configure()
{
  directionsDisplay = new google.maps.DirectionsRenderer(
    {
        suppressMarkers: true
    });
  directionsDisplay.setMap(map);
  directionsDisplay.setPanel(document.getElementById("directionsPanel"));

  var directionsService = new google.maps.DirectionsService();
  google.maps.event.addListener(map, 'dblclick', (event)=>{
    var start = new google.maps.LatLng(parseFloat(document.getElementById("sirina").value),parseFloat(document.getElementById("duzina").value));
    var end = new google.maps.LatLng(event.latLng.lat(), event.latLng.lng());

    if (endmark) {
      endmark.setPosition(end);
    }
    else {
        endmark = new google.maps.Marker({
        position: end,
        map: map,
      });
    }

		var request = {
      origin: start,
      destination: end,
      travelMode: google.maps.TravelMode.DRIVING
    };
    directionsService.route(request, function (response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
      }
    });			
  });

    // update UI after map has been dragged
    google.maps.event.addListener(map, "dragend", function() {

        // if info window isn't open
        // http://stackoverflow.com/a/12410385
        if (!info.getMap || !info.getMap())
        {
          update();
        }
    });

    // update UI after zoom level changes
    google.maps.event.addListener(map, "zoom_changed", function() {
      update();
    });

    // re-enable ctrl- and right-clicking (and thus Inspect Element) on Google Map
    // https://chrome.google.com/webstore/detail/allow-right-click/hompjdfbfmmmgflfjdlnkohcplmboaeo?hl=en
    document.addEventListener("contextmenu", function(event) {
        event.returnValue = true;
        event.stopPropagation && event.stopPropagation();
        event.cancelBubble && event.cancelBubble();
    }, true);
    $("#dodajSliku").css("display","block");
    update();
    autoUpdate();
}

var marker = null;

function autoUpdate() {
  navigator.geolocation.getCurrentPosition(function(position) {  
    var newPoint = new google.maps.LatLng(position.coords.latitude, 
                                          position.coords.longitude);
    document.getElementById("sirina").value = position.coords.latitude;
    document.getElementById("duzina").value = position.coords.longitude;



    if (marker) {
      marker.setPosition(newPoint);
      
    }
    else {
        var image = {
            url: "/static/images/marker.png",
            size: new google.maps.Size(30, 30),
            scaledSize: new google.maps.Size(30, 30),
          };
        marker = new google.maps.Marker({
        position: newPoint,
        icon:image,
        map: map,
      });
    }
  }); 
  setTimeout(autoUpdate, 5000);
}

function update()
{
    // get map's bounds
    var bounds = map.getBounds();
    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();

    // get places within bounds (asynchronously)
    var parameters = {
        ne: ne.lat() + "," + ne.lng(),
        sw: sw.lat() + "," + sw.lng()
    };
    $.getJSON(Flask.url_for("maps.update"), parameters)
    .done(function(data, textStatus, jqXHR) {

       // remove old markers from map
       removeMarkers();
       // add new markers to map
       for (var i = 0; i < data.length; i++)
       {
           addMarker(data[i]);
       }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
    });
}

function showInfo(marker, content)
{
    // start div
    var div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // end div
    div += "</div>";

    // set info window's content
    info.setContent(div);

    // open info window (if not already open)
    info.open(map, marker);
}

function removeMarkers()
{
    //prilazimo kroz niz markera
    for (var i in markers)
    {
        //brisemo svaki marker s mape
        markers[i].setMap(null);
    }
    //i na kraju praznimo niz
    markers=[];
}
function addMarker(place)
{
  //uzimamo poziciju markera na osnovu njegove geogradkse duzina i sirine
   var kordinate = new google.maps.LatLng(parseFloat(place.latitude), parseFloat(place.longitude));


  //kreiramo ikonicu za marker velicine 50x50px i govorimo gde ce se label nalaziti
   var image = {
    url: "/static/images/traffic.png",
    size: new google.maps.Size(50, 50),
    scaledSize: new google.maps.Size(50, 50),
  };

    var tacka = new google.maps.Marker({
        position: kordinate,
        icon: image
    });

//Београд
//44.860776, 20.591028

    tacka.addListener('click', ()=>{

      unos="<a target='_blank' class='nav-link' href='/lists/"+place.id+"'>"
        unos+="<img src='static/uploaded/images/"+place.id+".jpg' alt='Smiley face' height='100' width='150'>";
        showInfo(tacka, unos+"</a>");
    });
    //dodajemo makrker u niz
    markers.push(tacka);

    //i prikazujemo marker na mapi
    tacka.setMap(map);
}

