*****************
Advanced Concepts
*****************

**Last Updated:** November 17, 2014

The purpose of this tutorial will be to introduce some advanced concepts in Tethys app development. In the map page you created in the previous tutorials, you are able to view all of the stream gages on a map concurrently. In this tutorial you will add the ability to view individual stream gages on the map page. This will involve creating a new url map, new controller, and some modifications to the map template. This exercise will also serve as a good review of MVC development in Tethys Platform.

New URL Map and URL Variables
=============================

You can add variables to your URLs to make your controllers and web pages more dynamic. URL variables are denoted by single curly braces in the URL string like this: ``/example/url/{variable}``. Open the :file:`my_first_app/app.py` file in a text editor. Modify the ``url_maps()`` method by adding a new ``UrlMap`` object named "map_single" with a URL variable called "id". Your ``url_maps()`` method should look like this when you are done:

::

    class MyFirstApp(TethysAppBase):
        """
        Tethys App Class for My First App.
        """

        name = 'My First App'
        index = 'my_first_app:home'
        icon = 'my_first_app/images/icon.gif'
        package = 'my_first_app'
        root_url = 'my-first-app'
        color = '#3498db'

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
                               ),
            )

            return url_maps

        def persistent_stores(self):
            """
            Add one or more persistent stores
            """
            stores = (PersistentStore(name='stream_gage_db',
                                      initializer='init_stores:init_stream_gage_db',
                                      spatial=True
                    ),
            )

            return stores

.. note::

    The Django documentation on URL mapping will not be useful for Tethys apps. A different approach is used by Tethys that is easier to use than the Django method.

New Controller
==============

Notice that the ``map_single`` ``UrlMap`` object points to a controller named "map_single". This controller doesn't exist yet, so we will need to create it. Open the :file:`my_first_app/controllers.py` in a text editor and add the ``map_single`` controller function to it:

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

The ``map_single`` controller function is slightly different than the ``map`` controller you created earlier. It accepts an additional argument called "id". The ``id`` URL variable value will be passed to the ``map_single`` controller making the ``id`` variable available for use in the controller logic.

Anytime you create a URL with variables in it, the variables need to be added to the arguments of the controller function it maps to.

The ``map_single`` controller is similar but different from the ``map`` controller you created earlier. The SQLAlchemy query searches for a single stream gage record using the ``id`` variable via the``filter()`` method. The stream gage data returned by the query is reformatted into GeoJSON format as before and the ``map_options`` for the Gizmo are defined.

The context is expanded to include the ``id`` variable, so that it will be available for use in the template. The same :file:`map.html` template is being used by this controller as was used by the ``map`` controller. However, it will need to be modified slightly to make use of the new ``gage_id`` context variable.

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

There are two changes to the :file:`map.html` template that are worth noting. First, the template now overrides the ``app_navigation_block`` to provide links for each of the stream gages in the navigation. The ``if`` template tag is used in each of the nav items to highlight the appropriate link based on the ``gage_id``. Notice that all ``if`` tags must also end with a ``endif`` tag. The text between the two tags is displayed only if the conditional statement evaluates to ``True``. The ``href`` for each link is provided using the ``url``, but this time the ``id`` variable is also provided as an argument.

The other change to the template is the heading of the page (``<h1>``) is wrapped by ``if``, ``else``, and ``endif`` tags. The effect is to display "Stream Gage id#" when viewing only one stream gage and "Stream Gages" when viewing all of them.

View Updated Map Page
=====================

Just like that, you added a new page to your app using MVC. Save the changes to any files you edited and start up the development server using the ``tethys manage start`` command and browse to your app. Use the "Go To Map" action on the home page to browse to your new map page and use the options in the navigation pane to view the different gages. It should look like this (although you may need to pan and zoom some):

.. figure:: ../../images/map_single_page.png
    :width: 650px

Variable URLs
=============

Take note of the URL as you are viewing the different gages. You should see the ID of the current gage. For example, the URL for the gage with an ID of 1 would be `<http://127.0.0.1:8000/apps/my-first-app/map/1/>`_. You can manually change the ID in the URL to request the gage with that ID. Visit this URL `<http://127.0.0.1:8000/apps/my-first-app/map/3/>`_ and it will map the gage with ID 3.

Try this URL: `<http://127.0.0.1:8000/apps/my-first-app/map/100>`_. You should see a lovely error message, because you don't have a gage with ID 100 in the database. This uncovers a bug in your code that we won't take the time to fix in this tutorial. If this were a real app, you would need to handle the case when the ID doesn't match anything in the database so that it doesn't give you an error.

This exercise also exposes a vulnerability with using integer IDs in the URL--they can be guessed easily. For example if your app had a delete method, it would be very easy for an attacker to write a script that would increment through integers and call the delete method--effectively clearing your database. It would be a much better practice to use a UUID (see `Universally unique identifier <http://en.wikipedia.org/wiki/Universally_unique_identifier>`_) or something similar for IDs.