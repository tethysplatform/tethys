.. _tethys_components_reactpy:

***************************************
Pure-Python-Component-Based Development
***************************************

.. note::

    This guide assumes you have already installed Tethys Platform. 
    If you haven't done so, please first complete the :ref:`development_installation` guide.


Getting Started
===============

.. note::
    
    Be sure to `ref:activate_environment` before running any of the commands below.

1. Scaffold a new Tethys app using the ``reactpy`` template 
-----------------------------------------------------------

.. code-block:: bash

    tethys app scaffold <app_project_folder_name> -t reactpy

This command will prompt you to answer a few questions via the command line and then will create all of the necessary files and directories for your app, which are as follows:

::

    <app_project_folder_name>
    ├── install.yml - Tethys project configuration.
    ├── pyproject.toml - Python project configuration.
    ├── README.rst - Documentation.
    └── tethysapp/<app_project_folder_name>/ - Source code
            ├── __init__.py - Python package initialization file
            ├── app.py - Main application
            ├── public/images/ - Public images
            |   └── icon.png - Default icon
            └── tests/ - Test files
                └── ``test.py`` - Unit tests

2. Navigate to the newly created app directory
----------------------------------------------

.. code-block:: bash

    cd <app_project_folder_name>

3. Install the app into Tethys Platform:
----------------------------------------

.. code-block:: bash

    tethys install -d

Include ``-d`` to install the app in development mode, which allows you to make changes without needing to reinstall the app each time.

4. Start the Tethys server
--------------------------

.. code-block:: bash

    tethys start

5. Open your application in the browser
---------------------------------------

Navigate to http://localhost:8000/apps/<app-project-folder-name>.

6. Start Building Your App
--------------------------

Modify the ``app.py`` file to create the application of your dreams. The Tethys server will automatically reload your app when you save changes to the ``app.py`` file so you can view the changes in the browser.

The ``app.py`` File
===================

The ``app.py`` file is the heart of your Tethys app. It typically includes:

- An ``App`` class inheriting from ``ReactPyBase`` (required)
- The code for your app's Component-based Pages (optional, see note below)

.. note::

    As your app grows, you may want to organize your code into multiple files for better maintainability. For example, you can create a ``pages.py`` file to define your page functions and simply import your ``App`` class into them to access the page decorator. Or, you could even have a ``pages`` directory with multiple files, each containing a set of related page functions. Just make sure to import the ``App`` class from your ``app.py`` file in each of these files to use the page decorator.

The ``App`` Class
=================

The ``App`` class inherits from ``ReactPyBase`` and dictates your app's high-level metadata and configuration by overriding the appropriate properties of the ``ReactPyBase`` class. These properties include:

    - ``name``: The title of the app, as formally displayed to users.
    - ``description``: A brief description of the app. This will be displayed in the Tethys Portal when hovering over the app's info icon in the Apps Library page.
    - ``package``: The Python package name of the app. This is typically the <app_project_folder_name> specified when scaffolding the app. This should not ever be changed.
    - ``index``: The name of the default page to display when the app is accessed (also known as the app's main landing page, or home page).
    - ``icon``: The path to the app's icon image. This can be relative to the app's package directory or an absolute URL. The icon is displayed in the Tethys Portal and in the app's header.
    - ``root_url``: The URL path for the app. This is simply the slugified version of the app's name, which is used to construct the app's URL in the Tethys Portal. It should be unique across all apps.
    - ``color``: The primary color for the app's theme, in hexadecimal format (e.g., ``#d35400``). This color is used in the app's header and other UI elements.
    - ``tags``: A comma-separated list of tags for the app. If your portal ends up with many apps, this can help users find your app.
    - ``enable_feedback``: A boolean indicating whether to enable user feedback for the app. If true, this will display a feedback button in the app's header.
    - ``feedback_emails``: A list of email addresses to receive feedback from users.
    - ``exit_url``: The URL to redirect users to when they exit the app.
    - ``default_layout``: The default layout for the app, which defines the basic structure of your app's pages. Allowed values are ``"NavHeader"`` or ``None``. ``"NavHeader"`` provides a navigation header that can be configured via the ``nav_links`` property below, while ``None`` means no navigation header is used. This can be overridden on a per-page basis (see :ref:`tethys_components_pages`).
    - ``nav_links``: The navigation links for the app. This can be set to ``"auto"`` to automatically generate links based on the defined pages, or you can provide a list of dict objects, each with ``"title"`` and ``"href"`` keys with their appropriate values (see example below).
        
        .. code-block:: bash
            
            nav_links=[{"title": "Home", "href": "/apps/tutorial-app/home"}].

**Example:**

.. code-block:: python

    from tethys_sdk.components import ReactPyBase

    class App(ReactPyBase):
        """
        Tethys app class for ReactPy Demo.
        """
        name = 'Tutorial'
        description = 'This is a tutorial app.'
        package = 'tutorial_app'
        index = 'home'
        icon = f'{package}/images/icon.png'
        root_url = 'tutorial-app'
        color = '#d35400'
        tags = ''
        enable_feedback = False
        feedback_emails = []
        exit_url = '/apps/'
        default_layout = "NavHeader"
        nav_links = "auto"

.. _tethys_components_pages:

Pages (The ``App.page`` Decorator)
====================================

Pages are defined via functions decorated with ``App.page``, where ``App`` is your app class that inherits from ``ReactPyBase``.
These page functions can be defined anywhere in your app's source code, such as in a separate ``pages.py`` file or in multiple ``<page_name>.py`` files within a ``pages`` directory. 
The important thing is that they are decorated with the ``App.page`` decorator to register them as pages of your app.

Each decorated function must receive a ``lib`` argument, which provides access to built-in component libraries, hooks for managing state and app interactivity, and other relevant utilities (see :ref:`tethys_components_library`. Each page function should return a single :ref:`Component <tethys_components_components>` representing the page's content, which can as simple or complex as you'd like.

Various arguments can be passed to the ``App.page`` decorator to customize the page's behavior and appearance. See the API below:

.. autofunction:: tethys_apps.base.controller.page

**Examples:**

.. code-block:: python

    @App.page  # This uses the defaults, which work well for most apps
    def home(lib):
        # This is the home page of the app
        return lib.html.div(
            lib.html.h1("Welcome to My ReactPy App"),
            lib.html.p("This is the home page."),
        )
    
    @App.page(title='Hidden Page', url='page-not-in-nav', index=-1)
    def lost_page(lib):
        # This page will not be included in the navigation links
        return lib.html.div(
            lib.html.h2("This page is hidden from the navigation links!"),
            lib.html.p("You can still access it via its URL."),
        )

.. _tethys_components_custom_layout:

Custom Layout
-------------

You can define a custom layout for your app or a single page by creating a function that takes the ``lib``, ``app``, ``user``, and optional ``nav_links`` and ``content`` arguments. This function can then be passed by reference to either the ``App.page`` decorator or the ``default_layout`` property of the ``App`` class.
This function should return a single component that represents the layout of your app with the ``content`` argument being nested where the main content of your pages would go.

.. note::

    This is most helpful if you want to create a custom layout across multiple pages. If you only want a single page to have a custom layout, yout can simply set ``layout=None`` (in the ``App.page`` decorator of your unique page function) or ``default_layout=None`` (in the ``App`` class) and simply define the entire layout and content in the page function itself.

**Page example:**

.. code-block:: python

    def custom_page_layout(lib, app, user, nav_links=None, content=None):
        return lib.html.div(
            lib.html.h1("My Custom Page Layout"),
            lib.html.p("Check out the content below:"),
            lib.html.div(id="content")(
                content or lib.html.div("No content provided.")
            )
        )
    
    @App.page(layout=custom_page_layout)
    def custom_page(lib):
        return lib.html.div(
            lib.html.h2("This is a Crazy Page!"),
            lib.bs.Button(color="primary")("Click Me!")
        )


**App example:**

.. code-block:: python

    from tethys_sdk.components import ReactPyBase

    def custom_app_layout(lib, app, user, nav_links=None, content=None):
        return lib.html.div(
            lib.html.h1("My Custom App Layout"),
            lib.html.p("Check out the content below:"),
            lib.html.div(id="content")(
                content or lib.html.div("No content provided.")
            )
        )

    class App(ReactPyBase):
        """
        Tethys app class for ReactPy Demo.
        """
        # ... See other App class examples for other properties
        default_layout = custom_app_layout


.. _tethys_components_components:

Components
==========

A component is a single Python object that represents something that needs to be rendered on a page. 
It can be as simple or complex as desired - from a single header or button to a page with a map, popups, and a side panel containing a chart. 
The more complex components are made possible by components that are able to nest other components as children (as seen in the :ref:`tethys_components_custom_layout` section above).

All components within Tethys Platform are made availble and thus must be accessed via the ``lib`` object passed the decorated page function (see :ref:`tethys_components_pages`).

Each component can be accessed and defined via one of the following syntaxes:

.. code-block:: python

    lib.<library>.<ComponentName>()            
    lib.<library>.<ComponentName>(<props_as_kwargs>)
    lib.<library>.<ComponentName>(<children_as_args>)
    lib.<library>.<ComponentName>(<props_as_kwargs>)(<children_as_args>)

Where:
    - ``lib``: The library object passed to the page function.
    - ``<library>``: The built-in name of the component library.
    - ``<ComponentName>``: The name of the component (e.g., ``div``, ``Button``, ``Map``). Can be called directly without arguments if no ``<props_as_kwargs>`` or ``<children_as_args>`` are needed, with either one or the other if only one is needed. If both are are needed, you basically call the component twice, once with the ``<props_as_kwargs>`` and immediately after with the ``<children_as_args>``.
    - ``<props_as_kwargs>``: The properties to pass to the component as kwargs (e.g., ``color="primary"``, ``height="100px"``).
    - ``<children_as_args>``: The child components or content to render inside the component as args. This can be a single component, a list of components, or even plain text.


.. warning::
    
    The following syntax is not supported in Tethys apps using ReactPy:

    .. code-block:: python

        lib.<library>.<ComponentName>(<children_as_args>, <props_as_kwargs>)
        lib.<library>.<ComponentName>(<props_as_kwargs>, <children_as_args>)  # This is even illegal Python syntax, so don't use it!


**Examples:**

.. code-block:: python

    header_and_button = lib.html.div(
        lib.html.h1("Welcome to My ReactPy App"),
        lib.bs.Button(color="primary")("Click Me!")
    )

    map_display = lib.tethys.Display(
        lib.tethys.Map()
    )

.. _tethys_components_library:

Component-Based Page Library
============================

Every page function decorated with ``App.page`` will receive a ``lib`` argument at runtime, which provides access to various libraries and utilities that you can use to build your app's pages.

API Overview
------------

There are four main categories of libraries available via the ``lib`` object:

1. **HTML Elements**: These are basic HTML elements that can be used to build the structure of your page.

2. **Tethys Custom Components**: These are custom components provided by Tethys that extend the functionality of the basic HTML elements.

3. **Third-Party Libraries**: These are popular ReactJS component libraries that provide a wide range of UI components and utilities for building modern web applications.

4. **Hooks and Utilities**: These are ReactJS/ReactPy hooks and utility functions that help manage state, side effects, and other common tasks in your app.

HTML Elements
-------------
|
| **Library Accessor:** ``lib.html``
| **Description:** HTML Elements are the basic building blocks of any web page. This library leverages ReactPy's built-in HTML components, which Pythonify the standard HTML elements and attributes.
| **API:** See the `official ReactPy documentation <https://reactpy.dev/docs/api/reactpy.html>`_ or `Mozilla's HTML documentation <https://developer.mozilla.org/en-US/docs/Web/HTML>`_ for a complete list of available HTML elements and their properties.


Tethys Custom Components
------------------------
|
| **Library Accessor:** ``lib.tethys``
| **Description:** Tethys Components are custom components provided by Tethys that drastically simplify a few common, complex components. If you want more control over the components and their behavior, you can use the standard HTML elements or third-party libraries instead.
| **API:** See :ref:`tethys_components_custom`

Third-Party Libraries
---------------------
|
| **Library Accessor:** Various. See below.
| **Description:** These libraries provide Pythonic access to popular ReactJS component libraries that can be used to build modern web applications. In all of these cases, you will need to convert the ReactJS syntax to the Pythonic equivalent.
| **API:** Consult the ReactJS documentation itself for each library to see the available components and their properties, remembering that you must convert the officially documented ReactJS syntax to the Pythonic equivalent.

Here is a list of the built-in third-party libraries grouped by category and listed by their library accessor paired with a link to their official documentation:

**Standard UI components:**

    - ``lib.bs``: `Bootstrap <https://react-bootstrap.netlify.app/>`_
    - ``lib.chakra``: `Chakra UI <https://chakra-ui.com/docs/components/concepts/overview>`_
    - ``lib.mui``: `Material UI <https://mui.com/components/>`_
    - ``lib.icons``: `Boostrap Icons <https://www.npmjs.com/package/react-bootstrap-icons>`_

**Mapping and geospatial components:**

    - ``lib.mapgl``: `MapLibre GL JS <https://visgl.github.io/react-map-gl/docs/api-reference/maplibre/map>`_
    - ``lib.ol``: `OpenLayers <https://planetlabs.github.io/maps/>`_
    - ``lib.pm``: `Pigeon Maps <https://pigeon-maps.js.org/docs/map>`_

**Data visualization components:**

    - ``lib.rc``: `Recharts <https://recharts.org/en-US/api>`_
    - ``lib.ag``: `AG Grid <https://www.ag-grid.com/react-data-grid/getting-started/>`_

**Other specialized components:**

    - ``lib.rp``: `ReactPlayer <https://www.npmjs.com/package/react-player>`_
    - ``lib.lo``: `React-Loading-Overlay <https://www.npmjs.com/package/react-loading-overlay>`_

Hooks and Utilities
-------------------
|
| **Library Accessor:** Various. See below.
| **Description:** These libraries provide access to ReactPy hooks and utility functions that help manage state, side effects, and other common tasks in your app.
| **API:** See below for the available libraries and their respective APIs.

- ``lib.hooks``: Provides access to ReactPy hooks for managing state and side effects for creating dynamic, interactive components. See `ReactPy Hooks <https://reactpy.dev/docs/reference/hooks-api.html>`_ and `ReactPy-Django Hooks <https://reactive-python.github.io/reactpy-django/3.8.0/reference/hooks/>`_ for API documentation.
- ``lib.utils``: Provides access to utility functions for resource management and workspace operations. See :ref:`tethys_components_utils`.
- ``lib.register``: A function to register additional ReactJS component libraries dynamically (see below).

The general API of each specific component-based library follows the same pattern prescribed to all .. _tethys_components_components:. Rather than listing all of the available components here, we will refer you to the documentation for each library.


Registering Additional Component Libraries
------------------------------------------

You can register additional ReactJS component libraries dynamically using the ``lib.register`` function.

Here is the API:

.. autofunction:: tethys_components.library.ComponentLibrary.register


Additional References
=====================

.. toctree::
   :maxdepth: 1

   tethys_components/custom
   tethys_components/utils