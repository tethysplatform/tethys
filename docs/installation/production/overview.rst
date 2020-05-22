.. _production_overview:

********
Overview
********

**Last Updated:** May 2020

System Requirements
===================

System requirements for your Tethys Portal will largely depend on the apps that are installed on the server and the software dependencies of the apps (PostGIS database, GeoServer, etc.) We recommend the following *minimum* requirements for a single-server setup with Tethys Portal and PostgreSQL database installed.

* Processor: 4 CPU Cores @ 2 GHz+ each
* RAM: 4 GB
* Hard Disk: 100 GB

Operating System Differences
============================

* Debian / Ubuntu
* CentOS / RedHat

Servers
=======

NGINX
-----

Daphne
------

Orchestrator
============

Supervisor
----------

File Organization
=================

Tethys Configuration Files
--------------------------

* TETHYS_HOME: ~/.tethys

Tethys Files
------------

* STATIC_ROOT: /var/www/tethys/static
* TETHYS_WORKSPACE_ROOT: /var/www/tethys/workspaces

Database
--------

* Configuration
* Data

System Software Configuration
-----------------------------

* NGINX
* Daphne
* Supervisor

Logs
----

* /var/log



