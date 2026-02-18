.. _geojson_layer_map_view_recipe:

********************************
Add an ArcGIS REST Layer to a MapView
********************************

**Last Updated:** October 2025

This recipe builds on the :ref:`MapView Recipe <add_map_view_recipe>`

This recipe will show you how to add an ArcGIS REST layer to your MapView Gizmo.


Add ArcGIS Rest Layer to Map View
#############################

In order to display that data on the map, you'll need to add a GEOJSON layer. Add the following code to your controller function:

.. code-block:: python

    from tethys_sdk.gizmos import MapView, MVView, MVLayer
    ...

    arcgis_layer = MVLayer(
        source='TileArcGISRest',
        options={'url': 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/USA/MapServer',
                 'params': {
                    'layers': 'show:0',
                },
        },
        legend_title='U.S. Cities',
        feature_selection=True
    )

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
            center=[-120, 37],
            zoom=3,
            maxZoom=18,
            minZoom=2
        ),
        layers=[arcgis_layer]
    )
    ...

That's it! Open your app and now you should have a set of features representing U.S. cities showing up on your map, just like this:

.. figure:: ../../images/recipes/arcgis_layer_map_view_screenshot.png
    :width: 500px
    :align: center