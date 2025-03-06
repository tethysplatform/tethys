*************************
Distributed Configuration
*************************

**Last Updated:** September 2022

The Tethys Docker images can be used to easily install each of the software components of Tethys Platform on separate servers. However, you will not be able to use the Tethys commandline tools to install the Dockers as you do during development. The following article describes how to deploy each software component using the native Docker API.

Install Docker on Each Server
=============================

After you have provisioned servers for each of the Tethys software components, install Docker on each using the appropriate `Docker installation instructions <https://docs.docker.com/get-started/get-docker/>`_. Docker provides installation instructions for most major types of servers.

Server Requirements
===================

Tethys Platform is composed of several software components, each of which has the potential of using a copious amount of computing resources (see Figure 1). We recommend distributing the software components across several servers to optimize the use of computing resources and improve performance of Tethys Platform. Specifically, we recommend having a separate server for each of the following components:

* Tethys Portal
* PostgreSQL with PostGIS
* GeoServer
* 52 North WPS
* HTCondor
* CKAN

.. figure:: images/tethys_deploy_stack.png
      :width: 600px

      **Figure 1.** Tethys Platform consists of several software components that may be hosted on separate servers in a production environment.

The following requirements should be interpreted as minimum guidelines. It is likely you will need to expand storage, RAM, or processors as you add more apps. Each deployment of Tethys Platform will need to be fine tuned depending to fit the requirements of the apps that it is serving.

Tethys Portal
-------------

Tethys Portal is a Django web application. It needs to be able to handle requests from many users meaning it will need processors and memory. Apps should be designed to offload data storage onto one of the data storage nodes (CKAN, database, GeoServer) to prevent the Tethys Portal server from get bogged down with file reads and writes.

* Processor: 2 CPU Cores @ 2 GHz each
* RAM: 4 GB
* Hard Disk: 30 GB

GeoServer
---------

GeoServer is used to render maps and spatial data. It performs operations like coordinate transformations and format conversions on the fly, so it needs a decent amount of processing power and RAM. It also requires storage for the datasets that it is serving.

* Processor: 8 CPU Cores @ 2 GHz each
* RAM: 8 GB
* Hard Disk: 100 GB +


52 North WPS
------------

52 North WPS is a geoprocessing service provider and as such will require processing power.

* Processors: 4 CPU Cores @ 2 GHz each
* RAM: 8 GB
* Hard Disk: 100 GB +

PostgreSQL with PostGIS
-----------------------

PostgreSQL is a database server and it should be optimized for storage. The PostGIS extension also provide the server with geoprocessing capabilities, which may require more processing power than recommended here.

* Processors: 4 CPU Cores @ 2 GHz each
* RAM: 8 GB
* Hard Disk: 100 GB +

GeoServer Docker Deployment
===========================

Pull the Docker image for GeoServer using the following command:

::

    sudo docker pull tethysplatform/geoserver

This container has several environment variables that you can use to customize the performance of the geoserver:

* ENABLED_NODES: Number of GeoServer nodes to start up to 4.
* REST_NODES: Number of the enabled GeoServer nodes to have support the REST interface. We recommend setting this to 1.
* MAX_MEMORY: Maximum memory to allow each node to allocate in MB. Set this based on the memory available on the machine you are installing GeoServer on. Caution: the total memory will be  MAX_MEMORY * ENABLED_NODES.
* MIN_MEMORY: Minimum memory to allow each node to allocate initially in MB. Set this based on the memory available on the machine you are installing GeoServer on. Caution: the GeoServer will allocate MIN_MEMORY * ENABLED_NODES when it starts.
* NUM_CORES: The number of cores you want GeoServer to use. This should be less than or equal to the number of cores on the machine.
* MAX_TIMEOUT: Maximum time in seconds to wait before returning timeout. Defaults to 60 seconds.

After the image has been pulled, run a new Docker container as follows:

::

    sudo docker run -d -p 80:8080 --restart=always --name geoserver -e ENABLED_NODES=4 -e REST_NODES=1 -e MAX_MEMORY=1024 -e MIN_MEMORY=512 -e NUM_CORES=4 -e MAX_TIMEOUT=60 tethysplatform/geoserver

Refer to the `Docker Run Reference <https://docs.docker.com/engine/containers/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name.

More information about the GeoServer Docker can be found on the Docker Registry:

`<https://hub.docker.com/r/tethysplatform/geoserver>`_

.. important::

    The admin username and password can only be changed using the web admin interface. Be sure to log into GeoServer and change the admin password using the web interface. The default username and password are *admin* and *geoserver*, respectively.

PostgreSQL with PostGIS Docker Deployment
=========================================

We recommend using the `postgis/postgis <https://hub.docker.com/r/postgis/postgis/>`_ image to deploy PostgreSQL with PostGIS using Docker. This image is based on the official PostgreSQL image. Pull the Docker image for PostgreSQL with PostGIS using the following command:

::

    sudo docker pull postgis/postgis

Here is an example of how to start the container:

::

    sudo docker run -d -p 5432:5432 --restart=always --name postgis -e POSTGRES_PASSWORD=mysecretpassword postgis/postgis

Refer to the `Docker Run Reference <https://docs.docker.com/engine/containers/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name. It also set the passwords for each database at startup.

Once the container is running, you can initialize the database using the ``tethys db`` command from your Tethys Portal server.

First set the database settings:

::

    tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql --set DATABASES.default.NAME tethys_platform --set DATABASES.default.USER <TETHYS_DB_USERNAME> --set DATABASES.default.PASSWORD <TETHYS_DB_PASSWORD> --set DATABASES.default.HOST <TETHYS_DB_HOST> --set DATABASES.default.PORT <TETHYS_DB_PORT>

Then run the ``tethys db configure`` command, prepending it with the PGPASSWORD environment variable:

::

    PGPASSWORD=<POSTGRES_PASSWORD> tethys db configure --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <PORTAL_SUPERUSER_USERNAME> --portal-superuser-email '<PORTAL_SUPERUSER_EMAIL>' --portal-superuser-pass <PORTAL_SUPERUSER_PASSWORD>


More information about the PostgreSQL with PostGIS Docker can be found on the Docker Registry:

`<https://hub.docker.com/r/postgis/postgis/>`_


52 North WPS Docker Deployment
==============================

Pull the Docker image for 52 North WPS using the following command:

::

    sudo docker pull ciwater/n52wps

After the image has been pulled, run a new Docker container as follows:

::

    sudo docker run -d -p 80:8080 -e USERNAME="foo" -e PASSWORD="bar" --restart=always --name n52wps ciwater/n52wps


Refer to the `Docker Run Reference <https://docs.docker.com/engine/containers/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name. It also sets the username and password for the admin user.

You may pass several environmental variables to set the service metadata and the admin username and password:

* -e USERNAME=<ADMIN_USERNAME>
* -e PASSWORD=<ADMIN_PASSWORD>
* -e NAME=<INDIVIDUAL_NAME>
* -e POSITION=<POSITION_NAME>
* -e PHONE=<VOICE>
* -e FAX=<FACSIMILE>
* -e ADDRESS=<DELIVERY_POINT>
* -e CITY=<CITY>
* -e STATE=<ADMINISTRATIVE_AREA>
* -e POSTAL_CODE=<POSTAL_CODE>
* -e COUNTRY=<COUNTRY>
* -e EMAIL=<ELECTRONIC_MAIL_ADDRESS>

Here is an example of how to use the environmental variables to set metadata when starting a container:

::

    sudo docker run -d -p 80:8080 -e USERNAME="foo" -e PASSWORD="bar" -e NAME="Roger" -e COUNTRY="USA"  --restart=always --name n52wps ciwater/n52wps

More information about the 52 North WPS Docker can be found on the Docker Registry:

`<https://hub.docker.com/r/ciwater/n52wps>`_

.. important::

    Set strong passwords for the admin user for a production system.

Maintaining Docker Containers
=============================

This section briefly describes some of the common maintenance tasks for Docker containers. Refer to the `Docker Documentation <https://docs.docker.com/>`_ for a full description of Docker.

Status
------

You can view the status of containers using the following commands:

::

    # Running containers
    sudo docker ps

    # All containers
    sudo docker ps -a

Start and Stop
--------------

Docker containers can be stopped and started using the names assigned to them. For example, to stop and start a Docker named "postgis":

::

    sudo docker stop postgis
    sudo docker start postgis

Attach to Container
-------------------

You can attach to running containers to give you a command prompt to the container. This is useful for checking logs or modifying configuration of the Docker manually. For example, to attach to a container named "postgis":

::

    sudo docker exec --rm -it postgis bash
