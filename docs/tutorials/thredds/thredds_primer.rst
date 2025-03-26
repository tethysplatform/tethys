.. _tutorial_thredds_primer:

**************
THREDDS Primer
**************

**Last Updated:** July 2024

In this tutorial you will be introduced to THREDDS using the Docker container that is included with Tethys Platform. This primer is adapted from the `THREDDS Data Server Documentation <https://docs.unidata.ucar.edu/tds/5.0/userguide/index.html>`_. Topics covered include:

* Thematic Real-Time Environmental Distributed Data Services (THREDDS)
* THREDDS Data Server (TDS)
* Open-source Project for a Network Data Access Protocol (OpeNDAP)
* NetCDF Subset Serivce (NCSS)
* Web Mapping Service (WMS)
* Web Coverage Service (WCS)
* TDS Content Directory
* Catalog
* Datasets
* Services
* Tethys Docker Containers
* THREDDS Docker Image

1. Install TDS
==============

The THREDDS Data Server (TDS) can be installed either manually (see: `Getting Started with the TDS <https://docs.unidata.ucar.edu/tds/current/userguide/>`_) or using the Docker image developed by Unidata (see `THREDDS Docker image <https://hub.docker.com/r/unidata/thredds-docker/dockerfile>`_). For this tutorial, we recommend using the Docker image to install THREDDS. We have made it easier to install the THREDDS Docker image by adding it as an option to the Tethys Docker command.

.. warning::

    Docker needs to be installed to use the ``tethys docker`` command (see `Install Docker <https://docs.docker.com/get-started/get-docker/>`_). You will also need to add your user to the docker group and logout and log back in (see `Linux Post Install <https://docs.docker.com/engine/install/linux-postinstall/>`_).


1. Initialize the THREDDS Docker container, **making sure to bind the data directory** when prompted:

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
* http://localhost:8383/thredds/info/serverInfo.html

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

5. NetCDF Data Exercise
=======================

1. Download this :download:`National Water Model Short Range Forecast <https://drive.google.com/file/d/1Mrv54RoIlesWILria8fpSTRwS6StPhgU/edit>` data and extract it. The archive should contain the **first 3** of 18 NetCDF files each representing a 1-hour increment in an 18 hour forecast produced by the `National Water Model <https://water.noaa.gov/about/nwm>`_. Each file contains over 2.7 million forecast points where each point is associated a different stream reach on the `National Hydrogrophy Dataset <https://www.usgs.gov/national-hydrography/national-hydrography-dataset>`_.

2. Create a new :file:`nwm` directory in the :file:`public` directory of the TDS Content Directory (i.e.: :file:`<TDS_CONTENT_DIRECTORY>/public/nwm`).

3. Copy the NetCDF files from step 1 into :file:`<TDS_CONTENT_DIRECTORY>/public/nwm`.

4. Create a new catalog coniguration file at the root of the TDS Content Directory called :file:`nwmCatalog.xml` with the following contents:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0" xmlns:xlink="http://www.w3.org/1999/xlink"
       name="Unidata THREDDS-IDD NetCDF-OpenDAP Server" version="1.0.1">

      <service name="latest" serviceType="Resolver" base="" />
      <service name="all" serviceType="Compound" base="">
        <service name="ncdods" serviceType="OPENDAP" base="/thredds/dodsC/" />
        <service name="HTTPServer" serviceType="HTTPServer" base="/thredds/fileServer/" />
      </service>

      <dataset name="National Water Model Data" collectionType="TimeSeries">
        <metadata inherited="true">
          <serviceName>all</serviceName>
          <authority>edu.ucar.unidata</authority>
          <dataType>Points</dataType>
          <dataFormat>NetCDF</dataFormat>
          <documentation type="rights">Freely available</documentation>
          <documentation xlink:href="https://water.noaa.gov/about/nwm" xlink:title="National Water Model documentation"></documentation>
          <creator>
            <name vocabulary="DIF">DOC/NOAA/NWS/OWP</name>
            <contact url="https://water.noaa.gov/" email="nws.nwc.ops@noaa.gov" />
          </creator>
          <timeCoverage>
            <start>2020-01-06T00:00:00</start>
            <duration>18 hours</duration>
          </timeCoverage>
        </metadata>

        <datasetScan name="NWM Short Range Data" ID="nwm_short_range" path="nwm" location="content/nwm/" harvest="true">
          <metadata inherited="true">
            <documentation type="summary">National Water Model (NWM) - a hydrologic modelling framework that simulates observed and forecast streamflow over the entire continental United States.</documentation>
            <geospatialCoverage>
              <northsouth>
                <start>24.637987</start>
                <size>24.795109</size>
                <units>degrees_north</units>
              </northsouth>
              <eastwest>
                <start>-125.946552</start>
                <size>60.346914</size>
                <units>degrees_east</units>
              </eastwest>
              <updown>
                <start>0.0</start>
                <size>0.0</size>
                <units>km</units>
              </updown>
            </geospatialCoverage>
          </metadata>
          <sort>
            <lexigraphicByName increasing="true"/>
          </sort>
        </datasetScan>
      </dataset>
    </catalog>

5. Add a new catalog reference to the :file:`nwmCatalog.xml` at the bottom of the ``catalog`` section of :file:`catalog.xml`:

.. code-block:: xml

    <catalogRef xlink:title="National Water Model Catalog" xlink:href="nwmCatalog.xml" name=""/>

6. Restart the THREDDS server:

.. code-block:: bash

    tethys docker restart -c thredds

7. Navigate to `<http://localhost:8383/thredds/catalog/nwm/catalog.html>`_ to verify that the new data is available.



