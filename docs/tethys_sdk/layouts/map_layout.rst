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

The following examples demonstrates how to add WMS layers to a ``MapLayout``.

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
                layer_name='topp:states',
                layer_title="USA Population",
                layer_variable='population',
                geometry_attribute='the_geom',
                visible=True,  # Set to False if the layer should be hidden initially
                server_type='geoserver',
            )

            # Add layers to map
            map_view.layers.append(usa_population)

            # Define the layer groups
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

    The ellipsis (`...`) in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Add Legends
===========

Coming Soon...

Feature Selection
=================




Property Popups
===============


Click and Plot
==============


Drawing Tools
=============


Enable GeoCoding
================


API Documentation
=================

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
