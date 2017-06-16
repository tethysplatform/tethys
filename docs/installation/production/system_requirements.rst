*******************
System Requirements
*******************

**Last Updated:** April 18, 2015

Tethys Platform is composed of several software components, each of which has the potential of using a copious amount of computing resources (see Figure 1). We recommend distributing the software components across several servers to optimize the use of computing resources and improve performance of Tethys Platform. Specifically, we recommend having a separate server for each of the following components:

* Tethys Portal
* PostgreSQL with PostGIS
* GeoServer
* 52 North WPS
* HTCondor
* CKAN

.. figure:: ../../images/tethys_deploy_stack.png
      :width: 600px

      **Figure 1.** Tethys Platform consists of several software components that should be hosted on separate servers in a production environment.

The following requirements should be interpreted as minimum guidelines. It is likely you will need to expand storage, RAM, or processors as you add more apps. Each instance of Tethys Platform will need to be fine tuned depending to fit the requirements of the apps that it is serving.

Tethys Portal
-------------

Tethys Portal is a Django web application. It needs to be able to handle requests from many users meaning it will need processors and memory. Apps should be designed to offload data storage onto one of the data storage nodes (CKAN, database, GeoServer) to prevent the Tethys Portal server from get bogged down with file reads and writes.

* Processor: 2 CPU Cores @ 2 GHz each
* RAM: 4 GB
* Hard Disk: 20 GB

GeoServer
---------

GeoServer is used to render maps and spatial data. It performs operations like coordinate transformations and format conversions on the fly, so it needs a decent amount of processing power and RAM. It also requires storage for the datasets that it is serving.

* Processor: 4 CPU Cores @ 2 GHz each
* RAM: 8 GB
* Hard Disk: 500 GB +


52 North WPS
------------

52 North WPS is a geoprocessing service provider and as such will require processing power.

* Processors: 4 CPU Cores @ 2 GHz each
* RAM: 8 GB
* Hard Disk: 100 GB

PostgreSQL with PostGIS
-----------------------

PostgreSQL is a database server and it should be optimized for storage. The PostGIS extension also provide the server with geoprocessing capabilities, which may require more processing power than recommended here.

* Processors: 4 CPU Cores @ 2 GHz each
* RAM: 4 GB
* Hard Disk: 500 GB +

