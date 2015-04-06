/*****************************************************************************
 * FILE:    JavaScript Enclosure Template
 * DATE: 8/6/2014
 * AUTHOR: Alan Snow
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/
//only load if the map data is included
if(typeof jQuery('#fc_outer_container').attr('data-map') != 'undefined') {
  var FETCHCLIMATE_MAP = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library
    
    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
     var m_public_interface, m_drawing_types_enabled,m_initial_drawing_mode,
        m_grids,//contains all of the grids added to the map
        m_grids_json,//contains json grid information
        m_max_num_grids, //maxiumum_number of grids allowed
        m_points,//contains all of the points added to the map
        m_points_json,//contains json point information
        m_max_num_points, //maxiumum_number of points allowed
        m_info_window, //the info window popup
        m_map, // contains the object for the map
        m_map_json, // contains the object for the map
        m_drawing_manager, //contains the drawing manager for map
        m_current_drawing_modes, //contains the current drawing modes
        m_map_changed, //tells if the map has been modified
        m_zoom_to_all_control_div, //html button for the zoom to all control
        m_reset_layers_control_div;//html button for the reset control
    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
     var initGoogleMap, initLayersFromJSON, addResetLayersButton, updateZoomToAllButton, 
        zoomToAll, resetDrawingModes, createButton,getGeoJsonPoints, getGeoJsonGrids, 
        getGeoJsonString, updateMapChanged, overlayClick, overlayDrawingComplete,
        updateOverlay, createInfoWindow,geoJsonify, setValue, setValuePoint,
        setValueGrid, deleteOverlay, deletePoint, deleteGrid, deleteAllOverlays;

     /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    //FUNCTION: intializes map
    initGoogleMap = function() {
      // Variable declarations
      var map_options;
      var m_current_drawing_modes = [];
      var drawing_mode = null;
      //Make sure the drawing variables are initialized
      if (m_drawing_types_enabled.length <= 0 || typeof m_drawing_types_enabled == 'undefined') {
        m_drawing_types_enabled = ['RECTANGLE','POINTS'];
      } 
      //Find out which variables to draw
      var draw_rectangle = m_drawing_types_enabled.indexOf("RECTANGLE") !== -1;
      var draw_points = m_drawing_types_enabled.indexOf("POINTS") !== -1;
      // Configure drawing modes
      if (draw_rectangle) {
        m_current_drawing_modes.push(google.maps.drawing.OverlayType.RECTANGLE);
      }
      if (draw_points) {
        m_current_drawing_modes.push(google.maps.drawing.OverlayType.MARKER);
      }
      if (m_initial_drawing_mode !== '' && typeof m_initial_drawing_mode != 'undefined')
      {
        if ((m_initial_drawing_mode === 'RECTANGLE') && draw_rectangle) {
          drawing_mode = google.maps.drawing.OverlayType.RECTANGLE;
        }
        else if ((m_initial_drawing_mode === 'POINTS') && draw_points) {
          drawing_mode = google.maps.drawing.OverlayType.MARKER;
        }
      }
      // Configure map
      map_options = {
          center: new google.maps.LatLng(39.0, -96.0),
          zoom: 4,
          mapTypeId: google.maps.MapTypeId.HYBRID,
              scaleControl: true,
              rotateControl: true,
      };
      // init map
      m_map = new google.maps.Map(document.getElementById("fetchclimate_map"), map_options);
      // Setup drawing manager and configure
      m_drawing_manager = new google.maps.drawing.DrawingManager({
            drawingMode: drawing_mode,
            drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_RIGHT,
            drawingModes: m_current_drawing_modes
          },
          rectangleOptions: {
            editable: true,
            draggable: true,
            geodesic: true
          },
          markerOptions: {
            draggable: true
          }
      });
      m_drawing_manager.setMap(m_map);
      // Add the listeners
      google.maps.event.addListener(m_drawing_manager, 'overlaycomplete', overlayDrawingComplete);
      //add button to reset layers
      addResetLayersButton();
      //add JSON layers
      initLayersFromJSON();
      //make sure the modes match
      resetDrawingModes();
      // Bind stuff to the domready event
      google.maps.event.addListener(m_info_window, 'domready', function() {
      // Set the first input to be focused when info window is shown
          $('#infoWindowForm input:first').focus();    
      });
    };

    //FUNCTION: intializes layers from JSON in original HTML
    initLayersFromJSON = function() {
      deleteAllOverlays();
      //Add rectangles to the map if they exist
      if (m_grids_json.length>0) {
        for (var grid_id in m_grids_json) {
          var rect_bounds = new google.maps.LatLngBounds(
              new google.maps.LatLng(m_grids_json[grid_id].boundingBox[0], m_grids_json[grid_id].boundingBox[2]),
              new google.maps.LatLng(m_grids_json[grid_id].boundingBox[1], m_grids_json[grid_id].boundingBox[3]));
          var rectangle = new google.maps.Rectangle({
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
            gridResolution: m_grids_json[grid_id].gridResolution,
            map: m_map,
            bounds: rect_bounds,
            editable: true,
            draggable: true,
            geodesic: true
          });
          updateOverlay(rectangle,google.maps.drawing.OverlayType.RECTANGLE,m_grids_json[grid_id].title);
        }
      }
      //Add points to the map if they exist
      if(m_points_json.length>0) {
        for (var point_id in m_points_json) {
          var point_LatLng = new google.maps.LatLng(m_points_json[point_id].location[0],m_points_json[point_id].location[1]);
          var marker = new google.maps.Marker({
              position: point_LatLng,
              map: m_map,
              title: m_points_json[point_id].title,
              draggable: true
          });
          m_map.setZoom(17);
          updateOverlay(marker,google.maps.drawing.OverlayType.MARKER,m_points_json[point_id].title);
        }
      }
      //zoom to added layers
      zoomToAll();
      //add the zoom to all layers button if layers
      updateZoomToAllButton();
      //changes the drawing mode based on max num grids/points
      resetDrawingModes();
    };

    //FUNCTION: adds the reset layers button
    addResetLayersButton = function() {
      // Setup the click event listeners: simply zoom to all layers
      google.maps.event.addDomListener(m_reset_layers_control_div, 'click', function() {
        initLayersFromJSON();
      });
      m_map.controls[google.maps.ControlPosition.TOP_RIGHT].push(m_reset_layers_control_div);
    };

    //FUNCTION: only shows zoom to all button if there are overlays on the map
    updateZoomToAllButton = function() {
      if(m_grids.length>0 || m_points.length>0) {
        console.log(m_map.controls[google.maps.ControlPosition.TOP_RIGHT].length);
        if(m_map.controls[google.maps.ControlPosition.TOP_RIGHT].length == 1) {
          // Setup the click event listeners: simply zoom to all layers
          google.maps.event.addDomListener(m_zoom_to_all_control_div, 'click', function() {
            zoomToAll();
          });
          m_map.controls[google.maps.ControlPosition.TOP_RIGHT].push(m_zoom_to_all_control_div);
        }
      }
      else {
        if(m_map.controls[google.maps.ControlPosition.TOP_RIGHT].length > 1) {
          m_map.controls[google.maps.ControlPosition.TOP_RIGHT].pop();
        }
      }
    };

    //FUNCTION: zooms to all rectanges and points if added
    zoomToAll = function() {
      var bounds = new google.maps.LatLngBounds();
      if (typeof m_grids != 'undefined') {
        for (var grid_id in m_grids) {
          bounds.extend(m_grids[grid_id].getBounds().getNorthEast());
          bounds.extend(m_grids[grid_id].getBounds().getSouthWest());
        }
      }
      if (typeof m_points != 'undefined') {
        for (var point_id in m_points) {
          bounds.extend(m_points[point_id].getPosition());
        }
      }
      m_map.fitBounds(bounds);
    };

    //FUNCTION: turns off the drawing mode if the max number of the overlay type is reached
    resetDrawingModes = function() {
      var change_occur = false;
      if(m_grids.length < m_max_num_grids || m_max_num_grids == -1) {
        if(m_current_drawing_modes.indexOf(google.maps.drawing.OverlayType.RECTANGLE)==-1) {
          m_current_drawing_modes.unshift(google.maps.drawing.OverlayType.RECTANGLE);
          change_occur = true;
        }
      }
      else {
        if(m_current_drawing_modes.indexOf(google.maps.drawing.OverlayType.RECTANGLE)!=-1) {
          m_current_drawing_modes.splice(google.maps.drawing.OverlayType.RECTANGLE,1);
          change_occur = true;
        }
      }
      if(m_points.length < m_max_num_points || m_max_num_points == -1) {
        if(m_current_drawing_modes.indexOf(google.maps.drawing.OverlayType.MARKER)==-1) {
          m_current_drawing_modes.push(google.maps.drawing.OverlayType.MARKER);
          change_occur = true;
        }
      }
      else {
        if(m_current_drawing_modes.indexOf(google.maps.drawing.OverlayType.MARKER)!=-1) {
          m_current_drawing_modes.splice(google.maps.drawing.OverlayType.MARKER,1);
          change_occur = true;
        }
      }
      if(change_occur) {
        // Setup drawing manager and configure
        m_drawing_manager.setOptions({
                drawingControlOptions:{
                  position: google.maps.ControlPosition.TOP_RIGHT,
                  drawingModes: m_current_drawing_modes
                }
        });
      }
    };

    //FUNCTION: creates button with a given title and html
    createButton = function(title, innerHTML) {
      // Create a div to hold the control.
      var controlDiv = document.createElement('div');
      // Set CSS styles for the DIV containing the control
      // Setting padding to 5 px will offset the control
      // from the edge of the map.
      controlDiv.style.padding = '5px';
      // Set CSS for the control border.
      var controlUI = document.createElement('div');
      controlUI.style.backgroundColor = 'white';
      controlUI.style.borderStyle = 'solid';
      controlUI.style.borderWidth = '2px';
      controlUI.style.cursor = 'pointer';
      controlUI.style.textAlign = 'center';
      controlUI.title = title;
      controlDiv.appendChild(controlUI);
      // Set CSS for the control interior.
      var controlText = document.createElement('div');
      controlText.style.fontFamily = 'Arial,sans-serif';
      controlText.style.fontSize = '12px';
      controlText.style.paddingLeft = '4px';
      controlText.style.paddingRight = '4px';
      controlText.innerHTML = innerHTML;
      controlUI.appendChild(controlText);
      controlDiv.index = 1;
      return controlDiv;
    };

    //FUNCTION: converts google overlays to GeoJson
    geoJsonify = function(overlay, type) {
      var geo_json, coordinates;
      // Convert maps overlays into geoJSON
      if (type === google.maps.drawing.OverlayType.RECTANGLE) {
        var ne = overlay.getBounds().getNorthEast();
        var sw = overlay.getBounds().getSouthWest();
        geo_json = {
                  boundingBox: [sw.lat(),ne.lat(),sw.lng(),ne.lng()],
                  gridResolution: overlay.gridResolution,
                  title: overlay.title,
                  id: overlay.id
                  };
        return geo_json;
      }    
      else if (type === google.maps.drawing.OverlayType.MARKER) {
        var position = overlay.getPosition();
        geo_json = {
                  location: [position.lat(), position.lng()],
                  title: overlay.title,
                  id: overlay.id
                  };
        return geo_json;
      }
      return 'null';
    };


    //FUNCTION: Gets the points from the map as geo json
    getGeoJsonPoints = function() {
      var points = [];
      for (var i = 0; i < m_points.length; i ++) {
        points.push(geoJsonify(m_points[i], m_points[i].type));
      }
      return points;
    };

    //FUNCTION: Get the grids from the map as geo json
    getGeoJsonGrids = function() {
      var grids = [];
      for (var i = 0; i < m_grids.length; i ++) {
        grids.push(geoJsonify(m_grids[i], m_grids[i].type));
      }
      return grids;
    };
    
    //FUNCTION: sets map changed variable to true
    updateMapChanged = function() {
      // Set the contents of the text area
       m_map_changed = true;
    };

    //FUNCTION: handles the click function on an overlay
    overlayClick = function() {
        // Show edit info window
        createInfoWindow('Edit', 'Update', this);
    };

    //FUNCTION: function to fire when overlay drawing finishes
    overlayDrawingComplete = function(event) {
      m_drawing_manager.setDrawingMode(null);
      updateOverlay(event.overlay, event.type);
      updateZoomToAllButton();
      resetDrawingModes();
    };

    //FUNCTION: function to update overlay attributes
    updateOverlay = function(overlay,type,title) {
      // Add non-type specific properties to overlay
      overlay.type = type;
      // Add overlay click event handler method to overlay
      overlay.overlayClick = overlayClick;
      // Create a event listeners for the overlay
      google.maps.event.addListener(overlay, 'click', overlay.overlayClick);

      if (type === google.maps.drawing.OverlayType.RECTANGLE) {
        overlay.id = m_grids.length;
        overlay.title = typeof title !== 'undefined' ? title : "Rectangle-" + overlay.id;
        // Add polygon specific properties to overlay
        overlay.center = overlay.getBounds().getCenter();
        var rect_symbol = { strokeColor: '#FF0000',
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: '#FF0000',
                        fillOpacity: 0.35 };
        overlay.setOptions(rect_symbol);
        google.maps.event.addListener(overlay, 'bounds_changed', updateMapChanged);
        //add to maps grids
        m_grids.push(overlay);
        // Trigger info_window for the user to set the value
        createInfoWindow('Set Value', 'Save', m_grids[m_grids.length-1]);
      } 
      else if (type === google.maps.drawing.OverlayType.MARKER) {
        overlay.id = m_points.length;
        overlay.title = typeof title !== 'undefined' ? title : "Marker-" + overlay.id;
        var marker_symbol = { path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
               fillColor: '#0000ff',
               fillOpacity: 1.0,
               scale: 5,
               strokeColor: '#0000ff',
               strokeWeight: 1 };
        
        // Add marker specific properties to overlay
        overlay.center = overlay.getPosition();
        overlay.setOptions({ icon: marker_symbol });
        google.maps.event.addListener(overlay, 'dragend', updateMapChanged);
        //add to maps points
        m_points.push(overlay);
        // Trigger info_window for the user to set the value
        createInfoWindow('Set Value', 'Save', m_points[m_points.length-1]);
      }
      m_map_changed = true;
    };

    //FUNCTION: creates info window for given overlay
    createInfoWindow = function(title, save_button_title, overlay) {
      var overlay_id, value, type, center, center_marker, anchor,
          add_content;
      overlay_id = overlay.id;
      type = overlay.type;
      // Get center to be anchor of popup
      if (type === google.maps.drawing.OverlayType.RECTANGLE) {
          //add rectangle specific attributes
          anchor = overlay.getBounds().getCenter()
          var ne = overlay.getBounds().getNorthEast();
          var sw = overlay.getBounds().getSouthWest();
          add_content = '<div class="form-group">'+
                            '<div class="float-parent">'+
                              '<div class="float-left">'+
                                '<label class="control-label" for="inputLatMin">Lat Min</label>'+
                                '<input class="form-control" form="#inputLatMin" type="text" id="inputLatMin" name="Lat Min" value="' + sw.lat() + '">'+
                                '<label class="control-label" for="inputLonMin">Lon Min</label>'+
                                '<input class="form-control" form="#inputLonMin" type="text" id="inputLonMin" name="Lon Min" value="' + sw.lng() + '">'+
                              '</div>'+
                              '<div class="float-right">'+
                                '<label class="control-label" for="inputLatMax">Lat Max</label>'+
                                '<input class="form-control"form="#inputLatMax" type="text" id="inputLatMax" name="Lat Max" value="' + ne.lat() + '">'+
                                '<label class="control-label" for="inputLonMax">Lon Max</label>'+
                                '<input class="form-control" form="#inputLonMax" type="text" id="inputLonMax" name="Lon Max" value="' + ne.lng() + '">'+
                              '</div>'+
                            '</div>'+
                            '<div class="float-parent">'+
                              '<div class="float-left">'+
                                '<label class="control-label" for="inputResX">X Resolution</label>'+
                                '<input class="form-control" form="#inputResX" type="text" id="inputResX" name="X Resolution" value="' + 
                                    (typeof overlay.gridResolution !== 'undefined' ? overlay.gridResolution[0] : 25) + '">'+
                              '</div>'+
                              '<div class="float-right">'+
                                '<label class="control-label" for="inputResY">Y Resolution</label>'+
                                '<input class="form-control" form="#inputResY" type="text" id="inputResY" name="Y Resolution" value="' + 
                                    (typeof overlay.gridResolution !== 'undefined' ? overlay.gridResolution[1] : 25)  + '">'+
                              '</div>'+
                            '</div>'+
                        '</div>';
      } else if (type === google.maps.drawing.OverlayType.MARKER) {
          //add marker specific attributes
          anchor = overlay.getPosition();
          add_content = '<div class="form-group">'+
                          '<div class="controls">'+
                            '<div class="float-parent">'+
                              '<div class="float-left">'+
                                '<label class="control-label" for="inputLat">Lat</label>'+
                                '<input class="form-control" form="#inputLat" type="text" id="inputLat" name="Lat" value="' + 
                                    anchor.lat() + '">'+
                              '</div>'+
                              '<div class="float-right">'+
                                '<label class="control-label" for="inputLon">Lon</label>'+
                                '<input class="form-control" form="#inputLon" type="text" id="inputLon" name="Lon" value="' + 
                                    anchor.lng()  + '">'+
                              '</div>'+
                            '</div>'+
                          '</div>'+
                        '</div>';

      }
      // Setup content for info window
      var content_string = '<div>'+
                  '<h4>' + title + '</h4>'+
                  '<form id="infoWindowForm">'+
                    '<div class="form-group">'+
                      '<div class="controls">'+
                        '<label class="control-label" for="infoWindowInput">Title</label>'+
                        '<input class="form-control" form="#infoWindowForm" type="text" id="infoWindowInput" name="Title" value="' + overlay.title + '">'+
                        '<input type="hidden" id="overlayType" name="overlayType" value="' + type + '">'+
                      '</div>'+
                    '</div>'+ add_content +
                    '<div class="form-group">'+
                      '<div class="controls">'+
                        '<a class="btn btn-danger" onclick="FCMap_deleteOverlay('+
                                overlay_id + ');" href="javascript:void(0);">Delete</a>'+
                        '<a id="saveOverlayButton" class="btn btn-success pull-right" onclick="FCMap_setValue('+overlay_id+');" href="javascript:void(0);" >'+ save_button_title +'</a>'+
                      '</div>'+
                    '</div>'+
                  '</form>'+
                    '</div>';
      center_marker = new google.maps.Marker({ position: anchor });
      m_info_window.setContent(content_string);
      m_info_window.open(m_map, center_marker);
    };

    //FUNCTION: sets the value of an overlay on the map
    setValue = function(id) {
      // Find the appropriate overlay from the array of overlays
      var type = jQuery('input#overlayType').val();
      if(type ==='marker') {
        setValuePoint(id);
      }
      else if (type ==='rectangle') {
        setValueGrid(id);
      }
      // Close the pop-up window
      m_info_window.close();
      m_map_changed = true;
    };

    //FUNCTION: sets the value of a point on the map
    setValuePoint = function(id) {
      var title = jQuery('input#infoWindowInput').val();
      for (var i = 0; i < m_points.length; i ++) {
        if (m_points[i].id === id) {
          // Set new value and change default to match
          m_points[i].title = title;
          m_points[i].setPosition(
            new google.maps.LatLng(jQuery('input#inputLat').val(),jQuery('input#inputLon').val())
          );
          break;
        }
      }
    };

    //FUNCTION: sets the value of a grid on the map
    setValueGrid = function(id) {
      var title = jQuery('input#infoWindowInput').val();
      for (var i = 0; i < m_grids.length; i ++) {
        if (m_grids[i].id === id) {
          // Set new value and change default to match
          m_grids[i].title = title;
          m_grids[i].setBounds(new google.maps.LatLngBounds(
                new google.maps.LatLng(jQuery('input#inputLatMin').val(), jQuery('input#inputLonMin').val()),
                new google.maps.LatLng(jQuery('input#inputLatMax').val(), jQuery('input#inputLonMax').val()))
          );
          m_grids[i].gridResolution = [parseInt(jQuery('input#inputResX').val(),10),parseInt(jQuery('input#inputResY').val(),10)];
          break;
        }
      }
    };

    //FUNCTION: remove overlay from map and from memory
    deleteOverlay = function(id) {
      var type = jQuery('input#overlayType').val();
      if(type ==='marker') {
        deletePoint(id);
      }
      else if (type ==='rectangle') {
        deleteGrid(id);
      }
      // Close the pop-up window
      m_info_window.close();
      m_map_changed = true;
      updateZoomToAllButton();
      resetDrawingModes();
    };

    //FUNCTION: remove point from map and memory
    deletePoint = function(id) {
      var point_found = false;
      // Find the appropriate overlay from the array of overlays
      for (var i = 0; i < m_points.length; i++) {
        if (m_points[i].id === id) {
          // Remove it from the map
          m_points[i].setMap(null);
          
          // Remove it from the overlays array
          m_points.splice(i, 1);
          i--;
          point_found = true;
        } else if (point_found) {
          //update title number
          if(m_points[i].title == "Marker-" + m_points[i].id) {
            m_points[i].title = "Marker-" + i;
          }
          //reset id to match new array
          m_points[i].id = i;
        }
      }
    };

    //FUNCTION: remove grid from map and memory
    deleteGrid = function(id) {
      var grid_found = false;
      // Find the appropriate overlay from the array of overlays
      for (var i = 0; i < m_grids.length; i++) {
        if (m_grids[i].id === id) {
          // Remove it from the map
          m_grids[i].setMap(null);
          
          // Remove it from the overlays array
          m_grids.splice(i, 1);
          i--;
          grid_found = true;
        } else if (grid_found) {
          //update title number
          if(m_grids[i].title == "Rectangle-" + m_grids[i].id) {
            m_grids[i].title = "Rectangle-" + i;
          }
          //reset id to match new array
          m_grids[i].id = i;
        }
      }
    };

    //FUNCTION: removes all overlays from map and memory
    deleteAllOverlays = function () {
      for (var i = 0; i < m_grids.length; i++) {
        // Remove it from the map
        m_grids[i].setMap(null);
      }
      for (var i = 0; i < m_points.length; i++) {
        // Remove it from the map
        m_points[i].setMap(null);
      }
      m_grids = [];
      m_points = [];
      updateZoomToAllButton();
      resetDrawingModes();
    };

    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/
    /*
     * Library object that contains public facing functions of the package.
     * This is the object that is returned by the library wrapper function.
     * See below.
     * NOTE: The functions in the public interface have access to the private
     * functions of the library because of JavaScript function scope.
     */
    m_public_interface = {
      setValue: function(id) {
        setValue(id)
      },
      deleteOverlay: function(id) {
        deleteOverlay(id);
      },
      getPointsJSON: function() {
        return getGeoJsonPoints();
      },
      getGridsJSON: function() {
        return getGeoJsonGrids();
      },
      getMapChanged: function() {
        return m_map_changed;
      },
      resetMapChanged: function() {
        m_map_changed = false;
      },
      refreshMap: function() {
        google.maps.event.trigger(m_map, 'resize');
      }
    };
    
    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/
    
    // Initialization: jQuery function that gets called when 
    // the DOM tree finishes loading
    $(function() {
      //initialize global variables
      var map_data = jQuery('#fc_outer_container').attr('data-map');
      if(typeof map_data != 'undefined') {
        m_map_json = JSON.parse(map_data);
        m_max_num_grids = ('max_num_grids' in m_map_json.map_data? m_map_json.map_data.max_num_grids:-1);
        m_max_num_points = ('max_num_points' in m_map_json.map_data? m_map_json.map_data.max_num_points:-1);
        m_drawing_types_enabled = ('drawing_types_enabled' in m_map_json.map_data?m_map_json.map_data.drawing_types_enabled:[]);
        m_initial_drawing_mode = ('initial_drawing_mode' in m_map_json.map_data?m_map_json.map_data.initial_drawing_mode:[]);
        m_current_drawing_modes = [];
        m_grids_json = JSON.parse(jQuery('#fc_outer_container').attr('data-grids'));
        m_points_json = JSON.parse(jQuery('#fc_outer_container').attr('data-points'));
        m_grids = [];
        m_points = [];
        m_info_window = new google.maps.InfoWindow();
        m_map_changed = false;

        //initialize the html element for the zoom to all control
        m_zoom_to_all_control_div = createButton(
                      'Click to zoom to all objects added to the map.',
                      '<b>Zoom To All</b>');
        m_reset_layers_control_div = createButton(
                      'Click to reset layers to original layout.',
                      '<b>Reset Layers</b>');
        //initialize the map
        initGoogleMap();
      }
    });

    return m_public_interface;

  }()); // End of package wrapper 
  // NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper 
  // function immediately after being parsed.
  //-----------------------------------------------------------------------------
  //Public Functions
  //-----------------------------------------------------------------------------
  function FCMap_setValue(id) {
    FETCHCLIMATE_MAP.setValue(id);
  };

  function FCMap_deleteOverlay(id) {
    FETCHCLIMATE_MAP.deleteOverlay(id);
  };
}
