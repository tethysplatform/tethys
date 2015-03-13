*******************
Template Gizmos API
*******************

**Last Updated:** November 18, 2014

Template Gizmos are building blocks that can be used to create beautiful interactive controls for web apps. Using the Template Gizmos API, developers can add date-pickers, plots, and maps to their app templates with minimal coding. This article provides an overview of how to use Gizmos. If you are not familiar with templating in Tethys apps, please review :doc:`../getting_started/view` tutorial before proceeding.

Define Options Object
=====================

The best way to illustrate how to use Template Gizmos is to look at an example. The following example illustrates how to add a date picker using Gizmos. The first step is to define a dictionary with all the configuration options for the Gizmo. This should be done in the controller of the template where the Gizmo will be used.

In this case, the Gizmo options dictionary is called "date_picker_options" and it is passed to the template via the ``context``:

::

    def example_controller(request):
        """
        Example of a controller that defines options for a Template Gizmo.
        """
        date_picker_options = {'display_text': 'Date',
                               'name': 'date1',
                               'autoclose': True,
                               'format': 'MM d, yyyy',
                               'start_date': '2/15/2014',
                               'start_view': 'decade',
                               'today_button': True,
                               'initial': 'February 15, 2014'}

        context = {'date_picker_options': date_picker_options}

        return render(request, 'path/to/my/template.html', context)

See the :doc:`./gizmos_api` for a detailed description of the options object for each gizmo.

Load Gizmo Library
==================

After the Gizmo options have been defined in the controller, the Gizmo can be added to the template. At the top of the template, the ``tethys_gizmos`` library needs to be loaded using the Django ``load`` tag. This will make the Gizmo library accessible to the template and only needs to be done once for each template that uses Gizmos:

::

    {% load tethys_gizmos %}

Add the Gizmo
=============

The ``gizmo`` tag is used to insert the date picker anywhere in the template. The ``gizmo`` tag accepts two arguments: the name of the Gizmo to insert and a dictionary of configuration options for the Gizmo. In the example, the ``date_picker`` Gizmo is inserted and the ``date_picker_options`` dictionary that was defined in the controller is provided:

::

    {% gizmo date_picker date_picker_options %}

.. note::

    If you are using Gizmos in a Django project outside of Tethys Platform, you will also need to include the ``gizmo_dependencies`` tag. This tag is automatically included in the base template of Tethys app projects.

    Many of the Gizmos require CSS and JavaScript libraries to work properly. These dependencies are loaded using the ``gizmo_dependencies`` tag and it must be included in the template after all occurrences of the ``gizmo`` tag:

    ::

        {% gizmo_dependencies %}

Rendered Gizmo
==============

The date picker will be inserted at the location of the ``gizmo`` tag. The template with the rendered date picker would look something like this:

.. figure:: ../images/gizmo_example.png
    :width: 650px

Gizmo Showcase
==============

Live demos and documentation of the configuration options for each Gizmo is provided as a developer tool called "Gizmo Showcase" in every Tethys Platform installation. To access the Gizmo Showcase, start up the development server and navigate to the home page of your Tethys Portal at `<http://127.0.0.1:8000>`_. Login and select the Developer link from the main navigation. This will bring up the Developer Tools page of your Tethys Portal:

.. figure:: ../images/developer_tools_page.png
    :width: 650px


Select the Gizmos developer tool and you will be brought to the Gizmo Showcase page:

.. figure:: ../images/gizmo_showcase_page.png
    :width: 650px

In addition to the live demos, the Gizmo Showcase also provides code examples and tables detailing the different options that are available for each Gizmo. The Gizmo Showcase is the primary form of documentation on Gizmos for Tethys app developers.

Tag API Reference
=================

This section contains a brief explanation of the template tags provided by the ``tethys_gizmos`` library.

**gizmo**
---------

Inserts a Gizmo at the location of the tag.

*Parameters*:

* **name** (string or literal) - The name of the Gizmo to insert as either a string (e.g.: "date_picker") or a literal (e.g.: date_picker).
* **options** (dict) - The configuration options for the Gizmo. The options are Gizmo specific. See the Gizmo Showcase documentation for descriptions of the options that are available.

*Examples*:

::

    # With literal for name parameter
    {% gizmo date_picker date_picker_options %}

    # With string for name parameter
    {% gizmo "date_picker" date_picker_options %}


**gizmo_dependencies**
----------------------

Inserts the CSS and JavaScript dependencies at the location of the tag. This tag must appear after all occurrences of the ``gizmo`` tag.

*Parameters*:

* **type** (string or literal, optional) - The type of dependency to import. This parameter can be used to include the CSS and JavaScript dependencies at different locations in the template. Valid values include "css" for CSS dependencies or "js" for JavaScript dependencies.

*Examples*:

::

    # No type parameter
    {% gizmo_dependencies %}

    # CSS only
    {% gizmo_dependencies css %}

    # JavaScript only
    {% gizmo_dependencies js %}
