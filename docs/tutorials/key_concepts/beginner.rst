.. _key_concepts_beginner_tutorial:

*****************
Beginner Concepts
*****************

**Last Updated:** July 2024

This tutorial introduces important concepts for first-time or beginner Tethys developers. The topics covered include:

* The App Class
* Model View Controller
* Map Layout
* App Navigation

.. figure:: ../../images/tutorial/advanced/key-concepts-beginner-screenshot.png
    :width: 800px
    :align: center

1. App Class
============

The app class, located in ``app.py`` is the primary configuration file for Tethys apps. All app classes inherit from the ``TethysAppBase`` class.

a. Open ``app.py`` in your favorite Python IDE or text editor.

b. Change the theme color of your app by changing the value of the ``color`` property of the ``DamInventory`` class. Use a site like `color-hex <https://www.color-hex.com/>`_ to find an appropriate hexadecimal RGB color.

c. You can also change the icon of your app. Find a new image online (square images work best) and save it in the ``public/images/`` directory of your app. Then change the value of the ``icon`` property of the ``DamInventory`` class to match the name of the image.

.. tip::

    For more details about the app class, see the :doc:`../../tethys_sdk/app_class`.

.. warning::

    DO NOT change the value of the ``index``, ``package``, or ``root_url`` properties of your app class unless you know what you are doing. Doing so will break your app.

2. App Settings
===============

Other settings for your app can be configured in the app settings. App settings are stored in a database, meaning they can be changed dynamically by the administrator of your portal. Some app settings, like Name and Description, correspond with properties in the ``app.py`` script.

a. To access the app settings, click on the Settings button (gear icon) at the top right-hand corner of your app.

b. Change the Name and Description of your app by changing their respective values on the app settings page. Press the ``Save`` button, located at the bottom of the app settings page. Then navigate back to your app to see the changes.

You can also create custom settings for your app that can be configured on the app settings page:

a. Open the ``app.py`` and add the ``custom_settings()`` method to the ``DamInventory`` class. Don't forget to import ``CustomSetting``:

    .. code-block:: python

        from tethys_sdk.app_settings import CustomSetting

        ...

        class App(TethysAppBase):
            """
            Tethys app class for Dam Inventory.
            """
            ...

            def custom_settings(self):
                """
                Example custom_settings method.
                """
                custom_settings = (
                    CustomSetting(
                        name='max_dams',
                        type=CustomSetting.TYPE_INTEGER,
                        description='Maximum number of dams that can be created in the app.',
                        required=False
                    ),
                )
                return custom_settings

    .. warning::

        Ellipsis in code blocks in Tethys tutorials indicate code that is not shown for brevity. When there are ellipsis in the code, DO NOT COPY AND PASTE THE BLOCK VERBATIM.

b. Save changes to ``app.py``.

c. The development server should automatically restart when it detects changes to files. However if it does not restart, you can manually restart it by pressing ``CTRL-C`` to stop the server followed by the ``tethys manage start`` command to start it again.

d. Navigate to the settings page of your app and scroll down to the **Custom Settings** section and you should see an entry for the ``max_dams`` settings. Enter a value and save changes to the setting. You will learn how to use this custom setting in the app later on in the tutorial.

.. tip::

    For more information about app settings, see the :doc:`../../tethys_sdk/app_settings`.

3. Map Layout
=============

The ``MapLayout`` provides a drop-in full-screen map view for Tethys Apps. In this tutorial, we will use the ``MapLayout`` to display a map of all of the dams in the dam inventory. For a detailed explanation of the ``MapLayout`` see the :ref:`map_layout` and checkout the :ref:`Map Layout Tutorial <tutorial_map_layout>`.

a. Replace the ``home`` controller in ``controllers.py`` with a ``MapLayout`` controller class by replacing the contents of ``controllers.py`` with the following code:

.. code-block:: python

    from tethys_sdk.layouts import MapLayout
    from tethys_sdk.routing import controller
    from .app import App


    @controller(name="home")
    class HomeMap(MapLayout):
        app = App
        base_template = f'{App.package}/base.html'
        map_title = 'Dam Inventory'
        map_subtitle = 'Tutorial'
        basemaps = ['OpenStreetMap', 'ESRI']

The properties of the ``MapLayout`` class are used to configure the map. Here is a brief explanation of some of those used in the example above:

* ``map_title``: The title of the map that appears in the top left corner of the page.
* ``sub_title``: The subtitle of the map that appears below the title.
* ``basemaps``: A list of basemaps that are enabled on this map view. The user can switch between them using the basemap control on the map.

The :ref:`map_layout` documentation provides detailed information about the properties of the ``MapLayout`` class.

b. Save your changes to ``controllers.py`` and refresh the page to view the map.

4. Model View Controller
========================

Tethys apps are developed using the :term:`Model View Controller` (MVC) software architecture pattern. Model refers to the data model and associated code, View refers to the representations of the data, and Controller refers of the code that coordinates data from the Model for rendering in the View. In Tethys apps, the Model is usually an SQL database or files and the code for accessing them, the Views are most often the templates or HTML files, and Controllers are implemented as Python functions or classes.

.. tip::

    For more information about the MVC pattern, see :doc:`../../supplementary/key_concepts`.

5. Create a New Page
====================

Creating a new page in your app consists of three steps: (1) create a new template, (2) add a new controller function to ``controllers.py``, and (3) define the routing using the ``controller`` decorator.

a. Create a new file ``/templates/dam_inventory/add_dam.html`` and add the following contents:

    .. code-block:: html+django

        {% extends "dam_inventory/base.html" %}

    This is the simplest template you can create in a Tethys app, which amounts to a blank Tethys app page. You must extend the ``base.html`` for the page to inherit the default layout of the app.


b. Create a new controller function called ``add_dam`` at the bottom of the ``controllers.py``:

    .. code-block:: python

        @controller(url='dams/add')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            context = {}
            return App.render(request, 'add_dam.html', context)

    This is the most basic controller function you can write: a function that accepts an argument called ``request`` and a return value that is the result of the ``render`` function. The ``render`` function renders the Django template into valid HTML using the ``request`` and ``context`` provided.

    The ``controller`` decorator creates a route that maps a URL to this controller function. The ``url`` argument is used to provide a custom URL for a controller. The default URL that would have been generated without the use of the ``url`` argument would have been derived from the name of the function: ``'add-dam'``. URLs are defined relative to the root URL of the app. The full URL for the ``add_dam`` controller as shown above is ``'/apps/dam-inventory/dams/add/'``. Also note that the name of the route created by the ``controller`` decorator is, by default, the same as the function name (``add_dam``). Knowing the name of the route will be important when we need to reference it in a template.

c. At this point you should be able to access the new page by entering its URL into the address bar of your browser (`<http://localhost:8000/apps/dam-inventory/dams/add/>`_). It is not a very exciting page, because it is blank.

    .. tip::

        **New Page Pattern**: Adding new pages is an exercise of the Model View Controller pattern. Generally, the steps are:

        * Modify the model if necessary to provide the data for the new page
        * Create a new HTML template
        * Create a new controller function

6. View for the New Page
========================

Views for Tethys apps are constructed using the standard web programming tools: HTML, JavaScript, and CSS. Additionally, HTML templates can use the `Django Template Language <https://docs.djangoproject.com/en/5.0/ref/templates/language/>`_, because Tethys Platform is build on Django. This allows you to code logic into your HTML documents, using template tags, making the web pages of your app dynamic and reusable.

a. Modify the ``template/dam_inventory/add_dam.html`` with a title in the app content area and add ``Add`` and ``Cancel`` buttons to the app actions area:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <h1>Add Dam</h1>
        {% endblock %}

        {% block app_actions %}
        {% gizmo cancel_button %}
        {% gizmo add_button %}
        {% endblock %}

.. tip::

    **Django Template Language**: If you are familiar with HTML, the contents of this file may seem strange. That's because the file is actually a Django template, which contains special syntax (i.e.: ``{% ... %}`` and ``{{ ... }}`` to make the template dynamic. Django templates can contain variables, filters, and tags.

    **Variables.** Variables are denoted by double curly brace syntax like this: ``{{ variable }}``. Template variables are replaced by the value of the variable. Dot notation can be used to access attributes of an object, keys of dictionaries, and items in lists or tuples: ``{{ my_object.attribute }}`` , ``{{ my_dict.key }}``, and ``{{ my_list.3 }}``.

    **Filters.** Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Filters modify the value of the variable output such as formatting dates, formatting numbers, changing the letter case, or concatenating multiple variables.

    **Tags.** Tags use curly-brace-percent-sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``.

    **Blocks.** The block tags in the Tethys templates are used to override the content in the different areas of the app base template. For example, any HTML written inside the ``app_content`` block will render in the app content area of the app.

    For a better explanation of the Django Template Language and the blocks available in Tethys apps see the :doc:`../../tethys_sdk/templating`.

.. tip::

    **Gizmos**: The ``add_dam.html`` template used the ``gizmo`` Tethys template tag to insert a buttons using one line of code: ``{% gizmo add_button %}``. Gizmo tags require one argument, an object that defines the options for the gizmo. These gizmo options must be defined in the controller for that view. In the example above we define the options objects for the two gizmos on the ``home.html`` template and pass them to the template through the context dictionary.

    For more details on the Button Gizmo see: :doc:`../../tethys_sdk/gizmos/button` For more information about Gizmos in general see the :doc:`../../tethys_sdk/gizmos`.

7. Controller for the New Page
==============================

Basic controllers consist of a Python function that takes a ``request`` object as an argument. But as you saw with the ``MapLayout`` controller, they can also be classes. The ``request`` object contains all the information about the incoming request. Each controller function is also associated with one view or template via the ``render`` call. Any variable assigned to the ``context`` variable in a controller becomes a variable that can be used in the template.

a. Define the options for the ``Add`` and ``Cancel`` button gizmos in the ``add_dam`` controller in ``controllers.py``. Add the variables to the context so they are available to the template:

    .. code-block:: python

        from tethys_sdk.gizmos import Button

        ...

        @controller(url='dams/add')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success'
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'add_button': add_button,
                'cancel_button': cancel_button,
            }

            return App.render(request, 'add_dam.html', context)

b. Save your changes to ``controllers.py`` and ``add_dam.html`` and refresh the page to view the updated page.

8. Link to New Page
===================

Finally, you can also link to the page from another page using a button. Add custom header buttons for the **Map** and **Add Dam** pages to make it easier to navigate between the two pages.

a.  Open the ``/template/dam_inventory/base.html`` and add the following ``block``:

    .. code-block:: html+django

        {% block header_buttons %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          <div class="header-button glyphicon-button">
            <a href="{{ home_url }}" title="Map"><i class="bi bi-map"></i></a>
          </div>
          <div class="header-button glyphicon-button">
            <a href="{{ add_dam_url }}" title="Add Dam"><i class="bi bi-plus-circle"></i></a>
          </div>
        {% endblock %}

.. tip::

    **Bootstrap**: Tethys Platform provides a library called `Bootstrap <https://getbootstrap.com/>`_ that is used to create layouts and style the app. The ``glyphicon-button`` class used above is a custom class that is used to style the buttons in the header of the app. The ``bi bi-map`` and ``bi bi-plus-circle`` classes are used to add icons to the buttons. To see more icons available via Bootstrap, visit the `Bootstrap Icons <https://icons.getbootstrap.com/>`_.

9. Customize Navigation
=======================

In addition to Header button, you can add navigation links to the side left side bar of the app. Modify the app navigation to have links to the **Map** and **Add Dam** pages.

a. Open ``/templates/dam_inventory/base.html`` and replace the ``app_navigation_items`` block:

    .. code-block:: html+django

        {% block app_navigation_items %}
        <li class="nav-item title">Navigation</li>
        <li class="nav-item"><a class="nav-link active" href="{% url tethys_app|url:'home' %}">Map</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url tethys_app|url:'add_dam' %}">Add Dam</a></li>
        {% endblock %}

    Notice that the **Home** link in the app navigation is always highlighed, even if you are on the **Add Dam** page. The highlight is controlled by adding the ``active`` class to the appropriate navigation link. We can get the navigation to highlight appropriately using the following pattern.

b. Modify ``app_navigation_items`` block in ``/templates/dam_inventory/base.html`` to dynamically highlight active link:

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

10. Solution
============

This concludes the Beginner Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dam_inventory
    cd tethysapp-dam_inventory
    git checkout -b beginner-solution beginner-|version|
