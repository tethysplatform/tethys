*************
Spatial Input
*************

**Last Updated:** July 2024

1. Spatial Input Controller
===========================

Add a new controller to the :file:`controller.py` module:

.. code-block:: python

    from .app import App

    @controller
    def draw(request):
        drawing_options = MVDraw(
            controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Polygon'
        )

        map_options = MapView(
            height='450px',
            width='100%',
            layers=[],
            draw=drawing_options,
            basemap='OpenStreetMap'
        )

        geometry = ''

        if request.POST and 'geometry' in request.POST:
            geometry = request.POST['geometry']

        context = {'map_options': map_options,
                   'geometry': geometry}

        return App.render(request, 'draw.html', context)

2. Spatial Input Template
=========================

Create a new :file:`draw.html` template in your template directory and add the following contents:

.. code-block:: python

    {% extends tethys_app.package|add:"/base.html" %}
    {% load tethys %}

    {% block app_content %}
        <h1>Draw on the Map</h1>

        {% if geometry %}
            <p>{{ geometry }}</p>
        {% endif %}

        <form method="post">
            {% csrf_token %} 
            {% gizmo map_view map_options %}
            <input name="submit" type="submit" class="btn btn-primary mt-3">
        </form>
    {% endblock %}


3. Add Navigation Links
=======================

Replace the ``app_navigation_items`` block of the :file:`base.html` template with:

.. code-block:: html+django

    {% block app_navigation_items %}
      {% url tethys_app|url:'home' as home_url %}
      {% url tethys_app|url:'map' as map_url %}
      {% url tethys_app|url:'draw' as draw_url %}
      <li class="nav-item title">App Navigation</li>
      <li class="nav-item"><a href="{{ home_url }}" class="nav-link{% if request.path == home_url %} active{% endif %}">Upload Shapefile</a></li>
      <li class="nav-item"><a href="{{ map_url }}" class="nav-link{% if request.path == map_url %} active{% endif %}">GeoServer Layers</a></li>
      <li class="nav-item"><a href="{{ draw_url }}" class="nav-link{% if request.path == draw_url %} active{% endif %}">Draw</a></li>
    {% endblock %}


4. Test Spatial Input Page
==========================

Navigate to the spatial input page using the "Draw" link in your navigation (`<http://localhost:8000/apps/geoserver-app/draw/>`_). Use the drawing controls to add features to the map, then press the submit button. The GeoJSON encoded spatial data should be displayed when the page refreshes.

5. Solution
===========

This concludes the this part of the GeoServer tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-geoserver_app>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-geoserver_app
    cd tethysapp-geoserver_app
    git checkout -b map-draw-solution map-draw-solution-|version|
