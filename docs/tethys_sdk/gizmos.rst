*******************
Template Gizmos API
*******************

**Last Updated:** May 21, 2015

Template Gizmos are building blocks that can be used to create beautiful interactive controls for web apps. Using the Template Gizmos API, developers can add date-pickers, plots, and maps to their app pages with minimal coding. This article provides an overview of how to use Gizmos. If you are not familiar with templating in Tethys apps, please review :doc:`../tutorials/getting_started/view` tutorial before proceeding.

For a detailed explanation and code examples of each Gizmo, see the :doc:`./gizmos_api` documentation.

Working with Gizmos
===================

The best way to illustrate how to use Template Gizmos is to look at an example. The following example illustrates how to add a date picker to a page using the Date Picker Gizmo. The basic workflow involves three steps:

1. Define gizmo options in the controller for the template
2. Load gizmo library in the template
3. Insert the gizmo tag in the template

A detailed description of each step follows.


1. Define Gizmo Options
-----------------------

The first step is to import the appropriate options object and configure the Gizmo. This is performed in the controller of the template where the Gizmo will be used.

In this case, we import ``DatePicker`` and initialize a new object called ``date_picker_options`` with the appropriate options. Then we pass the object to the template via the ``context`` dictionary:

::

    from tethys_gizmos.gizmos_options import DatePicker

    def example_controller(request):
        """
        Example of a controller that defines options for a Template Gizmo.
        """
        date_picker_options = DatePicker(name='data1',
                                         display_text='Date',
                                         autoclose=True,
                                         format='MM d, yyyy',
                                         start_date='2/15/2014',
                                         start_view='decade',
                                         today_button=True,
                                         initial='February 15, 2014')

        context = {'date_picker_options': date_picker_options}

        return render(request, 'path/to/my/template.html', context)

.. note::

    The Gizmo Options objects are new as of version 1.1.0. Prior to this time, Gizmo options were defined using dictionaries. The dictionary parameterization of Gizmos is still supported, but will no longer be referenced in the documentation.

The :doc:`./gizmos_api` provides detailed descriptions of each Gizmo option object, valid parameters, and examples of how to use them.

2. Load Gizmo Library
---------------------

Now near the top of the template where the Gizmo will be inserted, load the ``tethys_gizmos`` library using the `Django load tag <https://docs.djangoproject.com/en/1.8/ref/templates/builtins/#load>`_. This only needs to be done once per template:

::

    {% load tethys_gizmos %}

3. Insert the Gizmo
-------------------

The ``gizmo`` tag is used to insert the date picker anywhere in the template. The ``gizmo`` tag accepts two arguments: the name of the Gizmo to insert and a dictionary of configuration options for the Gizmo:

::

    {% gizmo <name> <options> %}


For this example, the ``date_picker`` Gizmo is inserted and the ``date_picker_options`` object that was defined in the controller and passed to the template is provided:

::

    {% gizmo date_picker date_picker_options %}

Rendered Gizmo
==============

The Gizmo tag is replaced with the appropriate HTML, JavaScript, and CSS that is needed to render the Gizmo. In the example, the date picker is inserted at the location of the ``gizmo`` tag. The template with the rendered date picker would look something like this:

.. figure:: ../images/gizmo_example.png
    :width: 650px

Gizmo Showcase
==============

Live demos of each Gizmo is provided as a developer tool called "Gizmo Showcase". To access the Gizmo Showcase, start up your development server and navigate to the home page of your Tethys Portal at `<http://127.0.0.1:8000>`_. Login and select the ``Developer`` link from the main navigation. This will bring up the Developer Tools page of your Tethys Portal:

.. figure:: ../images/developer_tools_page.png
    :width: 650px


Select the Gizmos developer tool and you will be brought to the Gizmo Showcase page:

.. figure:: ../images/gizmo_showcase_page.png
    :width: 650px

For explanations the Gizmo Options objects and code examples, refer to the :doc:`./gizmos_api`.

Django Tag Reference
====================

This section contains a brief explanation of the template tags that power Gizmos. These are provided by the ``tethys_gizmos`` library that you load at the top of templates that use Gizmos.

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

Inserts the CSS and JavaScript dependencies at the location of the tag. This tag must appear after all occurrences of the ``gizmo`` tag. In Tethys Apps, these depenencies are imported for you, so this tag is not required. For external Django projects that use the tethys_gizmos Django app, this tag is required.

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
