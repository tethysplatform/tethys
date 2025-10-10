.. _app_resources_recipe :


App Resources
#############


**Last Updated:** September 2025

This recipe shows how to access the App Resources Path using the Tethys Paths API.

The App Resources Path is generally used for reading app resource files like config files or JSON or GeoJSON files.

For more information on other types of paths that can be used and more info on using the App Resources path, see the :ref:`Paths API documentation <tethys_paths_api>`

Reading from the App Resources Path
***********************************

Here is a common example of a Tethys MapLayout using the App Resources Path to open a geojson file to create a layer that will be displayed on the map:

.. code-block:: python

    from tethys_sdk.layouts import MapLayout
    from tethys_sdk.routing import controller

    @controller(name="home", app_resources=True)
    class ExampleMapLayout(MapLayout):
        ...

        def compose_layers(self, request, map_view, app_resources, *args, **kwargs):
            geojson_path = app_resources.path / "example_file.geojson"
            with open(geojson_path) as f:
                geojson_contents = json.loads(f.read())

            geojson_layer = self.build_geojson_layer(
                geojson=geojson_contents,
                layer_name='Test Layer',
                layer_title='Test Title',
                layer_variable='test_var',
                visible=True,
                selectable=True,
                plottable=True
            )

            layer_groups = [
                self.build_layer_group(
                    id='geojson_features',
                    display_name='GeoJSON Features',
                    layer_control='checkbox',
                    layers=[geojson_layer]
                )
            ]

            return layer_groups

Reading from the App Resources Path
***********************************

You can also access the App Resources path using the following functions/properties:

.. code-block:: python

    from .app import App 

    app_resources_path = App().resources_path.path

.. code-block:: python
    
    from tethys_sdk.paths import get_app_public

    def some_controller(request):
        app_resources_path = get_app_resources(request).path