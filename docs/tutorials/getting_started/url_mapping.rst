***********
URL Mapping
***********

**Last Updated:** May 20, 2015

Whenever you create a new controller, you will also need to associate it with a URL by creating URL map for it. When a URL is requested, the controller that it is mapped to will be executed.

In this tutorial you will create a new URL map for the new ``map`` controller you created in the previous tutorial.

Map Controller to URL
=====================

Mapping a controller to a URL is performed in the :term:`app configuration file` (:file:`app.py`). Open your app configuration file located at :file:`my_first_app/app.py`. Your :term:`app class` will already have a method called ``url_maps()``. This method must return a list or tuple of ``UrlMap`` objects. ``UrlMap`` objects require three attributes: ``name``, ``url``, and ``controller``.

Your :term:`app class` will already have one ``UrlMap`` for the home page called "home". Add a new ``UrlMap`` object for the ``map`` controller that you created in the previous step. Give it a name of "map", a url of "my-first-app/map", and a path to the controller of "my_first_app.controllers.map". The ``url_maps()`` method for your app should look something like this when you are done:

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
                               controller='my_first_app.controllers.home'),
                        UrlMap(name='map',
                               url='my-first-app/map',
                               controller='my_first_app.controllers.map'),
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

.. important::

    All of the URL patterns for your app should begin with the base URL of your app (e.g.: 'my-first-app') to prevent conflicts with other apps.

Now that you have created the URL map for your new map page, you can create a link to it from the home page. Open the :file:`home.html` template located at :file:`my_first_app/templates/my_first_app/home.html`. Replace the ``app_actions`` template block with the following:

::

    {% block app_actions %}
      <a href="{% url 'my_first_app:map' %}" class="btn btn-default">Go To Map</a>
    {% endblock %}

In this code, the ``url`` template tag is used to provide the url to the map page. It accepts a string with the following pattern: ``"name_of_app:name_of_url_map"``. The advantage of using the ``url`` tag as opposed to hard coding the URL is that if the URL ever needs to be changed, you will only need to change it in your app configuration file and not in every template that references that URL.

View New Map Page
=================

At this point, your app should be ready to run again. Save all changes in the files you edited and restart the development server using the ``tethys manage start`` command in the terminal (stop it using :kbd:`CTRL-C` if necessary). Browse to your app home page at `<http://127.0.0.1:8000/apps/my-first-app>`_. Use the "Go To Map" action to browse to your new map page. It should look similar to this:

.. figure:: ../../images/new_map_page.png
    :width: 650px
