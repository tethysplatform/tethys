************
Add Map View
************

**Last Updated:** July 2024

In this tutorial you will add a map to the Home Page using the Tethys MapView Gizmo. The following topics will be reviewed in this tutorial:

* Tethys MapView Gizmo
* Overriding the Default Template
* Remove Padding from App Content Area
* Custom CSS

.. figure:: ../../../images/tutorial/gee/map_view.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b dataset-controls-js-solution dataset-controls-js-solution-|version|

1. Remove App Actions Bar
=========================

You will not be using the app actions bar at the bottom of the content area and you'd like the map to fill the whole content area, so you'll remove the app actions bar to give the map a little more real estate.

1. Replace the ``app_actions`` block with the ``app_actions_override`` block in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django

    {% block app_actions_override %}
    {% endblock %}

2. Restyle the ``app-content`` area to take up full height in :file:`public/css/main.css`:

.. code-block:: css

    /* Remove padding on bottom where app-actions section used to be */
    #app-content-wrapper #app-content {
        padding-bottom: 0;
    }


.. tip::

    To verify that the app content area is indeed filling the whole area, you could temporarily add the following to :file:`public/css/main.css`:

    .. code-block:: css

        #app-content {
            background: red;
        }


2. Add Map View
===============

In this step you'll add the ``MapView`` to the home view. You'll also add a custom stylesheet to ensure the map fills the content area.

1. Add ``MapView`` gizmo to ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    from tethys_sdk.gizmos import MapView, MVView

.. code-block:: python

    map_view = MapView(
        height='100%',
        width='100%',
        controls=[
            'ZoomSlider', 'Rotate', 'FullScreen',
            {'ZoomToExtent': {
                'projection': 'EPSG:4326',
                'extent': [29.25, -4.75, 46.25, 5.2]  #: Kenya
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
        'platform_select': platform_select,
        'sensor_select': sensor_select,
        'product_select': product_select,
        'start_date': start_date,
        'end_date': end_date,
        'reducer_select': reducer_select,
        'load_button': load_button,
        'ee_products': EE_PRODUCTS,
        'map_view': map_view
    }


2. Add ``MapView`` gizmo to the ``app_content`` block of the :file:`templates/earth_engine/home.html`:

.. code-block:: html+django

    {% block app_content %}
      {% gizmo map_view %}
    {% endblock %}


3. Restyle the home page so that the map fills the screen by creating :file:`public/css/map.css` with the following contents:

.. code-block:: css

    /* Map Format */
    #app-content-wrapper #app-content {
        height: 100%;
    }

    #inner-app-content {
        height: 100%;
        padding: 0;
    }


4. Include the new :file:`public/css/map.css` script in the :file:`templates/earth_engine/home.html`:

.. code-block:: html+django

    {% block content_dependent_styles %}
        {{ block.super }}
        <link rel="stylesheet" href="{% static tethys_app|public:'css/map.css' %}" />
    {% endblock %}

3. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Verify the following:

1. The app actions bar that used to be at the bottom of the page should be gone.
2. The page should now feature a map that fills the content area including where the app actions bar used to be.
3. The map should be zoomed in and centered on Kenya.
4. Use the **Basemap** control to change the basemap.

4. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/map-view-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b map-view-solution map-view-solution-|version|