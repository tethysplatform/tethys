/*****************************************************************************
 * FILE:    Tethys Map View Library
 * DATE:    February 4, 2015
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) 2015 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_MAP_VIEW = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	// Constants
  var DEFAULT_PROJECTION = 'EPSG:3857',                     // Spherical Mercator Projection
      DEFAULT_OUTPUT_FORMAT = 'GeoJSON',                    // The default output format
      GEOJSON_FORMAT = 'GeoJSON',                           // GeoJSON format type
      WKT_FORMAT = 'WKT';                                   // Well know text format type

  // Options Attributes
  var ATTRIBUTE_TABLE_ATTRIBUTE = 'data-attribute-table',   // HTML attribute containing the attribute table options
      BASE_MAP_ATTRIBUTE = 'data-base-map',                 // HTML attribute containing the base map options
      CONTROLS_ATTRIBUTE = 'data-controls',                 // HTML attribute containing the controls options
      DRAW_ATTRIBUTE = 'data-draw',                         // HTML attribute containing the drawing options
      LAYERS_ATTRIBUTE = 'data-layers',                     // HTML attribute containing the layers options
      LEGEND_ATTRIBUTE = 'data-legend',                     // HTML attribute containing the legend options
      VIEW_ATTRIBUTE = 'data-view';                         // HTML attribute containing the view options

  // Objects
  var public_interface,				                              // Object returned by the module
      m_drawing_layer,                                      // Layer for drawing overlays
      m_drawing_interaction,                                // Drawing interaction used for drawing
      m_drag_box_interaction,                               // Drag box interaction used for drawing rectangles
      m_drag_feature_interaction,                           // Drag feature interaction
      m_modify_interaction,                                 // Modify interaction used for modifying features
      m_select_interaction,                                 // Select interaction for modify action
      m_map;					                                      // The map

  // Selectors
  var m_map_target,                                         // Selector for the map container
      m_textarea_target;                                   // Selector for the textarea target

  // Options
  var m_attribute_table_options,                            // Attribute table options json
      m_base_map_options,                                   // Base map options json
      m_controls_options,                                   // Controls options json
      m_draw_options,                                       // Draw options json
      m_layers_options,                                     // Layers options json
      m_legend_options,                                     // Legend options json
      m_view_options;                                       // View options json

  // Others
  var m_draw_id_counter;                                    // Draw id counter

	/************************************************************************
 	*                       PRIVATE METHOD DECLARATIONS
 	*************************************************************************/
  // Initialization Methods
 	var ol_base_map_init, ol_controls_init, ol_drawing_init, ol_layers_init, ol_map_init, ol_view_init, parse_options;

  // Drawing Methods
  var add_drawing_interaction, add_drag_box_interaction, add_drag_feature_interaction, add_modify_interaction,
      draw_end_callback, draw_change_callback, switch_interaction;

  // Feature Parser Methods
  var geojsonify, wellknowtextify;

  // Attribute Table Methods
  var initialize_feature_properties, generate_feature_id, get_feature_properties;

  // Layer Manipulation Methods

  // UI Management Methods
  var update_field;

  // Utility Methods
  var is_defined, in_array;

  // Class Declarations
  var DrawingControl, DragFeatureInteraction;

 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
  /***********************************
   * Initialization Methods
   ***********************************/

  // Initialize the background map
  ol_base_map_init = function()
  {
    // Constants
    var OPEN_STEET_MAP = 'OpenStreetMap',
        BING = 'Bing',
        MAP_QUEST = 'MapQuest';


    // Declarations
    var base_map_layer;

    // Default base map
    base_map_layer = new ol.layer.Tile({
      source: new ol.source.OSM()
    });

    if (is_defined(m_base_map_options)) {
      if (typeof m_base_map_options === 'string') {
        if (m_base_map_options === OPEN_STEET_MAP) {
          // Initialize default open street map layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.OSM()
          });

        } else if (m_base_map_options === BING) {
          // Initialize default bing layer

        } else if (m_base_map_options === MAP_QUEST) {
          // Initialize default map quest layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.MapQuest({layer: 'sat'})
          });

        }

      } else if (typeof m_base_map_options === 'object') {

        if (OPEN_STEET_MAP in m_base_map_options) {
          // Initialize custom open street map layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.OSM(m_base_map_options[OPEN_STEET_MAP])
          });

        } else if (BING in m_base_map_options) {
          // Initialize custom bing layer
          base_map_layer = new ol.layer.Tile({
            preload: Infinity,
            source: new ol.source.BingMaps(m_base_map_options[BING])
          });

        } else if (MAP_QUEST in m_base_map_options) {
          // Initialize custom map quest layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.MapQuest(m_base_map_options[MAP_QUEST])
          });
        }
      }
    }

    // Add the base map to layers
    m_map.addLayer(base_map_layer);
  };

  // Initialize the controls
  ol_controls_init = function()
  {
    // Constants
    var ZOOM_SLIDER = 'ZoomSlider',
        ROTATE = 'Rotate',
        ZOOM_EXTENT = 'ZoomToExtent',
        FULL_SCREEN = 'FullScreen',
        MOUSE_POSITION = 'MousePosition',
        SCALE_LINE = 'ScaleLine';

    var controls;

    // Start with defaults
    controls = ol.control.defaults();

    if (is_defined(m_controls_options)) {
      for (var i = 0; i < m_controls_options.length; i++) {
        var current_control;

        current_control = m_controls_options[i];

        // Handle string case
        if (typeof current_control === 'string') {
          if (current_control === ZOOM_SLIDER) {
            m_map.addControl(new ol.control.ZoomSlider());
          }
          else if (current_control === ROTATE) {
            m_map.addControl(new ol.control.Rotate());
          }
          else if (current_control === ZOOM_EXTENT) {
            m_map.addControl(new ol.control.ZoomToExtent());
          }
          else if (current_control === FULL_SCREEN) {
            m_map.addControl(new ol.control.FullScreen());
          }
          else if (current_control === MOUSE_POSITION) {
            m_map.addControl(new ol.control.MousePosition());
          }
          else if (current_control === SCALE_LINE) {
            m_map.addControl(new ol.control.ScaleLine());
          }

        // Handle object case
        } else if (typeof current_control === 'object') {
          if (ZOOM_SLIDER in current_control){
            m_map.addControl(new ol.control.ZoomSlider(current_control[ZOOM_SLIDER]));
          }
          else if (ROTATE in current_control){
            m_map.addControl(new ol.control.Rotate(current_control[ROTATE]));
          }
          else if (FULL_SCREEN in current_control){
            m_map.addControl(new ol.control.FullScreen(current_control[FULL_SCREEN]));
          }
          else if (MOUSE_POSITION in current_control){
            m_map.addControl(new ol.control.MousePosition(current_control[MOUSE_POSITION]));
          }
          else if (SCALE_LINE in current_control){
            m_map.addControl(new ol.control.ScaleLine(current_control[SCALE_LINE]));
          }
          else if (ZOOM_EXTENT in current_control){
            var control_obj = current_control[ZOOM_EXTENT];

            // Transform coordinates to default CRS
            if ('projection' in control_obj && 'extent' in control_obj) {
              control_obj['extent'] = ol.proj.transformExtent(control_obj['extent'], control_obj['projection'], DEFAULT_PROJECTION);
              delete control_obj['projection'];
            }
            m_map.addControl(new ol.control.ZoomToExtent(control_obj));
          }
        }
      }
    }

    return controls;

  };

  // Initialize the drawing tools
  ol_drawing_init = function()
  {
    // Constants
    var VALID_GEOMETRY_TYPES = ['Polygon', 'Point', 'LineString', 'Box'];
    var INITIAL_FILL_COLOR = 'rgba(255, 255, 255, 0.2)',
        INITIAL_STROKE_COLOR = '#ffcc33',
        INITIAL_POINT_FILL_COLOR = '#ffcc33',
        BUTTON_SPACING = 30,
        BUTTON_OFFSET_UNITS = 'px';

    var controls_added = [],
        button_left_offset = 50,
        initial_drawing_mode = 'Point';

    if (is_defined(m_draw_options)) {
      // Initialize the overlay layer
      m_drawing_layer = new ol.FeatureOverlay({
        style: new ol.style.Style({
          fill: new ol.style.Fill({
            color: INITIAL_FILL_COLOR
          }),
          stroke: new ol.style.Stroke({
            color: INITIAL_STROKE_COLOR,
            width: 2
          }),
          image: new ol.style.Circle({
            radius: 4,
            fill: new ol.style.Fill({
              color: INITIAL_POINT_FILL_COLOR
            })
          }),
        })
      });

      // Add layer to the map
      m_drawing_layer.setMap(m_map);

      // Set initial drawing interaction
      if (is_defined(m_draw_options.initial) &&
          in_array(m_draw_options.initial, VALID_GEOMETRY_TYPES) &&
          is_defined(m_draw_options.controls) &&
          in_array(m_draw_options.initial, m_draw_options.controls)
      ) {
        initial_drawing_mode = m_draw_options.initial;
      }

      switch_interaction(initial_drawing_mode);
      
      // Add drawing controls to the map
      if (is_defined(m_draw_options.controls)) {
        var draw_controls = m_draw_options.controls;

        // Add modify control first
        if (in_array('Modify', draw_controls)) {
          var modify_control;

          modify_control = new DrawingControl({
            control_type: 'modify',
            left_offset: button_left_offset.toString() + BUTTON_OFFSET_UNITS,
            active: false
          });


          button_left_offset += BUTTON_SPACING;
          m_map.addControl(modify_control);
        }

        if (in_array('Move', draw_controls)) {
          var drag_feature_control;

          // Add drag feature control next
          drag_feature_control = new DrawingControl({
            control_type: 'drag',
            left_offset: button_left_offset.toString() + BUTTON_OFFSET_UNITS,
            active: false
          });

          button_left_offset += BUTTON_SPACING;
          m_map.addControl(drag_feature_control);
        }

        for (var i = 0; i < draw_controls.length; i++) {

          var current_control_type = draw_controls[i];

          if (in_array(current_control_type, VALID_GEOMETRY_TYPES) && (!in_array(current_control_type, controls_added))) {
            var offset_string,
                new_control;

            var is_initial = false;

            // Convert offset to string
            offset_string = button_left_offset.toString() + BUTTON_OFFSET_UNITS;

            // Create new control
            if (current_control_type === initial_drawing_mode) {
              is_initial = true;
            }

            new_control = new DrawingControl({
              control_type: current_control_type,
              left_offset: offset_string,
              active: is_initial
            });

            m_map.addControl(new_control);

            // Stash and increment
            controls_added.push(current_control_type);
            button_left_offset += BUTTON_SPACING;
          }
        }
      }
    }
  };

  // Initialize the layers
  ol_layers_init = function()
  {
    // Constants
    var GEOJSON = 'GeoJSON',
        IMAGE_WMS = 'WMS',
        KML = 'KML',
        VECTOR = 'Vector',
        TILED_WMS = 'TiledWMS';

    if (is_defined(m_layers_options)) {
      for (var i = 0; i < m_layers_options.length; i++) {
        var current_layer,
            layer;

        current_layer = m_layers_options[i];

        if (GEOJSON in current_layer) {
          layer = new ol.layer.Vector({
            source: ol.source.GeoJSON(current_layer[GEOJSON])
          });

        }
        else if (IMAGE_WMS in current_layer) {
          layer = new ol.layer.Image({
            source: new ol.source.ImageWMS(current_layer[IMAGE_WMS])
          });

        }
        else if (KML in current_layer) {
          layer = new ol.layer.Vector({
            source: new ol.source.KML(current_layer[KML])
          });

        }
        else if (VECTOR in current_layer) {

        }
        else if (TILED_WMS in current_layer) {
          layer = new ol.layer.Tile({
            source: new ol.source.TileWMS(current_layer[TILED_WMS])
          });
        }

        if (typeof layer !== typeof undefined) {
          m_map.addLayer(layer);
        }
      }
    }

    //layer = new ol.layer.Image({
    //  source: new ol.source.ImageWMS({
    //    url: 'http://192.168.59.103:8181/geoserver/wms',
    //    params: {'LAYERS': 'topp:states'},
    //    serverType: 'geoserver'
    //  })
    //});

    //m_map.addLayer(layer);

  };

  // Initialize the map
 	ol_map_init = function()
  {
    // Init Map
    m_map = new ol.Map({
      target: m_map_target,
      view: new ol.View({
        center: [0, 0],
        zoom: 2,
        minZoom: 0,
        maxZoom: 28
      })
    });
  };

  // Initialize the map view
  ol_view_init = function()
  {
    // Declarations
    var view_json;

    // Get view settings from data attribute
    view_json = $('#' + m_map_target).attr('data-view');

    if (typeof view_json !== typeof undefined && view_json !== false) {
      var view_obj;

      view_obj = JSON.parse(view_json);

      if ('projection' in view_obj && 'center' in view_obj) {
        // Transform coordinates to default CRS
        view_obj['center'] = ol.proj.transform(view_obj['center'], view_obj['projection'], DEFAULT_PROJECTION);
        delete view_obj['projection'];
      }

      m_map.setView(new ol.View(view_obj));
    }

  };

  parse_options = function ()
  {
    var $map_element = $('#' + m_map_target);

    // Read attributes
    m_attribute_table_options = $map_element.attr(ATTRIBUTE_TABLE_ATTRIBUTE);
    m_base_map_options = $map_element.attr(BASE_MAP_ATTRIBUTE);
    m_controls_options = $map_element.attr(CONTROLS_ATTRIBUTE);
    m_draw_options = $map_element.attr(DRAW_ATTRIBUTE);
    m_layers_options = $map_element.attr(LAYERS_ATTRIBUTE);
    m_legend_options = $map_element.attr(LEGEND_ATTRIBUTE);
    m_view_options = $map_element.attr(VIEW_ATTRIBUTE);

    // Parse JSON
    if (is_defined(m_attribute_table_options)) {
      m_attribute_table_options = JSON.parse(m_attribute_table_options);
    }

    if (is_defined(m_base_map_options)) {
      m_base_map_options = JSON.parse(m_base_map_options);
    }

    if (is_defined(m_controls_options)) {
      m_controls_options = JSON.parse(m_controls_options);
    }

    if (is_defined(m_draw_options)) {
      m_draw_options = JSON.parse(m_draw_options);
    }

    if (is_defined(m_layers_options)) {
      m_layers_options = JSON.parse(m_layers_options);
    }

    if (is_defined(m_legend_options)) {
      m_legend_options = JSON.parse(m_legend_options);
    }

    if (is_defined(m_view_options)) {
      m_view_options = JSON.parse(m_view_options);
    }
  };

  /***********************************
   * Drawing Methods
   ***********************************/
  add_drawing_interaction = function(geometry_type) {
    // Create new drawing interaction
    m_drawing_interaction = new ol.interaction.Draw({
      features: m_drawing_layer.getFeatures(),
      type: geometry_type
    });

    // Bind events to the interaction
    m_drawing_interaction.on('drawend', function(event) {
      draw_end_callback(event.feature);
    });

    // Add new drawing interaction to map
    m_map.addInteraction(m_drawing_interaction);
  };

  add_drag_box_interaction = function() {
    // Add a drag box interaction
    m_drag_box_interaction = new ol.interaction.DragBox({
      condition: ol.events.condition.noModifierKeys,
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: '#0099ff',
          width: 3
        })
      })
    });

    // Capture bounds and add to drawn feature layer on drag box end
    m_drag_box_interaction.on('boxend', function(event){
      var extent, feature;

      // Get extent of bounding box
      extent = this.getGeometry().getExtent();

      // Create a new feature with extent
      feature = new ol.Feature({
        geometry: new ol.geom.Polygon.fromExtent(extent)
      });

      // Add feature to drawing layer
      m_drawing_layer.addFeature(feature);

      // Call draw end callback
      draw_end_callback(feature);
    });

    m_map.addInteraction(m_drag_box_interaction);

  };

  add_drag_feature_interaction = function() {
    // Add Drag feature interaction
    m_drag_feature_interaction = new DragFeatureInteraction();
    m_map.addInteraction(m_drag_feature_interaction);
  };

  add_modify_interaction = function() {
    // Modify interaction works in conjunction with a selection interaction
    var selected_features;

    selected_features = null;

    // Create select interaction
    m_select_interaction = new ol.interaction.Select();
    m_map.addInteraction(m_select_interaction);

    // Get selected features
    selected_features = m_select_interaction.getFeatures();

    // Create modify interaction
    m_modify_interaction = new ol.interaction.Modify({
      features: selected_features,
      deleteCondition: function(event) {
        return ol.events.condition.shiftKeyOnly(event) && ol.events.condition.singleClick(event);
      }
    });
    m_map.addInteraction(m_modify_interaction);
  };

  draw_end_callback = function(feature) {
    // Initialize the feature properties
    initialize_feature_properties(feature);

    // Bind change event to new feature
    feature.on('change', draw_change_callback);

    // Update the field
    update_field();
  };

  draw_change_callback = function(event) {
    update_field();
  };

  switch_interaction = function(interaction_type)
  {
    // Remove all interactions
    m_map.removeInteraction(m_drawing_interaction);
    m_map.removeInteraction(m_select_interaction);
    m_map.removeInteraction(m_modify_interaction);
    m_map.removeInteraction(m_drag_feature_interaction);
    m_map.removeInteraction(m_drag_box_interaction);

    // Set appropriate drawing interaction
    if (interaction_type === 'modify') {
      add_modify_interaction();
    } else if (interaction_type === 'drag') {
      add_drag_feature_interaction();
    } else if (interaction_type === 'Box') {
      add_drag_box_interaction();
    } else {
      add_drawing_interaction(interaction_type);
    }
  };

  /***********************************
   * Feature Parser Methods
   ***********************************/
  geojsonify = function()
  {
    var features, geometry_collection;

    // Get the features
    features = m_drawing_layer.getFeatures();

    // Setup geometry collection
    geometry_collection = {'type': 'GeometryCollection',
                           'geometries': []};

    features.forEach(function(feature){
      var geojson, crs, coordinates, properties,
          geometry, map_crs, geom_type;

      // Clone geometry so transformation doesn't affect features on the map
      geometry = feature.getGeometry().clone();
      geom_type = geometry.getType();

      // Transform the CRS to standard Lat-Long: EPSG-4326
      map_crs = m_map.getView().getProjection();
      geometry = geometry.transform(map_crs, 'EPSG:4326');

      // Get coordinates
      coordinates = geometry.getCoordinates();

      // Create CRS
      crs = {
        type: 'link',
        properties: {
           href: 'http://spatialreference.org/ref/epsg/4326/proj4/',
           type: 'proj4'
        }
      };

      // Parse Properties
      properties = get_feature_properties(feature);

      // Formulate GeoJSON
      geojson = {
        type: geom_type,
        coordinates: coordinates,
        properties: properties,
        crs: crs
      };

      geometry_collection.geometries.push(geojson);
    });

    return geometry_collection;
  };

  wellknowtextify = function()
  {
    var features, geometry_collection;

    // Get the features
    features = m_drawing_layer.getFeatures();

    // Setup geometry collection
    geometry_collection = {'type': 'GeometryCollection',
                           'geometries': []};

    features.forEach(function(feature){
      var wktjson, wkt, crs, coordinates, properties,
          geometry, map_crs, geom_type;

      // Clone geometry so transformation doesn't affect features on the map
      geometry = feature.getGeometry().clone();
      geom_type = geometry.getType();

      // Transform the CRS to standard Lat-Long: EPSG-4326
      map_crs = m_map.getView().getProjection();
      geometry = geometry.transform(map_crs, 'EPSG:4326');

      // Get coordinates
      coordinates = geometry.getCoordinates();

      // Assemble well know text parameters
      wkt = '';

      if (geom_type === 'Point') {
        wkt = 'POINT(' + coordinates[0] + ' ' + coordinates[1] + ')';

      } else if (geom_type === 'Polygon') {
        var first_coordinate = geometry.getFirstCoordinate();
        wkt = 'POLYGON((';

        for (var i = 0; i < coordinates[0].length; i++) {
          var pair = coordinates[0][i];
          wkt += pair[0] + ' ' + pair[1] + ', ';
        }

        wkt += (first_coordinate[0] + ' ' + first_coordinate[1] + '))');

      } else if (geom_type === 'LineString') {
        var pairs = [];

        wkt = 'POLYLINE(';

        for (var i = 0; i < coordinates.length; i++) {
          var pair = coordinates[i];
          var wkt_pair = pair[0] + ' ' + pair[1];
          pairs.push(wkt_pair);
        }

        wkt += pairs.join(', ') + ')';
      }

      // Create CRS
      crs = {
        type: 'link',
        properties: {
           href: 'http://spatialreference.org/ref/epsg/4326/proj4/',
           type: 'proj4'
        }
      };

      // Parse Properties
      properties = get_feature_properties(feature);

      // Formulate WKT JSON
      wktjson = {
        type: geom_type,
        wkt: wkt,
        properties: properties,
        crs: crs
      };

      geometry_collection.geometries.push(wktjson);
    });

    return geometry_collection;
  };

  /***********************************
   * Attribute Table Methods
   ***********************************/
  generate_feature_id = function() {
    var id = m_draw_id_counter;
    ++m_draw_id_counter;
    return id;
  };

  get_feature_properties = function(feature) {
    var feature_properties, properties;

    properties = {id: feature.getId()};
    feature_properties = feature.getProperties();

    for (var property in feature_properties) {
      if (property != 'geometry') {
        properties[property] = feature_properties[property];
      }
    }

    return properties;
  };

  initialize_feature_properties = function(feature) {
    // Set the id
    feature.setId(generate_feature_id());

    // Initialize with properties and defaults provided
    //feature.setProperties({
    //  'prop1': 1,
    //  'prop2': 'cool'
    //});
  };

  /***********************************
   * Layer Manipulation Methods
   ***********************************/

  /***********************************
   * Initialization Methods
   ***********************************/
  update_field = function() {
    var $textarea,
        textarea_string;

    $textarea = $('#' + m_textarea_target);
    textarea_string = '';

    // Default output format to GeoJSON
    if (is_defined(m_draw_options.output_format)) {
      if (m_draw_options.output_format === WKT_FORMAT) {
        textarea_string = JSON.stringify(wellknowtextify());
      } else {
        textarea_string = JSON.stringify(geojsonify());
      }
    } else {
      textarea_string = JSON.stringify(geojsonify());
    }

    // Set value of textarea
    $textarea.val(textarea_string);
  };

  /***********************************
   * Utility Methods
   ***********************************/
  in_array = function(item, array)
  {
    return array.indexOf(item) !== -1;
  };

  is_defined = function(variable)
  {
    return !!(typeof variable !== typeof undefined && variable !== false);
  };

  /***********************************
   * Class Implementations
   ***********************************/
  DrawingControl = function(opt_options) {
    var options,
        button,
        button_image,
        button_wrapper,
        icon_class,
        handle_drawing_interaction_switch;

    options = opt_options || {};

    // Create Button
    icon_class = 'tethys-map-view-draw-icon ' + options.control_type.toLowerCase();

    if (is_defined(options.active) && options.active === true) {
      icon_class += ' active';
    }

    button = document.createElement('button');
    button_image = document.createElement('div');
    button_image.className = icon_class;
    button.appendChild(button_image);
    button_wrapper = document.createElement('div');
    button_wrapper.className = 'tethys-map-view-draw-control ol-unselectable ol-control';
    button_wrapper.style.left = options.left_offset;
    button_wrapper.appendChild(button);

    // Create action handler
    handle_drawing_interaction_switch = function(event) {

      // Switch Interaction
      switch_interaction(options.control_type);

      // Reset button active state
      $('.tethys-map-view-draw-icon').each(function(){
        $(this).removeClass('active');
      });

      // Set current button to active state
      $(event.toElement).addClass('active');
    };

    // Bind switch action to click and touch events
    button.addEventListener('click', handle_drawing_interaction_switch, false);
    button.addEventListener('touchstart', handle_drawing_interaction_switch, false);

    // Call parent constructor
    ol.control.Control.call(this, {
      element: button_wrapper,
      target: options.target
    });
  };
  ol.inherits(DrawingControl, ol.control.Control);

  // Custom interaction for dragging and moving features
  // Credits: http://openlayers.org/en/v3.3.0/examples/drag-features.html?q=drag
  DragFeatureInteraction = function() {
    ol.interaction.Pointer.call(this, {
      handleDownEvent: DragFeatureInteraction.prototype.handleDownEvent,
      handleDragEvent: DragFeatureInteraction.prototype.handleDragEvent,
      handleMoveEvent: DragFeatureInteraction.prototype.handleMoveEvent,
      handleUpEvent: DragFeatureInteraction.prototype.handleUpEvent
    });

    this.coordinate_ = null;
    this.cursor_ = 'pointer';
    this.feature_ = null;
    this.previousCursor_ = undefined;

  };
  ol.inherits(DragFeatureInteraction, ol.interaction.Pointer);

  // Trigger a drag feature
  DragFeatureInteraction.prototype.handleDownEvent = function(event) {
    var map = event.map;

    var feature = map.forEachFeatureAtPixel(event.pixel,
        function(feature, layer) {
          return feature;
        });

    if (feature) {
      this.coordinate_ = event.coordinate;
      this.feature_ = feature;
    }

    return !!feature;
  };
  
  // Handle drag feature
  DragFeatureInteraction.prototype.handleDragEvent = function(event) {
    var map = event.map;

    var feature = map.forEachFeatureAtPixel(event.pixel,
        function(feature, layer) {
          return feature;
        });

    var deltaX = event.coordinate[0] - this.coordinate_[0];
    var deltaY = event.coordinate[1] - this.coordinate_[1];

    var geometry = /** @type {ol.geom.SimpleGeometry} */
        (this.feature_.getGeometry());
    geometry.translate(deltaX, deltaY);

    this.coordinate_[0] = event.coordinate[0];
    this.coordinate_[1] = event.coordinate[1];
  };

  // Handle map movement
  DragFeatureInteraction.prototype.handleMoveEvent = function(event) {
    if (this.cursor_) {
      var map = event.map;
      var feature = map.forEachFeatureAtPixel(event.pixel,
          function(feature, layer) {
            return feature;
          });
      var element = event.map.getTargetElement();
      if (feature) {
        if (element.style.cursor != this.cursor_) {
          this.previousCursor_ = element.style.cursor;
          element.style.cursor = this.cursor_;
        }
      } else if (this.previousCursor_ !== undefined) {
        element.style.cursor = this.previousCursor_;
        this.previousCursor_ = undefined;
      }
    }
  };

  // Un-trigger drag feature
  DragFeatureInteraction.prototype.handleUpEvent = function(event) {
    this.coordinate_ = null;
    this.feature_ = null;
    return false;
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

  function get_map() {
    return m_map;
  }

  function get_target() {
    return m_map_target;
  }

  public_interface = {
    getMap: get_map,
    getTarget: get_target
  };

  /************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
    // Map container selector
    m_map_target = 'map_view';
    m_textarea_target = 'map_view_geometry';

    m_draw_id_counter = 1;

    // Parse options
    parse_options();

    // Initialize the map
    ol_map_init();

    // Initialize controls
    ol_controls_init();

    // Initialize base map
    ol_base_map_init();

    // Initialize layers
    ol_layers_init();

    // Initialize View
    ol_view_init();

    // Initialize Drawing
    ol_drawing_init();

	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.