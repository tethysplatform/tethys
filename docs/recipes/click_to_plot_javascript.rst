.. _click_to_plot_javascript_recipe :

******************************
Click to Plot Using JavaScript
******************************

**Last Updated:** September 2025

While it can be convenient to use the Tethys Map Layout to add an interactive map to your Tethys App, you may also want to add a map in other places in your app, and allow for plotting data from that map's features.

This recipe will demonstrate how to implement click to plot features using JavaScript, allowing you to place your map wherever you'd like in your page. We'll be using the MapView Gizmo and the Plotly Gizmo to do this.

Adding a MapView Gizmo
######################
We'll begin by adding a MapView Gizmo to a page in your app. First open your :file:`controllers.py` file and add the following:

.. code-block:: python

    from tethys_sdk.gizmos import MapView, MVView

Next, in your controller function, you'll need to create a MapView Gizmo like so:

.. code-block:: python
    :emphasize-lines: 3-30

    def home(request):
        ...
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
                center=[37.880859, 0.219726],
                zoom=7,
                maxZoom=18,
                minZoom=2
            )
        )

        context = {
            'map_view': map_view
        }

Next, add your Gizmo to your page template:

.. code-block:: html+django

    {% block app_content %}
        <h1>This is a MapView Gizmo:</h1>
        {% gizmo map_view %}
    {% endblock %}

Now open to this page in your app and you should see a label above an interactive map. 

Add Features to Map
###################