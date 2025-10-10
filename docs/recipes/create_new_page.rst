.. _create_new_page_recipe :


*****************
Create a New Page
*****************

**Last Updated:** June 2025

This recipe will show you how to add additional pages to your Tethys app. You may need to create a new page to display various types of data, include explanatory text, or have a home page separate from a map viewer.

1. Create a new :file:`templates/new_app/new_page.html` with the following contents:

.. code-block:: html+django

    {% extends tethys_app.package|add:"/base.html" %}
    {% load static tethys %}

    {% block app_content %}
    <h1>Welcome to your brand new page</h1>
    {% endblock %}

2. Create a new ``new_page`` controller in :file:`controllers.py`:

.. code-block:: python

    from tethys_sdk.routing import controller
    @controller(name='new_page', url='new_page')
    def new_page(request):
        """
        Controller for the app home page.
        """
        context = {}
        return App.render(request, 'new_page.html', context)

3. Navigate to `<http://localhost:8000/apps/new_app/new_page/>`_ and verify that the new page loads with text "Welcome to your brand new page".

.. figure:: ../../docs/images/recipes/new_page.png
    :width: 500px
    :align: center

.. tip::  
    
    For more details on navigating between pages in your app see the :ref:`Add Navigation Buttons Recipe <add_navigation_buttons_recipe>` recipe and :ref:`templating_api`.


    For more details templating a new page see the :ref:`templating_api`.

