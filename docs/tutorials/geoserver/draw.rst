*************
Spatial Input
*************

**Last Updated:** September 30, 2016


Spatial Input Page UrlMap
=========================

Add a new ``UrlMap`` to the ``url_maps`` method of the :file:`app.py` module:

::

    UrlMap(name='draw',
           url='geoserver-app/draw',
           controller='geoserver_app.controllers.draw'),

Spatial Input Controller
========================

Add a new controller to the :file:`controller.py` module:

::

    @login_required
    def draw(request):
        
        user = request.user
        drawing_options = MVDraw(
            controls=['Modify', 'Move', 'Point', 
                      'LineString', 'Polygon', 'Box'],
            initial='Polygon'
        )

        map_options = MapView(height='450px',
                              width='100%',
                              layers=[],
                              draw=drawing_options)

        geometry = ''

        if request.POST and 'geometry' in request.POST:
            geometry = request.POST['geometry']

        context = {'map_options': map_options,
                   'geometry': geometry}

        return render(request, 'geoserver_app/draw.html', context)

Spatial Input Template
======================

Create a new :file:`draw.html` template in your template directory and add the following contents:

::

    {% extends "geoserver_app/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
        <h1>Draw on the Map</h1>

        {% if geometry %}
            <p>{{ geometry }}</p>
        {% endif %}

        <form action="" method="post">
            {% csrf_token %} 
            {% gizmo map_view map_options %}
            <input name="submit" type="submit">
        </form>
    {% endblock %}


Add Navigation Links
====================

Replace the ``app_navigation_items`` block of the :file:`base.html` template with:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      <li><a href="{% url 'geoserver_app:home' %}">Upload Shapefile</a></li>
      <li><a href="{% url 'geoserver_app:map' %}">GeoServer Layers</a></li>
      <li><a href="{% url 'geoserver_app:draw' %}">Draw</a></li>
    {% endblock %}


Test Spatial Input Page
=======================

Navigate to the spatial input page using the "Draw" link in your navigation (`<http://localhost:8000/apps/geoserver-app/draw/>`_). Use the drawing controls to add features to the map, then press the submit button. The GeoJSON encoded spatial data should be displayed when the page refreshes.