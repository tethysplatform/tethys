************
Installation
************

**Last Updated:** November 17, 2014

This section describes how to install Tethys Platform. These installation instructions are optimized for Ubuntu 14.04, which is the recommended platform for running Tethys Platform. However, Tethys Platform is cross platform and could be installed on other platforms with some adaptation.

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Install the Dependencies
---------------------------

a. If you are using a :term:`Debian` based Linux operating system (like Ubuntu), you can install most of the dependencies via :command:`apt-get`. Open a terminal and execute the following command:

  ::

      $ sudo apt-get install python-dev postgresql-9.3 libpq-dev postgresql-9.3-postgis-2.1 python-pip python-virtualenv git-core

  You may be prompted to enter your password to authorize the installation of these packages. If you are prompted about the disk space that will be used to install the dependencies, enter :kbd:`Y` and press :kbd:`Enter` to continue.

  There will be a lot of text printed to the terminal as the dependencies are installed and it may take several minutes to complete. When it is finished you will see a normal terminal cursor again.

b. If you not using a :term:`Debian` based Linux operating system find the best way to install the following dependencies for your operating system:

  ==================  ====================================================================================================
  Dependency          Description
  ==================  ====================================================================================================
  Python              `Python Programming Language, version 2.7. <https://www.python.org/download/releases/2.7/>`_
  PostgreSQL          `PostgreSQL database system, version 9.0 or higher (9.3 recommended). <http://www.postgresql.org/download/>`_
  PostGIS 2.1         `PostGIS spatial extension for PostgreSQL, version 2.1 or higher. <http://postgis.net/install>`_
  GeoServer*          `GeoServer server for sharing geospatial data. <http://docs.geoserver.org/stable/en/user/installation/index.html>`_
  Tomcat*             `Tomcat open source Java Servlet, version 7.0. <http://tomcat.apache.org/download-70.cgi>`_
  52°North WPS*       `52°North open source web processing service for geoprocessing. <http://52north.org/communities/geoprocessing/wps/installation.html>`_
  GRASS GIS*          `GRASS GIS, version 7. <http://grass.osgeo.org/download/>`_
  wps-grass-bridge*   `Libraries and applications for easy and convenient GRASS7 GIS WPS integration. <https://code.google.com/p/wps-grass-bridge/>`_
  pip                 `Python package management and installation tool. <http://pip.readthedocs.org/en/latest/installing.html>`_
  virtualenv          `virtualenv isolated Python environment creator. <http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation>`_
  git                 `Git open source distributed version control system. <http://git-scm.com/downloads>`_
  ==================  ====================================================================================================

  \* Note: The feature requiring this software is not fully implemented at this time, so installation of this dependency is optional.

2. Install Advanced Dependencies
--------------------------------

Installing some of the software dependencies is more involved. This section provides a more detailed explanation for these dependencies.

CKAN (optional)
===============

Apps developed with Tethys Platform may use CKAN for dataset storage. This is done using the REST API of CKAN, which means that the CKAN instance can be external to your Tethys Platform installation. For example, you may wish to configure your Tethys Platform to use `data.gov <http://www.data.gov/>`_ or some other CKAN installation (see `CKAN instances around the world <http://ckan.org/instances/#>`_).

If you wish to install your own instance of CKAN, refer to `Installing CKAN <http://docs.ckan.org/en/latest/maintaining/installing/index.html>`_.

3. Create Virtual Environment and Install Tethys Platform
---------------------------------------------------------

Python virtual environments are used to create isolated Python installations to avoid conflicts with dependencies of other Python applications on the same system. The following commands should be executed in a a terminal.

a. Create a :term:`Python virtual environment` and activate it::

    $ sudo mkdir -p /usr/lib/tethys
    $ sudo chown `whoami` /usr/lib/tethys
    $ virtualenv --no-site-packages /usr/lib/tethys
    $ . /usr/lib/tethys/bin/activate


.. important::

    The final command above activates the Python virtual environment for Tethys. You will know the virtual environment is active, because the name of it will appear in parenthesis in front of your terminal cursor::

        (tethys) $ _

    The Tethys virtual environment must remain active for the entire installation. If you need to logout or close the terminal in the middle of the installation, you will need to reactivate the virtual environment. This can be done at anytime by executing the following command (don't forget the dot)::

        $ . /usr/lib/tethys/bin/activate

b. Install Tethys Platform into the virtual environment with the following commands::

    $ git clone https://github.com/CI-WATER/tethys /usr/lib/tethys/src


c. Install the Python modules that Tethys requires::

    $ pip install -r /usr/lib/tethys/src/requirements.txt

d. Restart the Python virtual environment::

    $ deactivate
    $ . /usr/lib/tethys/bin/activate

4. Create Database and Database Users
-------------------------------------

Create three database users and databases. You will be prompted to create passwords for each user. Take note of the passwords, because you will need to use them in the next step. To do so, run the following commands in the terminal::

    $ sudo -u postgres createuser -S -D -R -P tethys_default
    $ sudo -u postgres createdb -O tethys_default tethys_default -E utf-8

    $ sudo -u postgres createuser -S -d -R -P tethys_db_manager
    $ sudo -u postgres createdb -O tethys_db_manager tethys_db_manager -E utf-8

    $ sudo -u postgres createuser --superuser -d -R -P tethys_super
    $ sudo -u postgres createdb -O tethys_super tethys_super -E utf-8


.. important::
    Run each line above one at a time to avoid errors.

.. tip::

    If you would like to have access to the Tethys databases through a graphical user interface such as `PGAdmin III <http://www.pgadmin.org/>`_, use the **tethys_super** database user and password as credentials for the connection. See the :doc:`./supplementary/pgadmin` article for more information.

5. Create Settings File and Configure Settings
----------------------------------------------

Create a new settings file for your Tethys Platform installation using the :command:`tethys` commandline utility. Execute the following command in the terminal::

    $ tethys gen settings -d /usr/lib/tethys/src/tethys_portal

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_portal`. As the name suggests, the :file:`settings.py` file contains all of the settings for the Tethys Platform Django project. There are a few settings that need to be configured in this file.

.. note::

    The :file:`usr` directory is located in the root directory which can be accessed using a file browser and selecting :file:`Computer` from the menu on the left.

Open the :file:`settings.py` file that you just created (:file:`/usr/lib/tethys/src/tethys_portal/settings.py`) in a text editor and modify the following settings appropriately.

a. Replace the password for the main Tethys Portal database, **tethys_default**, with the password you created in the previous step. This is done by changing the value of the PASSWORD parameter of the DATABASES setting::

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

b. Find the TETHYS_APPS_DATABASE_MANAGER_URL and TETHYS_APPS_SUPERUSER_URL settings near the bottom of the file and replace "pass" with the appropriate passwords that you created in the previous step::

    TETHYS_APPS_DATABASE_MANAGER_URL = 'postgresql://tethys_db_manager:pass@localhost:5432/tethys_db_manager'
    TETHYS_APPS_SUPERUSER_URL = 'postgresql://tethys_super:pass@localhost:5432/tethys_super'

c. Set the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY with an appropriate Google Maps v3 API key. If you do not have a Google Maps API key, use the `Obtaining an API Key <https://developers.google.com/maps/documentation/javascript/tutorial#api_key>`_ instructions::

    TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY = 'Th|$I$@neXAmpL3aPik3Y'

d. If you wish to configure a sitewide dataset service (CKAN or HydroShare), add the TETHYS_DATASET_SERVICES dictionary with the appropriate parameters. See the :doc:`./tethys_sdk/dataset_services` documentation for more details. For example::

    TETHYS_DATASET_SERVICES = {
        'ckan_example': {
            'ENGINE': 'tethys_datasets.engines.CkanDatasetEngine',
            'ENDPOINT': 'http:/www.exampleckan.org/api/3/action',
            'APIKEY': 'putYOURapiKEYhere',
        },
        'example_hydroshare': {
            'ENGINE': 'tethys_datasets.engines.HydroShareDatasetEngine',
            'ENDPOINT': 'http://www.hydroshare.org/api',
            'USERNAME': 'someuser',
            'PASSWORD': 'password',
        }
    }

e. Save your changes and close the :file:`settings.py` file.

6. Create Database Tables
-------------------------

Execute the Django :command:`syncdb` command to create the database tables. In the terminal::

    $ tethys manage syncdb

.. important::

  When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the user you use to manage your Tethys Portal.

7. Start up the Django Development Server
-----------------------------------------

You are now ready to start the Django development server and view your instance of Tethys Portal. In the terminal, execute the following command::

    $ tethys manage start

Open `<http://127.0.0.1:8000/>`_ in a new tab in your web browser and you should see the default Tethys Portal landing page. Feel free to log in using the system administrator username and password that you created in the previous step and take a look around.

.. figure:: ./images/tethys_portal_landing.png
    :width: 650px


What's Next?
------------

Head over to :doc:`./getting_started` and create your first app. You can also check out the :doc:`./tethys_sdk` documentation to familiarize yourself with all the features that are available.









