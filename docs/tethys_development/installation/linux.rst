*********************************
Development Installation on Linux
*********************************

**Last Updated:** March 4, 2015

.. important::

  Tethys Platform is built on the Python web framework Django. If you are not familiar with Django development, it is required that you read and complete all of the tutorials in the **First Steps** section of the `Django Documentation <https://docs.djangoproject.com/en/1.7/>`_ before embarking on Tethys Platform development.

1. Install the Dependencies
---------------------------

Complete steps 1-3 from the normal :doc:`../../installation/linux` instructions.

2. Create Project Directory
---------------------------

Create a project directory for the Tethys source code in a convenient location. This will be the directory you will work out of. For this tutorial, the directory will be called :file:`tethysdev` and it will be located in the home directory. Also, create a directory inside your project directory called :file:`apps` for any Tethys app projects you work on during development of Tethys.

::

    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ mkdir apps

3. Pull the Source Code
-----------------------

Tethys Platform is versioned with Git and hosted on GitHub. Change into the project directory you created in the previous step and execute the following commands to download the source code:

::

    $ git clone https://github.com/CI-WATER/tethys.git
    $ git clone https://github.com/CI-WATER/tethys_dataset_services.git
    $ git clone https://github.com/CI-WATER/tethys_docker.git

When you are done, your project directory should have the following contents:

::

  tethysdev/
    |-- apps/
    |-- tethys/
    |-- tethys_dataset_services/
    |-- tethys_docker/

A brief explanation of each directory is provided below. For more details about the organization of Tethys Platform source code, see :doc:`../overview`.

* **apps**: a directory to that will contain Tethys app projects used for development purposes.
* **tethys**: The main Django site project for Tethys. Most of the logic for tethys is contained in this project.
* **tethys_dataset_services**: A Python module providing an interface with CKAN, HydroShare, and GeoServer.
* **tethys_docker**: The Dockerfiles for the Tethys Docker images.

4. Create Virtual Environment and Install Tethys Platform
---------------------------------------------------------

Many of the Tethys commandline utilities depend on Tethys being installed in a default location: :file:`/usr/lib/tethys/src` for unix environments. This location is not ideal for development, so instead you will create a symbolic link from where you downloaded the source to the default location. The virtual environment will also be installed in the default location.

a. If you have an existing installation of Tethys in :file:`/usr/lib/tethys`, you should delete it::

    $ sudo rm -rf /usr/lib/tethys

b. Create a :term:`Python virtual environment` and activate it::

    $ sudo mkdir -p /usr/lib/tethys
    $ sudo chown `whoami` /usr/lib/tethys
    $ virtualenv --no-site-packages /usr/lib/tethys
    $ . /usr/lib/tethys/bin/activate

c. Create a symbolic link from the :file:`tethys` source code you downloaded to the default location::

    $ ln -s ~/tethysdev/tethys /usr/lib/tethys/src

d. Install each of the projects that you downloaded in development mode. Development mode any changes you make to the source code to take effect immediately without requiring you to reinstall the project::

    $ cd ~/tethysdev/tethys_dataset_services && python setup.py develop

e. Install the Python modules that Tethys requires::

    $ pip install -r /usr/lib/tethys/src/requirements.txt
    $ python /usr/lib/tethys/src/setup.py develop

f. Restart the Python virtual environment::

    $ deactivate
    $ . /usr/lib/tethys/bin/activate


5. Install Tethys Software Suite Using Docker
---------------------------------------------

a. Initialize the Tethys Software Suite Docker containers with the default parameters:

  ::

    $ tethys docker init -d

  Here are the default passwords that you will need to know to finish setup:

  PostGIS Database User Passwords:

  * **tethys_default**: pass
  * **tethys_db_manager**: pass
  * **tethys_super**: pass

  Geoserver Username and Password:

  * **admin**: geoserver

  52 North WPS Username and Password:

  * **wps**: wps

b. Start the Docker containers:

  ::

      $ tethys docker start

  .. note::

    Although each Docker container appears to start instantaneously, it may take several minutes for the started containers to be fully up and running.

6. Create Settings File and Configure Settings
----------------------------------------------

Create a new settings file for your Tethys Platform installation using the :command:`tethys` :doc:`../../tethys_sdk/tethys_cli`. Execute the following command in the terminal::

    $ tethys gen settings -d /usr/lib/tethys/src/tethys_apps

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_apps`. Because your source code has been symbolically linked to this location, the :file:`settings.py` file will also be located in :file:`~/tethysdev/tethys/tethys_apps`. There are a few settings that need to be configured in this file.

Open the :file:`settings.py` file that you just created from your source code location(:file:`~/tethysdev/tethys/tethys_apps/settings.py`) in a text editor and modify the following settings appropriately.

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
          'PORT': '5435'
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


d. Save your changes and close the :file:`settings.py` file.

7. Create Database Tables
-------------------------

Execute the :command:`tethys manage syncdb` command from the Tethys :doc:`../../tethys_sdk/tethys_cli` to create the database tables. In the terminal::

    $ tethys manage syncdb

.. important::

  When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the user you use to manage your Tethys Portal.

8. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Platform. The website that is provided with Tethys Platform is called Tethys Portal. In the terminal, execute the following command from the Tethys :doc:`../../tethys_sdk/tethys_cli`::

    $ tethys manage start

Open `<http://localhost:8000/>`_ in a new tab in your web browser and you should see the default Tethys Portal landing page.

.. figure:: ../../images/tethys_portal_landing.png
    :width: 650px

9. Web Admin Setup
------------------

You are now ready to configure your Tethys Platform installation using the web admin interface. Follow the :doc:`../../installation/web_admin_setup` tutorial to finish setting up your Tethys Platform.









