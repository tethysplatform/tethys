.. _docker_dockerfile:

*****************
Create Dockerfile
*****************

**Last Updated:** February 2023

With Docker installed and a basic understanding of how it works under your belt, you are now ready to create a Docker image containing the Tethys Portal with your apps installed. In this tutorial you will create a Docker image with some of the tutorial apps installed. A similar process can be used to create a Docker image for your Tethys Portal.

Prerequisites
=============

Please ensure you have the following prerequisites before continuing:

* :ref:`Docker Installed <docker_get_started>`
* `Git Installed <https://git-scm.com/downloads>`_
* Acquire a :ref:`tutorial_google_earth_engine_service_account`.

Project Setup
=============

Before you can start creating the :file:`Dockerfile` there is some setup that needs to be completed. This includes creating a folder to house all of the artifacts that you will use for the Docker build and acquiring the source code for the apps that will be installed in the Tethys Portal. It will also include setting up a Git repository. An important part of creating Docker projects is knowing how to properly version it with version control software, so this tutorial will instruct you which files to commit. Follow these instructions to set up the Docker project.

1. Create New Directory
-----------------------

Create a new directory to house the :file:`Dockerfile` and other artifacts that will be used for the build.

.. code-block:: bash

    mkdir tethys_portal_docker
    cd tethys_portal_docker

.. tip::

    If you are on Windows, we recommend using the **Git Bash** terminal that comes with `Git for Windows <https://git-scm.com/download/win>`_ when running commands in this tutorial.

2. Create Initial Files
-----------------------

a. Create the following text files in the :file:`tethys_portal_docker` directory:

    .. code-block:: bash

        touch README.md LICENSE Dockerfile

b. Add the following contents each the files:

    **README.md**

    .. code-block:: markdown

        # Demonstration Tethys Portal Docker Project

        This repository demonstrates how to make a Docker image containing a custom Tethys Portal with apps installed. The apps installed are the solutions to several of the Tethys Platform tutorials and include:

        * [Dam Inventory](https://github.com/tethysplatform/tethysapp-dam_inventory)
        * [THREDDS Tutorial](https://github.com/tethysplatform/tethysapp-thredds_tutorial)
        * [Earth Engine](https://github.com/tethysplatform/tethysapp-earth_engine)
        * [PostGIS App](https://github.com/tethysplatform/tethysapp-postgis_app.git)
        * [Bokeh Tutorial](https://github.com/tethysplatform/tethysapp-bokeh_tutorial)

    **LICENSE**

    Choose an open source license from `Licenses and Standards | Open Source Initiative <https://opensource.org/licenses>`_. Copy it into the :file:`LICENSE` file.

    **Dockerfile**

    Leave this empty for now as it will be discussed in depth in the next steps.

3. Initialize Git Repository
----------------------------

Initialize a new Git repository in the :file:`tethys_portal_docker` directory. Then add all the files and create the first commit.

.. code-block:: bash

    git init
    git add .
    git commit -m "First commit"


4. Checkout App Solutions
-------------------------

In this step you'll add the source code of the apps you want to install to the :file:`tethys_portal_docker` directory so they can be used in the build. Generally, only files in the same directory as the :file:`Dockerfile` are accessible to use during a docker build operation.

Adding the files to this directory could be as simple as copying the ``tethyapp-xyz`` folders into the directory. However, the apps we are installing are available on GitHub, so we can use `Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_, which allows you to add a Git repository as a submodule of another Git repository. The advantage of this approach is that as the apps update, we need only pull the latest version in each submodule and then we can build an updated Docker image.

Add the app repositories as Git submodules as follows:

**Bokeh App**:

.. code-block:: bash

    git submodule add -b master https://github.com/tethysplatform/tethysapp-bokeh_tutorial

**Dam Inventory**:

.. code-block:: bash

    git submodule add -b advanced-solution https://github.com/tethysplatform/tethysapp-dam_inventory

**Earth Engine**:

.. code-block:: bash

    git submodule add -b prepare-publish-solution https://github.com/tethysplatform/tethysapp-earth_engine

**PostGIS App**:

.. code-block:: bash

    git submodule add -b master https://github.com/tethysplatform/tethysapp-postgis_app

**THREDDS Tutorial**:

.. code-block:: bash

    git submodule add -b plot-at-location-solution https://github.com/tethysplatform/tethysapp-thredds_tutorial

5. Commit Changes
-----------------

Commit the new submodules configuration that was generated (:file:`.gitmodules`):

.. code-block:: bash

    git commit -am "Added apps as submodules"

Edit Dockerfile
===============

With the app source code checked out it is time to build out the Dockerfile. A :file:`Dockerfile` is composed of several different types of instructions. The instructions used in our :file:`Dockerfile` will be explained as it is built-out, but you can refer to the `Dockerfile Reference | Docker Documentation <https://docs.docker.com/reference/dockerfile/>`_ for full explanations of any instructions.

1. Add ``FROM`` instruction
---------------------------

All Dockerfiles must begin with a `FROM <https://docs.docker.com/reference/dockerfile/#from>`_ instruction that specifies the base image or starting point for the image. Tethys Platform provides a :ref:`base image <docker_official_image_env>` that already has Tethys Platform installed. Add the ``FROM`` instruction to the top of the :file:`Dockerfile` as follows:

.. code-block:: dockerfile

    FROM tethysplatform/tethys-core:latest

.. note::

    The ``latest`` portion of the image name is a tag that specifies the latest released version will be used for the build. Alternatively, you can replace the ``latest`` tag with either a specific version of Tethys Platform (e.g. ``4.0.0``) or with the ``dev`` tag to use the latest development version. For a list of all available tags see: `tethysplatform/tethys-core Tags <https://hub.docker.com/r/tethysplatform/tethys-core/tags>`_.


2. Define environment variables
-------------------------------

The `ENV <https://docs.docker.com/reference/dockerfile/#env>`_ instruction can be used to specify environment variables that are used during the build and when the container is running. Environment variables are often overridden when creating the container and can be thought of as arguments for a container to configure it for the specific deployment use case. The base Tethys Platform image provides many environment variables, some of which we will use during our build. For a full list of the Tethys Platform image environment variables see :ref:`docker_official_image_env`.

For this image, define environment variables for the various settings for the apps that will be installed. Add the following lines to the :file:`Dockerfile`:

.. code-block:: dockerfile

    ###############
    # ENVIRONMENT #
    ###############
    ENV DAM_INVENTORY_MAX_DAMS="50" \
        EARTH_ENGINE_PRIVATE_KEY_FILE="" \
        EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL="" \
        THREDDS_TUTORIAL_TDS_USERNAME="admin" \
        THREDDS_TUTORIAL_TDS_PASSWORD="CHANGEME!" \
        THREDDS_TUTORIAL_TDS_CATALOG="/thredds/catalog/catalog.xml" \
        THREDDS_TUTORIAL_TDS_PRIVATE_PROTOCOL="http" \
        THREDDS_TUTORIAL_TDS_PRIVATE_HOST="localhost" \
        THREDDS_TUTORIAL_TDS_PRIVATE_PORT="8080" \
        THREDDS_TUTORIAL_TDS_PUBLIC_PROTOCOL="http" \
        THREDDS_TUTORIAL_TDS_PUBLIC_HOST="localhost" \
        THREDDS_TUTORIAL_TDS_PUBLIC_PORT="8080"

.. note::

    The ``#`` character is used to denote comments in Dockerfiles.

3. Add files to image
---------------------

The `ADD <https://docs.docker.com/reference/dockerfile/#add>`_ and `COPY <https://docs.docker.com/reference/dockerfile/#copy>`_ instructions let you copy files into the docker image. The difference between the two is that ``ADD`` will automatically decompress archive files (e.g.: ``.tar.gz``) and it can take a URL as the source of the copy (though confusingly if the URL is pointing to an archive, it won't decompress it automatically). It is recommended to use ``COPY`` unless you specifically need the extra features of ``ADD``.

Copy the directories containing the app source code to the ``${TETHYS_HOME}/apps`` directory, which is the recommended directory for app source code. Add the following lines to the :file:`Dockerfile`:

.. code-block:: dockerfile

    #############
    # ADD FILES #
    #############
    COPY tethysapp-bokeh_tutorial ${TETHYS_HOME}/apps/tethysapp-bokeh_tutorial
    COPY tethysapp-dam_inventory ${TETHYS_HOME}/apps/tethysapp-dam_inventory
    COPY tethysapp-earth_engine ${TETHYS_HOME}/apps/tethysapp-earth_engine
    COPY tethysapp-postgis_app ${TETHYS_HOME}/apps/tethysapp-postgis_app
    COPY tethysapp-thredds_tutorial ${TETHYS_HOME}/apps/tethysapp-thredds_tutorial

4. Add files for custom theme
-----------------------------

a. Download the following images to use in the custom theme for the Tethys Portal:

    * :download:`leaf-logo.png <images/leaf-logo.png>`
    * :download:`favicon.ico <images/favicon.ico>`

b. Create a new folder called :file:`images` in the :file:`tethys_portal_docker` directory:

    .. code-block:: bash

        mkdir images

c. Add the downloaded images to the new :file:`images` directory.
d. Add the following lines to the Dockefile to add the images to the container image in the tmp directory (they will need to be moved at runtime):

    .. code-block:: dockerfile

        ###################
        # ADD THEME FILES #
        ###################
        COPY images/ /tmp/custom_theme/images/

5. Install apps
---------------

The `RUN <https://docs.docker.com/reference/dockerfile/#run>`_ instruction can be used to run any command during the build. For long commands, the ``\`` (backslash) character can be used to continue a ``RUN`` instruction on the next line for easier readability.

For this image we need to run the ``tethys install`` command for each of our apps. The trickiest part about doing this in a Docker build is activating the ``tethys`` environment, which must be done before installing the apps. Add the following lines to the :file:`Dockerfile`:

.. code-block:: dockerfile

    ###########
    # INSTALL #
    ###########
    # Activate tethys conda environment during build
    ARG MAMBA_DOCKERFILE_ACTIVATE=1
    # Bokeh App
    RUN cd ${TETHYS_HOME}/apps/tethysapp-bokeh_tutorial && \
        tethys install --no-db-sync
    # Dam Inventory
    RUN cd ${TETHYS_HOME}/apps/tethysapp-dam_inventory && \
        tethys install --no-db-sync
    # Earth Engine
    RUN cd ${TETHYS_HOME}/apps/tethysapp-earth_engine && \
        tethys install --no-db-sync
    # PostGIS App
    RUN cd ${TETHYS_HOME}/apps/tethysapp-postgis_app && \
        tethys install --no-db-sync
    # THREDDS Tutorial
    RUN cd ${TETHYS_HOME}/apps/tethysapp-thredds_tutorial && \
        tethys install --no-db-sync

.. note::

    The ``--no-db-sync`` option should be used when running ``tethys install`` in a Dockerfiles. This is because there will not be (and should not be) a database for Tethys to sync to during a Docker build. Any database initialization steps need to occur when the container starts (run time), not when the image is built (build time).

.. note::

    Remember that commands are run by ``sh`` by default. To run ``tethys`` commands in a ``RUN`` instruction you need to activate the Tethys Conda environment. The following line has the effect of activating the Tethys Conda environment for any `RUN` instruction after it:

    .. code-block:: dockerfile

        ARG MAMBA_DOCKERFILE_ACTIVATE=1


6. Expose ports (optional)
--------------------------

The `EXPOSE <https://docs.docker.com/reference/dockerfile/#expose>`_ instruction is used to tell Docker which ports the application running inside the container listens on. In the :ref:`Tethys Platform Docker image <docker_official_image_env>`, Tethys Portal has been configured to run on port 80, which is the standard HTTP port. Add the following lines to the :file:`Dockerfile` to inform Docker of this fact:

.. code-block:: dockerfile

    #########
    # PORTS #
    #########
    EXPOSE 80

.. note::

    This step is optional, because port 80 is already exposed by the :ref:`Tethys Platform Docker image <docker_official_image_env>`. However, having it in your :file:`Dockerfile` is a good reminder.

7. Default command (optional)
-----------------------------

The `CMD <https://docs.docker.com/reference/dockerfile/#cmd>`_ instruction is used to specify the default command that is executed when the container starts. The :ref:`Tethys Platform Docker image <docker_official_image_env>` provides a :ref:`run.sh <docker_official_run_script>` script that performs the tasks that need to happen when the container starts, including starting the servers that run Tethys Portal.

The `WORKDIR <https://docs.docker.com/reference/dockerfile/#workdir>`_ instruction is used to specify the working directory for the ``CMD``, ``RUN``, ``COPY``, and ``ADD`` instructions. You are welcome to use ``WORKDIR`` multiple times throughout the :file:`Dockerfile` to simplify any custom ``RUN`` instructions you may need. However, we recommend setting it to ``${TETHYS_HOME}`` before the ``CMD`` instruction, as the base image assumes this is the case.

Add the following lines to the :file:`Dockerfile`:

.. code-block:: dockerfile

    #######
    # RUN #
    #######
    WORKDIR ${TETHYS_HOME}
    CMD bash run.sh

.. note::

    This step is optional, because the ``CMD`` instruction is already set by the :ref:`Tethys Platform Docker image <docker_official_image_env>` as shown above. However, having it in your Dockerfile is a good reminder of the default behavior. You may also use ``CMD`` in your :file:`Dockerfile` to override the default behavior by providing a custom script or command. If you do so, place your custom script in ``${TETHYS_HOME}`` and be sure to call the :file:`run.sh` at the end of your custom script to make sure Tethys Platform starts up appropriately. To learn more about the :file:`run.sh` see: :ref:`docker_official_run_script`.

8. Commit Changes
-----------------

Add the images to the repository and commit the changes to the :file:`Dockerfile`:

.. code-block:: bash

    git add .
    git commit -m "Initial Dockerfile complete"

Solution
========

This concludes this portion of the tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethys_portal_docker>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethys_portal_docker
    cd tethys_portal_docker
    git checkout -b dockerfile-solution dockerfile-solution-|version|

What's Next?
============

Continue to the next tutorial to learn how to perform runtime initialization when the container starts.

