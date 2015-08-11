****************************
Installation on Ubuntu 14.04
****************************

**Last Updated:** August 11, 2015

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Install the Dependencies
---------------------------

a. Install most of the dependencies via :command:`apt-get`. Open a terminal and execute the following commands:

  ::

      $ sudo apt-get update
      $ sudo apt-get install python-dev python-pip python-virtualenv libpq-dev libxml2-dev libxslt1-dev libffi-dev git-core docker.io

  You may be prompted to enter your password to authorize the installation of these packages. If you are prompted about the disk space that will be used to install the dependencies, enter :kbd:`Y` and press :kbd:`Enter` to continue.

  There will be a lot of text printed to the terminal as the dependencies are installed and it may take several minutes to complete. When it is finished you will see a blinking terminal cursor again.


2. Finish the Docker Installation
---------------------------------

There are a few additional steps that need to be completed to finish the installation of Docker.

a. Execute the following command to finish the installation of Docker:

  ::

    $ source /etc/bash_completion.d/docker.io

b. Add your user to the Docker group. This is necessary to use the Tethys Docker commandline tools. In a command prompt execute:

  ::

    $ sudo groupadd docker
    $ sudo gpasswd -a ${USER} docker
    $ sudo service docker.io restart

c. Close the terminal, then **log out** and **log back in** to make the changes take effect.

.. important::

    **DO NOT FORGET PART C!** Be sure to logout of Ubuntu and log back in before you continue. You will not be able to complete the installation without completing this step.

.. warning::

    Adding a user to the Docker group is the equivalent of declaring a user as root. See `Giving non-root access <https://docs.docker.com/installation/ubuntulinux/#giving-non-root-access>`_ for more details.

3. Install HTCondor (Optional)
---------------------------------------------------------

HTCondor is a job scheduling and resource management system that is used by the Tethys Compute module. Distributed computing can be configured without installing HTCondor. For more information on how HTCondor is used for distributed computing in Tethys and the different configuration options see :doc:`../tethys_sdk/cloud_computing`. Use one of the following links for instructions on how to install HTCondor through the package manager:

    Enterprise Linux: `HTCondor YUM Repository <http://research.cs.wisc.edu/htcondor/yum/>`_

    Debian Linux: `HTCondor Debian Repository <http://research.cs.wisc.edu/htcondor/debian/>`_

4. Create Virtual Environment and Install Tethys Platform
---------------------------------------------------------

Python virtual environments are used to create isolated Python installations to avoid conflicts with dependencies of other Python applications on the same system. The following commands should be executed in a terminal.

a. Create a :term:`Python virtual environment` and activate it::

    $ sudo mkdir -p /usr/lib/tethys
    $ sudo chown `whoami` /usr/lib/tethys
    $ virtualenv --no-site-packages /usr/lib/tethys
    $ . /usr/lib/tethys/bin/activate

.. hint::

    You may be tempted to enter single quotes around the *whoami* directive above, but those characters are actually `grave accent <http://www.wikiwand.com/en/Grave_accent>`_ characters: :kbd:`\``. This key is usually located to the left of the :kbd:`1` key or in that vicinity.

.. important::

    The final command above activates the Python virtual environment for Tethys. You will know the virtual environment is active, because the name of it will appear in parenthesis in front of your terminal cursor::

        (tethys) $ _

    The Tethys virtual environment must remain active for the entire installation. If you need to logout or close the terminal in the middle of the installation, you will need to reactivate the virtual environment. This can be done at anytime by executing the following command (don't forget the dot)::

        $ . /usr/lib/tethys/bin/activate

b. Install Tethys Platform into the virtual environment with the following command::

    (tethys) $ git clone https://github.com/tethysplatform/tethys /usr/lib/tethys/src

.. tip::

    If you would like to install a different version of Tethys Platform, you can use git to checkout the tagged release branch. For example, to checkout version 1.0.0:

    ::

        $ cd /usr/lib/tethys/src
        $ git checkout tags/1.0.0

    For a list of all tagged releases, see `Tethys Platform Releases <https://github.com/tethysplatform/tethys/releases>`_. Depending on the version you intend to install, you may need to delete your entire virtual environment (i.e.: the ``/usr/lib/tethys`` directory) to start fresh.

c. Install the Python modules that Tethys requires::

    (tethys) $ pip install --upgrade -r /usr/lib/tethys/src/requirements.txt
    (tethys) $ python /usr/lib/tethys/src/setup.py develop

d. Restart the Python virtual environment::

    (tethys) $ deactivate
             $ . /usr/lib/tethys/bin/activate


5. Install Tethys Software Suite Using Docker
---------------------------------------------

Tethys Platform provides a software suite that addresses the unique needs of water resources web app development including:

* PostgreSQL with PostGIS enabled for spatial database storage,
* 52 North WPS with GRASS and Sextante enabled for geoprocessing services, and
* GeoServer for spatial dataset publishing.

Installing some of these dependencies can be VERY difficult, so they have been provided as Docker containers to make installation EASY. The following instructions will walk you through installation of these software using Docker. See the `Docker Documentation <https://docs.docker.com/>`_ for more information about Docker containers.


Initialize the Docker Containers
================================

Tethys provides set of commandline tools to help you manage the Docker containers. You must activate your Python environment to use the commandline tools. Execute the following Tethys commands using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli` to initialize the Docker containers:

::

  (tethys) $ tethys docker init


.. tip::

    Running into errors with this command? Make sure you have completed all of step 2, including part c.

The first time you initialize the Docker containers, the images for each container will be downloaded. These images are large and it may take a long time for them to download.

After the images have been downloaded, the containers will automatically be installed. During installation, you will be prompted to enter various parameters needed to customize your instance of the software. Some of the parameters are usernames and passwords. **Take note of the usernames and passwords that you specify**. You will need them to complete the installation.

Start the Docker Containers
===========================

Use the following Tethys command to start the Docker containers:

::

  (tethys) $ tethys docker start

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.



6. Create Settings File and Configure Settings
----------------------------------------------

In the next steps you will configure your Tethys Platform and link it to each of the software in the software suite. Create a new settings file for your Tethys Platform installation using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli`. Execute the following command in the terminal::

    (tethys) $ tethys gen settings -d /usr/lib/tethys/src/tethys_apps

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_apps`. As the name suggests, the :file:`settings.py` file contains all of the settings for the Tethys Platform. There are a few settings that need to be configured in this file.

.. note::

    The :file:`usr` directory is located in the root directory which can be accessed using a file browser and selecting :file:`Computer` from the menu on the left.

Open the :file:`settings.py` file that you just created (:file:`/usr/lib/tethys/src/tethys_apps/settings.py`) in a text editor and modify the following settings appropriately.

a. Run the following command to obtain the host and port for Docker running the database (PostGIS). You will need these in the following steps:

  ::

    (tethys) $ tethys docker ip

b. Replace the password for the main Tethys Portal database, **tethys_default**, with the password you created in the previous step. Also make sure that the host and port match those given from the ``tethys docker ip`` command (PostGIS). This is done by changing the values of the PASSWORD, HOST, and PORT parameters of the DATABASES setting:

  ::

    DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2',
          'NAME': 'tethys_default',
          'USER': 'tethys_default',
          'PASSWORD': 'pass',
          'HOST': '127.0.0.1',
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

d. Setup social authentication

  If you wish to enable social authentication capabilities for testing your Tethys Portal, follow the :doc:`../tethys_portal/social_auth` instructions.


e. Save your changes and close the :file:`settings.py` file.

7. Create Database Tables
-------------------------

Execute the :command:`tethys manage syncdb` command from the Tethys :doc:`../tethys_sdk/tethys_cli` to create the database tables. In the terminal::

    (tethys) $ tethys manage syncdb

.. important::

  When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the user you use to manage your Tethys Platform installation.

8. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Platform. The website that comes with Tethys Platform is called Tethys Portal. In the terminal, execute the following command from the Tethys :doc:`../tethys_sdk/tethys_cli`::

    (tethys) $ tethys manage start

Open `<http://localhost:8000/>`_ in a new tab in your web browser and you should see the default Tethys Portal landing page.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

9. Web Admin Setup
------------------

You are now ready to configure your Tethys Platform installation using the web admin interface. Follow the :doc:`./web_admin_setup` instructions to finish setting up your Tethys Platform.









