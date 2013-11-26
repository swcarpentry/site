---
---
var SWC = SWC || {};

SWC.maps = (function() {
  var maps = {};

  function MarkerPin(color) {
    var pin = new google.maps.MarkerImage(
      "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
      new google.maps.Size(21, 34),
      new google.maps.Point(0,0),
      new google.maps.Point(10, 34));
    return pin;
  }

  function MarkerPinCluster(url, sizeX, sizeY) {
    var pin = new google.maps.MarkerImage(
    url,
    new google.maps.Size(sizeX,sizeY),
    new google.maps.Point(0,0),
    new google.maps.Point(10,34));
    return pin;
  }

  function set_info_window(map, marker, info_window, content) {
    google.maps.event.addListener(marker, 'click', function () {
      info_window.setContent(content);
      info_window.open(map, marker);
    });
  }

  function toggle_marker_visibility(marker) {
    if (marker.getVisible()) {
      marker.setVisible(false);
    } else {
      marker.setVisible(true);
    }
  }

  function toggle_markers_mc_visibility(markers, mc) {
    markers.forEach(toggle_marker_visibility);
    if (markers[0].visible) {
      mc.setMap(markers[0].getMap());
    }
    else {
      mc.setMap(null);
    }
  }

  function bootcamps(bc_data_type) {
    var mapOptions = {
      zoom: 2,
      center: new google.maps.LatLng(25,8),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    },
    info_window   = new google.maps.InfoWindow({}),
    map           = new google.maps.Map(document.getElementById('map_canvas'), mapOptions),
    bc_date, split_date, today = new Date(),
    info_string;

    // Go over all the upcoming camps and create pins in the map
    {% for bootcamp in site.bootcamps %}
      split_date = "{{bootcamp.startdate}}".split("-");
      bc_date = new Date(split_date[0], split_date[1]-1, split_date[2]); // year, month, day

      {% if bootcamp.latlng %}
        var marker = new google.maps.Marker({
          position: new google.maps.LatLng({{bootcamp.latlng}}),
          map: map,
          title: "{{bootcamp.venue}}, {{bootcamp.humandate}}",
          visible: false,
        });

        info_string = '<div class="info-window">' +
          '<h5><a href="{% if bootcamp.url %}{{bootcamp.url}}{% else %}{{page.root}}/{{bootcamp.path}}{% endif %}">{{bootcamp.venue|replace: '\'','\\\''}}</a></h5>' +
          '<h6><a href="{{page.root}}/{{bootcamp.path}}">{{bootcamp.humandate}}</a></h6>' +
          '</div>';

        if (bc_data_type === "upcoming" && bc_date >= today)
          marker.visible = true;
        if (bc_data_type === "past" && bc_date < today)
          marker.visible = true;

        set_info_window(map, marker, info_window, info_string);
      {% endif %}

    {% endfor %}
  }

  /* Use the URL to figure out what map to load */
  maps.load = function() {
    var url_bn  = document.URL.replace(/^.*\/|\.[^.]*$/g, '');
    if (url_bn === "index")
      bootcamps("upcoming");
    if (url_bn === "past")
      bootcamps("past");
  }

  return maps;
})();
