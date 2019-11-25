*************
Spatial Input
*************

**Last Updated:** November 2019


1. Spatial Input Page UrlMap
============================

Add a new ``UrlMap`` to the ``url_maps`` method of the :file:`app.py` module:

::

    UrlMap(
        name='draw',
        url='geoserver-app/draw',
        controller='geoserver_app.controllers.draw'
    ),

2. Spatial Input Controller
===========================

Add a new controller to the :file:`controller.py` module:

::

    @login_required()
    def draw(request):
        drawing_options = MVDraw(
            controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Polygon'
        )

        map_options = MapView(
            height='450px',
            width='100%',
            layers=[],
            draw=drawing_options
        )

        geometry = ''

        if request.POST and 'geometry' in request.POST:
            geometry = request.POST['geometry']

        context = {'map_options': map_options,
                   'geometry': geometry}

        return render(request, 'geoserver_app/draw.html', context)

3. Spatial Input Template
=========================

Create a new :file:`draw.html` template in your template directory and add the following contents:

::

    {% extends "geoserver_app/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
        <h1>Draw on the Map</h1>

        {% if geometry %}
            <p>{{ geometry }}</p>
        {% endif %}

        <form method="post">
            {% csrf_token %} 
            {% gizmo map_view map_options %}
            <input name="submit" type="submit">
        </form>
    {% endblock %}


4. Add Navigation Links
=======================

Replace the ``app_navigation_items`` block of the :file:`base.html` template with:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      {% url 'geoserver_app:home' as home_url %}
      {% url 'geoserver_app:map' as map_url %}
      {% url 'geoserver_app:draw' as draw_url %}
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Upload Shapefile</a></li>
      <li class="{% if request.path == map_url %}active{% endif %}"><a href="{{ map_url }}">GeoServer Layers</a></li>
      <li class="{% if request.path == draw_url %}active{% endif %}"><a href="{{ draw_url }}">Draw</a></li>
    {% endblock %}


5. Test Spatial Input Page
==========================

Navigate to the spatial input page using the "Draw" link in your navigation (`<http://localhost:8000/apps/geoserver-app/draw/>`_). Use the drawing controls to add features to the map, then press the submit button. The GeoJSON encoded spatial data should be displayed when the page refreshes.

6. Solution
===========

This concludes the GeoServer Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-geoserver_app>`_ or clone it as follows:

.. parsed-literal::

    git clone git@github.com:tethysplatform/tethysapp-geoserver_app.git
    cd tethysapp-geoserver_app
    git checkout -b solution solution-|version|
