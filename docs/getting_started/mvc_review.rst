**********
MVC Review
**********

**Last Updated:** November 13, 2014

Up to this point, you have learned about each component of MVC development in detail to add a new map page to your app. The purpose of this tutorial will be to provide a review of these concepts and to introduce some advanced concepts. In the map page you created in the previous tutorials, you are able to view all of the stream gages on a map concurrently. In this tutorial you will add the ability to see individual stream gages on the map page. This will involve creating a new controller, url map, and some modifications to the map template.

New URL Map and URL Variables
=============================

You can add variables to your URLs to make your controllers and web pages more dynamic. URL variables are denoted by single curly braces in the URL string like this: ``/example/url/{variable}``. Open the :file:`my_first_app/app.py` file in a text editor. Modify the ``url_maps()`` method by adding a new ``UrlMap`` object named "map_single" with a URL variable called "id". Your ``url_maps()`` method should look like this when you are done:

::

    class MyFirstApp(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...

        def url_maps(self):
            """
            Add controllers
            """
            UrlMap = url_map_maker(self.root_url)

            url_maps = (UrlMap(name='home',
                               url='my-first-app',
                               controller='my_first_app.controllers.home'
                               ),
                        UrlMap(name='map',
                               url='my-first-app/map',
                               controller='my_first_app.controllers.map'
                               ),
                        UrlMap(name='map_single',
                               url='my-first-app/map/{id}',
                               controller='my_first_app.controllers.map_single'
                               )
            )

            return url_maps

.. note::

    The Django documentation on URL mapping will not be useful for Tethys apps. A different approach is used by Tethys that is easier to use than the Django method.

New Controller
==============

Notice that the map_single ``UrlMap`` object points to a controller named "map_single". This controller doesn't exist yet, so we will need to create it. Open the :file:`my_first_app/controllers.py` in a text editor and add the ``map_single`` controller function to it:

::

    def map_single(request, id):
        """
        Controller for map page.
        """
        # Create a session
        session = SessionMaker()

        # Query DB for gage objects
        gage = session.query(StreamGage).filter(StreamGage.id==id).one()

        # Create geometry objects for the gage
        gage_geometry = dict(type="Point",
                             coordinates=[gage.latitude, gage.longitude],
                             properties={"value": gage.value})

        # Create geojson object
        geojson_gages = dict(type="GeometryCollection",
                             geometries=[gage_geometry])

        map_options = {'height': '600px',
                       'width': '100%',
                       'input_overlays': geojson_gages}

        context = {'map_options': map_options,
                   'gage_id': id}

        return render(request, 'my_first_app/map.html', context)

The ``map_single`` controller function is slightly different than the ``map`` controller you created earlier. It accepts and additional argument called "id". The ``id`` URL variable value will be passed to the ``map_single`` controller making the ``id`` variable available for use in the controller logic. Anytime you create a URL with variables in it, the variables need to be added to the arguments of the controller function it maps to.

The ``map_single`` controller is similar but different from the ``map`` controller you created earlier. Searches for a single stream gage record using the ``id`` variable and the SQLAlchemy ``filter()`` method. The gage is reformatted into GeoJSON format as before and the ``map_options`` for the Gizmo are defined. The context is expanded to include the ``id`` variable, so that it will be available for use in the template. The same :file:`map.html` template is being used by this controller as was used by the ``map`` controller. We will need to modify it slightly to make use of the new ``gage_id`` context variable.

Modify the Template
===================

Open the :file:`map.html` template located at :file:`my_first_app/templates/my_first_app/map.html`. Modify the template so that it matches this:

::

    {% extends "my_first_app/base.html" %}

    {% load tethys_gizmos %}

    {% block app_navigation_items %}
      <li class="title">Gages</li>
      <li{% if not gage_id %} class="active"{% endif %}>
        <a href="{% url 'my_first_app:map' %}">All Gages</a>
      </li>
      <li{% if gage_id == '1' %} class="active"{% endif %}>
        <a href="{% url 'my_first_app:map_single' id=1 %}">Stream Gage 1</a>
      </li>
      <li{% if gage_id == '2' %} class="active"{% endif %}>
        <a href="{% url 'my_first_app:map_single' id=2 %}">Stream Gage 2</a>
      </li>
      <li{% if gage_id == '3' %} class="active"{% endif %}>
        <a href="{% url 'my_first_app:map_single' id=3 %}">Stream Gage 3</a>
      </li>
      <li{% if gage_id == '4' %} class="active"{% endif %}>
        <a href="{% url 'my_first_app:map_single' id=4 %}">Stream Gage 4</a>
      </li>
    {% endblock %}

    {% block app_content %}
      {% if gage_id %}
        <h1>Stream Gage {{gage_id}} </h1>
      {% else %}
        <h1>Stream Gages</h1>
      {% endif %}

      {% gizmo editable_google_map map_options %}
    {% endblock %}

    {% block app_actions %}
      <a href="{% url 'my_first_app:home' %}" class="btn btn-default">Back</a>
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      {% gizmo_dependencies %}
    {% endblock %}

There are two changes to the :file:`map.html` template that are worth noting. First, the template now overrides the ``app_navigation_block`` to provide links for each of the stream gages in the navigation. The ``if`` template tag is used in each of the nav items to highlight the appropriate link based on the ``gage_id``. Notice that all ``if`` tags must also end with a ``endif`` tag. The text between the two tags is displayed only if the conditional statement evaluates to ``True``. The ``href`` for each link is provided using the ``url`` tag as before, but this time, the ``id`` variable is also provided.

The other change to the template is the heading of the page (``<h1>``) is wrapped by ``if``, ``else``, and ``endif`` tags. The effect is to display "Stream Gage id#" when viewing only one stream gage and "Stream Gages" when viewing all of them.

View Updated Map Page
=====================

Just like that, you added a new view of your data. Start up the development server using the ``tethys manage start`` command and browse to your app. Use the "Go To Map" action on the home page to browse to your new map page and use the options in the navigation pane to view the different gages (see Figure 1).

.. figure:: ../images/map_single_page.png
    :width: 650px

    **Figure 1:** Map page displaying a single stream gage.

Variable URLs
=============

Take note of the URL as you are viewing the different gages. You should see the ID of the current gage. For example, the URL for the gage with an ID of 1 would be `<http://127.0.0.1/apps/my-first-app/map/1/>`_. You can manually change the ID to request the gage with that ID. Visit this URL `<http://127.0.0.1/apps/my-first-app/map/3/>`_ and it will map the gage with ID 3.

Try this URL: `<http://127.0.0.1/apps/my-first-app/map/100>`_. You should see a lovely error message, because you don't have a gage with ID 100 in the database. This uncovers a bug in your code that we won't take the time to fix in this tutorial. You would need to handle the case when the ID doesn't match anything in the database. This also exposes a vulnerability with using integer IDs in the URL--they can be guessed easily. It would be a much better practice to use a UUID (see `Universally unique identifier <http://en.wikipedia.org/wiki/Universally_unique_identifier>`_) or something similar for IDs.