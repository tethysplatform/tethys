.. _key_concepts_new_app_project_tutorial:

**********************
New Tethys App Project
**********************

**Last Updated:** October 2019

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

.. tip::

   You will need to use the command line/terminal to manage your app and run the development server. See the :doc:`../../supplementary/terminal_quick_guide` article for some tips if you are new to command line.

1. Generate Scaffold
====================

To generate a new app using the scaffold, open a terminal, press :kbd:`CTRL-C` to stop the development server if it is still running, and execute the following commands:


**Linux and Mac:**

::

    t
    mkdir ~/tethysdev
    cd ~/tethysdev
    tethys scaffold dam_inventory

**Windows:**

Locate the ``tethys_cmd.bat`` (in the TETHYS_HOME directory) and double-click it to open a new command windows with the Tethys environment activated.  Then run the following commands:

::

    mkdir C:%HOMEPATH%\tethysdev
    cd %HOMEPATH%\tethysdev
    tethys scaffold dam_inventory

.. tip::

    Windows Users: If you have admin rights on your computer, it is even better to right-click on the ``tethys_cmd.bat`` and select **Run as Administrator**.

You will be prompted to enter metadata about your app such as, proper name, version, author, and description. All of these metadata are optional. You can accept the default value by pressing enter, repeatedly.

In a file browser change into your :file:`Home` directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-dam_inventory`. All of the source code for your app is located in this directory. For more information about the app project structure, see :doc:`../../supplementary/app_project`.

2. Development Installation
===========================

Now that you have a new Tethys app project, you need to install the app on your development Tethys Portal. In a terminal, change into the :file:`tethysapp-dam_inventory` directory and execute the :command:`tethys install -d` command. Be sure to activate the Tethys :term:`Python conda environment` if it is not already activated (see line 1 of the first code block):

**Linux and Mac:**

::

    cd ~/tethysdev/tethysapp-dam_inventory
    tethys install -d

**Windows:**

::

    cd C:%HOMEPATH%\tethysdev\tethysapp-dam_inventory
    tethys install -d

.. tip::

    Windows Users: If you get an error when running ``tethys install -d``, then you have insufficient permissions to install your app in development mode. Either try opening the ``tethys_cmd.bat`` as an administrator and run the commands again, or run ``tethys install``. The disadvantage to this method is that each time you want Tethys to reflect changes to your app code, you will need to run ``tethys install`` again.


3. View Your New App
====================

Use start up the development server:

::

    tethys manage start

.. note::

    If you get errors related to Tethys not being able to connect to the database, start the database by running:

    ::

        tethys db start

    You can also stop the Tethys database by running:

    ::

        tethys db stop

Browse to `<http://127.0.0.1:8000/apps>`_ in a web browser and login the default portal user is:

* **username**: admin
* **password**: pass


If all has gone well, you should see your app listed on the app library page. Click on the app tile to launch it. Exploring your new app won't take long, because there is only one page. Familiarize yourself with different parts of the app interface (see below).

.. figure:: ../../images/app_controls.png
    :width: 650px

**Parts of a Tethys app interface: (1) app navigation toggle and app branding; (2) exit button, settings, button, and custom buttons; (3) app navigation, (4) app content, and (5) app actions.**

.. tip::

    To stop the development server press :kbd:`CTRL-C`.



4. App Project Paths
====================

Throughout the tutorial, you will be asked to open various files. Most of the files will be located in your :term:`app package` directory which shares the name of your app: "dam_inventory". If you generated your scaffold exactly as above, this directory will be located at the following path:

::

    # Linux and Mac
    ~/tethysdev/tethysapp-dam_inventory/tethysapp/dam_inventory/

    # Windows
    C:%HOMEPATH%\tethysdev\tethysapp-dam_inventory\tethys_app\dam_inventory\



For convenience, all paths in the following tutorials will be given relative to the :term:`app package` directory. For example:

::

    # This path:
    ~/tethysdev/tethysapp-dam_inventory/tethysapp/dam_inventory/controllers.py

    # Will be referred to as:
    controllers.py

.. tip::

    As you explore the contents of your app project, you will notice that many of the directories have files named :file:`\_\_init\_\_.py`. Though many of these files are empty, they are important and should not be deleted. They inform Python that the containing directory is a Python package. Python packages and their contents can be imported in Python scripts. Removing the :file:`\_\_init\_\_.py` files will result in breaking import statements and it could make some of your code inaccessible.

    Similarly, if you add a directory to your project that contains Python modules and you would like them to be made available to your code, add a :file:`\_\_init\_\_.py` file to the directory to make it a package.


.. warning::

    The :file:`tethysapp` directory should no longer contain an :file:`\_\_init\_\_.py` as it did in version of Tethys Platform prior to 3.0. This directory is a Python namespace directory and in Tethys Platform 3.0 the implicit namespace pattern is used. Adding an :file:`\_\_init\_\_.py` to this directory will break the app.
