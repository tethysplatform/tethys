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

    sudo mkdir -p /usr/lib/tethys/src
    sudo chown `whoami` /usr/lib/tethys/src
    cd /usr/lib/tethys/src
    git clone https://github.com/swainn/tethys


c. Install the Python modules that Tethys requires::

    pip install -r /usr/lib/tethys/src/tethys/requirements.txt

d. Restart the Python virtual environment::

    deactivate
    . /usr/lib/tethys/bin/activate




1. Download Source
==================

Download the source for the CKAN Apps plugin using git. In a terminal execute the following commands::

	$ mkdir ~/tethysdev
	$ cd ~/tethysdev
	$ git clone https://swainn@bitbucket.org/swainn/ckanext-tethys_apps.git

.. hint::

	The "~" (tilde) character is a shortcut to the home directory in a unix terminal. Thus, :file:`~/tethysdev` refers to a directory called "tethysdev" in the home directory.


2. Install into Python
======================

Activate your CKAN Python virtual environment, change into the :file:`ckanext-tethys_apps` directory, and run the setup script. If you have used the defaults for installing CKAN, this can be done like so::

	$ . /usr/lib/ckan/default/bin/activate
	$ cd ~/tethysdev/ckanext-tethys_apps
	$ python setup.py install

.. caution::

	Don't forget the "." operator when activating your Python environment. This is needed to execute the :file:`activate` script.

3. Modify CKAN Configuration
============================

Add the term "tethys_apps" to the **ckan.plugins** parameter of your CKAN configuration (e.g.: :file:`/etc/ckan/default/development.ini`). The parameter should look similar to this when your done:

::

    ckan.plugins = tethys_apps

.. note::
    
    Depending on the different plugins that are enabled for your CKAN installation, the **ckan.plugins** parameters may have several other plugin names listed with "tethys_apps". This is ok.

4. Copy the Source Directory
============================

Copy the :file:`tethys_apps` directory from the source into the :file:`ckanext` directory of the CKAN source. This can be done like so::

	$ cp ~/tethysdev/ckanext-tethys_apps/ckanext/tethys_apps /usr/lib/ckan/src/ckan/ckanext/


5. Create Database Users
========================

Create a database user and database for Tethys Apps. The plugin needs it's own database user to assist with the automatic database provisioning feature. Create the user and give it a password using hte interactive prompt. You will need to remember this password for the next step.

::

    $ sudo -u postgres createuser -S -d -R -P tethys_db_manager
    $ sudo -u postgres createdb -O tethys_db_manager tethys_db_manager -E utf-8
    
Next, create a database superuser for Tethys and it's associtated database. Remember the password that you assign to this user for the next step.

::

    $ sudo -u postgres createuser --superuser -d -R -P tethys_super
    $ sudo -u postgres createdb -O tethys_super tethys_super -E utf-8



6. Modify the Tethys Apps Config
================================

Open the Tethys Apps configuration file (:file:`/usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/tethys_apps.ini`) and edit the ``tethys.database_manager_url`` and ``tethys.superuser_url`` parameters so that the username, password, host, port, and database match the databases and users that you created in the last step. The url uses the following pattern:

::

    postgresql://<username>:<password>@<host>:<port>/<database>

The ``tethys.database_manager_url``  and ``tethys.superuser_url`` parameters should look something like this when you are done:

::
    
    tethys.database_manager_url = postgresql://tethys_db_manager:pass@localhost:5432/tethys_db_manager
    tethys.superuser_url = postgresql://tethys_super:pass@localhost:5432/tethys_super

Next, make sure the ``tethys.ckanapp_directory`` parameter is set to the path to your :file:`ckanapp` directory. For a default installation of CKAN and Tethys Apps, this will be at :file:`/usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/ckanapp`. This parameter should look similar to this when you are done:

::

    tethys.ckanapp_directory = /usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/ckanapp

.. hint::

    Do **NOT** use double or single quotes for the url or directory parameters in the Tethys configuration file.



7. Start CKAN
=============

Deactivate and reactivate your CKAN Python virtual environment and start up the Paster server:

::

    $ deactivate
    $ . /usr/lib/ckan/default/bin/activate
    $ paster serve /etc/ckan/default/development.ini

.. note::

    If your virtual environment was already deactivated the :command:`deactivate` command will fail. This is ok. Just activate your virtual environment and start paster server.

Navigate to your CKAN page in a web browser (likely at http://localhost:5000). Installation has been successful if the :guilabel:`Apps` link appears in the header of your CKAN page.


Working With Tethys Under Development
=====================================

The Tethys Apps plugin is currently under heavy development. It is likely that you will want to pull the latest changes frequently until a stable version is released. To prevent the need to reinstall the app everytime you pull changes, you will need to use the following modifications when installing the Tethys Apps plugin:

Use the :command:`develop` command instead of the :command:`install` command  when running the setup script. This creates a link between the Tethys Apps source and Python instead of hard copying it. This will allow any changes you pull to be propegated without reinstalling the plugin.

::

	$ . /usr/lib/ckan/default/bin/activate
	$ cd ~/tethysdev/ckanext-tethys_apps
	$ python setup.py develop

Create a symbolic link between :file:`tethys_apps` and :file:`ckanext`, rather than copying for the same reasons as above::

	$ ln -s ~/tethysdev/ckanext-tethys_apps/ckanext/tethys_apps /usr/lib/ckan/default/src/ckan/ckanext/tethys_apps

Pull Latest Changes
-------------------

Changes can be pulled from the git repository like so::

$ cd ~/tethysdev/ckanext-tethys_apps
$ git pull
