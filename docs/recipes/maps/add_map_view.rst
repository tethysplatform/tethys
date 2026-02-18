.. _add_map_view_recipe:


**********************
Adding a MapView Gizmo
**********************

This recipe will demonstrate how to add a MapView Gizmo to your app. In contrast with the MapLayout, a MapView Gizmo allows you to choose where to put your interactive map on the page. 

Creating the MapView Gizmo
##########################
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
                center=[0,0],
                zoom=7,
                maxZoom=18,
                minZoom=2
            )
        )

        context = {
            'map_view': map_view
        }

Adding the MapView Gizmo to your Page
#####################################

Next, add your Gizmo to your page template:

.. code-block:: html+django

    {% block app_content %}
        {% gizmo map_view %}
    {% endblock %}

Now open your app, and you should find an interactive map that looks like this: 

.. figure:: ../../images/recipes/add_map_view_screenshot.png
    :width: 500px
    :align: center

