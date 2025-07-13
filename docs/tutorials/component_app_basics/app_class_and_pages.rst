**********************************
The `App` Class and Page Functions
**********************************

When you scaffolded a new app project in the previous step, a basic app structure was created for you, including an `app.py` file that defines the main class and pages for your app.

That file is located here, relative to the root app project directory:

``tethysapp-geoglows_tutorial/tethysapp/geoglows_tutorial/app.py``

Open this file in your favorite editor
--------------------------------------

It's content should look like this:

.. code-block:: python

    from tethys_sdk.components import ComponentBase


    class App(ComponentBase):
        """
        Tethys app class for {{proper_name}}.
        """
        
        name = "Geoglows Tutorial"
        description = "Place a brief description of your app here."
        package = "geoglows_tutorial"  # WARNING: Do not change this value
        index = "home"
        icon = f"{package}/images/icon.png"
        root_url = "geoglows-tutorial"
        color = "#d35400"  # This is randomly generated, so yours may be different
        tags = ""
        enable_feedback = False
        feedback_emails = []
        exit_url = "/apps/"
        default_layout = "NavHeader"
        nav_links = "auto"


    @App.page
    def home(lib):
        return lib.tethys.Display(
            lib.tethys.Map()
        )

You'll note that this file contains only two main sections of code: the ``App`` class and a ``home`` function.

The ``App`` class 
^^^^^^^^^^^^^^^^^

The `App` class inherits from ``ComponentBase`` and defines the basic, high-level metadata and visual properties of your app - a few of which were chosen when you scaffolded the app. 
All of these properties can be customized to suit your app's needs, with the exception of the ``package`` property, which should always be set to the name of your app project.

Although most of the properties are pretty straightforward, note the following:

- The ``index`` property is set to ``"home"``, which indicates that the index (i.e. default) page of your app will be defined by the ``home`` function.
- The ``default_layout`` property is set to ``"NavHeader"``, which means that the app's pages will use the built-in navigation header layout by default.
- The ``nav_links`` property is set to ``"auto"``, which means that the navigation links will be automatically generated based on the pages defined in your app.

The ``home`` function
^^^^^^^^^^^^^^^^^^^^^

The ``home`` function defines the default page of your app - and the only page at this point.

.. note::
    
    This "default page" behavior is not due specifically to ``home`` being the only function, but due to ``App.index`` being explicitly set to ``"home"``, as we mentioned in the previous section.
    If ``App.index`` were changed to something else, the app would look for that function instead to use as the default page.

Each page of your app must be defined by a single function that:

- Is decorated with the ``@App.page`` decorator
- Accepts a single argument, ``lib``, which is an instance of the :ref:`tethys_components_library` that provides namespaced access to various modules for building your app's user interface
- Returns a Component object representing the content that is to be displayed on the page (a.k.a. the content tree)

Accordingly, the ``home`` function is decorated with the ``@App.page`` decorator, accepts a single ``lib`` argument, and returns a single Display component that itself contains a Map component.

While seemingly straightforward, what exactly are Components? Continue on to find out!

Key Takeaways
=============

- The `app.py` file defines the main `App` class and page functions for your Tethys app.
- The `App` class sets important metadata and configuration, such as the app name, description, index page, and layout.
- Each page is defined by a function decorated with `@App.page`, which takes a `lib` argument and returns a Component object.