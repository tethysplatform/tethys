********************
App Basics: Beginner
********************

**Last Updated:** May 2017

.. warning::

   UNDER CONSTRUCTION


* MVC
* Templating API
* Controllers
* App Base Class API
* URL Maps
* Simple Gizmos API

Narrative
* Introduce MVC concepts and show files in app project that coorespond
* Open Home Template and explain templating API / Django Templating Language
* Open Controller file and explain controller
* Open app base class and explain purpose
* Add empty map to home page
* Create new template, controller, and url map to be used for adding new dams to inventory
* Create "Add Dam" button in actions area that opens new page

Model View Controller
=====================

Tethys apps are developed using the :term:`Model View Controller` (MVC) software architecture pattern. Following the MVC pattern will make your app project easier to develop and maintain in the future. Most of the code in your app will fall into one of the three MVC categories. The Model represents the data of your app, the View is composed of the representation of the data, and the Controller consists of the logic to prepare the data for the view and any other logic your app needs. In the next few tutorials, you will be introduced to how the MVC development paradigm is used to develop Tethys apps. For more information about MVC, see :doc:`../../supplementary/key_concepts`.

App Class
=========

* Open app.py
* Change color of app
* Add custom app icon

:doc:`../../tethys_sdk/app_class`

App Admin Settings
==================

* View app settings in the Admin interface

Add a Map to the Home Page
==========================

Intro to templates... :doc:`../../tethys_sdk/templating`
Twitter Bootstrap...
JQuery...
Intro to Gizmo tags... :doc:`../../tethys_sdk/gizmos`

Open ``templates/dam_inventory/home.html`` and replace it's contents with the following:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
      {% gizmo dam_inventory_map %}
    {% endblock %}

    {% block app_actions %}
      {% gizmo add_dam_button %}
    {% endblock %}

Define Gizmos in Home Controller
================================

Intro to controllers...
Intro to Gizmo options objects... :doc:``../../tethys_sdk/gizmos/map_view` and :doc:`../../tethys_sdk/gizmos/button`

Define the ``dam_inventory_map`` and ``add_dam_button`` gizmos in your home controller. Open ``controllers.py`` and change the ``home`` controller function as follows:

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

Add Dam Page
============

Create a new file ``templates/dam_inventory/add_dam.html`` and add the follow contents:

::

    {% extends "dam_inventory/base.html" %}

    {% block app_content %}
      <h1>Add Dam</h1>
    {% endblock %}

Add Dam Controller
==================

Create a new controller function called ``add_dam`` at the bottom of the ``controllers.py``:

::

    @login_required()
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """

        context = {}
        return render(request, 'dam_inventory/add_dam.html', context)

Add Dam URL Map
===============

Intro to URL Maps...

Create a new URL Map for the ``add_dam`` controller in the ``url_maps`` method of App Class in ``app.py``:

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

Link to Add Dam Page
====================

Intro to linking...

Modify the ``add_dam_button`` to link to the newly created page:

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

Add Buttons to Add Dam Page
===========================

Modify the ``template/dam_inventory/add_dam.html`` to add ``Add`` and ``Cancel`` buttons to the app actions area:

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

Define the ``Add`` and ``Cancel`` button gizmos in the ``add_app`` controller:

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


Add Navigation
==============

Intro to base.html template...

Open ``templates/dam_inventory/base.html`` and replace the ``app_navigation_items`` block:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      <li class="active"><a href="{% url 'dam_inventory:home' %}">Home</a></li>
      <li class=""><a href="{% url 'dam_inventory:add_dam' %}">Add Dam</a></li>
    {% endblock %}


Dynamic Active Link in Navigation
=================================

Modify ``app_navigation_items`` block in ``templates/dam_inventory/base.html``:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      {% url 'dam_inventory:home' as home_url %}
      {% url 'dam_inventory:add_dam' as add_dam_url %}
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
    {% endblock %}
