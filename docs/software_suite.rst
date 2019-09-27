**************
Software Suite
**************

**Last Updated:** May 18, 2016

The Software Suite is the component of Tethys Platform that provides access to resources and functionality that are commonly required to develop water resources web apps. The primary motivation of creating the Tethys Software Suite was overcome the hurdle associated with selecting a GIS software stack to support spatial capabilities in apps. Some of the more specialized needs for water resources app development arise from the spatial data components of the models that are used in the apps. Distributed hydrologic models, for example, are parameterized using raster or vector layers such as land use maps, digital elevation models, and rainfall intensity grids.

.. figure:: images/features/tethys_platform_diagram.png
    :width: 600px
    :align: center

A majority of the software projects included in the software suite are web GIS projects that can be used to acquire, modify, store, visualize, and analyze spatial data, but Tethys Software Suite also includes other software projects to address computing and visualization needs of water resources web apps. This article will describe the components included in the Tethys Software Suite in terms of the functionality provided by the software.


Spatial Database Storage
========================

.. image:: images/software/postgis.png
   :width: 170px
   :align: right

Tethys Software Suite includes the `PostgreSQL <http://www.postgresql.org/>`_ database with `PostGIS <http://postgis.net/>`_, a spatial database extension, to provide spatial data storage capabilities for Tethys web apps. PostGIS adds spatial column types including raster, geometry, and geography. The extension also provides database functions for basic analysis of GIS objects.

To use a PostgreSQL database in your app use the :doc:`./tethys_sdk/tethys_services/persistent_store`. To use a spatially enabled database with PostGIS use the :doc:`./tethys_sdk/tethys_services/spatial_persistent_store`.

Map Publishing
==============

.. image:: images/software/geoserver.png
   :width: 200px
   :align: right

Tethys Software Suite provides `GeoServer <http://geoserver.org/>`_ for publishing spatial data as web services. GeoServer is used to publish common spatial files such as Shapefiles and GeoTIFFs in web-friendly formats.

To use the map publishing capabilities of GeoServer in your app refer to the :doc:`./software_suite/geoserver` documentation and use the :doc:`./tethys_sdk/tethys_services/spatial_dataset_services`.

Geoprocessing
=============

.. image:: images/software/52n-logo.gif
   :width: 150px
   :align: right

`52°North Web Processing Service (WPS) <http://52north.org/communities/geoprocessing/wps/>`_ is included in Tethys Software Suite as one means for supporting geoprocessing needs in water resources web app development. It can be linked with geoprocessing libraries such as `GRASS <http://grass.osgeo.org/>`_, `Sextante <http://www.wikiwand.com/es/SEXTANTE_(SIG)>`_, and `ArcGIS® Server <http://www.esri.com/software/arcgis/arcgisserver>`_ for out-of-the-box geoprocessing capabilities.

The PostGIS extension, included in the software suite, can also provide geoprocessing capabilities on data that is stored in a spatially-enabled database. PostGIS includes SQL geoprocessing functions for splicing, dicing, morphing, reclassifying, and collecting/unioning raster and vector types. It also includes functions for vectorizing rasters, clipping rasters with vectors, and running stats on rasters by geometric region.

To use 52°North WPS or other WPS geoprocessing services in your app use the :doc:`./tethys_sdk/tethys_services/web_processing_services`.

Visualization
=============

.. image:: images/software/openlayers.png
   :width: 75px
   :align: right

`OpenLayers 3 <http://openlayers.org/>`_ is a JavaScript web-mapping client library for rendering interactive maps on a web page. It is capable of displaying 2D maps of OGC web services and a myriad of other spatial formats and sources including GeoJSON, KML, GML, TopoJSON, ArcGIS REST, and XYZ.

To use an OpenLayers map in your app use the **Map View Gizmo** of the :doc:`./tethys_sdk/gizmos`.

.. image:: images/software/googlemaps.png
   :width: 75px
   :align: right

`Google Maps™ <https://developers.google.com/maps/web/>`_ provides the ability to render spatial data in a 2D mapping environment similar to OpenLayers, but it only supports displaying data in KML formats and data that are added via JavaScript API. Both maps provide a mechanism for drawing on the map for user input.

To use an OpenLayers map in your app use the **Google Map View Gizmo** of the :doc:`./tethys_sdk/gizmos`.

.. image:: images/software/highcharts.png
   :width: 75px
   :align: right

Plotting capabilities are provided by `Highcharts <http://www.highcharts.com/>`_, a JavaScript library created by Highsoft AS. The plots created using Highcharts are interactive with hovering effects, pan and zoom capabilities, and the ability to export the plots as images.

To use an OpenLayers map in your app use the **Plot View Gizmo** of the :doc:`./tethys_sdk/gizmos`.

Distributed Computing
=====================

.. image:: images/software/htcondor.png
   :width: 300px
   :align: right

To facilitate the large-scale computing that is often required by water resources applications, Tethys Software Suite leverages the computing management middleware `HTCondor <http://research.cs.wisc.edu/htcondor/>`_. HTCondor is both a resource management and a job scheduling software.

To use the HTCondor and the computing capabilities in your app use the :doc:`./tethys_sdk/jobs` and the :doc:`./tethys_sdk/compute`.

File Dataset Storage
====================

Tethys Software Suite does not include software for handling flat file storage. However, Tethys SDK provides APIs for working with CKAN and HydroShare to address flat file storage needs. Descriptions of CKAN and HydroShare are provided here for convenience.

.. image:: images/software/ckan.png
   :width: 150px
   :align: right

`CKAN <http://ckan.org/>`_ is an open source data sharing platform that streamlines publishing, sharing, finding, and using data. There is no central CKAN hub or portal, rather data publishers setup their own instance of CKAN to host the data for their organization.

.. image:: images/software/hydroshare.png
   :width: 200px
   :align: right

`HydroShare <http://hydroshare.cuahsi.org/>`_ is an online hydrologic model and data sharing portal being developed by CUAHSI. It builds on the sharing capabilities of CUAHSI’s Hydrologic Information System by adding support for sharing models and using social media functionality.

To use a CKAN instance for flat file storage in your app use the :doc:`./tethys_sdk/tethys_services/dataset_services`. HydroShare is not fully supported at this time, but when it is you will use the :doc:`./tethys_sdk/tethys_services/dataset_services` to access HydroShare resources.

WebSocket Communication
=======================

.. image:: images/software/django-channels.png
   :width: 200px
   :align: right

Tethys Platform supports WebSocket connections using `Django Channels <https://channels.readthedocs.io/en/latest/>`_. Django Channels is an official Django project that brings asynchronous and long-running connections to the synchronous Django.

The WebSocket protocol provides a persistent connection between the client and the server. In contrast to the traditional HTTP protocol, the webscoket protocol allows for bidirectional communication between the client and the server (i.e. the server can trigger a response without the client sending a request). Django Channels uses Consumers to structure code and handle client/server communication in a similar way Controllers are used with the HTTP protocol. When creating a WebSocket connection, a "handshake" needs to be established between the client and server.

For more information about Django Channels and Consumers visit `the Django Channels docummentation <https://channels.readthedocs.io/en/latest/>`_.

For more information on establishing a WebSocket connection see `the JavaScript WebSocket API <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/>`_. Alternatively, other existing JavaScript or Python WebSocket clients can we used.

To create a URL mapping using the WebSocket protocol see the example provided in the `App Base Class API documentation <./tethys_sdk/app_class.html#override-methods>`_.

Docker Installation
===================

.. image:: images/software/docker.png
   :width: 300px
   :align: right

Tethys Software Suite uses `Docker <https://www.docker.com/>`_ virtual container system to simplify the installation of some elements. Docker images are created and used to create containers, which are essentially stripped down virtual machines running only the software included in the image. Unlike virtual machines, the Docker containers do not partition the resources of your computer (processors, RAM, storage), but instead run as processes with full access to the resources of the computer.

Three Docker images are provided as part of Tethys Software Suite including:

* PostgreSQL with PostGIS
* 52° North WPS
* GeoServer.

The installation procedure for each software has been encapsulated in a Docker image reducing the installation procedure to three simple steps:

1. Install Docker
2. Download the Docker images
3. Deploy the Docker images as containers

SDK Relationships
=================

Tethys Platform provides a software development kit (SDK) that provides application programming interfaces (APIs) for interacting with each of the software included in teh Software Suite. The appropriate APIs are referenced in each section above, but a summary table of the relationship between the Software Suite and the SDK is provided as a reference.

=====================================  ===============================================================  ============================================
Software                               API                                                              Functionality
=====================================  ===============================================================  ============================================
PostgreSQL                             :doc:`./tethys_sdk/tethys_services/persistent_store`             SQL Database Storage
PostGIS                                :doc:`./tethys_sdk/tethys_services/spatial_persistent_store`     Spatial Database Storage and Geoprocessing
GeoServer                              :doc:`./tethys_sdk/tethys_services/spatial_dataset_services`     Spatial File Publishing
52° North WPS                          :doc:`./tethys_sdk/tethys_services/web_processing_services`      Geoprocessing Services
OpenLayers, Google Maps, HighCharts    :doc:`./tethys_sdk/gizmos`                                       Spatial and Tabular Visualization
HTCondor                               :doc:`./tethys_sdk/compute` and                                  Computing and Job Management
                                       :doc:`./tethys_sdk/jobs`
CKAN, HydroShare                       :doc:`./tethys_sdk/tethys_services/dataset_services`             Flat File Storage
=====================================  ===============================================================  ============================================

References
==========

.. toctree::
   :maxdepth: 1

   software_suite/geoserver