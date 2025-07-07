.. _component_app_basics_new_app_project:

*********************
Component App Project
*********************

In this section, you will create a new Tethys Component App project using Tethys Platform's :ref:`tethys_cli`.

Let's get started!

Open a terminal and :ref:`activate_environment`
-----------------------------------------------

All bash code blocks you will see throughout this tutorial must be entered via command line within the :ref:`virtual_environment` you created when installing Tethys Platform.
Such code blocks will look like the following example:

.. code-block:: bash

    echo "This example code block must be entered via command line"

Scaffold a new Tethys app using the ``component`` project template
------------------------------------------------------------------

.. code-block:: bash

    tethys scaffold geoglows_tutorial -t component

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

Navigate to the newly created app project directory
---------------------------------------------------

.. code-block:: bash

    cd tethysapp-geoglows_tutorial

Install the app into Tethys Platform:
-------------------------------------

.. code-block:: bash

    tethys install -d

Include ``-d`` to install the app in development mode, which allows you to make changes without needing to reinstall the app each time. The Tethys server will automatically reload your app when you save changes to any Python files within the project.

Apply migrations
----------------

.. code-block:: bash

    tethys db migrate

.. note::
    
    This migration is only necessary if this is the first time you are creating a Component App. For subsequent Component Apps, this can be skipped.


Start the Tethys server
-----------------------

.. code-block:: bash

    tethys start

Open your application in the browser
------------------------------------

Navigate to http://localhost:8000/apps/geoglows-tutorial and login using the default credentials:

|
| **username:** admin
| **password:** pass

You should be redirected to a page that looks like this:

.. note::

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