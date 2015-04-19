*******************
System Requirements
*******************

**Last Updated:** April 18, 2015

Tethys Platform is composed of several software components, each of which draw on quite a bit of computing resources. We strongly recommend distributing the software components across several servers to optimize the use of computing resources and improve performance of Tethys Platform. Specifically, we recommend having a separate server for each of the following components:

* Tethys Portal
* PostgreSQL with PostGIS
* GeoServer
* 52 North WPS

**INSERT FIGURE HERE SHOWING A TETHYS STACK**

The following requirements should be taken as baseline guidelines. It is likely you will need to expand storage, RAM, or processors as you add more apps. Each instance of Tethys Platform will need to be fine tuned depending on the requirements of the apps that it is serving.

Tethys Portal
-------------

Tethys Portal is a Django web application. It needs to be able to handle requests from many users meaning it will need processors and memory. If the apps are designed right, they will off load data to other servers (like the database server), so the Tethys Portal Server should not need a lot of storage. This depends a lot on what the apps do with data.

* Processor: Quad Core
* RAM: 4 GB
* Hard Disk: 50 GB+

GeoServer
---------

GeoServer is used to render maps and spatial data. It performs operations like coordinate transformations and format conversions on the fly, so it needs a lot of processing power. It also requires storage for the data sets that it is serving.

* Processor: Quad Core
* RAM: 4 GB
* Hard Disk: 100 GB+


52 North WPS
------------

52 North WPS is a geoprocessing service and will require processing capabilities. It will also need disk space for temporary storage of the datasets it is processing.

* Processors: Quad Core
* RAM: 4GB
* Hard Disk: 50GB

PostgreSQL with PostGIS
-----------------------

PostgreSQL is a database should be given a lot of storage space.

* Processors: Dual Core
* RAM: 4 GB
* Hard Disk: 500 GB +