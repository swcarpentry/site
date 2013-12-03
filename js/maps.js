---
---
var SWC = SWC || {};

SWC.maps = (function() {
  var maps = {},
      i_window; // Info window "class"

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

  // Help us with the html in the window
  w_text = (function(c) {
    var _class = typeof c !== 'undefined' ? c : 'info-window',
        i_start = '<div class="' + _class + '">',
        i_end = '</div>',
        name = '', n_link = '',
        dates = {};

    // bootcamp name, link, date, date link
    function add(_name, _nl, _date, _dl) {
      name = _name;
      n_link = _nl;
      dates[_date] = _dl;
    }

    function dates_to_string() {
      var s = '';
      for (var _date in dates)
         if(dates.hasOwnProperty(_date))
            s = s + '<h6><a href="' + dates[_date]  + '">' + _date + '</a></h6>';
      return s;
    }

    function html() {
      return i_start +
             '<h5><a href="' + n_link + '">' + name + '</a></h5>' +
             dates_to_string() +
             i_end;
    }

    return {
      "add": add,
      "html": html
    };
  });

  function bootcamps(bc_data_type) {
    var mapOptions = {
      zoom: 2,
      center: new google.maps.LatLng(25,8),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    },
    info_window   = new google.maps.InfoWindow({}),
    map           = new google.maps.Map(document.getElementById('map_canvas'), mapOptions),
    bc_date, split_date, today = new Date(),
    his = {}, // Hash to detect multiple instaces of a bootcamp
    info_string, bc_venue;

    // Go over all the upcoming camps and create pins in the map
    {% for bootcamp in site.bootcamps %}
      split_date = "{{bootcamp.startdate}}".split("-");
      bc_date = new Date(split_date[0], split_date[1]-1, split_date[2]); // year, month, day

      {% if bootcamp.latlng %}
        /*
        var marker = new google.maps.Marker({
          position: new google.maps.LatLng({{bootcamp.latlng}}),
          map: map,
          title: "{{bootcamp.venue}}, {{bootcamp.humandate}}",
          visible: false,
        });
        */
        var marker = new MarkerWithLabel({
          position: new google.maps.LatLng({{bootcamp.latlng}}),
          map: map,
          title: "{{bootcamp.venue}}, {{bootcamp.humandate}}",
          visible: false,
          labelContent: 0,
          labelAnchor: new google.maps.Point(0, 0),
          labelClass: "labels", // the CSS class for the label
          labelStyle: {opacity: 0.75}
        });

        /*
        info_string = '<div class="info-window">' +
          '<h5><a href="{% if bootcamp.url %}{{bootcamp.url}}{% else %}{{page.root}}/{{bootcamp.path}}{% endif %}">{{bootcamp.venue|replace: '\'','\\\''}}</a></h5>' +
          '<h6><a href="{{page.root}}/{{bootcamp.path}}">{{bootcamp.humandate}}</a></h6>' +
          '</div>';
        */

        bc_venue = "{{bootcamp.venue}}";
        if (bc_venue in his) {
          info_string = his[bc_venue].text;
        }
        else {
          info_string = w_text('info-window');
          his[bc_venue] = { num_instances: 0 };
        }

        add_info_string = function() {
          info_string.add(
            "{{bootcamp.venue}}",
            "{% if bootcamp.url %}{{bootcamp.url}}{% else %}{{page.root}}/{{bootcamp.path}}{% endif %}",
            "{{bootcamp.humandate}}",
            "{{page.root}}/{{bootcamp.path}}"
          );
        };

        if (bc_data_type === "upcoming" && bc_date >= today) {
          marker.visible = true;
          add_info_string();
        }
        if (bc_data_type === "past" && bc_date < today) {
          marker.visible = true;
          add_info_string();
        }


        his[bc_venue].text = info_string;
        his[bc_venue].num_instances += 1;
        marker.labelContent = his[bc_venue].num_instances;

        set_info_window(map, marker, info_window, info_string.html());
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
