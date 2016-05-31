Tethys Platform
===============

Tethys Platform provides both a development environment and a hosting environment for water resources web apps.

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
GeoServer*          `GeoServer server for sharing geospatial data. <http://docs.geoserver.org/stable/en/user/installation/index.html>`_
Tomcat*             `Tomcat open source Java Servlet, version 7.0. <http://tomcat.apache.org/download-70.cgi>`_
52°North WPS*       `52°North open source web processing service for geoprocessing. <http://52north.org/communities/geoprocessing/wps/installation.html>`_
GRASS GIS*          `GRASS GIS open source geospatial data management and analysis system, version 7. <http://grass.osgeo.org/download/>`_
CKAN*               `CKAN open source data management system. <http://docs.ckan.org/en/latest/maintaining/installing/index.html>`_
wps-grass-bridge*   `Libraries and applications for easy and convenient GRASS7 GIS WPS integration. <https://code.google.com/p/wps-grass-bridge/>`_
pip                 `Python package management and installation tool. <http://pip.readthedocs.org/en/latest/installing.html>`_
virtualenv          `virtualenv isolated Python environment creator. <http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation>`_
git                 `Git open source distributed version control system. <http://git-scm.com/downloads>`_
==================  ====================================================================================================
* Note: The feature requiring this software is not fully implemented at this time and installation of this software is optional.

2. Configure Dependencies
-------------------------

* PostGIS environmental variables to enable GDAL drivers

3. Install Tethys Platform into a Python Virtual Environment
------------------------------------------------------------

Python virtual environments are used to create isolated Python installations to avoid conflicts with dependencies of
other Python applications on the same system. The following commands should be executed in a a terminal.

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
    terminal in the middle of the installation, you will need to reactivate the virtual environment. This can be done
    at anytime by executing the following command (don't forget the dot)::

        . /usr/lib/tethys/bin/activate

b. Install Tethys Platform into the virtual environment with the following commands::

    git clone https://github.com/CI-WATER/tethys /usr/lib/tethys/src


c. Install the Python modules that Tethys requires::

    pip install -r /usr/lib/tethys/src/requirements.txt

d. Restart the Python virtual environment::

    deactivate
    . /usr/lib/tethys/bin/activate

4. Create Database and Database Users
-------------------------------------

Create three database users with databases. You will be prompted to create passwords for each user. Take note of the
passwords, because you will need to use them in the next step.To do so, run the following commands in the terminal::

    sudo -u postgres createuser -S -D -R -P tethys_default
    sudo -u postgres createdb -O tethys_default tethys_default -E utf-8

    sudo -u postgres createuser -S -d -R -P tethys_db_manager
    sudo -u postgres createdb -O tethys_db_manager tethys_db_manager -E utf-8

    sudo -u postgres createuser --superuser -d -R -P tethys_super
    sudo -u postgres createdb -O tethys_super tethys_super -E utf-8


.. tip::

    If you would like to have access to the Tethys databases through a graphical user interface such as
    `pgAdmin III <http://www.pgadmin.org/>`_, use the **tethys_super** database user and password as credentials
    for the connection.

5. Create Settings File and Configure Settings
----------------------------------------------

Create a new settings file for your Tethys Platform installation using the :command:`tethys` commandline utility. In the
terminal::

    tethys gen settings -d /usr/lib/tethys/src/tethys_portal

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_portal`. As the
name suggests, the :file:`settings.py` file contains all of the settings for the Tethys Platform Django project. There
are a few settings that need to be configured in this file.

Open the :file:`settings.py` file (:file:`/usr/lib/tethys/src/tethys_portal/settings.py`) that you just created and modify the
following settings appropriately.

a. Replace the password for the main Tethys Portal database, **tethys_default**, with the password you created
in the previous step. This is done by changing the value of the PASSWORD parameter of the DATABASES setting::

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tethys_default',
        'USER': 'tethys_default',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': '5432'
        }
    }

b. Find the TETHYS_DATABASES setting and set with the appropriate passwords that you created in the previous step. Also set
the HOST and PORT if necessary::

    TETHYS_DATABASES = {
        'tethys_db_manager': {
            'NAME': 'tethys_db_manager',
            'USER': 'tethys_db_manager',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '5435'
        },
        'tethys_super': {
            'NAME': 'tethys_super',
            'USER': 'tethys_super',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '5435'
        }
    }

c. Set the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY with an appropriate Google Maps v3 API key. If you do not have a Google
Maps API key, use the `Obtaining an API Key <https://developers.google.com/maps/documentation/javascript/tutorial#api_key>`_
instructions::

    TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY = 'Th|$I$@neXAmpL3aPik3Y'

d. Save your changes and close the :file:`settings.py` file.

6. Create Database Tables
-------------------------

Execute the Django :command:`syncdb` command to create the database tables. You will be prompted to create a system
administrator for your Tethys Portal. Remember the username and password that you give it. In the terminal::

    python /usr/lib/tethys/src/manage.py syncdb

7. Start up the Django Development Server
-----------------------------------------

You are now ready to start the Django development server and view your instance of Tethys Portal. In the terminal::

    python /usr/lib/tethys/src/manage.py runserver

Open `<http://127.0.0.1:8000/>`_ in a web browser and you should see the default Tethys Portal landing page. Feel free to
login using the system administrator username and password and take a look around.
