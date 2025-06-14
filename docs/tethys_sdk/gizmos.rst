.. _gizmos_api:

*******************
Template Gizmos API
*******************

**Last Updated:** March 2022

Template Gizmos are building blocks that can be used to create beautiful interactive controls for web apps. Using the Template Gizmos API, developers can add date-pickers, plots, and maps to their app pages with minimal coding. This article provides an overview of how to use Gizmos.

For a detailed explanation and code examples of each Gizmo, see the :ref:`gizmo_options` section.

Working with Gizmos
===================

The best way to illustrate how to use Template Gizmos is to look at an example. The following example illustrates how to add a date picker to a page using the ``DatePicker Gizmo``. The basic workflow involves three steps:

1. Define gizmo options object in the controller for the template
2. Load gizmo library in the template
3. Insert the gizmo tag in the template at the desired location

A detailed description of each step follows.


1. Define Gizmo Options Object in Controller
--------------------------------------------

The first step is to import the appropriate options object and configure the Gizmo. This is performed in the controller of the template where the Gizmo will be used.

In this case, we import ``DatePicker`` and initialize a new object called ``date_picker`` with the desired options. Then we pass the object to the template via the ``context`` dictionary:

::

    from tethys_sdk.gizmos import DatePicker
    from .app import App

    def gizmo_controller(request):
        """
        Example of a controller that defines options for a Template Gizmo.
        """
        date_picker = DatePicker(
            name='date',
            display_text='Date',
            autoclose=True,
            format='MM d, yyyy',
            start_date='2/15/2014',
            start_view='decade',
            today_button=True,
            initial='February 15, 2017'
        )

        context = {'date_picker': date_picker}

        return App.render(request, 'template.html', context)

The :ref:`gizmo_options` section provides detailed descriptions of each Gizmo option object, valid parameters, and examples of how to use them.

2. Load Gizmo Library in Template
---------------------------------

Now near the top of the template where the Gizmo will be inserted, load the ``tethys`` library using the `Django load tag <https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#load>`_. This only needs to be done once per template:

::

    {% load tethys %}


4. Insert the Gizmo
-------------------

The ``gizmo`` tag is used to insert the date picker anywhere in the template. The ``gizmo`` tag accepts a Gizmo object of configuration options for the Gizmo:

::

    {% gizmo <options> %}


For this example, call the ``gizmo`` tag with the ``date_picker`` object that was defined in the controller and passed to the template as an argument:

::

    {% gizmo date_picker %}

Rendered Gizmo
==============

The Gizmo tag is replaced with the appropriate HTML, JavaScript, and CSS that is needed to render the Gizmo. In the example, the date picker is inserted at the location of the ``gizmo`` tag. The template with the rendered date picker would look something like this:

.. figure:: ../images/gizmo_example.png
    :width: 650px

Gizmo Showcase App
==================

The Gizmo Showcase App provides live demos and code examples of every Tethys Gizmo. See :ref:`installation_gizmo_showcase_app` to learn how to install the Gizmo Showcase app. For explanations of the Gizmo Options objects and code examples, refer to the :ref:`gizmo_options` section.

API Documentation
=================

This section contains a brief explanation of the template tags that power Gizmos. These are provided by the ``tethys`` library that you load at the top of templates that use Gizmos.

.. code-block:: html+django

    {% load tethys%}

**gizmo**
---------

Inserts a Gizmo at the location of the tag.

*Parameters*:

* **options** (dict) - The configuration options for the Gizmo. The options are Gizmo specific. See the Gizmo Showcase documentation for descriptions of the options that are available.

*Example*:

::

    {% gizmo date_picker %}

**import_gizmo_dependency**
---------------------------

Tells the ``gizmo_dependencies`` to load in the dependencies for the gizmo. This tag must be in the ``import_gizmos`` block. This is useful for pre-loading the dependencies of a gizmo that is not loaded on the initial page load (e.g.: loading the gizmos using AJAX after the initial page load).

*Parameters*:

* **name** (string or literal) - The name of the Gizmo for which to load dependencies as a string (e.g.: "date_picker") or a literal (e.g.: date_picker).

.. note:: You can get the name of the gizmo through the *gizmo_name* attribute of the gizmo object.


*Controller Example*:

::

    from tethys_sdk.gizmos import DatePicker

    def example_controller(request):
        """
        Example of a controller that defines options for a Template Gizmo.
        """
        context = {'date_picker_name': DatePicker.gizmo_name}

        return render(request, 'path/to/my/template.html', context)

*Template Example*:

::

    {% block import_gizmos %}
        {% import_gizmo_dependency date_picker_name %}
    {% endblock %}

**gizmo_dependencies**
----------------------

Inserts of the CSS and JavaScript dependencies at the location of the tag for all gizmos loaded in the template with the ``gizmo`` tag. This tag must appear after all occurrences of the ``gizmo`` tag. In Tethys Apps, these dependencies are imported for you, so this tag is not required. For external Django projects that use the tethys_gizmos Django app, this tag is required.

*Parameters*:

* **type** (string or literal, optional) - The type of dependency to import. This parameter can be used to include the CSS and JavaScript dependencies at different locations in the template. Valid values include "css" for CSS dependencies, "global_css" for CSS library dependencies, "js" for JavaScript dependencies, and "global_js" for JavaScript library dependencies.

*Examples*:

::

    # No type parameter
    {% gizmo_dependencies %}

    # CSS only
    {% gizmo_dependencies global_css %}
    {% gizmo_dependencies css %}

    # JavaScript only
    {% gizmo_dependencies global_js %}
    {% gizmo_dependencies js %}

.. _gizmo_options:

Gizmos Options Objects
======================

This section provides explanations of each of the Gizmo Options Objects available for configuring Gizmos. It also provides code and usage examples for each object.

.. toctree::
   :maxdepth: 1

   gizmos/button
   gizmos/date_picker
   gizmos/range_slider
   gizmos/select_input
   gizmos/text_input
   gizmos/toggle_switch
   gizmos/message_box
   gizmos/slide_sheet
   gizmos/table_view
   gizmos/datatable_view
   gizmos/plot_view
   gizmos/plotly_view
   gizmos/bokeh_view
   gizmos/map_view
   gizmos/cesium_map_view
   gizmos/esri_map
   gizmos/jobs_table
