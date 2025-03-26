.. _docker_salt_state:

****************
Salt State Files
****************

**Last Updated:** February 2023

The Tethys Platform Docker uses `Salt States <https://docs.saltproject.io/en/latest/topics/tutorials/starting_states.html>`_, one component of `Salt Stack <https://docs.saltproject.io/en/latest/topics/index.html>`_, to perform runtime initialization of Tethys and apps. Salt States are YAML files that specify the various commands to run when Tethys starts up. It is best understood through examples. For this Docker image, we'll create three Salt State files that will perform the following tasks:

1. Create the Tethys Services our apps need (THREDDS and PostGIS)
2. Configure the app settings for each app
3. Apply a custom theme to the Tethys Portal

Create Salt State Files
=======================

Complete the following steps to create Salt State files that initialize the Tethys Portal and apps.

1. Create :file:`salt` directory
--------------------------------

Create a new directory in :file:`tethys_portal_docker` called :file:`salt` to container the Salt State files:

.. code-block:: bash

    mkdir salt

2. Create empty Salt State files
--------------------------------

Create the following empty Salt State files in the :file:`tethys_portal_docker/salt`

.. code-block:: bash

    touch salt/tethys_services.sls salt/init_apps.sls salt/portal_theme.sls salt/top.sls

3. :file:`tethys_services.sls`
------------------------------

The :file:`tethys_services.sls` Salt State file will contain the steps needed to create the Tethys Services that the installed apps will require. Tethys Services are objects that define connections to external services for use by Tethys apps. Examples of Tethys Services commonly used by apps include PostGIS databases, THREDDS Data Servers, and GeoServers. Tethys Services are usually created in the admin pages of Tethys Portal, but they can also be created programmatically using the ``tethys services`` command.

Two of the apps that are installed requires a PostGIS database (Dam Inventory and PostGIS App) and one of the apps requires a THREDDS Data Server (THREDDS Tutorial). PostGIS database services can host many databases, so the two apps that require a PostGIS database can share the same service. In fact, they can share the database service that Tethys Portal will use for its primary database.

**Using Environment Variables in Salt State Files**

The first step to defining the Tethys Services will be to import the environment variables that contain the connection information for the services. In the case of the PostGIS database service, we'll use the environment variables that contain the database connection information for the Tethys Portal that are already defined by the base Tethys Platform image: ``TETHYS_DB_HOST``, ``TETHYS_DB_PORT``, ``TETHYS_DB_SUPERUSER``, ``TETHYS_DB_SUPERUSER_PASS``. For the THREDDS service, we'll use the app-specific environment variables we defined in the custom Dockerfile: ``THREDDS_TUTORIAL_TDS_USERNAME``, ``THREDDS_TUTORIAL_TDS_PASSWORD``, ``THREDDS_TUTORIAL_TDS_PROTOCOL``, ``THREDDS_TUTORIAL_TDS_HOST``, and ``THREDDS_TUTORIAL_TDS_PORT``.

Open the new :file:`tethys_services.sls` file and add the following lines to import the needed environment variables:

.. code-block:: sls

    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
    {% set TETHYS_DB_HOST = salt['environ.get']('TETHYS_DB_HOST') %}
    {% set TETHYS_DB_PORT = salt['environ.get']('TETHYS_DB_PORT') %}
    {% set TETHYS_DB_SUPERUSER = salt['environ.get']('TETHYS_DB_SUPERUSER') %}
    {% set TETHYS_DB_SUPERUSER_PASS = salt['environ.get']('TETHYS_DB_SUPERUSER_PASS') %}
    {% set THREDDS_TUTORIAL_TDS_USERNAME = salt['environ.get']('THREDDS_TUTORIAL_TDS_USERNAME') %}
    {% set THREDDS_TUTORIAL_TDS_PASSWORD = salt['environ.get']('THREDDS_TUTORIAL_TDS_PASSWORD') %}
    {% set THREDDS_TUTORIAL_TDS_CATALOG = salt['environ.get']('THREDDS_TUTORIAL_TDS_CATALOG') %}
    {% set THREDDS_TUTORIAL_TDS_PRIVATE_PROTOCOL = salt['environ.get']('THREDDS_TUTORIAL_TDS_PRIVATE_PROTOCOL') %}
    {% set THREDDS_TUTORIAL_TDS_PRIVATE_HOST = salt['environ.get']('THREDDS_TUTORIAL_TDS_PRIVATE_HOST') %}
    {% set THREDDS_TUTORIAL_TDS_PRIVATE_PORT = salt['environ.get']('THREDDS_TUTORIAL_TDS_PRIVATE_PORT') %}
    {% set THREDDS_TUTORIAL_TDS_PUBLIC_PROTOCOL = salt['environ.get']('THREDDS_TUTORIAL_TDS_PUBLIC_PROTOCOL') %}
    {% set THREDDS_TUTORIAL_TDS_PUBLIC_HOST = salt['environ.get']('THREDDS_TUTORIAL_TDS_PUBLIC_HOST') %}
    {% set THREDDS_TUTORIAL_TDS_PUBLIC_PORT = salt['environ.get']('THREDDS_TUTORIAL_TDS_PUBLIC_PORT') %}

**Custom Variables**

You can also define custom variables in the Salt State files using `Jinja templating syntax <https://jinja.palletsprojects.com/en/stable/templates/>`_. For this example, define the following variables for use in the Salt State steps:


.. code-block:: sls

    {% set THREDDS_SERVICE_NAME = 'tethys_thredds' %}
    {% set POSTGIS_SERVICE_NAME = 'tethys_postgis' %}
    {% set THREDDS_SERVICE_PRIVATE_URL = THREDDS_TUTORIAL_TDS_USERNAME + ':' + THREDDS_TUTORIAL_TDS_PASSWORD + '@' + THREDDS_TUTORIAL_TDS_PRIVATE_PROTOCOL +'://' + THREDDS_TUTORIAL_TDS_PRIVATE_HOST + ':' + THREDDS_TUTORIAL_TDS_PRIVATE_PORT + THREDDS_TUTORIAL_TDS_CATALOG %}
    {% set THREDDS_SERVICE_PUBLIC_URL = THREDDS_TUTORIAL_TDS_PUBLIC_PROTOCOL +'://' + THREDDS_TUTORIAL_TDS_PUBLIC_HOST + ':' + THREDDS_TUTORIAL_TDS_PUBLIC_PORT + THREDDS_TUTORIAL_TDS_CATALOG %}
    {% set POSTGIS_SERVICE_URL = TETHYS_DB_SUPERUSER + ':' + TETHYS_DB_SUPERUSER_PASS + '@' + TETHYS_DB_HOST + ':' + TETHYS_DB_PORT %}

**Run Arbitrary Commands in Salt State Files**

The `cmd.run <https://docs.saltproject.io/en/latest/ref/states/all/salt.states.cmd.html>`_ state module can be used to run arbitrary commands, similar to the ``RUN`` instruction in the Dockerfile. It is used in the :file:`tethys_services.sls` to run the ``tethys services`` commands that create the Tethys Services. Add the following lines to the :file:`tethys_services.sls` to create the PostGIS Tethys Service:

.. code-block:: sls

    Create_PostGIS_Database_Service:
      cmd.run:
        - name: "tethys services create persistent -n {{ POSTGIS_SERVICE_NAME }} -c {{ POSTGIS_SERVICE_URL }}"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

**Explanation:**

* ``Create_PostGIS_Database_Service``: This is the name of the step. It needs to be unique across all the Salt State steps that are run, including those run by the base Tethys Platform image.
* The ``name`` parameter of the ``cmd.run`` module is where the command to run should be defined.
* The ``shell`` parameter of the ``cmd.run`` module can be used to specify the shell to use to run the command. Use the ``/bin/bash`` shell for running ``tethys`` commands.
* The ``unless`` parameter of the ``cmd.run`` module can be used to specify a condition that when true will prevent the command from being executed. In this case, the check is to see if a file named ``tethys_services_complete`` exists in the ``TETHYS_PERSIST`` directory. We'll add a step at the end of the script that creates this file. This pattern will result in any steps with this ``unless`` check only running the first time the container is started up.
* ``{{ <variable> }}``: this is the Jinja2 syntax for printing a variable. These are used throughout the step to insert the values of variables in the commands.
* ``TETHYS_PERSIST``: This environment variable contains the path to a directory that will be persisted, meaning it won't be deleted when the container is removed. This will be discussed more in the next tutorial.

**Create THREDDS Tethys Service**

Add the following lines to create the THREDDS Tethys Service:

.. code-block:: sls

    Create_THREDDS_Spatial_Dataset_Service:
      cmd.run:
        - name: "tethys services create spatial -t THREDDS -n {{ THREDDS_SERVICE_NAME }} -c {{ THREDDS_SERVICE_PRIVATE_URL }} -p {{ THREDDS_SERVICE_PUBLIC_URL }}"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

**Create Setup Complete File**

Finally, add the following lines to create the :file:`tethys_services_complete` file:

.. code-block:: sls

    Flag_Tethys_Services_Setup_Complete:
      cmd.run:
        - name: touch {{ TETHYS_PERSIST }}/tethys_services_complete
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

4. :file:`init_apps.sls`
------------------------

The :file:`init_apps.sls` file will contain the steps required to initialize the apps, including connecting them with the Tethys Services they require. Other common initialization that needs to be performed includes initializing persistent stores and setting the values of other settings. Add the following contents to :file:`init_apps.sls`:

.. code-block:: sls

    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
    {% set DAM_INVENTORY_MAX_DAMS = salt['environ.get']('DAM_INVENTORY_MAX_DAMS') %}
    {% set EARTH_ENGINE_PRIVATE_KEY_FILE = salt['environ.get']('EARTH_ENGINE_PRIVATE_KEY_FILE') %}
    {% set EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL = salt['environ.get']('EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL') %}
    {% set THREDDS_SERVICE_NAME = 'tethys_thredds' %}
    {% set POSTGIS_SERVICE_NAME = 'tethys_postgis' %}

    Sync_Apps:
      cmd.run:
        - name: tethys db sync
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Set_Custom_Settings:
      cmd.run:
        - name: >
            tethys app_settings set dam_inventory max_dams {{ DAM_INVENTORY_MAX_DAMS }} &&
            tethys app_settings set earth_engine service_account_email {{ EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL }} &&
            tethys app_settings set earth_engine private_key_file {{ EARTH_ENGINE_PRIVATE_KEY_FILE }}
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Link_Tethys_Services_to_Apps:
      cmd.run:
        - name: >
            tethys link persistent:{{ POSTGIS_SERVICE_NAME }} dam_inventory:ps_database:primary_db &&
            tethys link persistent:{{ POSTGIS_SERVICE_NAME }} postgis_app:ps_database:flooded_addresses &&
            tethys link spatial:{{ THREDDS_SERVICE_NAME }} thredds_tutorial:ds_spatial:thredds_service
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Sync_App_Persistent_Stores:
      cmd.run:
        - name: tethys syncstores all
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Flag_Init_Apps_Setup_Complete:
      cmd.run:
        - name: touch {{ TETHYS_PERSIST }}/init_apps_setup_complete
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

**Explanation:**

* **Sync_Apps**: Run the ``tethys sync db`` command to ensure the database is up-to-date with the apps that were installed at build time. See :ref:`tethys_db_cmd` for more details.
* **Set_Custom_Settings**: Set the values of the custom settings from the corresponding environment variables. Only two of the apps installed have custom settings: Earth Engine and Dam Inventory. See: :ref:`tethys_cli_app_settings` for more details.
* **Link_Tethys_Services_to_Apps**: Link the PostGIS and THREDDS services with the apps that need them using the ``tethys link`` command. See: :ref:`tethys_cli_link` for more details.
* **Sync_App_Persistent_Stores**: After linking apps with the PostGIS databases, we now need to initailize the database using the ``tethys syncstores`` command. See: :ref:`tethys_syncstores_cmd` for more details.
* **Flag_Init_Apps_Setup_Complete**: Add the file that will indicate that the steps have been completed so they don't run everytime the container starts up.

5. :file:`portal_theme.sls`
---------------------------

The :file:`portal_theme.sls` file will contain the steps required to customize the Tethys Portal theme and content. The :ref:`tethys site <tethys_site_cmd>` command can be used to set Site Settings programmatically. This includes settings such as the portal title, theme colors, and logo. For a complete list of settings that can be set with this command, see :ref:`tethys_site_cmd` and :ref:`tethys_configuration_site_settings`.

Add the following contents to :file:`portal_theme.sls`:

.. code-block:: sls

    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
    {% set STATIC_ROOT = salt['environ.get']('STATIC_ROOT') %}

    Move_Custom_Theme_Files_to_Static_Root:
      cmd.run:
        - name: mv /tmp/custom_theme {{ STATIC_ROOT }}
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/custom_theme_setup_complete" ];"

    Apply_Custom_Theme:
      cmd.run:
        - name: >
            tethys site
            --site-title "My Custom Portal"
            --brand-text "My Custom Portal"
            --apps-library-title "Tools"
            --primary-color "#01200F"
            --secondary-color "#358600"
            --background-color "#ffffff"
            --brand-image "/custom_theme/images/leaf-logo.png"
            --favicon "/custom_theme/images/favicon.ico"
            --copyright "Copyright © 2023 My Organization"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/custom_theme_setup_complete" ];"

    Flag_Custom_Theme_Setup_Complete:
      cmd.run:
        - name: touch {{ TETHYS_PERSIST }}/custom_theme_setup_complete
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/custom_theme_setup_complete" ];"

.. note::

    The paths for the ``--logo`` and ``--favicon`` options need to be specified relative to the ``STATIC_ROOT`` directory. Alternatively, you can specify a link to an image hosted on a different website.


6. Create custom Top file
-------------------------

Finally, the :file:`top.sls` that is included in Tethys Platform image needs to be overridden. This file instructs Salt which Salt State files should be executed and in what order. The default :file:`top.sls` has the following contents:

.. code-block:: sls

    base:
      '*':
        - pre_tethys
        - tethyscore
        - post_app

The :file:`pre_tethys.sls`, :file:`tethyscore.sls`, and :file:`post_app.sls` Salt States need to be executed to properly initialize Tethys. As the name suggests, the :file:`post_app.sls` should be executed after any of your custom app configuration Salt States. The best approach is to start with the contents of the the original :file:`top.sls` file (above) and add your custom Salt State files  between the ``tethyscore`` and ``post_app`` items.

We've created a new :file:`top.sls` that we'll use to overwrite the :file:`top.sls` provided by the Tethys Platform image. Add the following contents to it:

.. code-block:: sls

    base:
      '*':
        - pre_tethys
        - tethyscore
        - tethys_services
        - init_apps
        - portal_theme
        - post_app

7. Add Salt State files to image
--------------------------------

With the Salt State files created, the :file:`Dockerfile` will need to be modified to add them to the image. Add the following lines to the :file:`Dockerfile` after the **INSTALL** section and before the **PORTS** section:

.. code-block:: dockerfile

    ##################
    # ADD SALT FILES #
    ##################
    COPY salt/ /srv/salt/

.. note::

    This ``COPY`` instruction will copy the contents of the local :file:`salt` directory into the :file:`/srv/salt/` directory. Any files with the same names will be replaced. In this case, our :file:`top.sls` will overwrite the :file:`top.sls` placed in :file:`/srv/salt/` by the base image.

8. Commit Changes
-----------------

Add the Salt State files and commit changes to the :file:`Dockerfile`:

.. code-block:: bash

    git add .
    git commit -m "Added Salt State scripts for runtime initialization."

Solution
========

This concludes this portion of the tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethys_portal_docker>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethys_portal_docker
    cd tethys_portal_docker
    git checkout -b salt-state-solution salt-state-solution-|version|

What's Next?
============

Continue to the next tutorial to learn how build the image.