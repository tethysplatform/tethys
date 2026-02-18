.. _geojson_layer_map_layout_recipe :


******************************
Add a Geojson Layer to Map Layout
******************************

**Last Updated:** October 2025

Start with the :ref:`Map Layout Recipe <add_map_layout_recipe>`

Add GeoJSON Data
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

Add GeoJSON Layer to Map Layout
###############################

In order to display that data on the map, you'll need to add a GeoJSON layer.
Add this method to your MapLayout class:

.. code-block:: python
    :emphasize-lines: 5-30

    @controller(name="home", app_workspace=True)
    class MapLayoutTutorialMap(MapLayout):
    ...

    def compose_layers(self, reuqest, map_view, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        geojson_layer = self.build_geojson_layer(
            geojson=geojson_data,
            layer_name='geojson-layer',
            layer_title='GeoJSON Layer',
            layer_variable='geojson_layer',
            visible=True
        )

        map_view.layers.append(geojson_layer)

        layer_groups = [
            self.build_layer_group(
                id='geojson-layer-group',
                display_name='GeoJSON',
                layer_control='radio',  # 'radio' or 'check'
                layers=[
                    geojson_layer,
                ],
            ),
        ]

        return layer_groups

That's it! Open your app and now you should have a set of features showing up on your map, just like this: 

.. figure:: ../../images/recipes/geojson_layer_screenshot.png
    :width: 500px
    :align: center