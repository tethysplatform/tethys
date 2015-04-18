*************************
Distributed Configuration
*************************

**Last Updated:** April 18, 2015

Tethys Platform is composed of several software components, each of which draw on quite a bit of computing resources. We strongly recommend distributing the software components across several servers to optimize the use of computing resources and improve performance. Specifically, we recommend having a separate server for each of the following components:

* Tethys Portal
* PostgreSQL with PostGIS
* GeoServer
* 52 North WPS

**INSERT FIGURE HERE SHOWING A TETHYS STACK**

Fortunately, the Tethys Docker images make installing the software components on separate machines fairly straight forward. However, you will not be able to use the Tethys commandline tools to install the Dockers as you did during development. The following article describes how to deploy each software component using the native Docker API.

Install Docker on Each Server
=============================

The first step is to provision a server for the PostgreSQL, GeoServer, and 52 North WPS components and install Docker on each using the appropriate `Docker installation instructions <http://docs.docker.com/installation/>`_. Docker provides installation instructions for most major types of servers.

GeoServer Docker Deployment
===========================

Pull the Docker image for GeoServer using the following command:

::

    $ sudo docker pull ciwater/geoserver

After the image has been pulled, run a new Docker container as follows:

::

    $ sudo docker run -d -p 80:8080 --restart=always --name geoserver ciwater/geoserver

Refer to the `Docker Run Reference <https://docs.docker.com/reference/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name.

More information about the GeoServer Docker can be found on the Docker Registry:

`<https://registry.hub.docker.com/u/ciwater/geoserver/>`_

.. important::

    The admin username and password can only be changed using the web admin interface. Be sure to log into GeoServer and change the admin password using the web interface. The default username and password are *admin* and *geoserver*, respectively.

Backup
------



PostgreSQL with PostGIS Docker Deployment
=========================================

Pull the Docker image for PostgreSQL with PostGIS using the following command:

::

    $ sudo docker pull ciwater/postgis

The PostgreSQL with PostGIS Docker automatically initializes with the three database users that are needed for Tethys Platform:

* tethys_default
* tethys_db_manager
* tethys_super

The default password for each is “pass”. For production, you will obviously want to change these passwords. Do so using the appropriate environmental variable:

* -e TETHYS_DEFAULT_PASS=<TETHYS_DEFAULT_PASS>
* -e TETHYS_DB_MANAGER_PASS=<TETHYS_DB_MANAGER_PASS>
* -e TETHYS_SUPER_PASS=<TETHYS_SUPER_PASS>

Here is an example of how to use the environmental variables to set passwords when starting a container:

::

    $ sudo docker run -d -p 80:5432 -e TETHYS_DEFAULT_PASS="pass" -e TETHYS_DB_MANAGER_PASS="pass" -e TETHYS_SUPER_PASS="pass" --restart=always --name postgis ciwater/postgis

Refer to the `Docker Run Reference <https://docs.docker.com/reference/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name. It also set the passwords for each database at startup.

More information about the PostgreSQL with PostGIS Docker can be found on the Docker Registry:

`<https://registry.hub.docker.com/u/ciwater/postgis/>`_

.. important::

    Set strong passwords for each database user for a production system.

Backup
------


52 North WPS Docker Deployment
==============================

Pull the Docker image for 52 North WPS using the following command:

::

    $ sudo docker pull ciwater/n52wps

After the image has been pulled, run a new Docker container as follows:

::

    $ sudo docker run -d -p 80:8080 -e USERNAME="foo" -e PASSWORD="bar" --restart=always --name n52wps ciwater/n52wps


Refer to the `Docker Run Reference <https://docs.docker.com/reference/run/>`_ for an explanation of each parameter. To summarize, this will start the container as a background process on port 80, with the restart policy set to always restart the container after a system reboot, and with an appropriate name. It also sets the username and password for the admin user.

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

    $ sudo docker run -d -p 80:8080 -e USERNAME="foo" -e PASSWORD="bar" -e NAME="Roger" -e COUNTRY="USA"  --restart=always --name n52wps ciwater/n52wps

More information about the 52 North WPS Docker can be found on the Docker Registry:

`<https://registry.hub.docker.com/u/ciwater/n52wps/>`_

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
    $ sudo docker ps

    # All containers
    $ sudo docker ps -a

Start and Stop
--------------

Docker containers can be stopped and started using the names assigned to them. For example, to stop and start a Docker named "postgis":

::

    $ sudo docker stop postgis
    $ sudo docker start postgis

Attach to Container
-------------------

You can attach to running containers to give you a command prompt to the container. This is useful for checking logs or modifying configuration of the Docker manually. For example, to attach to a container named "postgis":

::

    $ sudo docker exec --rm -it postgis bash
