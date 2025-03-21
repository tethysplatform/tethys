**************
THREDDS Docker
**************

**Last Updated:** December 2019

Features
========

* Tethys can setup a `THREDDS <https://docs.unidata.ucar.edu/tds/current/userguide/index.html>`_ docker container
* It can be configured to mount a data directory that contains the following items:

   * Public Data Directory
   * Logs directory
   * Config files for catalog, wmsSettings etc.

* By default the catalog will be accessible at http://localhost:8383/thredds/catalog.html (for machines running latest docker clients)

Installation
============

Installing the THREDDS Docker is done using the Tethys Command Line Interface (see: :ref:`tethys_cli_docker` ). To install it, open a terminal, activate the Tethys virtual environment, and execute the command:

::

    $ . /usr/lib/tethys/bin/activate
    $ tethys docker init -c thredds

This command will initiate the download of the THREDDS Docker image. Once the image finishes downloading it will be used to create a Docker container and you will be prompted to configure it. Here is a brief explanation of each of the configuration options:

* **TDM Password**: Password for the THREDDS Data Manager
* **TDS Host**: The domain name that the TDS will be accessed at (e.g. thredds.example.com).
* **TDS JVM Max Heap Size**: The maximum amount of memory the TDS will be able to use.
* **TDS JVM Min Heap Size**: The minimum amount of memory the TDS will acquire when starting up.
* **TDM JVM Max Heap Size**: The maximum amount of memory the TDM will be able to use.
* **TDM JVM Min Heap Size**: The minimum amount of memory the TDM will acquire when starting up.

  .. warning::

      BE CAREFUL WITH THIS. If you set the min memory to be 4 GB for both the TDS and the TDM, the Docker container will try to allocate 8GB of memory. If your machine doesn't have 8GB of memory, it will get overwhelmed and lock down.

* **Bind the THREDDS data directory to the Host** (HIGHLY RECOMMENDED): This allows you to mount one of the directories on your machine into the docker container. This will give you direct access to the THREDDS data directory outside of the docker container. This is useful if you want to configure your catalog.xml or threddsConfig.xml, add data directly to the data directory. The THREDDS docker container will automatically add the default test data to this directory after starting up for the first time.

  .. warning::

      If the directory that you are binding to doesn't exist or you don't have permission to write to it, the setup operation may fail. To be safe you should create the directory before hand and ensure you can write to it.

.. tip::

    For more information about the Unidata THREDDS Docker image, see the README in the `THREDDS Docker GitHub Repository <https://github.com/Unidata/thredds-docker>`_.

Managing the Docker Instance
===============================


1. Start and Stop Commands

  ::

      (tethys) $ tethys docker start -c thredds
      (tethys) $ tethys docker stop -c thredds

2. Remove the container (also stops it if its running). Its highly recommended to delete the data directory if you are trying to setup a brand new instance:

  ::

      (tethys) $ tethys docker remove -c thredds