.. _wms_layer_map_layout_recipe :


********************
WMS Layer Map Layout
********************

tasmania_cities

**Last Updated:** October 2025

This recipe will show you how to add a WMS layer to a map layout. WMS Layers are often used to display GeoServer or THREDDS server assets on a map.


Start with the :ref:`Map Layout Recipe <add_map_layout_recipe>` and the :ref:`GeoSever Shapefile Upload Recipe <upload_shape_file_to_geoserver_recipe>`.

Add WMS Layer to MapLayout
##########################

Add the following code to your MapLayout class:

.. code-block:: python
    :emphasize-lines: 5-32

    class MyMapLayout(MapLayout):

        ...

        def compose_layers(self, request, map_view, *args, **kwargs):
            """
            Add layers to the MapLayout and create associated layer group objects.
            """
            geoserver_layer = self.build_wms_layer(
                endpoint='http://localhost:8181/geoserver/wms',
                server_type='geoserver',
                layer_name='topp:states',
                layer_title='U.S. States',
                layer_variable='us_states',
                visible=True,
            )

            map_view.layers.append(geoserver_layer)

            layer_groups = [
                self.build_layer_group(
                    id="geoserver-layer-group",
                    display_name='U.S. States',
                    layer_control='radio',
                    layers=[
                        geoserver_layer
                    ],
                )
            ]

            return layer_groups

And that's it! Open your app and you should see this:

.. figure:: ../../images/recipes/wms_map_layout_screenshot.png
    :width: 500px
    :align: center