.. _docker_custom_image:

**************************
Custom Tethys Docker Image
**************************

**Last Updated:** November 2021

With Docker installed and a basic understanding of how it works under your belt, you are now ready to create a Docker image containing the Tethys Portal with your apps installed. In this tutorial you will create a Docker image with some of the tutorial apps installed. A similar process can be used to create a Docker image for your Tethys Portal.

Prerequisites
=============

* :ref:`Docker Installed <docker_get_started>`
* `Git Installed <https://git-scm.com/downloads>`_
* `GitHub Account <https://github.com/signup>`_
* `Docker Hub Account <https://hub.docker.com/signup>`_

1. Create New Directory
=======================

Create a new directory to house the :file:`Dockerfile` and other artifacts that will be used for the build.

.. code-block::

    mkdir tethys_portal_docker
    cd tethys_portal_docker

.. tip::

    If you are on Windows, we recommend using the **Git Bash** terminal that comes with `Git for Windows <https://git-scm.com/download/win>`_ when running commands in this tutorial.

2. Create Initial Files
=======================

a. Create the following text files in the :file:`tethys_portal_docker` directory:

    .. code-block::

        touch  README.md LICENSE Dockerfile

b. Then add the following contents each the files:

    **README.md**

    .. code-block:: markdown

        # Demonstration Tethys Portal Docker Project

        This repository demonstrates how to make a Docker image containing a custom Tethys Portal with apps installed. The apps installed are the solutions to several of the Tethys Platform tutorials and include:

        * [Dam Inventory](https://github.com/tethysplatform/tethysapp-dam_inventory.git)
        * [THREDDS Tutorial](https://github.com/tethysplatform/tethysapp-thredds_tutorial)
        * [Earth Engine](https://github.com/tethysplatform/tethysapp-earth_engine.git)
        * [PostGIS App](https://github.com/tethysplatform/tethysapp-postgis_app.git)
        * [Bokeh Tutorial](https://github.com/tethysplatform/tethysapp-bokeh_tutorial)

    **LICENSE**

    Choose an open source license from `Licenses and Standards | Open Source Initiative <https://opensource.org/licenses>`_. Copy it into the :file:`LICENSE` file.

    **Dockerfile**

    Leave this empty for now as it will be discussed in depth in the next steps.

3. Initialize Git Repository
============================

Initialize a new Git repository in the :file:`tethys_portal_docker` directory. Then add all the files and create the first commit.

.. code-block::

    git init
    git add .
    git commit -m "First commit"


4. Checkout App Solutions
=========================

In this step you'll add the source code of the apps you want to install to the :file:`tethys_portal_docker` directory so they can be used in the build. Generally, only files in the same directory as the :file:`Dockerfile` are accessible to use during a docker build operation.

Adding the files to this directory could be as simple as copying the ``tethyapp-xyz`` folders into the directory. However, the apps we are installing are available on GitHub, so we can use `Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_, which allows you to keep a Git repository as a submodule of another Git repository. The advantage of this approach is that as the apps update, we need only pull the latest version in each submodule and then we can build an updated Docker image.

a. Add the app repositories as Git submodules as follows:

    **Bokeh App**:

    .. code-block::

        git submodule add -b master https://github.com/tethysplatform/tethysapp-bokeh_tutorial

    **Dam Inventory**:

    .. code-block::

        git submodule add -b advanced-solution https://github.com/tethysplatform/tethysapp-dam_inventory

    **Earth Engine**:

    .. code-block::

        git submodule add -b prepare-publish-solution https://github.com/tethysplatform/tethysapp-earth_engine

    **PostGIS App**:

    .. code-block::

        git submodule add -b master https://github.com/tethysplatform/tethysapp-postgis_app

    **THREDDS Tutorial**:

    .. code-block::

        git submodule add -b plot-at-location-solution https://github.com/tethysplatform/tethysapp-thredds_tutorial

b. Commit the new submodules configuration:

    .. code-block::

        git commit -am "Added apps as submodules"

5. Edit Dockerfile
==================

With the app source code checked out it is time to build out the Dockerfile. A :file:`Dockerfile` is composed of several different types of instructions. The instructions used in our :file:`Dockerfile` will be explained as it is built-out, but you can refer to the `Dockerfile Reference | Docker Documentation <https://docs.docker.com/engine/reference/builder/>`_ for full explanations of any instructions.

a. Add ``FROM`` instruction
---------------------------

All Dockerfiles must begin with a `FROM <https://docs.docker.com/engine/reference/builder/#from>`_ instruction that specifies the base image or starting point for the image. Tethys Platform provides a :ref:`base image <docker_official_image_env>` that already has Tethys Platform installed. Add the ``FROM`` instruction to the top of the :file:`Dockerfile` as follows:

.. code-block::

    FROM tethysplatform/tethys-core:latest

.. note::

    The ``latest`` portion of the image name is a tag that specifies the latest released version will be used for the build. Alternatively, you can replace the ``latest`` tag with either a specific version of Tethys Platform (e.g. ``3.3.0``) or with the ``master`` tag to use the latest development version. For a list of all available tags see: `tethysplatform/tethys-core Tags <https://hub.docker.com/r/tethysplatform/tethys-core/tags>`_.


b. Define environment variables
-------------------------------

The `ENV <https://docs.docker.com/engine/reference/builder/#env>`_ instruction can be used to specify environment variables that are used during the build and when the container is running. Environment variables are often overridden when creating the container and can be thought of as arguments for a container to configure it for the specific deployment use case. The base Tethys Platform image provides many environment variables, some of which we will use during our build. For a full list of the Tethys Platform image environment variables see :ref:`docker_official_image_env`.

For this image, define environment variables for the various settings for the apps that will be installed. Add the following lines to the end of the :file:`Dockerfile`:

.. code-block::

    ###############
    # ENVIRONMENT #
    ###############
    ENV DAM_INVENTORY_MAX_DAMS="50" \
        EARTH_ENGINE_PRIVATE_KEY_FILE="" \
        EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL="" \
        THREDDS_TUTORIAL_TDS_PROTOCOL="http" \
        THREDDS_TUTORIAL_TDS_HOST="localhost" \
        THREDDS_TUTORIAL_TDS_PORT="8080"

.. note::

    The ``#`` character is used to denote comments in Dockerfiles.

c. Add files to image
---------------------

The `ADD <https://docs.docker.com/engine/reference/builder/#add>`_ and `COPY <https://docs.docker.com/engine/reference/builder/#copy>`_ instructions let you copy files into the docker image. The difference between the two is that ``ADD`` will automatically decompress archive files (e.g.: ``.tar.gz``) and it can take a URL as the source of the copy (though confusingly if the URL is pointing to an archive, it won't decompress it automatically). It is recommended to use ``COPY`` unless you specifically need the extra features of ``ADD``.

Copy the directories containing the app source code to the ``${TETHYS_HOME}/apps`` directory, which is the recommended directory for app source code. Add the following lines to the bottom of the :file:`Dockerfile`:

.. code-block::

    #############
    # ADD FILES #
    #############
    COPY tethysapp-bokeh_tutorial ${TETHYS_HOME}/apps/tethysapp-bokeh_tutorial
    COPY tethysapp-dam_inventory ${TETHYS_HOME}/apps/tethysapp-dam_inventory
    COPY tethysapp-earth_engine ${TETHYS_HOME}/apps/tethysapp-earth_engine
    COPY tethysapp-postgis_app ${TETHYS_HOME}/apps/tethysapp-postgis_app
    COPY tethysapp-thredds_tutorial ${TETHYS_HOME}/apps/tethysapp-thredds_tutorial

d. Add files for custom theme
-----------------------------

Download the following images to use in the custom theme for the Tethys Portal:

* :download:`leaf-logo.png <images/leaf-logo.png>`
* :download:`favicon.ico <images/favicon.ico>`

Create a new folder called :file:`images` in the :file:`tethys_portal_docker` directory and the images to it.

Add the following lines to the bottom of the Dockefile to add the images to the container image in the static files directory:

.. code-block::

    ###################
    # ADD THEME FILES #
    ###################
    COPY images/* ${STATIC_ROOT}/custom_theme/images/

e. Install apps
---------------

The `RUN <https://docs.docker.com/engine/reference/builder/#run>`_ instruction can be used to run any command during the build. For long commands, the ``\`` (backslash) character can be used to continue a ``RUN`` instruction on the next line for easier readability.

For this image we need to run the ``tethys install`` command for each of our apps. The trickiest part about doing this in a Docker build is activating the ``tethys`` environment, which must be done for each ``RUN`` call. Add the following lines to the end of the :file:`Dockerfile`:

.. code-block::

    ###########
    # INSTALL #
    ###########
    # Bokeh App
    RUN /bin/bash -c "cd ${TETHYS_HOME}/apps/tethysapp-bokeh_tutorial && \
        . ${CONDA_HOME}/bin/activate tethys && \
        tethys install --no-db-sync"
    # Dam Inventory
    RUN /bin/bash -c "cd ${TETHYS_HOME}/apps/tethysapp-dam_inventory && \
        . ${CONDA_HOME}/bin/activate tethys && \
        tethys install --no-db-sync"
    # Earth Engine
    RUN /bin/bash -c "cd ${TETHYS_HOME}/apps/tethysapp-earth_engine && \
        . ${CONDA_HOME}/bin/activate tethys && \
        tethys install --no-db-sync"
    # PostGIS App
    RUN /bin/bash -c "cd ${TETHYS_HOME}/apps/tethysapp-postgis_app && \
        . ${CONDA_HOME}/bin/activate tethys && \
        tethys install --no-db-sync"
    # THREDDS Tutorial
    RUN /bin/bash -c "cd ${TETHYS_HOME}/apps/tethysapp-thredds_tutorial && \
        . ${CONDA_HOME}/bin/activate tethys && \
        tethys install --no-db-sync"

.. note::

    The ``--no-db-sync`` option should be used when running ``tethys install`` in a Dockerfiles. This is because there will not be (and should not be) a database for Tethys to sync to during a Docker build. Any database initialization steps need to occur when the container starts (run time), not when the image is built (build time).

.. note::

    Remember that commands are run by ``sh`` by default. When running ``tethys`` commands in a ``RUN`` instruction you should use ``bash`` to execute the ``activate`` and ``tethys`` commands as illustrated above. This pattern is summarized as follows:

    .. code-block::

        /bin/bash -c . "${CONDA_HOME}/bin/activate tethys && tethys <command>"

    The ``-c`` option to the ``bash`` command allows you to specify a command to run. Place the command in quotes as shown above. The ``&&`` operator is used to join commands on one line. If the first command fails, the second will not be executed. Alternatively, you may use ``;`` operator to join commands and all of the commands will be executed regardless of the outcome of the previous commands.


f. Expose port 80 (optional)
----------------------------

The `EXPOSE <https://docs.docker.com/engine/reference/builder/#expose>`_ instruction is used to tell Docker which ports the application running inside the container listens on. In the :ref:`Tethys Platform Docker image <docker_official_image_env>`, Tethys Portal has been configured to run on port 80, which is the standard HTTP port. Add the following lines to the bottom of the :file:`Dockerfile` to inform Docker of this fact:

.. code-block::

    #########
    # PORTS #
    #########
    EXPOSE 80

.. note::

    This step is optional, because port 80 is already exposed by the :ref:`Tethys Platform Docker image <docker_official_image_env>`. However, having it in your :file:`Dockerfile` is a good reminder.

g. Set default command (optional)
---------------------------------

The `CMD <https://docs.docker.com/engine/reference/builder/#cmd>`_ instruction is used to specify the default command that is executed when the container starts. The :ref:`Tethys Platform Docker image <docker_official_image_env>` provides a :ref:`run.sh <docker_official_run_script>` script that performs the tasks that need to happen when the container starts, including starting the servers that run Tethys Portal.

The `WORKDIR <https://docs.docker.com/engine/reference/builder/#workdir>`_ instruction is used to specify the working directory for the ``CMD``, ``RUN``, ``COPY``, and ``ADD`` instructions. You are welcome to use ``WORKDIR`` multiple times throughout the :file:`Dockerfile` to simplify any custom ``RUN`` instructions you may need. However, we recommend setting it to ``${TETHYS_HOME}`` before the ``CMD`` instruction, as the base image assumes this is the case.

Add the following lines to the bottom of the :file:`Dockerfile`:

.. code-block::

    #######
    # RUN #
    #######
    WORKDIR ${TETHYS_HOME}
    CMD bash run.sh

.. note::

    This step is optional, because the ``CMD`` instruction is already set by the :ref:`Tethys Platform Docker image <docker_official_image_env>` as shown above. However, having it in your Dockerfile is a good reminder of the default behavior. You may also use ``CMD`` in your :file:`Dockerfile` to override the default behavior by providing a custom script or command. If you do so, place your custom script in ``${TETHYS_HOME}`` and be sure to call the :file:`run.sh` at the end of your custom script to make sure Tethys Platform starts up appropriately. To learn more about the :file:`run.sh` see: :ref:`docker_official_run_script`.

6. Create Salt Script(s)
========================

The Tethys Platform Docker uses `Salt States <https://docs.saltproject.io/en/getstarted/fundamentals/states.html>`_, one component of `Salt Stack <https://docs.saltproject.io/en/latest/topics/index.html>`_, to perform runtime initialization of Tethys and apps. Salt States are YAML files that specify the various commands to run when Tethys starts up. It is best understood through examples. For this Docker image, we'll create three Salt State files that will perform the following tasks:

1. Create the Tethys Services our apps need (e.g.: THREDDS, PostGIS)
2. Configure the app settings for each app
3. Apply a custom theme to the Tethys Portal

a. Create directory for Salt State files
----------------------------------------

Create a new directory in :file:`tethys_portal_docker` called :file:`salt` to container the Salt State files:

.. code-block::

    mkdir salt

b. Create empty Salt State files
--------------------------------

Create the following empty Salt State files in the :file:`tethys_portal_docker/salt`

.. code-block::

    cd salt
    touch tethys_services.sls init_apps.sls portal_theme.sls top.sls
    cd ..

c. Set up Tethys Services - tethys_services.sls
-----------------------------------------------

The :file:`tethys_services.sls` Salt State file will contain the steps needed to create the Tethys Services the installed apps require. Tethys Services are objects that define connections to external services for use by Tethys apps. Examples of Tethys Services commonly used by apps include PostGIS databases, THREDDS Data Servers, and GeoServers. Tethys Services are usually created in the admin pages of Tethys Portal, but they can also be created programmatically using the ``tethys services`` command.

Two of the apps that are installed requires a PostGIS database (Dam Inventory and PostGIS App) and one of the apps requires a THREDDS Data Server (THREDDS Tutorial). PostGIS database services can host many databases, so the two apps that require a PostGIS database can share the same service. In fact, they can share the database service that Tethys Portal will use for its primary database.

**Using Env Variables in Salt State Files**

The first step to defining the Tethys Services will be to import the environment variables that contain the connection information for the services. In the case of the PostGIS database service, we'll use the environment variables that contain the database connection information for the Tethys Portal that are already defined by the base Tethys Platform image: ``TETHYS_DB_HOST``, ``TETHYS_DB_PORT``, ``TETHYS_DB_SUPERUSER``, ``TETHYS_DB_SUPERUSER_PASS``. For the THREDDS service, we'll use the app-specific environment variables we defined in the custom Dockerfile: ``THREDDS_TUTORIAL_TDS_PROTOCOL``, ``THREDDS_TUTORIAL_TDS_HOST``, and ``THREDDS_TUTORIAL_TDS_PORT``.

Open the new :file:`tethys_services.sls` file and add the following lines to import the needed environment variables:

.. code-block::

    {% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
    {% set TETHYS_DB_HOST = salt['environ.get']('TETHYS_DB_HOST') %}
    {% set TETHYS_DB_PORT = salt['environ.get']('TETHYS_DB_PORT') %}
    {% set TETHYS_DB_SUPERUSER = salt['environ.get']('TETHYS_DB_SUPERUSER') %}
    {% set TETHYS_DB_SUPERUSER_PASS = salt['environ.get']('TETHYS_DB_SUPERUSER_PASS') %}
    {% set THREDDS_TUTORIAL_TDS_PROTOCOL = salt['environ.get']('THREDDS_TUTORIAL_TDS_PROTOCOL') %}
    {% set THREDDS_TUTORIAL_TDS_HOST = salt['environ.get']('THREDDS_TUTORIAL_TDS_HOST') %}
    {% set THREDDS_TUTORIAL_TDS_PORT = salt['environ.get']('THREDDS_TUTORIAL_TDS_PORT') %}

**Custom Variables**

You can also define custom variables in the Salt State files using `Jinja templating syntax <https://jinja.palletsprojects.com/en/3.0.x/templates/>`_. For this example, define the following variables for use in the Salt State steps:


.. code-block::

    {% set THREDDS_SERVICE_NAME = 'tethys_thredds' %}
    {% set THREDDS_SERVICE_URL = THREDDS_TUTORIAL_TDS_PROTOCOL +'://' + THREDDS_TUTORIAL_TDS_HOST + ':' + THREDDS_TUTORIAL_TDS_PORT %}
    {% set POSTGIS_SERVICE_NAME = 'tethys_postgis' %}
    {% set POSTGIS_SERVICE_URL = TETHYS_DB_SUPERUSER + ':' + TETHYS_DB_SUPERUSER_PASS + '@' + TETHYS_DB_HOST + ':' + TETHYS_DB_PORT %}

**Run Arbitrary Commands in Salt State Files**

The `cmd.run <https://docs.saltproject.io/en/latest/ref/states/all/salt.states.cmd.html>`_ state module can be used to run arbitrary commands, similar to the ``RUN`` instruction in the Dockerfile. It is used in the :file:`tethys_services.sls` to run the ``tethys services`` commands that create the Tethys Services. Add the following lines to the :file:`tethys_services.sls` to create the PostGIS Tethys Service:

.. code-block::

    Create_PostGIS_Database_Service:
      cmd.run:
        - name: ". {{ CONDA_HOME }}/bin/activate tethys && tethys services create persistent -n {{ POSTGIS_SERVICE_NAME }} -c {{ POSTGIS_SERVICE_URL }}"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

**Explanation:**

* ``Create_PostGIS_Database_Service``: This is the name of the step. It needs to be unique across all the Salt State steps that are run, including those run by the base Tethys Platform image.
* The ``name`` parameter of the ``cmd.run`` module is where the command to run should be defined.
* The ``shell`` parameter of the ``cmd.run`` module can be used to specify the shell to use to run the command. Use the ``/bin/bash`` shell for running ``tethys`` commands.
* The ``unless`` parameter of the ``cmd.run`` module can be used to specify a condition that when true will prevent the command from being executed. In this case, the check is to see if a file named ``tethys_services_complete`` exists in the ``TETHYS_PERSIST`` directory. We'll add a step at the end of the script that creates this file. This pattern will result in any steps with this ``unless`` check only running the first time the container is started up.
* ``{{ <variable> }}``: this is the Jinja2 syntax for printing a variable. These are used throughout the step to insert the values of variables in the commands.
* ``TETHYS_PERSIST``: This environment variable contains the path to a directory that should be persisted, meaning it won't be deleted when the container is removed. This will be discussed more in the next tutorial.

**Create THREDDS Tethys Service**

Add the following lines to create the THREDDS Tethys Service:

.. code-block::

    Create_THREDDS_Spatial_Dataset_Service:
      cmd.run:
        - name: ". {{ CONDA_HOME }}/bin/activate tethys && tethys services create spatial -t THREDDS -n {{ THREDDS_SERVICE_NAME }} -c {{ THREDDS_SERVICE_URL }}"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

**Create Setup Complete File**

Finally, add the following lines to create the :file:`tethys_services_complete` file:

.. code-block::

    Flag_Tethys_Services_Setup_Complete:
      cmd.run:
        - name: touch {{ TETHYS_PERSIST }}/tethys_services_complete
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/tethys_services_complete" ];"

d. Configure App Settings - init_apps.sls
-----------------------------------------

The :file:``init_apps.sls`` file will contain the steps required to initialize the apps, including connecting them with the Tethys Services they require. Other common initialization that needs to be performed includes initializing persistent stores and setting the values of other settings. Add the following contents to :file:`init_apps.sls`:

.. code-block::

    {% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
    {% set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') %}
    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
    {% set DAM_INVENTORY_MAX_DAMS = salt['environ.get']('DAM_INVENTORY_MAX_DAMS') %}
    {% set EARTH_ENGINE_PRIVATE_KEY_FILE = salt['environ.get']('EARTH_ENGINE_PRIVATE_KEY_FILE') %}
    {% set EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL = salt['environ.get']('EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL') %}
    {% set THREDDS_SERVICE_NAME = 'tethys_thredds' %}
    {% set POSTGIS_SERVICE_NAME = 'tethys_postgis' %}

    Sync_Apps:
      cmd.run:
        - name: >
            . {{ CONDA_HOME }}/bin/activate tethys &&
            tethys db sync
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Set_Custom_Settings:
      cmd.run:
        - name: >
            . {{ CONDA_HOME }}/bin/activate tethys &&
            tethys app_settings set dam_inventory max_dams {{ DAM_INVENTORY_MAX_DAMS }} &&
            tethys app_settings set earth_engine service_account_email {{ EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL }} &&
            tethys app_settings set earth_engine private_key_file {{ EARTH_ENGINE_PRIVATE_KEY_FILE }}
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Link_Tethys_Services_to_Apps:
      cmd.run:
        - name: >
            . {{ CONDA_HOME }}/bin/activate tethys &&
            tethys link persistent:{{ POSTGIS_SERVICE_NAME }} dam_inventory:ps_database:primary_db &&
            tethys link persistent:{{ POSTGIS_SERVICE_NAME }} postgis_app:ps_database:flooded_addresses &&
            tethys link spatial:{{ THREDDS_SERVICE_NAME }} thredds_tutorial:ds_spatial:thredds_service
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/init_apps_setup_complete" ];"

    Sync_App_Persistent_Stores:
      cmd.run:
        - name: >
            . {{ CONDA_HOME }}/bin/activate tethys &&
            tethys syncstores all
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

e. Apply custom Tethys Portal theme - portal_theme.sls
------------------------------------------------------

The :file:`portal_theme.sls` file will contain the steps required to customize the Tethys Portal theme and content. The :ref:`tethys site <tethys_site_cmd>` command can be used to set Site Settings programmatically. This includes settings such as the portal title, theme colors, and logo. For a complete list of settings that can be set with this command, see :ref:`tethys_site_cmd` and :ref:`tethys_configuration_site_settings`.

Add the following contents to :file:`portal_theme.sls`:

.. code-block::

    {% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
    {% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}

    Apply_Custom_Theme:
      cmd.run:
        - name: >
            . {{ CONDA_HOME }}/bin/activate tethys &&
            tethys site
            --title "My Custom Portal"
            --tab-title "My Custom Portal"
            --library-title "Tools"
            --primary-color "#01200F"
            --secondary-color "#358600"
            --background-color "#ffffff"
            --logo "/custom_theme/images/leaf-logo.png"
            --favicon "/custom_theme/images/favicon.ico"
            --copyright "Copyright © 2021 My Organization"
        - shell: /bin/bash
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/custom_theme_setup_complete" ];"

    Flag_Custom_Theme_Setup_Complete:
      cmd.run:
        - name: touch {{ TETHYS_PERSIST }}/custom_theme_setup_complete
        - shell: /bin/bash

.. note::

    The paths for the ``--logo`` and ``--favicon`` options need to be specified relative to the ``STATIC_ROOT`` directory. Alterntively, you can specify a link to an image host on a different website.


f. Create custom Top file
-------------------------

Finally, the :file:`top.sls` that is included in Tethys Platform image needs to be overridden. This file instructs Salt which Salt State files should be executed and in what order. The default :file:`top.sls` has the following contents:

.. code-block::

    base:
      '*':
        - pre_tethys
        - tethyscore
        - post_app

The :file:`pre_tethys.sls`, :file:`tethyscore.sls`, and :file:`post_app.sls` Salt States need to be executed to properly initialize Tethys. As the name suggests, the :file:`post_app.sls` should be executed after any of your custom app configuration Salt States. The best approach is to start with the contents of the the original :file:`top.sls` file (above) and add your custom Salt State files  between the ``tethyscore`` and ``post_app`` items.

We've created a new :file:`top.sls` that we'll use to overwrite the :file:`top.sls` provided by the Tethys Platform image. Add the following contents to it:

.. code-block::

    base:
      '*':
        - pre_tethys
        - tethyscore
        - tethys_services
        - init_apps
        - portal_theme
        - post_app

g. Add Salt State files to image
--------------------------------

With the Salt State files created, the :file:`Dockerfile` will need to be modified to add them to the image. Add the following lines to the :file:`Dockerfile` after the **INSTALL** section but before the **PORTS** section:

.. code-block::

    ##################
    # ADD SALT FILES #
    ##################
    COPY salt/ /srv/salt/

.. note::

    This ``COPY`` instruction will copy the contents of the local :file:`salt` directory into the :file:`/srv/salt/` directory. Any files with the same names will be replaced. In this case, our :file:`top.sls` will overwrite the :file:`top.sls` placed in :file:`/srv/salt` by the base image.

7. Build Image
==============

With the :file:`Dockerfile` and Salt State scripts complete, the custom Docker image can now be built. Change back into the :file:`tethys_portal_docker` directory if necessary and run the command:

.. code-block::

    docker build -t tethys-portal-docker .

Run the following command to verify that the image was created:

.. code-block::

    docker images

You should see an image with a repository "tethys-portal-docker" and tag "latest" in the list of images similar to this:

.. code-block::

    REPOSITORY             TAG       IMAGE ID       CREATED          SIZE
    tethys-portal-docker   latest    426b6a6f36c5   1 minute ago   2.91GB

.. note::

    The ``-t`` option is used name or tag the docker image. The name can have two parts, separated by a ``:``: ``<name>:<tag>``. If a ``<tag>`` isn't given, it defaults to ``latest``.

9. Commit Changes
=================

Commit the changes to the Dockerfile and salt script as follows:

.. code-block::

    git add .
    git commit -m "Filled in Dockerfile and added Salt State scripts."

What's Next?
============

With the image built, its now time to run the container. Tethys Portal requires a database to run. The database can be created using a Docker image as well, but that means starting two Docker images with one that depends on the other and the easiest way to manage that is with Docker Compose. Continue to the next tutorial to learn how to run the custom Tethys image with Docker Compose.