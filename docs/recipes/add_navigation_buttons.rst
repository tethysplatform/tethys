.. _add_navigation_buttons_recipe:


**********************
Add Navigation Buttons
**********************

**Last Updated:** June 2025

Your app may contain multiple pages (i.e. map viewer, home page, disclaimer, etc.).  Navigation buttons provide a convinent way to switch between pages in your app.  To add navigation buttons:

a. Open ``/templates/<app_name>/base.html`` and replace the ``app_navigation_items`` block with your code:

    .. code-block:: html+django

        {% block app_navigation_items %}
        <li class="nav-item title">App Navigation</li>
        <li class="nav-item"><a class="nav-link" href="#">PAGE NAME 1</a></li>
        <li class="nav-item"><a class="nav-link" href="#">PAGE NAME 2</a></li>
        <li class="nav-item"><a class="nav-link" href="#">PAGE NAME 3</a></li>
        {% endblock %}

.. note:: Replace "`#`" with the page url you are linking to.
    
b. You can also modify ``app_navigation_items`` block to dynamically highlight the active link:

    .. code-block:: html+django

        {% block app_navigation_items %}
        {% url tethys_app|url:'home' as home_url %}
        {% url tethys_app|url:'add_dam' as add_dam_url %}
        <li class="nav-item title">Navigation</li>
        <li class="nav-item"><a class="nav-link{% if request.path == home_url %} active{% endif %}" href="{{ home_url }}">Map</a></li>
        <li class="nav-item"><a class="nav-link{% if request.path == add_dam_url %} active{% endif %}" href="{{ add_dam_url }}">Add Dam</a></li>
        {% endblock %}

.. tip::

    **url**: The ``url`` tag is used in templates to lookup URLs using the name of the route (as defined in by the ``controller`` decorator), namespaced by the app package name (i.e.: ``namespace:controller_name``). 
    
    **if**: The ``if`` tag is used in templates to render content on the page conditionally. If the ``if`` condition is met, the content will be shown, otherwise it will not.
    
    **as**: In the code above we assign the URLs to two variables, ``home_url`` and ``add_dam_url``, using the ``as`` operator in the ``url`` tag.
    
    A combination of these three tags is used to conditionally highlight the nav link by adding the ``active`` class if the page URL matches the link url.

.. tip:: 

    For more details on the navigation items see the :ref:`templating_api`.