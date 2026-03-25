.. _arcgis_layer_map_layout_recipe :


********************
ArcGIS REST Layer Map Layout
********************

**Last Updated:** October 2025

Start with the :ref:`Map Layout Recipe <add_map_layout_recipe>`

In this recipe, you'll learn how to add an ArcGIS REST Map Layer onto your map to display data.

Add ArcGIS REST Layer to Map Layout
###########################

Start by adding the following code to your MapLayout class:

.. code-block:: python
    :emphasize-lines: 9-38

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
            precip_layer = self.build_arc_gis_layer(
                endpoint='https://mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer',
                layer_name='25',  # ArcGIS MapServer Layer ID
                layer_title='RFC QPE Last 24 Hours (inches)',
                layer_variable='precipitation',
                visible=True,
                extent=[-65.69, 23.81, -129.17, 49.38],  # CONUS bbox
            )

            # Add layer to map
            map_view.layers.append(precip_layer)

            # Add layer to layer group
            layer_groups = [
                self.build_layer_group(
                    id='precip-layer-group',
                    display_name='Precipitation',
                    layer_control='radio',
                    layers=[
                        precip_layer
                    ]
                )
            ]

            return layer_groups

Now, go ahead and open your app and refresh the page. You should see something similar to this showing up on top of your map:

.. figure:: ../../images/recipes/arcgis_layer_map_layout_screenshot.png
    :width: 500px
    :align: center