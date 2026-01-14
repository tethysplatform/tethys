**********************
New Tethys App Project
**********************

**Last Updated:** July 2024

In this tutorial you will create a new Tethys App project using the scaffold. The following topics will be reviewed in this tutorial:

* Scaffolding New Tethys Apps
* Managing App Dependencies
* Adding a Custom Icon
* Customizing App Theme Color

.. figure:: ./resources/new_app_project_solution.png
    :width: 800px
    :align: center

1. Generate Scaffold
====================

To generate a new Tethys App using the scaffold, open a terminal, :ref:`activate_environment`, and execute the following commands:

.. code-block:: bash

    # Create a working directory (if it doesn't exist already)
    mkdir ~/tethysdev
    cd ~/tethysdev

.. code-block:: bash

    # Scaffold a new Tethys app
    tethys scaffold map_layout_tutorial

You will be prompted to enter metadata about the app such as, proper name, version, author, and description. All of these metadata are optional and can be changed later in the generated :file:`app.py` file (as you'll note later on). You can accept the default values by pressing enter, repeatedly.

In a file browser change into your :file:`Home` directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-map_layout_tutorial`. All of the source code for your app is located in this directory. For more information about the app project structure, see :doc:`../../supplementary/app_project`.

2. Add App Dependencies to :file:`install.yml`
==============================================

App dependencies should be managed using the :file:`install.yml` instead of the :file:`setup.py`. This app will only require the third-party ``pandas`` package, which will be used to read in the NextGen CSV outputs that we'll explore in the next section. This package is available on ``conda-forge``, which is the preferred Conda channel for Tethys. Open :file:`tethysapp-map_layout_tutorial/install.yml` and add this dependency to the ``requirements.conda`` section of the file:

.. code-block:: yaml

    # This file should be committed to your app code.
    version: 1.1
    # This should be greater or equal to your tethys-platform in your environment
    tethys_version: ">=4.0.0"
    # This should match the app - package name in your setup.py
    name: map_layout_tutorial

    requirements:
        # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
        skip: false
        conda:
            channels:
            - conda-forge
            packages:
            - pandas

        pip:

        npm:

    post:

3. Development Installation
===========================

Install the app and it's dependencies into your development Tethys Portal. In a terminal, change into the :file:`tethysapp-map_layout_tutorial` directory and execute the :command:`tethys install -d` command.

.. code-block:: bash

    cd ~/tethysdev/tethysapp-map_layout_tutorial
    tethys install -d

4. Customize App Icon and Theme Color
=====================================

Download this :download:`NOAA Digital Logo <./resources/noaa_digital_logo-2022.png>` or find one that you like and save it to the :file:`public/images` directory. Modify the ``icon`` property of your :term:`app class` to reference the new image. Also change the ``color`` property to the ``#003087`` color:

.. code-block:: python

    class App(TethysAppBase):
        """
        Tethys app class for Map Layout Tutorial.
        """

        name = 'Map Layout Tutorial'
        package = 'map_layout_tutorial'  # WARNING: Do not change this value
        index = 'home'
        icon = f'{package}/images/noaa_digital_logo-2022.png'
        root_url = 'map-layout-tutorial'
        color = '#003087'
        ...

5. View Your New App
====================

1. Start up the development server to view the new app:

.. code-block:: bash

    tethys manage start

.. tip::

    To stop the development server press :kbd:`CTRL-C`.

1. Browse to `<http://127.0.0.1:8000/apps/>`_ in a web browser and login. The default portal user is:

* **username**: admin
* **password**: pass

Verify the following:

1. The default app icon should be replaced with the custom image you added in step 4.
2. The primary color for the app should be a dark blue (see screenshot at the beginning of the tutorial).

6. Solution
===========

This concludes the New App Project portion of the Map Layout Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-map_layout_tutorial/tree/new-app-project-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-map_layout_tutorial
    cd tethysapp-map_layout_tutorial
    git checkout -b new-app-project-solution new-app-project-solution-|version|