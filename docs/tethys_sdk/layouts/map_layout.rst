.. _map_layout:

**************
Map Layout API
**************

**Last Updated:** March 2022

The ``MapLayout`` provides a drop-in full-screen map view for Tethys Apps. Displaying a map with a few layers can be accomplished in tens of lines of code and implementing more advanced functionality can be accomplished in hundreds It includes a layer tree with visibility controls and actions such as "Zoom to Layer". The view can also includes many optional features such as displaying legends for layers, feature selection, map annotation / drawing tools, location lookup via geocoding, and a click-and-plot feature.

Setup
=====

Setting up a new ``MapLayout`` involves the following steps:

1. Create a new class in :file:`controllers.py` that inherits from ``MapLayout``.
2. Decorate the new class with the :ref:`controller-decorator` to set up routing. 
3. Configure the new ``MapLayout`` by setting properties on the new class. Review the :ref:`MapLayout properties <map_layout_properties>` for a full list. For example, set the ``map_title`` property to set the title of the view that appears in the navigation bar. 

The following example demonstrates how to create a new ``MapLayout`` view:

.. code-block:: python

    from django.urls import reverse_lazy
    from tethys_sdk.layouts import MapLayout
    from tethys_sdk.routing import controller


    @controller(
        name="map",
        url="my_first-app/map"
    )
    class MyMapLayout(MapLayout):
        app = app
        base_template = 'my_first_app/base.html'
        back_url = reverse_lazy('my_first_app:home')
        map_title = 'My Map Layout'
        map_subtitle = 'Subtitle'
        basemaps = [
            'OpenStreetMap',
            'ESRI',
            'Stamen',
            {'Stamen': {'layer': 'toner', 'control_label': 'Black and White'}},
        ]
        default_center = [-98.583, 39.833]  # USA Center
        initial_map_extent = [-65.69, 23.81, -129.17, 49.38]  # USA EPSG:2374
        default_zoom = 5
        max_zoom = 16
        min_zoom = 2


Add Layers
==========

To add layers to the map in a ``MapLayout``, override the :ref:`compose_layers <map_layout_compose_layers>` method. The ``MapLayout`` view uses the :ref:`MapView Gizmo <map-view>` under the covers and it is given to the ``compose_layers()`` method via the ``map_view`` argument. Use the ``map_view`` argument to add new :ref:`MVLayers <gizmo_mvlayer>` to the ``MapView``.

While the ``MapView`` Gizmo will be able to accept any ``MVLayer`` object, the ``MapLayout`` needs layers to have additional metadata attached for them to be recognized by the layers in the Layer Tree, legend, and other features of ``MapLayout``. Several helper methods are provided by ``MapLayout`` to assist with building ``MVLayer`` objects in the correct way: :ref:`build_wms_layer() <map_layout_build_wms_layer>`, :ref:`build_geojson_layer() <map_layout_build_geojson_layer>`, and :ref:`build_arc_gis_layer() <map_layout_build_arc_gis_layer>`.

In addition, the ``compose_layers()`` method needs to return a ``list`` of at least one Layer Group. A Layer Group contains a list of layers and is used by the Layer Tree of ``MapLayout`` to organize layers. In addition, a control type is specified for each Layer Group (``'check' or 'radio'``), and can be used to control whether all the layers in a Layer Group can be viewed simultaneously (``'check'``) or only one at a time (``'radio'``). Create Layer Groups using the :ref:`map_layout_build_layer_group` helper method.

WMS Layer
---------

The following example demonstrates how to add WMS layers to a ``MapLayout`` using the ``build_wms_layer`` method:

.. code-block:: python

    @controller(
        name="map",
        url="my_first-app/map"
    )
    class MyMapLayout(MapLayout):

        ...

        def compose_layers(self, request, map_view, *args, **kwargs):
            """
            Add layers to the MapLayout and create associated layer group objects.
            """
            # WMS Layer
            usa_population = self.build_wms_layer(
                endpoint='http://localhost:8181/geoserver/wms',
                server_type='geoserver',
                layer_name='topp:states',
                layer_title='USA Population',
                layer_variable='population',
                visible=True,  # Set to False if the layer should be hidden initially
            )

            # Add layer to map
            map_view.layers.append(usa_population)

            # Add layer to layer group
            layer_groups = [
                self.build_layer_group(
                    id='usa-layer-group',
                    display_name='United States',
                    layer_control='radio',  # 'radio' or 'check'
                    layers=[
                        usa_population,
                    ],
                ),
            ]

            return layer_groups


.. caution::

    The ellipsis (`...`) in code examples indicate code that is not shown for brevity. **DO NOT COPY VERBATIM**.

GeoJSON Layers
--------------

The following example demonstrates how to add a GeoJSON layer to a ``MapLayout`` using the ``build_geojson_layer`` method:

.. code-block:: python

    @controller(
        name="map",
        url="my_first-app/map"
    )
    class MyMapLayout(MapLayout):

        ...

        def compose_layers(self, request, map_view, *args, **kwargs):
            """
            Add layers to the MapLayout and create associated layer group objects.
            """
            # Load GeoJSON From File
            us_states_path = Path(app_workspace.path) / 'my_first_app' / 'us-states.json'
            with open(us_states_path) as gj:
                us_states_geojson = json.loads(gj.read())

            # GeoJSON Layer
            us_states_layer = self.build_geojson_layer(
                geojson=us_states_geojson,
                layer_name='us-states',
                layer_title='U.S. States',
                layer_variable='reference',
                visible=True,
            )

            # Add layer to map
            map_view.layers.append(us_states_layer)

            # Add layer to layer group
            ...

Vector Layer Styles
+++++++++++++++++++

Use the ``get_vector_style_map`` method of ``MapLayout`` to define custom styles for GeoJSON layers. The method expects a dictionary to be returned containing keys that coorespond to feature types (e.g.: "Point", "LineString", "Polygon") and values that are the style definition. The style definitions are created using a Python dictionary syntax that mirrors the `OpenLayers Style API <https://openlayers.org/en/latest/examples/geojson.html>`_. The For example:

.. code-block:: python

    @controller(
        name="map",
        url="my_first-app/map"
    )
    class MyMapLayout(MapLayout):

        ...
        @classmethod
        def get_vector_style_map(cls):
            return {
                'Point': {'ol.style.Style': {
                    'image': {'ol.style.Circle': {
                        'radius': 5,
                        'fill': {'ol.style.Fill': {
                            'color': 'red',
                        }},
                        'stroke': {'ol.style.Stroke': {
                            'color': 'red',
                            'width': 2
                        }}
                    }}
                }},
                'LineString': {'ol.style.Style': {
                    'stroke': {'ol.style.Stroke': {
                        'color': 'green',
                        'width': 3
                    }}
                }},
                'MultiPolygon': {'ol.style.Style': {
                    'stroke': {'ol.style.Stroke': {
                        'color': 'blue',
                        'width': 3
                    }}
                }},
                'Polygon': {'ol.style.Style': {
                    'stroke': {'ol.style.Stroke': {
                        'color': 'blue',
                        'width': 3
                    }}
                }},
            }

ArcGIS REST Layer
-----------------

The following example demonstrates how to add an ArcGIS REST layer to a ``MapLayout`` using the ``build_arc_gis_layer`` method:

.. code-block:: python

    @controller(
        name="map",
        url="my_first-app/map"
    )
    class MyMapLayout(MapLayout):

        ...

        def compose_layers(self, request, map_view, *args, **kwargs):
            """
            Add layers to the MapLayout and create associated layer group objects.
            """
            # ArcGIS Layer
            us_highways_layer = self.build_arc_gis_layer(
                endpoint='https://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer',
                layer_name='ESRI_StateCityHighway',
                layer_title='US Highways',
                layer_variable='highways',
                visible=False,
                extent=[-173, 17, -65, 72],
            )

            # Add layer to map
            map_view.layers.append(us_highways_layer)

            # Add layer to layer group
            ...

.. _map_layout_feature_selection:

Feature Selection
=================

The ``MapLayout`` layout supports two modes of feature selection: Feature Selection for Vector Layers and Feature Selection for WMS Layers. Although similar in functionality, the selection is handled differently and mixing the two is not recommended.

Vector Layers
-------------

Feature Selection for Vector Layers, such as GeoJSON layers, can be enabled on a layer-by-layer basis by setting the ``selectable`` argument to ``True``. Select features by clicking on the feature and select multiple layers by holding the ``SHIFT`` key while clicking on features.

.. code-block:: python

    # Load GeoJSON From File
    us_states_path = Path(app_workspace.path) / 'my_first_app' / 'us-states.json'
    with open(us_states_path) as gj:
        us_states_geojson = json.loads(gj.read())

    # GeoJSON Layer
    us_states_layer = self.build_geojson_layer(
        geojson=us_states_geojson,
        layer_name='us-states',
        layer_title='U.S. States',
        layer_variable='reference',
        visible=True,
        selectable=True
    )

.. note::

    Clicking inside a polygon feature will not select it. Instead, click on the border of the polygon to select it.

JavaScript
++++++++++

Use the ``getSelectInteraction()`` method of the underlying ``MapView`` Gizmo to bind functions to the Vector feature selection event:

.. code-block:: javascript

    window.addEventListener('load', function() { // wait for page to load
        let selection_interaction = TETHYS_MAP_VIEW.getSelectInteraction();

        // Called each time the select interaction's list of features changes
        selection_interaction.getFeatures().on('change:length', function(e) {
            // Check if there is at least 1 feature selected
            if (e.target.getLength() > 0) {
                // Do something with the feature
                let selected_feature = e.target.item(0); // 1st feature in Collection
                console.log(`Selected State: ${selected_feature.get('name')}`);
            }
        });
    });

.. tip::

    See the :ref:`map_layout_custom_template` section for how to define a custom template for a ``MapLayout`` and add custom JavaScript.

WMS Layers
----------

``MapLayout`` also supports feature selection for WMS layers that are hosted by a GeoServer and are derived from a vector source (e.g. created from a Shapefile or SQLView). Enabling feature selection is done on a layer by layer basis by setting the ``selectable`` argument to ``True`` as shown in the example below:

.. code-block:: python

    # WMS Layer
    usa_population = self.build_wms_layer(
        endpoint='http://localhost:8181/geoserver/wms',
        server_type='geoserver',
        layer_name='topp:states',
        layer_title='USA Population',
        layer_variable='population',
        visible=True,  # Set to False if the layer should be hidden initially
        selectable=True
    )

Geometry attribute
++++++++++++++++++

The ``build_wms_layer`` method takes an additional feature-selection related argument that is sometimes necessary: ``geometry attribute``. Use this argument to specify a different value if the partiuclar layer uses a different naming convention for the feature attribute that stores the geometry. The default value for ``geometry_attribute`` is ``"the_geom"``. For example:

.. code-block:: python

    # WMS Layer
    usa_population = self.build_wms_layer(
        endpoint='http://localhost:8181/geoserver/wms',
        server_type='geoserver',
        layer_name='topp:states',
        layer_title='USA Population',
        layer_variable='population',
        visible=True,  # Set to False if the layer should be hidden initially
        selectable=True,
        geometry_attribute='geometry',  # Defaults to "the_geom"
    )

Class Properties
++++++++++++++++

There are two class properties that can be used to modify the behavior of the WMS feature selection: ``feature_selection_multiselect`` and ``feature_selection_sensitivity``.

Set ``feature_selection_multiselect`` to ``True`` to allow selecting multiple features from WMS layers that have feature selection enabled. This is done by holding the ``SHIFT`` key while selecting. The default behavior is to allow only one feature to be selected at a time.

set the ``feature_selection_sensitivty`` to adjust the relative search radius around the clicked point of the selection algorithm. The default value is 4.

.. code-block:: python

    class MyMapLayout(MapLayout):
        feature_selection_multiselect = True
        feature_selection_sensitivty = 8

Property Popups
===============

Enable pop-ups displaying the properties of selected features by setting the ``show_properties_popup`` to ``True``:


.. code-block:: python

    class MyMapLayout(MapLayout):
        show_properties_popup = True

.. note::
    
    This feature only works for the layer types supported by :ref:`map_layout_feature_selection`. 

Exclude properties from being displayed in the properties pop-ups using the ``excluded_properties`` argument of the build methods. The ``id``, ``type``, ``geometry``, ``the_geom``, and ``layer_name`` properties are automatically excluded.

.. code-block:: python

    # WMS Layer
    usa_population = self.build_wms_layer(
        endpoint='http://localhost:8181/geoserver/wms',
        server_type='geoserver',
        layer_name='topp:states',
        layer_title='USA Population',
        layer_variable='population',
        visible=True,  # Set to False if the layer should be hidden initially
        selectable=True,
        geometry_attribute='geometry',  # Defaults to "the_geom"
        excluded_properties=['STATE_FIPS', 'SUB_REGION'],
    )

.. note::

    Names of properties displayed in pop-ups have been reformatted by replacing any underscores (``_``) or hyphens (``-``) with spaces and changing the case to title case. For example, a property called ``STATE_FIPS`` would be displayed as ``State Fips``. You must specify the pre-formatted/original version of the property name for the ``excluded_properties`` argument.

Map Clicks
==========



Click and Plot
==============



Drawing Tools
=============



Enable GeoCoding
================



Add Legends
===========

Coming Soon...

.. _map_layout_custom_template:

Custom Template
===============

The HTML template for the ``MapLayout`` can be customized by creating an HTML document that extends ``tethys_layouts/map_layout/map_layout.html``. This is most often done to add custom CSS or JavaScript to the template as shown in this example:

.. code-block:: html+django

    {% extends "tethys_layouts/map_layout/map_layout.html" %}
    {% load static %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'layout_showcase/js/map.js' %}" type="text/javascript"></script>
    {% endblock %}

Tell the ``MapLayout`` to use the custom template using the ``template_name`` property:

.. code-block:: python

    class MyMapLayout(MapLayout):
        template_name = 'my_first_app/custom_map_layout.html'
        ...

API Documentation
=================

.. _map_layout_class:

MapLayout Class
---------------

.. _map_layout_properties:

Properties
++++++++++

The following properties can be overridden customize the behavior of the ``MapLayout`` view. It is recommended that the following properties be overridden everytime: ``app``, ``base_template``, ``map_subtitle``, and ``map_title``.

.. autoclass:: tethys_layouts.views.map_layout.MapLayout

.. _map_layout_override_methods:

Override Methods
++++++++++++++++

Override these methods to customize the behavior of the ``MapLayout`` for your application. For example, override the ``compose_layers`` method to add layers to the ``MapLayout``.

.. _map_layout_compose_layers:

MapLayout.compose_layers
++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.compose_layers

MapLayout.get_plot_for_layer_feature
++++++++++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.get_plot_for_layer_feature

MapLayout.get_vector_style_map
++++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.get_vector_style_map

MapLayout.should_disable_basemap
++++++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.should_disable_basemap

MapLayout.save_custom_layers
++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.save_custom_layers

MapLayout.remove_custom_layer
+++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.remove_custom_layer

.. _map_layout_methods:

Helper Methods and Properties
+++++++++++++++++++++++++++++

These methods and properties simplify common workflows that are used in ``MapLayout`` implementations. Don't override these unless you know what you are doing.

MapView.map_extent
++++++++++++++++++

.. autoproperty:: tethys_layouts.views.map_layout.MapLayout.map_extent

MapView.default_view
++++++++++++++++++++

.. autoproperty:: tethys_layouts.views.map_layout.MapLayout.default_view

MapLayout.get_initial_map_extent
++++++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.get_initial_map_extent

.. _map_layout_build_wms_layer:

MapLayout.build_wms_layer
+++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_wms_layer

.. _map_layout_build_geojson_layer:

MapLayout.build_geojson_layer
+++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_geojson_layer

.. _map_layout_build_arc_gis_layer:

MapLayout.build_arc_gis_layer
+++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_arc_gis_layer

.. _map_layout_build_layer_group:

MapLayout.build_layer_group
+++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_layer_group

MapLayout.build_legend
++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_legend

MapLayout.generate_custom_color_ramp_divisions
++++++++++++++++++++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.generate_custom_color_ramp_divisions

MapLayout.build_param_string
++++++++++++++++++++++++++++

.. automethod:: tethys_layouts.views.map_layout.MapLayout.build_param_string
