.. _production_overview:

********
Overview
********

**Last Updated:** September 2024

Introduction
============

The purpose of this section of the guide is to provide background information on important aspects of the production installation of Tethys Portal. Every production installation is different due to the different requirements imposed by the apps that are installed. This section will help you to learn about the different components and how they work together.

It is also important to understand that this guide provides instructions only for the minimal installation and configuration that is required and most installations will require modification. Taking time upfront to understand the different components, why they are needed, and where the important files are stored will save you time when you are debugging issues with the installation later on.

System Requirements
===================

System requirements for your Tethys Portal will largely depend on the apps that are installed on the server and the software dependencies of the apps (PostGIS database, GeoServer, etc.) We recommend the following *minimum* requirements for a single-server setup with Tethys Portal and PostgreSQL database installed.

* Processor: 4 CPU Cores @ 2 GHz+ each
* RAM: 4 GB
* Hard Disk: 100 GB

Operating System
================

This guide provides instructions for installing Tethys Portal for production on Ubuntu 24.04 and Rocky Linux 9 servers. Installation instructions on other Linux distributions will be similar.

Production Server
=================

Tethys Portal is a Django web application with the `Django Channels app <https://channels.readthedocs.io/en/latest/>`_ installed, which makes it an `Asynchronous Server Gateway Interface (ASGI) <https://asgi.readthedocs.io/en/latest/>`_ application. As such, it requires an ASGI server to host it.

In this guide you will host Tethys Portal using the `Daphne <https://github.com/django/daphne>`_ ASGI server with `NGINX <https://docs.nginx.com>`_ acting as the primary HTTP server (see: `Example Setups <https://channels.readthedocs.io/en/latest/deploying.html#example-setups>`_). Alternatively, the `Apache <https://httpd.apache.org/>`_ server can also be used as the primary HTTP server. All incoming HTTP traffic will be handled by the HTTP server which will route most of it to Daphne. Daphne in turn will be hosting the Tethys Portal. The response will be returned up the chain through Daphne to NGINX and back to the client. The HTTP server will handle requests for static files directly for efficiency.

.. figure:: ./images/tethys_production_diagram.png
    :width: 800px
    :align: center

Daphne can and should be configured to run multiple processes or workers. The default configuration will create four (4) Daphne processes for example. To make managing the Daphne processes and HTTP server process more manageable, `Supervisor <https://supervisord.org/>`_ will be used to allow all five processes to be started, stopped, and restarted with a single command.

NGINX
-----

A high-performance HTTP server and reverse proxy. It is know for it's rich feature set and simple configuration. NGINX is used in the Tethys Portal production installation as the primary HTTP server. It serves the static files directly and routes other traffic to the Daphne server.

Apache
------

A popular HTTP server and reverse proxy. It is known for it's flexibility and power. Apache can be used as the primary HTTP server in the Tethys Portal production installation. It serves the static files directly and routes other traffic to the Daphne server.

Daphne
------

An ASGI server for hosting Django Channels web applications, of which Tethys Portal is one. Daphne is used in the Tethys Portal production installation to host Tethys Portal, which is an ASGI application.

Supervisor
----------

An orchestrator or process control system. It is used in the Tethys Portal production installation to more easily manage the NGINX and Daphne server processes.

File Organization
=================

The files for a production Tethys Portal are stored in several different locations on the file system. The following general guidelines may help:

* Configuration files are stored in ``TETHYS_HOME`` and linked to :file:`/etc`
* Static Files and Data Files are stored in :file:`/var/www/tethys`
* Logs are located in the :file:`/var/log`

Configuration Files
-------------------

All configuration files are stored in ``TETHYS_HOME``. The default location of ``TETHYS_HOME`` is :file:`~/.tethys`. Files that will be located here include:

* :file:`portal_config.yml`
* :file:`asgi_supervisord.conf`
* :file:`nginx_supervisord.conf`
* :file:`tethys_nginx.conf`

The NGINX and Supervisor configuration files are symbolically linked to the appropriate location in :file:`/etc` (see: :ref:`production_system_configuration`).

.. note::

    There is no :file:`daphne.conf`. The Daphne configuration is contained in the :file:`asgi_supervisord.conf` file in the from of arguments to the ``daphne`` command.

.. _production_system_configuration:

System Configuration
--------------------

Most system configuration files are located in :file:`/etc` including the configuration files for NGINX and Supervisor. The NGINX and Supervisor files in ``TETHYS_HOME`` are symbolically linked to these locations:

**Ubuntu**:

* :file:`/etc/supervisor/conf.d/asgi_supervisord.conf`
* :file:`/etc/supervisor/conf.d/nginx_supervisord.conf`
* :file:`/etc/nginx/sites-enabled/tethys_nginx.conf`

**Rocky Linux**:

* :file:`/etc/supervisord.d/asgi_supervisord.conf`
* :file:`/etc/supervisord.d/nginx_supervisord.conf`
* :file:`/etc/nginx/conf.d/tethys_nginx.conf`

Data Files
----------

The data files include files generated by apps or users (workspaces and media files) and the static files (JavaScript, CSS, Images). These files are located in the ``STATIC_ROOT``, ``MEDIA_ROOT``, and ``TETHYS_WORKSPACES_ROOT`` directories, respectively. The recommend locations for these directories are:

* ``STATIC_ROOT``: :file:`/var/www/tethys/static`
* ``MEDIA_ROOT``: :file:`/var/www/tethys/media`
* ``TETHYS_WORKSPACES_ROOT``: :file:`/var/www/tethys/workspaces`

.. note::

    The directory :file:`/var/www` is usually the home directory of the ``NGINX_USER``.


Logs
----

Logs for all of the various applications, including Tethys, can be found in :file:`/var/log`. The following logs are those that you will likely be most interested in:

* :file:`/var/log/tethys/tethys.log`
* :file:`/var/log/nginx/error.log`
* :file:`/var/log/nginx/access.log`
* :file:`/var/log/supervisor/supervisor.log`

Database
--------

The data files *and* configuration files for a system-installed PostgreSQL are located in the same directory:

**Ubuntu**:

* :file:`/var/lib/postgresql/<version>/main`

**Rocky Linux**:

* :file:`/var/lib/pgsql/<version>/data`
