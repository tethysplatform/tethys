************
Installation
************

**Last Updated:** October 18, 2014

This section describes how to install Tethys Platform. These installation instructions are optimized for Ubuntu 14.04,
which is the recommended platform for running Tethys Platform. However, these instructions should work with other
types of Linux with some adaptation.

1. Install the Dependencies
---------------------------

If you are using a Debian-based operating system (like Ubuntu), you can install the dependencies as follows::

    sudo apt-get install python-dev postgresql-9.3 libpq-dev postgresql-9.3-postgis-2.1 python-pip python-virtualenv git-core

If you not using a Debian-based operating system find the best way to install the following dependencies for your
operating system:

==================  ====================================================================================================
Dependency          Description
==================  ====================================================================================================
Python              `Python Programming Language, version 2.7. <https://www.python.org/download/releases/2.7/>`_
PostgreSQL          `PostgreSQL database system, version 9.0 or higher (9.3 recommended). <http://www.postgresql.org/download/>`_
PostGIS 2.1         `PostGIS spatial extension for PostgreSQL, version 2.1 or higher. <http://postgis.net/install>`_
GeoServer           `GeoServer server for sharing geospatial data. <http://docs.geoserver.org/stable/en/user/installation/index.html>`_
Tomcat              `Tomcat open source Java Servlet, version 7.0. <http://tomcat.apache.org/download-70.cgi>`_
52°North WPS        `52°North open source web processing service for geoprocessing. <http://52north.org/communities/geoprocessing/wps/installation.html>`_
GRASS GIS           `GRASS GIS open source geospatial data management and analysis system, version 7. <http://grass.osgeo.org/download/>`_
CKAN                `CKAN open source data management system. <http://docs.ckan.org/en/latest/maintaining/installing/index.html>`_
wps-grass-bridge    `Libraries and applications for easy and convenient GRASS7 GIS WPS integration. <https://code.google.com/p/wps-grass-bridge/>`_
pip                 `Python package management and installation tool. <http://pip.readthedocs.org/en/latest/installing.html>`_
virtualenv          `virtualenv isolated Python environment creator. <http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation>`_
git                 `Git open source distributed version control system. <http://git-scm.com/downloads>`_
==================  ====================================================================================================

2. Configure Dependencies
-------------------------

TODO: Add stuff here.

* PostGIS environmental variables to enable GDAL drivers

3. Install Tethys Platform into a Python Virtual Environment
------------------------------------------------------------

Python virtual environments are used to create isolated Python installations to avoid conflicts with dependencies of
other Python applications on the same system. The following commands should be executed in a the Terminal.

a. Create a Python virtual environment and activate it::

    sudo mkdir -p /usr/lib/tethys
    sudo chown `whoami` /usr/lib/tethys
    virtualenv --no-site-packages /usr/lib/tethys
    . /usr/lib/tethys/bin/activate


.. important::

    The final command above activates the Python virtual environment for Tethys. You can tell if a virtual environment
    is active, because the name of it will appear in parenthesis in front of your terminal cursor::

        (tethys) $ _

    The Tethys virtual environment must remain active for the entire installation. If you need to logout or close the
    Terminal in the middle of the installation, you will need to reactivate the virtual environment. This can be done
    at anytime by executing the following command (don't forget the dot)::

        . /usr/lib/tethys/bin/activate

b. Install Tethys Platform into the virtual environment with the following commands::

    cd /usr/lib/tethys
    git clone https://github.com/swainn/tethys src


c. Install the Python modules that Tethys requires::

    pip install -r /usr/lib/tethys/src/tethys/requirements.txt

d. Restart the Python virtual environment::

    deactivate
    . /usr/lib/tethys/bin/activate

4. Create Database and Database Users
-------------------------------------

Create three database users with databases. You will be prompted to create passwords for each user. Take note of the
passwords, because you will need to use them in the next step.To do so, run the following commands in a Terminal::

    sudo -u postgres createuser -S -D -R -P tethys_default
    sudo -u postgres createdb -O tethys_default tethys_default -E utf-8

    sudo -u postgres createuser -S -d -R -P tethys_db_manager
    sudo -u postgres createdb -O tethys_db_manager tethys_db_manager -E utf-8

    sudo -u postgres createuser --superuser -d -R -P tethys_super
    sudo -u postgres createdb -O tethys_super tethys_super -E utf-8


.. tip::

    If you would like to have access to the Tethys databases through a graphical user interface such as PgAdminIII, use
    the **tethys_super** database user and password as credentials for the connection.

5. Create Settings File and Configure Settings
----------------------------------------------

Create a new settings file for your Tethys Platform installation. In the Terminal::

    cd /usr/lib/tethys/src/tethys_portal

