---
---
var SWC = SWC || {};

SWC.maps = (function() {
  var maps = {},
      i_window, // Info window "class"
      bootcamps; // Store all the bootcamp info

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

  bootcamps = (function() {
    var bcs = {},
        total = 0;

    function add(venue, link, human_date, proot, startdate, latlng) {
      var split_date = startdate.split("-"),
          js_date = new Date(split_date[0], split_date[1]-1, split_date[2]), // year, month, day
          split_latlng = latlng.split(","),
          lat = split_latlng[0], lng = split_latlng[1];

      if (!(venue in bcs))
        bcs[venue] = [];

      bcs[venue].push({
        "venue": venue,
        "link": link,
        "human_date": human_date,
        "proot": proot,
        "lat": +lat,
        "lng": +lng,
        "js_date": js_date
      });
    }

    function load() {
      {% for bootcamp in site.bootcamps %}
        {% if bootcamp.latlng %}
          add("{{bootcamp.venue}}",
              "{% if bootcamp.url %}{{bootcamp.url}}{% else %}{{page.root}}/{{bootcamp.path}}{% endif %}",
              "{{bootcamp.humandate}}",
              "{{page.root}}/{{bootcamp.path}}",
              "{{bootcamp.startdate}}",
              "{{bootcamp.latlng}}");
          total += 1;
        {% endif %}
      {% endfor %}
      console.log("# of bootcamp instances loaded: " + total);
    }

    // Giveme only the bootcamps that match logic (date filtering)
    function filter(f_logic) {
      var f_bcs = {},
          total = 0; // filtered bcs;
      for (var venue in bcs) { // each bootcamp
        if (bcs.hasOwnProperty(venue)) {
          var instances = bcs[venue];
          for (var i=0; i<instances.length; i++) { // each bootcamp instance
            var c = instances[i]; // current bootcamp
            if (f_logic(c.js_date)) { // Should this instance be in the current map?
              if (!(c.venue in f_bcs))
                f_bcs[c.venue] = [];
              f_bcs[c.venue].push(c);
              total += 1;
            }
          }
        }
      }
      console.log("# of bootcamp instances after filtering: " + total);
      return f_bcs;
    }

    function load_pins(map, info_window, filter_logic) {
      var f_bcs = filter(filter_logic);
      for (var venue in f_bcs) {
        if (f_bcs.hasOwnProperty(venue)) { // each bootcamp for the current map
          var instances = f_bcs[venue],
              bubble_text = w_text();

          for (var i=0; i<instances.length; i++) { // each bootcamp instance
            var c = instances[i]; // current bc
            bubble_text.add(c.venue,
                            c.link,
                            c.human_date,
                            c.proot);
          }

          var marker = new MarkerWithLabel({
            position: new google.maps.LatLng(instances[0].lat, instances[0].lng),
            map: map,
            title: instances[0].venue + ", " + instances[0].human_date,
            visible: true,
            labelContent: instances.length,
            labelAnchor: new google.maps.Point(0, 0),
            labelClass: "labels", // the CSS class for the label
            labelStyle: {opacity: 0.75}
          });

          set_info_window(map, marker, info_window, bubble_text.html());
        }
      }
    }

    load();
    return { "load_pins": load_pins };
  })();

  /* Use the URL to figure out what map to load */
  maps.load = function() {
    var url_bn = document.URL.replace(/^.*\/|\.[^.]*$/g, ''),
        mapOptions = {
          zoom: 2,
          center: new google.maps.LatLng(25,8),
          mapTypeId: google.maps.MapTypeId.ROADMAP
      },
      info_window = new google.maps.InfoWindow({}),
      map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions),
      today = new Date();

    bootcamps.load_pins(map, info_window, function(bc_date) {
      if (url_bn === "index")
        return bc_date >= today;
      if (url_bn === "past")
        return bc_date < today;
    });

  };

  return maps;
})();
