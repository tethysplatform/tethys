****************************
Installation on Ubuntu Linux
****************************

**Last Updated:** January 3, 2015

.. warning::

   UNDER CONSTRUCTION

This section describes how to install Tethys Platform on Ubuntu Linux. These installation instructions are optimized for Ubuntu 14.04, which is the recommended platform for running Tethys Platform. However, Tethys Platform could be installed on other distributions of Linux with some adaptation.

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Install the Dependencies
---------------------------

a. If you are using a :term:`Debian` based Linux operating system (like Ubuntu), you can install most of the dependencies via :command:`apt-get`. Open a terminal and execute the following command:

  ::

      $ sudo apt-get update
      $ sudo apt-get install python-dev python-pip python-virtualenv libpq-dev libxml2-dev libxslt1-dev git-core docker.io

  You may be prompted to enter your password to authorize the installation of these packages. If you are prompted about the disk space that will be used to install the dependencies, enter :kbd:`Y` and press :kbd:`Enter` to continue.

  There will be a lot of text printed to the terminal as the dependencies are installed and it may take several minutes to complete. When it is finished you will see a normal terminal cursor again.


b. If you are not using a :term:`Debian` based Linux operating system find the best way to install the following dependencies for your operating system:

  ==================  ====================================================================================================
  Dependency          Description
  ==================  ====================================================================================================
  Python              `Python Programming Language, version 2.7. <https://www.python.org/download/releases/2.7/>`_
  pip                 `Python package management and installation tool. <http://pip.readthedocs.org/en/latest/installing.html>`_
  virtualenv          `virtualenv isolated Python environment creator. <http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation>`_
  git                 `Git open source distributed version control system. <http://git-scm.com/downloads>`_
  docker              `Docker virtual container system. <https://www.docker.com/>`_
  other libraries     libpq-dev, libxml2-dev, and libxslt1-dev
  ==================  ====================================================================================================

2. Finish the Docker Installation
---------------------------------

Execute the following command to finish the installation of Docker:

::

  $ source /etc/bash_completion.d/docker.io

Add User to the Docker Group
============================

Add your user to the Docker group. This is necessary to use the Tethys Docker commandline tools. In a command prompt execute:

::

  $ sudo groupadd docker
  $ sudo gpasswd -a ${USER} docker
  $ sudo service docker.io restart

Finally, log out and log back in to make the changes take effect.

.. warning::

    Adding a user to the Docker group is the equivalent of declaring a user as root. See `Giving non-root access <https://docs.docker.com/installation/ubuntulinux/#giving-non-root-access>`_ for more details.


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

Tethys provides set of commandline tools to help you manage the Docker containers. You must activate your Python environment to use the commandline tools. Execute the following Tethys commands in a terminal to initialize the Docker containers:

::

  $ . /usr/lib/tethys/bin/activate
  $ tethys docker init

The first time you initialize the Docker containers, the images for each container will be downloaded. These images are large and it will take some time to download them.

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

  Although each Docker container seem to start instantaneously, it may take several minutes for the started containers to be fully up and running.


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

a. Replace the password for the main Tethys Portal database, **tethys_default**, with the password you created in the previous step. Also make sure that he host and port match those given from the ``tethys docker ip`` command (PostGIS). This is done by changing the values of the PASSWORD, HOST, and PORT parameters of the DATABASES setting::

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

b. Find the TETHYS_APPS_DATABASE_MANAGER_URL and TETHYS_APPS_SUPERUSER_URL settings near the bottom of the file and replace "pass" with the appropriate passwords that you created in the previous step. Also make sure the host and port are set correctly::

    TETHYS_APPS_DATABASE_MANAGER_URL = 'postgresql://tethys_db_manager:pass@localhost:5432/tethys_db_manager'
    TETHYS_APPS_SUPERUSER_URL = 'postgresql://tethys_super:pass@localhost:5432/tethys_super'

c. Set the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY with an appropriate Google Maps v3 API key. If you do not have a Google Maps API key, use the `Obtaining an API Key <https://developers.google.com/maps/documentation/javascript/tutorial#api_key>`_ instructions::

    TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY = 'Th|$I$@neXAmpL3aPik3Y'

d. If you wish to configure a sitewide dataset service (CKAN or HydroShare), add the TETHYS_DATASET_SERVICES dictionary with the appropriate parameters. See the :doc:`../tethys_sdk/dataset_services` documentation for more details. For example::

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

  When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the user you use to manage your Tethys Portal.

7. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Portal. In the terminal, execute the following command from the Tethys :doc:`../tethys_sdk/tethys_cli`::

    $ tethys manage start

Open `<http://localhost:8000/>`_ in a new tab in your web browser and you should see the default Tethys Portal landing page.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

8. Web Admin Setup
------------------

Login using the administrator username and password that you created in step 5...


What's Next?
------------

Head over to :doc:`../getting_started` and create your first app. You can also check out the :doc:`../tethys_sdk` documentation to familiarize yourself with all the features that are available.









