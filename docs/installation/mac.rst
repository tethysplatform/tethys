***********************
Installation on Mac OSX
***********************

**Last Updated:** January 12, 2015

.. warning::

   UNDER CONSTRUCTION

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Install the Dependencies
---------------------------

a. Open a terminal and execute the following command to install the `Homebrew <http://brew.sh/>`_ package manager:

  ::

      $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

  Open your .bash_profile file:

  ::

      $ open ~/.bash_profile

  Add the following lines to the bottom of the file:

  ::

      # Homebrew Path
      export PATH=/usr/local/bin:/usr/local/sbin:$PATH

  Save your changes and close the file.

  .. note::

      You may need to close the terminal and open it again for these changes to take effect.

b. Use Homebrew to install the dependencies:

  ::

      $ brew install python
      $ brew link --overwrite python

  Homebrew will automatically install pip and virtualenv with the Python installation.

c. Install *git* and other dependencies with Homebrew:

  ::

      $ brew install git libpqxx libxml2 libxslt

d. Install Docker using the `Installing Docker on Mac OSX <https://docs.docker.com/installation/mac/#installation>`_ instructions.


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

b. Install Tethys Platform into the virtual environment with the following command::

    $ git clone https://github.com/CI-WATER/tethys /usr/lib/tethys/src


c. Install the Python modules that Tethys requires::

    $ pip install -r /usr/lib/tethys/src/requirements.txt

d. Restart the Python virtual environment::

    $ deactivate
    $ . /usr/lib/tethys/bin/activate


4. Install Tethys Software Suite Using Docker
---------------------------------------------

Tethys Platform provides a software suite that addresses the unique needs of water resources web app development including:

* PostgreSQL with PostGIS enabled for spatial database storage,
* 52 North WPS with GRASS and Sextante enabled for geoprocessing services, and
* GeoServer for spatial dataset publishing.

Installing some of these dependencies can be VERY difficult, so they have been provided as Docker containers to make installation easier. The following instructions will walk you through installation of these software using Docker. See the `Docker Documentation <https://docs.docker.com/>`_ for more information about Docker.


Initialize the Docker Containers
================================

Tethys provides set of commandline tools to help you manage the Docker containers. You must activate your Python environment to use the commandline tools. Execute the following Tethys commands using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli` to initialize the Docker containers:

::

  $ tethys docker init

The first time you initialize the Docker containers, the images for each container will be downloaded. These images are large and it may take a long time for them to download.

After the images have been downloaded, the containers will automatically be installed. During installation, you will be prompted to enter various parameters needed to customize your instance of the software. Some of the parameters are usernames and passwords. **Take note of the usernames and passwords that you specify**. The important ones to remember are listed here:

Database Users for PostGIS Container:

* **tethys_default** database user password
* **tethys_db_manager** database user password
* **tethys_super** database user password

52 North WPS Admin:

* Admin username
* Admin password

You will need these to complete the installation.

Start the Docker Containers
===========================

Use the following Tethys command to start the Docker containers:

::

  $ tethys docker start

.. note::

  Although each Docker container appears to start instantaneously, it may take several minutes for the started containers to be fully up and running.


What is Running
===============

After you run the `tethys docker start` command, you will have running instances of the following software:

* PostgreSQL with PostGIS
* 52 North WPS
* GeoServer

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.

5. Create Settings File and Configure Settings
----------------------------------------------

In the next steps you will configure your Tethys Platform and link it to each of the software in the software suite. Create a new settings file for your Tethys Platform installation using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli`. Execute the following command in the terminal::

    $ tethys gen settings -d /usr/lib/tethys/src/tethys_portal

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_portal`. As the name suggests, the :file:`settings.py` file contains all of the settings for the Tethys Platform. There are a few settings that need to be configured in this file.

.. note::

    The :file:`usr` directory is located in the root directory which can be accessed using a file browser and selecting :file:`Computer` from the menu on the left.

Open the :file:`settings.py` file that you just created (:file:`/usr/lib/tethys/src/tethys_portal/settings.py`) in a text editor and modify the following settings appropriately.

a. Run the following command to obtain the host and port for Docker running the database (PostGIS). You will need these in the following steps:

  ::

    $ tethys docker ip

b. Replace the password for the main Tethys Portal database, **tethys_default**, with the password you created in the previous step. Also make sure that the host and port match those given from the ``tethys docker ip`` command (PostGIS). This is done by changing the values of the PASSWORD, HOST, and PORT parameters of the DATABASES setting:

  ::

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

c. Find the TETHYS_DATABASES setting near the bottom of the file and set the PASSWORD parameters with the passwords that you created in the previous step. If necessary, also change the HOST and PORT to match the host and port given by the ``tethys docker ip`` command for the database (PostGIS)::

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

d. Set the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY with an appropriate Google Maps v3 API key. If you do not have a Google Maps API key, use the `Obtaining an API Key <https://developers.google.com/maps/documentation/javascript/tutorial#api_key>`_ instructions::

    TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY = 'Th|$I$@neXAmpL3aPik3Y'

e. If you wish to configure a sitewide dataset service (CKAN or HydroShare), add the TETHYS_DATASET_SERVICES dictionary with the appropriate parameters. See the :doc:`../tethys_sdk/dataset_services` documentation for more details. For example::

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

Execute the :command:`tethys manage syncdb` command from the Tethys :doc:`../tethys_sdk/tethys_cli` to create the database tables. In the terminal::

    $ tethys manage syncdb

.. important::

  When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the user you use to manage your Tethys Platform installation.

7. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Platform. The website that comes with Tethys Platform is called Tethys Portal. In the terminal, execute the following command from the Tethys :doc:`../tethys_sdk/tethys_cli`::

    $ tethys manage start

Open `<http://localhost:8000/>`_ in a new tab in your web browser and you should see the default Tethys Portal landing page.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

8. Web Admin Setup
------------------

You are now ready to configure your Tethys Platform installation using the web admin interface. Follow the :doc:`./web_admin_setup` tutorial to finish setting up your Tethys Platform.















