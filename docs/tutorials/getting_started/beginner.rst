*****************
Beginner Concepts
*****************

**Last Updated:** May 2017

This tutorial introduces important concepts for first-time or beginner Tethys developers.

1. App Class
============

a. Open ``app.py`` in your favorite Python IDE or text editor. The app class, located in ``app.py`` is the primary configuration file for Tethys apps. All app classes inherit from the ``TethysAppBase`` class.

b. Change the theme color of your app by changing the value of the ``color`` property of the ``DamInventory`` class. Use a site like `color-hex <http://www.color-hex.com/>`_ to find an appropriate hexadecimal RGB color.

c. You can also change the icon of your app. Find a new image online and save it in the ``public/images/`` directory of your app. Then change the value of the ``icon`` property of the ``DamInventory`` class to match the name of the image.

For more details about the app class, see the :doc:`../../tethys_sdk/app_class`.

.. warning::

    DO NOT change the value of the ``index``, ``package``, or ``root_url`` properties of your app class unless you know what you are doing. Doing so will break your app.

2. App Settings
===============

Other settings for your app can be configured in the app settings. To access the app settings, click on the Settings button (gear icon) at the top right-hand corner of the screen. App settings are stored in a database, meaning they can be changed dynamically by the administrator of your portal. Some app settings, like Name and Description, correspond with properties in the ``app.py`` script.

a. Change the Name and Description of your app by changing their respective values on the app settings page. Press the ``Save`` button, located at the bottom of the app settings page. Then navigate back to your app to see the changes.

You can also create custom settings for your app that can be configured on the app settings page. This is done in the ``app.py``

b. Open the ``app.py`` and add the ``custom_settings()`` method to the ``DamInventory`` class:

    ::

        from tethys_sdk.app_settings import CustomSetting

        class DamInventory(TethysAppBase):
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

c. Save changes to ``app.py`` then restart your development server (press ``CTRL-C`` to stop followed by the ``tms`` command to start it again).

d. Navigate to the settings page of your app and scroll down to the **Custom Settings** section and you should see an entry for the ``max_dams`` settings. Enter a value and save changes to the setting. You will learn how to use this custom setting in the app later on in the tutorial.

For more information about app settings, see the :doc:`../../tethys_sdk/app_settings`.

3. Model View Controller
========================

Tethys apps are developed using the :term:`Model View Controller` (MVC) software architecture pattern. Model refers to the data model and associated code, View refers to the representations of the data, and Controller refers of the code that coordinates data from the Model for rendering in the View. In Tethys apps, the Model is usually an SQL database or files and the code for accessing them, the Views are most often the templates or HTML files, and Controllers are implemented as Python functions.

For more information about the MVC pattern, see :doc:`../../supplementary/key_concepts`.


a. Views
--------

Views for Tethys apps are constructed using the standard web programming tools: HTML, JavaScript, and CSS. Additionally, Tethys Platform provides the Django Python templating language allowing you to insert Python code into your HTML documents. The result is dynamic, reusable templates for the web pages of your app.

i. Open ``templates/dam_inventory/home.html`` and replace it's contents with the following:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
      {% gizmo dam_inventory_map %}
    {% endblock %}

    {% block app_actions %}
      {% gizmo add_dam_button %}
    {% endblock %}


Django Templating Language
++++++++++++++++++++++++++

If you are familiar with HTML, the contents of this file may seem strange. That's because the file is actually a Django template, which contains special syntax (i.e.: ``{% ... %}`` and ``{{ ... }}`` to make the template dynamic. Django templates can contain variables, filters, and tags.

**Variables.** Variables are denoted by double curly brace syntax like this: ``{{ variable }}``. Template variables are replaced by the value of the variable. Dot notation can be used access attributes of a variable, keys of dictionaries, and items in lists: ``{{ my_object.attribute }}`` , ``{{ my_dict.key }}``, and ``{{ my_list.3 }}``.

**Filters.** Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Filters perform modifying functions on variable output such as formatting dates, formatting numbers, changing the letter case, and concatenating multiple variables.

**Tags.** Tags use curly-brace-percent-sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``.

**Blocks.** The block tags in the Tethys templates coorespond with different areas in the app. For example, any HTML written inside the ``app_content`` block will render in the app content area of the app.

.. tip::

    For a better explanation of variables, filters and tags, see the :doc:`../../tethys_sdk/templating`.

b. Controllers
--------------

This ``home.html`` template used a Tethys template tag, ``gizmo``, to insert a map and a button with only one line of code: ``{% gizmo dam_inventory_map %}``. Gizmo tags require one argument, an object that defines the options for the gizmo. These gizmo options must be defined in the controller for that view.

i. Open ``controllers.py``.

ii. Define the ``dam_inventory_map`` and ``add_dam_button`` gizmos in your home controller. Open ``controllers.py`` and change the ``home`` controller function as follows:

::

    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from tethys_sdk.gizmos import MapView, Button


    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """

        dam_inventory_map = MapView(
            height='100%',
            width='100%',
            layers=[],
            basemap='OpenStreetMap',
        )


        add_dam_button = Button(
            display_text='Add Dam',
            name='add-dam-button',
            icon='glyphicon glyphicon-plus',
            style='success'
        )

        context = {
            'dam_inventory_map': dam_inventory_map,
            'add_dam_button': add_dam_button
        }

        return render(request, 'dam_inventory/home.html', context)

Any variable assigned to the ``context`` variable in a controller becomes a variable on the template specified in the ``render`` function. In this case we created the options objects for the two gizmos on the ``home.html`` template.

For more details on the Map View or Button Gizmos see: :doc:`../../tethys_sdk/gizmos/map_view` and :doc:`../../tethys_sdk/gizmos/button` For more information about Gizmos in general see the :doc:`../../tethys_sdk/gizmos`.

4. Create a New Page
====================

Creating a new page in your app consists of three steps: (1) create a new template, (2) add a new controller to ``controllers.py``, and (3) add a new ``UrlMap`` to the ``app.py``.

a. Create a new file ``templates/dam_inventory/add_dam.html`` and add the following contents:

::

    {% extends "dam_inventory/base.html" %}

This is the simplest template you can create in a Tethys app, which amounts to a blank Tethys app page. You must still extend the ``base.html`` to retain the styling of an app page.


b. Create a new controller function called ``add_dam`` at the bottom of the ``controllers.py``:

::

    @login_required()
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """

        context = {}
        return render(request, 'dam_inventory/add_dam.html', context)

This is the most basic controller function you can write: a function that accepts an argument called ``request`` and a return value that is the result of the ``render`` function. The ``render`` function renders the Django template into valid HTML using the ``request`` and ``context`` provided.

c. Create a new URL Map for the ``add_dam`` controller in the ``url_maps`` method of App Class in ``app.py``:

::

    ...

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='dam-inventory',
                controller='dam_inventory.controllers.home'
            ),
            UrlMap(
                name='add_dam',
                url='dam-inventory/dams/add',
                controller='dam_inventory.controllers.add_dam'
            )
        )

        return url_maps

A ``UrlMap`` is an object that maps a URL for your app to controller function that should handle requests to that URL.

5. Link to New Page
===================

You can access the new page of your app simply be entering the URL `<http://localhost:8000/apps/dam-inventory/dams/add/>`_ into the address bar of your browser. However, you can also link to the page from another page using a button.

a. Modify the ``add_dam_button`` on the Home page to link to the newly created page:

::

    from django.core.urlresolvers import reverse

    ...

    @login_required()
    def home(request):
        ...

        add_dam_button = Button(
            display_text='Add Dam',
            name='add-dam-button',
            icon='glyphicon glyphicon-plus',
            style='success',
            href=reverse('dam_inventory:add_dam')
        )

6. Build Out New Page
=====================

a. Modify the ``template/dam_inventory/add_dam.html`` with a title in the app content area and add ``Add`` and ``Cancel`` buttons to the app actions area:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
      <h1>Add Dam</h1>
    {% endblock %}

    {% block app_actions %}
      {% gizmo add_button %}
      {% gizmo cancel_button %}
    {% endblock %}

b. Define the options for the ``Add`` and ``Cancel`` button gizmos in the ``add_app`` controller in ``controllers.py``:

::

    @login_required()
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        add_button = Button(
            display_text='Add',
            name='add-button',
            icon='glyphicon glyphicon-plus',
            style='success'
        )

        cancel_button = Button(
            display_text='Cancel',
            name='cancel-button',
            href=reverse('dam_inventory:home')
        )

        context = {
            'add_button': add_button,
            'cancel_button': cancel_button,
        }

        return render(request, 'dam_inventory/add_dam.html', context)


7. Add Navigation
=================

Now that there are two pages in the app, we should modify the app navigation to have links to the **Home** and **Add Dam** pages.

a. Open ``templates/dam_inventory/base.html`` and replace the ``app_navigation_items`` block:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      <li class="active"><a href="{% url 'dam_inventory:home' %}">Home</a></li>
      <li class=""><a href="{% url 'dam_inventory:add_dam' %}">Add Dam</a></li>
    {% endblock %}

Notice that the **Home** link in the app navigation is always highlighed, even if you are on the **Add Dam** page. The highlight is controlled by adding the ``active`` class to the appropriate navigation link. We can get the navigation to highlight appropriately using the following pattern.

b. Modify ``app_navigation_items`` block in ``templates/dam_inventory/base.html`` to dynamically highlight active link:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      {% url 'dam_inventory:home' as home_url %}
      {% url 'dam_inventory:add_dam' as add_dam_url %}
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
    {% endblock %}

The ``url`` tag can be used in templates to lookup URLs using the name of the UrlMap, namespaced by the app package name (i.e.: ``namespace:url_map_name``). We assign the urls to two variables, ``home_url`` and ``add_dam_url``, using the ``as`` operator in the ``url`` tag. Then we wrap the ``active`` class of each navigation link in an ``if`` tag. If the expression given to an ``if`` tag evaluates to true, then the content of the ``if`` tag is rendered, otherwise it is left blank. In this case the result is that the ``active`` class is only added to link of the page we are visiting.

8. Solution
===========

This concludes the Beginner Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

::

    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout beginner-solution
