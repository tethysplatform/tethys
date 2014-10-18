******************************
Docker Development Environment
******************************

**Last Updated:** May 30, 2014

This method make use of the `Docker virtualization container <https://www.docker.io/>`_ system. A pair of Docker container images have been prepared with a full installation of the Tethys Apps development environment. At this time, an Ubuntu installation is still required to use this method. Follow the :ref:`install_ubuntu` instructions to setup Ubuntu. Then follow the instructions below to install Docker and the Tethys development environment containers. After Ubuntu is installed, plan on about 10-15 minutes to get the development environment setup. This method is the next fastest way to get setup if you do not have VMWare.

There are two Docker containers that are needed to deploy the Tethys development environment: ``tethys_dev`` and ``tethys_dev_data``. The ``tethys_dev`` container is comprised of CKAN with all the plugins for Tethys Apps installed to provide a development environment for Tethys app development. The ``tethys_dev_data`` container houses all of the data dependencies for the Tethys Apps development environment (postgresql, filestore, datastore, solr, and tethys apps databases). This allows user data, app data, and datasets to be persisted when the ``tethys_dev`` container is updated.

Install Docker
==============

Start up your Ubuntu computer and follow the instructions on for `Installing Docker on Ubuntu <http://docs.docker.io/installation/ubuntulinux/>`_ to install Docker. Be sure to follow the instructions for the version of Ubuntu that you are using.

Pull Docker Images
==================

Pull the ``tethys_dev`` and ``tethys_dev_data`` images from the Docker Public Repository. In a terminal:

::

    $ sudo docker pull ciwater/tethys_dev
    $ sudo docker pull ciwater/tethys_dev_data

Confirm that this worked by executing the following command:

::

    $ sudo docker images

You should see the ``tethys_dev`` and ``tethys_dev_data`` images listed in the print out.

.. _create_docker_containers:

Create Containers
=================

After you have pulled the Docker images, you will need to use the Docker :command:`run` command to create the containers:

::

    $ sudo docker run -d -p 5555:5432 -p 8080:8080 --name tethys_dev_data ciwater/tethys_dev_data
    $ sudo docker run -i -t -p 5000:5000 --link tethys_dev_data:data --volumes-from tethys_dev_data -v <apps_working_directory>:/usr/lib/ckan/apps_projects:rw --name tethys_dev ciwater/tethys_dev

Replace **<apps_working_directory>** with the directory where you will create your app projects. The ``tethys_dev`` Docker will automatically install and load any app in this directory.

The Docker container instances are assigned names that match their image names to make them more covenient to work with ("tethys_dev_data" for the ``tethys_data_dev`` container and "tethys_dev" for the ``tethys_dev`` container). When you run the ``tethys_dev`` container, it will print status output from the server that is running CKAN to the terminal.

After you have created the containers, stop them. Stop the ``tethys_dev`` container by using the key combination :kbd:`ctrl-C` in the terminal where it is running. The ``tethys_dev_data`` container can be stopped using the following command:

::

    $ sudo docker stop tethys_dev_data
    
Check to make sure both containers were created correctly with the following command:

::

    $ sudo docker ps -a
    
This will list all of the Docker containers that are available for running. You should see two Docker containers with the names "tethys_dev" and "tethys_dev_data". Notice that the "tethys_dev_data" container has a second name: "tethys_dev/data" This is because these containers are linked. Remember that "tethys_dev_data" must be started before "tethys_dev", because they are linked.

Start and Stop Containers
=========================

After the containers have been created the first time, they can be started everytime after that using the following commands:

::

    $ sudo docker start tethys_dev_data
    $ sudo docker start -a -i tethys_dev

NOTE: The containers must be started in this order. The ``tethys_dev`` container depends on the ``tethys_dev_data`` container running.

The "a" and "i" options allow you to see the output from the server that is running CKAN and Tethys apps. This is useful for debugging. To stop the ``tethys_dev`` container, use the key combination :kbd:`ctrl-C` as before. Both containers can be stopped in another terminal using:

::

    $ sudo docker stop tethys_dev_data
    $ sudo docker stop tethys_dev

Create New App Projects
=======================

New app projects can be created using the Tethys app scaffold by issuing the following command:

::

    $ sudo docker run --rm -i -t -v <apps_working_directory>:/usr/lib/ckan/apps_projects:rw ciwater/tethys_dev ./createapp <app_name>

Replace **<apps_working_directory>** with the path to the directory where you will work on your apps projects (same as in the :ref:`create_docker_containers` section). Also, replace **<app_name>** with the name of the app that you would like to create. The app name must have "ckanapp-" as a prefix. The new app project will be created in the **<apps_working_directory>**.

Data Inspection
===============

You can inspect the CKAN and TETHYS database using a PostgreSQL client such as `PGAdminIII <http://askubuntu.com/questions/220123/how-do-i-install-pgadmin-iii-for-postgresql-9-2>`_. To do so, start the ``tethys_dev_data`` container and use the following credentials to connect:

::

    Host: localhost
    Port: 5555
    Username: tethys
    Password: pass
    Database: tethys

.. note::

    The *tethys* user is a superuser for the database.

The various data directories and log directories can be inspected by creating a new docker container that binds to the volumes of ``tethys_dev_data``:

::

    $ sudo docker run --rm -i -t --volumes-from tethys_dev_data ubuntu bash

Useful directories include:

::

    /var/lib/ckan/default    (FileStore data directory)
    /etc/solr/conf           (Solr configuration)
    /var/log/supervisor      (Solr/Jetty and PostgreSQL logs)

Tethys Development Client
=========================

There is a command line client available for working with the Tethys development environment. To install the client execute the following in a terminal:

::

    $ cd /tmp
    $ wget "https://bitbucket.org/swainn/tethys_docker/raw/83598c78c41d9fdad06b16f8793bed3ea361fe58/development/tethys_dev_client/tethysdc"
    $ chmod +x tethysdc
    $ sudo mv tethysdc /usr/local/bin

There are three commands that you can use with the Tethys development client: :command:`start`, :command:`stop`, and :command:`create`. Use the :command:`start` to start the Tethys development Docker containers:

::

    $ tethysdc start db
    $ tethysdc start tethys

Use the client to stop your Tethys development containers:

::

    $ tethysdc stop

.. note::

    To stop the ``tethys_dev`` while output is printing to the terminal, press :kbd:`ctrl-C` as before.

Use the client to create new apps using the :command:`create` command:

::

    $ tethysdc create <apps_working_directory> <app_name>

Replace **<apps_working_directory>** with the path to the directory with your Tethys app projects and replace **<app_name>** with the name of the app to be created. Follow the interactive prompts to set metadata about your app. The **<app_name>** must start with the "ckanapp-" prefix (e.g.: ckanapp-my_first_app). The new app project will be created in the **<apps_working_directory>**.

Build Docker Images from Source
===============================

You may want to build from source if you want the very latest version of the Tethys Apps plugin or if you are aiding in the development of the Tethys Apps Dockers.

1. Create working directory:

::

    $ mkdir ~/tethysdev

.. note::

    This directory can be located wherever you would like, but be sure to use your path in the following steps if you don't use the suggested directory.

2. Retrive the tethys_docker source repository:

::

    $ cd ~/tethysdev
    $ git clone https://swainn@bitbucket.org/swainn/tethys_docker.git

3. Build container images from docker files:

::

    $ cd ~/tethysdev/tethys_docker/development/tethys_dev_data
    $ sudo docker build -t ciwater/tethys_dev_data .
    $ cd ~/tethysdev/tethys_docker/development/tethys_dev
    $ sudo docker build -t ciwater/tethys_dev .

.. hint::

    Often the build will fail due connection problems during apt-get update. It may be necessary to run the Docker :command:`build` command **MANY** times before it finally succeeds.


