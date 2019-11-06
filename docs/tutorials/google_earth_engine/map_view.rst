************
Add Map View
************

**Last Updated:** November 2019

1. Remove App Actions Bar
=========================

1. Replace the `app_actions` block with the `app_actions_override` block in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django

    {% block app_actions_override %}
    {% endblock %}

2. Restyle the `app-content` area to take up full height in :file:`public/css/main.css`:

.. code-block:: css

    /* Remove padding on bottom where app-actions section used to be */
    #app-content-wrapper #app-content {
        padding-bottom: 0;
    }


.. tip::

    To verify that the app content area is indeed filling the whole area, you could temporarily add the following to `main.css`:

    .. code-block:: css

        #app-content {
            background: red;
        }


2. Add Map View
===============

1. Add `MapView` gizmo to `home` controller in :file:`controllers.py`:

.. code-block:: python

    from tethys_sdk.gizmos import MapView, MVView

    ...

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
            'Stamen',
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


2. Add `MapView` gizmo to the `app_content` block of the :file:`templates/earth_engine/home.html`:

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
        <link rel="stylesheet" href="{% static 'earth_engine/css/map.css' %}" />
    {% endblock %}

