.. _component_app_basics_new_app_project:

*********************
Component App Project
*********************

In this section, you will create a new Tethys Component App project. This process involves using the Tethys command line interface to scaffold a new app, installing it into your Tethys Platform, and verifying that it runs correctly. Follow the steps below to get started.

.. note::
    
    Be sure to :ref:`activate_environment` before running any of the commands below.

1. Scaffold a new Tethys app using the ``component`` project template
---------------------------------------------------------------------

.. code-block:: bash

    tethys app scaffold geoglows_tutorial -t component

This command will prompt you for input via the command line. For this tutorial, accept all of the defaults by simply hitting ``Enter`` with each prompt. 

The completed command will create all of the necessary files and directories for your app, which are as follows:

::

    tethysapp-geoglows_tutorial  - App project root
    ├── install.yml - Tethys project configuration.
    ├── pyproject.toml - Python project configuration.
    ├── README.rst - Documentation.
    └── tethysapp/geoglows_tutorial/ - Python package root
            ├── __init__.py - Python package initialization
            ├── app.py - Application code
            ├── public/images/ - Public images
            |   └── icon.png - Default icon
            └── tests/ - Tests
                └── ``test.py`` - Test

2. Navigate to the newly created app project directory
------------------------------------------------------

.. code-block:: bash

    cd tethysapp-geoglows_tutorial

3. Install the app into Tethys Platform:
----------------------------------------

.. code-block:: bash

    tethys install -d

Include ``-d`` to install the app in development mode, which allows you to make changes without needing to reinstall the app each time. The Tethys server will automatically reload your app when you save changes to any Python files within the project.

4. Apply migrations
-------------------

.. code-block:: bash

    tethys db migrate

.. tip::
    
    This migration is only necessary if this is the first time you are creating a Component App. For subsequent Component Apps, this can be skipped.


5. Start the Tethys server
--------------------------

.. code-block:: bash

    tethys start

6. Open your application in the browser
---------------------------------------

Navigate to http://localhost:8000/apps/geoglows-tutorial.

You should see a page that looks like this:

.. note::

    You may need to login first.

    The color of the header may be different than what is shown below, since we instructed you to accept the randomly generated default when scaffolding the app.

.. figure:: ../../images/tutorial/component_app_basics/new_app_project.png
    :width: 800px
    :align: center

    New Component App Project

This is the default page of your new Component App project. It includes the following features:

- A navigation header containing: 
    - A hamburger menu icon meant for navigating to other pages of your app (which currently only reflects the "Home" page that you are on)
    - A default app icon
    - The name of your app
    - A gear icon for accessing the admin app settings
    - An "X" icon for exiting the app and returning to the "Apps" library page
- An interactive map with a default basemap and basic controls.

You will see these features reflected in the code of your app during the next step.