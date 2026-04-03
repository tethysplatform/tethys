.. _wms_layer_map_view_recipe :


******************
WMS Layer MapView
******************

**Last Updated:** October 2025

This recipe builds on the :ref:`MapView Recipe <add_map_view_recipe>` and the :ref:`GeoServer Shapefile Upload Recipe <upload_shape_file_to_geoserver_recipe>`

In this recipe you'll learn to add a WMS layer to your MapView Gizmo's interactive map. WMS Layers are often used to display GeoServer or THREDDS server assets on a map.

Add WMS Layer to MapView
########################

Add the following code to your controller with your MapView Gizmo:

.. code-block:: python

    geoserver_layer = MVLayer(
        source='ImageWMS',
        options={'url': 'http://localhost:8181/geoserver/wms',
            'params': {'LAYERS': 'topp:states'},
            'serverType': 'geoserver'},
        legend_title='USA Population',
        legend_extent=[-126, 24.5, -66.2, 49],
    )


Next, add this layer to your MapView Gizmo:

.. code-block:: python
    
    map_view = MapView(
            height='100%',
            width='100%',
            controls=[
                'ZoomSlider', 'Rotate', 'FullScreen',
                {'ZoomToExtent': {
                    'projection': 'EPSG:4326',
                    'extent': [29.25, -4.75, 46.25, 5.2]
                }}
            ],
            basemap=[
                'CartoDB',
                {'CartoDB': {'style': 'dark'}},
                'OpenStreetMap',
                'ESRI'
            ],
            view=MVView(
                projection='EPSG:4326',
                center=[-95.5, 36.5],
                zoom=4,
                maxZoom=18,
                minZoom=2
            ),
            layers=[geoserver_layer]
        )

That's all you need to do! Open your app and you should see this on your map:

.. figure:: ../../images/recipes/wms_map_view_screenshot.png
    :width: 500px
    :align: center


