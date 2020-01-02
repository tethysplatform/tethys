**************
THREDDS Primer
**************

**Last Updated:** December 2019

In this tutorial you will be introduced to THREDDS using the Docker container that is included with Tethys Platform. This primer is adapted from the `THREDDS Data Server Documentation <https://docs.unidata.ucar.edu/tds/5.0/userguide/index.html>`_. Topics covered include:

* Tethys Docker Containers
* THREDDS
* TDS
* OpeNDAP
* NCSS
* WMS
* WCS
* TDS Content Directory
* Catalog
* Datasets
* Services
* Docker
* THREDDS Docker Image

1. Install TDS
==============

The THREDDS Data Server (TDS) can be installed either manually or using their Docker container. For this tutorial recommend using the `THREDDS Docker image <https://hub.docker.com/r/unidata/thredds-docker/dockerfile>`_, which has been integrated with the Tethys Docker command for convenience.

1. Initialize the THREDDS Docker container, making sure to bind the data directory when prompted:

.. code-block:: bash

    tethys docker init -c thredds

.. note::

    The command ``tethys docker init`` only needs to be run the first time you are creating a container. If it already exists, you can skip to the next step.


2. Start the THREDDS Docker container:

.. code-block:: bash

    tethys docker start -c thredds

.. tip::

    To stop the docker container:

    .. code-block:: bash

        tethys docker stop -c thredds

    For more information about the Docker interface in Tethys Platform see the :ref:`tethys_cli_docker` reference.

3. Obtain the endpoint for the THREDDS Docker container:

.. code-block:: bash

    tethys docker ip

.. tip::

    Alternatively, you may install TDS manually using the `Getting Started with the TDS guide <https://docs.unidata.ucar.edu/tds/5.0/userguide/index.html>`_. You may also use an existing TDS server, provided you have access to it's content directory.

2. Explore the Content Directory
================================

Navigate to the TDS Content Directory and explore the contents. This directory stores all of the TDS configuration information and data. Review the `TDS Content Directory tutorial <https://docs.unidata.ucar.edu/tds/5.0/userguide/tds_content_directory.html>`_ for an explanation of each of the files and folders in the content directory.

.. tip::

    When using the THREDDS docker container, the location of this directory is the folder that you specified during the bind step. The default bind location is :file:`~/.tethys/thredds`.

3. Customize TDS
================

The TDS Configuration File (:file:`threddsConfig.xml`) is used to control the behavior of the TDS including metadata about the server and which services are enabled.

1. Open :file:`threddsConfig.xml` in a text editor.

2. Customize the following parameters in the **serverInformation** section:

* **name**: Name of the TDS Server
* **logoUrl**: Logo for the TDS Server
* **logoAltText**: Text description of logo for screen readers
* **abstract**: Description of the data hosted on the TDS Server
* **keywords**: Keywords for the type of data hosted on the TDS Server
* **contact**
    * **name**: Name of TDS Server Maintainer
    * **organization**: Organization of TDS Server Maintainer
    * **email**: Email of TDS Server Maintainer
* **hostInstitution**
    * **name**: Institution/organization hosting the TDS Server
    * **webSite**: Website of institution/organization hosting the TDS Server
    * **logoUrl**: Logo of institution/organization hosting the TDS Server
    * **logoAltText**: Text description of logo for screen readers

3. Save your changes and restart the TDS:

.. code-block:: bash

    tethys docker restart -c thredds

.. tip::

    You can view the logs TDS server in the Docker container using the Docker CLI:

    .. code-block:: bash

        docker logs tethys_thredds

    This is useful for debugging issues when the container won't start, such as malformed XML in the :file:`threddsConfig.xml`.

4. Navigate to the following locations to see how this metadata is incorporated into the TDS:

* http://localhost:8383/thredds/catalog.html
* http://localhost:8383/thredds/serverInfo.html

.. tip::

    See `Basic TDS Configuration <https://docs.unidata.ucar.edu/tds/5.0/userguide/basic_tds_configuration.html>`_ for more information about configuring TDS.

5. The TDS Configuration File is also used to control which data services are enabled. Services that are supported by TDS include Web Coverage Service (WCS), Web Map Service (WMS), ncISO, and NetCDF Subset Service (NCSS). Most of these services are disabled by default in the docker version of TDS and need to be enabled. Review the following documentation about how to enable the various data services in TDS:

* `Adding OGC/ISO Services (WMS, WCS, ncISO) <https://docs.unidata.ucar.edu/tds/5.0/userguide/adding_ogc_iso_services.html>`_
* `Adding the NetCDF Subset Service (NCSS) <https://docs.unidata.ucar.edu/tds/5.0/userguide/adding_ncss.html>`_

6. You can further customize the look and feel of your TDS using CSS. Navigate to the ``htmlSetup`` section of the TDS Configuration File (:file:`threddsConfig.xml`) and note the names of the css files for different pages (e.g. :file:`tds.css`, :file:`tdsCat.css`, :file:`tdsDap.css`). If you create these files in the :file:`public` directory, you'll be able to customize the CSS of the associated pages. See the `Customizing the TDS Look and Feel <https://docs.unidata.ucar.edu/tds/5.0/userguide/customizing_tds_look_and_feel.html>`_ documentation for more details.


4. Client/Configuration Catalogs
================================

1. Review the following documentation on catalog configuration (ignore exercises):

* `Basic Client Catalog Primer <https://docs.unidata.ucar.edu/tds/5.0/userguide/basic_client_catalog.html>`_
* `Nested Datasets <https://docs.unidata.ucar.edu/tds/5.0/userguide/nested_datasets.html>`_
* `Client Catalog Metadata <https://docs.unidata.ucar.edu/tds/5.0/userguide/client_catalog_metadata.html>`_
* `Catalog References <https://docs.unidata.ucar.edu/tds/5.0/userguide/client_catalog_references.html>`_
* `Compound Service Elements <https://docs.unidata.ucar.edu/tds/5.0/userguide/compound_service_elements.html>`_
* `Default TDS Configuration Catalog <https://docs.unidata.ucar.edu/tds/5.0/userguide/default_config_catalog.html>`_
* `Basics of Configuration Catalogs <https://docs.unidata.ucar.edu/tds/5.0/userguide/basic_config_catalog.html>`_
* `Configuration Catalogs <https://docs.unidata.ucar.edu/tds/5.0/userguide/config_catalog.html>`_

.. tip::

    It is easy to confuse the TDS Root Configuration Catalog (:file:`catalog.xml`) and the TDS Configuration File (:file:`threddsConfig.xml`). Remember:

    * TDS Root Configuration Catalog (:file:`catalog.xml`): Used to define and configure datasets hosted by the TDS server.
    * TDS Configuration File (:file:`threddsConfig.xml`): Used to customize TDS server information and behaviour.



