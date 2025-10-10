.. _click_to_plot_recipe:


*************
Click to Plot
*************

**Last Updated:** September 2025

Start with the :ref:`Map Layout Recipe <add_map_layout_recipe>`

Add the following attribute to your map layout class.

.. code-block:: python
    :emphasize-lines: 7

    @controller(name="home", app_workspace=True)
    class MapLayoutTutorialMap(MapLayout):
        app = App
        base_template = f'{App.package}/base.html'
        map_title = 'Map Layout Recipe'
        map_subtitle = 'Map Subtitle'
        plot_slide_sheet = True

Now add the following method to your map layout class.

.. code-block:: python

    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, *args, **kwargs):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            layer_name (str): Name/id of layer.
            feature_id (str): ID of feature.
            layer_data (dict): The MVLayer.data dictionary.
            feature_props (dict): The properties of the selected feature.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """

Your implementation of `get_plot_for_layer_feature needs` to return three things: a graph title, a data list, and a layout dictionary.

Your data list should be in the following format:

.. code-block:: python

    data = [
        dict(
            x=[1, 2, 3],
            y=[1, 2, 3],
            name='Name of plot',
            line={'color': "#000000", 'width': 2 'shape': 'spline'}
        )
    ]

Your layout dictionary should be in the following format:

.. code-block:: python

    layout = {
        'title': 'Title of the Plot',
        'xaxis': {'title': 'X Axis Label'}
        'yaxis': {'title': 'Y Axis Label'}
    }

Here is an example completed version of `get_plot_for_layer_feature`:

.. code-block:: python

    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, *args, **kwargs):
        data = [
            {
                'x': [1, 3, 4, 7],
                'y': [5, 2, 16, 9]
                name='Example Plot Name',
                line={'color': '#008000', 'width': 3, 'shape': 'spline'}
            }
        ]

        layout = {
            'title': f'Example Plot Title for feature with id: {feature_id}',
            'xaxis': {'title': 'Random X Axis Numbers'},
            'yaxis': {'title': 'Random Y Axis Numbers'},
        }

        return "Example plot title", data, layout"

Now, open your app and click on a feature on the map. You should see something like this:   

.. figure:: ../../docs/images/recipes/click_to_plot_graph.png
    :width: 500px
    :align: center