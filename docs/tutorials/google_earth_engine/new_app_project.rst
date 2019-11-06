**********************
New Tethys App Project
**********************

**Last Updated:** November 2019

In this tutorial you will create a new Tethys App project using the scaffold. The following topics will be reviewed in this tutorial:

* Scaffolding a New Apps
* Managing App Dependencies
* Adding a Custom Icon
* Customizing App Theme Color

1. Generate Scaffold
====================

To generate a new Tethys App using the scaffold, open a terminal and execute the following commands:


**Linux and Mac:**

::

    # Activate the tethys environment
    conda activate tethys

    # Create a working directory (if it doesn't exist already)
    mkdir ~/tethysdev
    cd ~/tethysdev

    # Scaffold a new Tethys app
    tethys scaffold earth_engine

You will be prompted to enter metadata about the app such as, proper name, version, author, and description. All of these metadata are optional. You can accept the default values by pressing enter, repeatedly.

In a file browser change into your :file:`Home` directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-earth_engine`. All of the source code for your app is located in this directory. For more information about the app project structure, see :doc:`../../supplementary/app_project`.

2. Add App Dependencies to :file:`install.yml`
==============================================

App dependencies should be managed using the :file:`install.yml` instead of the :file:`setup.py`. This app will require the `earthengine-api` and `oauthclient` packages to allow it to use Google Earth Engine services. Both packages are available on `conda-forge`, which is the preferred Conda channel for Tethys. Open :file:`tethysapp-earth_engine/install.yml` and add these dependences to the `requirements.conda` section of the file:

::

    # This file should be committed to your app code.
    version: 1.0
    # This should match the app - package name in your setup.py
    name: earth_engine

    requirements:
      # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
      skip: false
      conda:
        channels:
          - conda-forge
        packages:
          - earthengine-api
          - oauth2client
      pip:

    post:


3. Development Installation
===========================

Install the app and it's dependencies into your development Tethys Portal. In a terminal, change into the :file:`tethysapp-earth_engine` directory and execute the :command:`tethys install -d` command.

**Linux and Mac:**

::

    cd ~/tethysdev/tethysapp-earth_engine
    tethys install -d


4. View Your New App
====================

Start up the development server to view the new app:

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

.. tip::

    To stop the development server press :kbd:`CTRL-C`.

5. Customize App Icon and Theme Color
=====================================

Download this :download:`Google Earth Engine App Icon <./resources/earth-engine-logo.png>` or find one that you like and save it to the :file:`public/images` directory. Modify the `icon` property of your :term:`app class` to reference the new image. Also change the `color` property to the `#524745` color:

::

    class EarthEngine(TethysAppBase):
        """
        Tethys app class for Google Earth Engine Tutorial.
        """

        name = 'Google Earth Engine Tutorial'
        index = 'earth_engine:home'
        icon = 'earth_engine/images/earth-engine-logo.png'
        package = 'earth_engine'
        root_url = 'earth-engine'
        color = '#524745'
        ...
