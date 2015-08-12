---
---
var SWC = SWC || {};

SWC.maps = (function() {
  var maps = {};

  function toggleScrollwheel(map, enabled) {
      if(map) map.setOptions({ scrollwheel: enabled });
  }

  function add_cluster_event_listeners(clusterer, map, info_window) {
      google.maps.event.addListener(clusterer, 'clusterclick', function(cluster) {
        info_window.setPosition(cluster.getCenter());
        var info_string = "<div class=\"info-window\">";
        var i=0;
        var markers = cluster.getMarkers();
        for (; i < markers.length; i++ )
        {
          info_string += markers[i].getTitle();
        }
        info_string += "</div>";
        // reset content so that scroll bar in new content will always be at
        // top of content
        info_window.setContent( "<div class=\"info-window\"></div>");
        info_window.setContent(info_string);
        info_window.open(map);
        // when the info window has a scroll bar, we want the mouse scroll wheel
        //   to scroll in the info window, NOT zoom the map.  Disable map zoom.
        toggleScrollwheel(map, false);
      });
      // zooming changes our clusters completely.  The info window is no longer
      //  accurate.  Close it.  Make people pick a new cluster or marker.
      google.maps.event.addListener(map, 'zoom_changed', function(event){
        info_window.close();
      });
      // when the info window is closed, restore mousewheel zoom on the map
      google.maps.event.addListener(info_window, 'closeclick', function(){
      toggleScrollwheel(map, true);
      });
  };


  maps.upcoming = function() {
      var mapOptions = {
        zoom: 2,
        center: new google.maps.LatLng(25,8),
        mapTypeId: google.maps.MapTypeId.ROADMAP
      },
      map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
      var markers = [];
      // Go over all the upcoming camps and create pins in the map
      {% for workshop in site.workshops %}
        {% if workshop.latlng and workshop.startdate >= site.today %}
          var marker = new google.maps.Marker({
            position: new google.maps.LatLng({{workshop.latlng}}),
            map: map,
              title: "<h5><a href=\"{% if workshop.url %}{{workshop.url}}{% else %}{{page.root}}/{{workshop.path}}{% endif %}\">{{workshop.venue}}</a></h5>" +
                  "<h6><a href=\"{{page.root}}/{{workshop.path}}\">{{workshop.humandate}}</a></h6>",
            visible: false  // marker not shown directly, just clustered
          });
          markers.push(marker)
        {% endif %}
      {% endfor %}
      var mcOptions = {
        zoomOnClick: false,
        maxZoom: null,
        gridSize: 25,
        minimumClusterSize: 1
      }
      var mc = new MarkerClusterer(map, markers, mcOptions);
      info_window = new google.maps.InfoWindow();
      add_cluster_event_listeners(mc, map, info_window);
  }

  maps.previous = function() {
      var mapOptions = {
        zoom: 2,
        center: new google.maps.LatLng(25,8),
        mapTypeId: google.maps.MapTypeId.ROADMAP
      },
      map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
      var markers = [];
      // Go over all the previous camps and create pins in the map
      {% for workshop in site.workshops reversed %}
        {% if workshop.latlng and workshop.startdate < site.today %}
          var marker = new google.maps.Marker({
            position: new google.maps.LatLng({{workshop.latlng}}),
            map: map,
            title: "<h5><a href=\"{% if workshop.url %}{{workshop.url}}{% else %}{{page.root}}/{{workshop.path}}{% endif %}\">{{workshop.venue}}</a></h5>" +
            "<h6><a href=\"{{page.root}}/{{workshop.path}}\">{{workshop.humandate}}</a></h6>",
            visible: false  // marker not shown directly, just clustered
          });
          markers.push(marker); // For clustering
        {% endif %}
      {% endfor %}

      var mcOptions = {
        zoomOnClick: false,
        maxZoom: null,
        gridSize: 25,
        minimumClusterSize: 1
      }
      var mc = new MarkerClusterer(map, markers, mcOptions);
      info_window = new google.maps.InfoWindow();
      add_cluster_event_listeners(mc, map, info_window);
  }

  maps.instructors = function() {
      var mapOptions = {
      zoom: 2,
      center: new google.maps.LatLng(25,8),
      mapTypeId: google.maps.MapTypeId.ROADMAP
      },
      map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
      var markers = [];
      // Go over all airports to read instructor location
      {% for airport in site.airports %}
          {% for person in airport.instructors %}
            var marker = new google.maps.Marker({
              position: new google.maps.LatLng({{airport.latitude}}, {{airport.longitude}}),
              map: map,
              visible: false, // marker not shown directly, just clustered
              title: "<h5><a href=\"{{site.url}}/pages/team.html#{{person.user}}\">{{person.name}}</a></h5>"
              });
            markers.push(marker); // For clustering
          {% endfor %}
      {% endfor %}
      var mcOptions = {
        zoomOnClick: false,
        maxZoom: null,
        gridSize: 25,
        minimumClusterSize: 1
      }
      var mc = new MarkerClusterer(map,markers,mcOptions);
      info_window = new google.maps.InfoWindow({}),
      add_cluster_event_listeners(mc, map, info_window);
  }

  return maps;
})();
