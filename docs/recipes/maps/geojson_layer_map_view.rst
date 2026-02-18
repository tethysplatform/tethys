.. _geojson_layer_map_view_recipe:

********************************
Add a GEOJSON Layer to a MapView
********************************

**Last Updated:** October 2025

This recipe builds on the :ref:`MapView Recipe <add_map_view_recipe>`

This recipe will show you how to add a GEOJSON layer to your MapView Gizmo.


Add GEOJSON Data
################

You'll begin by importing or adding some GEOJSON data. In general, you can import this kind of data from a file, but in this example, you'll just add the necessary data as a dictionary in your :file:`controllers.py` file like so:

.. code-block:: python

    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [37.9298581001699, -0.4095546339709415]
                },
                "properties": {
                    "id": 1,
                    "country": "Kenya"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [96.16675244714385, 58.69226440065236]
                },
                "properties": {
                    "id": 2,
                    "country": "Russia"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-107.54285714285714, 37.55243048451766]
                },
                "properties": {
                    "id": 3,
                    "country": "United States of America"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-102.28571428571428, 20.464738671152944]
                },
                "properties": {
                    "id": 4,
                    "country": "Mexico"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-49.94285714285714, -16.345107903438816]
                },
                "properties": {
                    "id": 5,
                    "country": "Brazil"
                }
            },
        ]
    }

This data defines the coordinates on the map for a set of 5 points, along with some metadata for each point. 


Add GEOJSON Layer to Map View
#############################

In order to display that data on the map, you'll need to add a GEOJSON layer. Add the following code to your controller function:

.. code-block:: python
    :emphasize-lines: 1, 4-9, 34-35

    from tethys_sdk.gizmos import MapView, MVView, MVLayer
    ...

    geojson_layer = MVLayer(
        source='GeoJSON',
        options=geojson_data,
        legend_title='Points',
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
                center=[0,0],
                zoom=1,
                maxZoom=18,
                minZoom=2
            ),
            layers=[geojson_layer]
        )

That's it! Open your app and now you should have a set of features showing up on your map, just like this:

.. figure:: ../../images/recipes/geojson_layer_screenshot.png
    :width: 500px
    :align: center