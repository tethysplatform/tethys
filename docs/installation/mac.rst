***********************
Installation on Mac OSX
***********************

**Last Updated:** May 27, 2015

Use these instructions to install a development environment on OSX. These instructions have been tested with OSX Yosemite.

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Install the Dependencies
---------------------------

a. Many of the commandline tools for the Mac are provided through Xcode. You will need to install or update the Xcode commandline tools by opening a Terminal and executing the following command:

  ::

      $ xcode-select --install

Follow the prompts to download and install commandline developer tools.

  .. note::

      If you do not have Xcode installed, you may need to install it before running this command. You can install it using the Mac App Store.

b. One feature that Mac OSX lacks that many Linux distributions provide is a package manager on the commandline. `Homebrew <http://brew.sh/>`_ is an excellent package manager for Mac OSX and you will use it to install the Tethys dependencies. Install `Homebrew <http://brew.sh/>`_ by  executing the following command in a Terminal:

  ::

      $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

  After `Homebrew <http://brew.sh/>`_ is installed, you will need to add a few entries to the PATH variable. In a terminal, execute the following command:

  ::

      $ sudo nano /etc/paths

  * Enter your password if prompted.
  * Add the following two paths at the **top of the file** if they are not already present

    ::

        /usr/local/bin
        /usr/local/sbin

  * Press ``control-x`` to quit and enter ``Y`` to save the changes.

  .. note::

      You may need to close Terminal and open it again for these changes to take effect.

c. You will need a fresh installation of ``Python`` with the ``pip`` and ``virtualenv`` installed. Fortunately, `Homebrew <http://brew.sh/>`_ automatically installs ``pip`` and ``virtualenv`` with its ``Python`` package. Install Python and other dependencies using `Homebrew <http://brew.sh/>`_ as follows:

  ::

      $ brew install git libpqxx libxml2 libxslt libffi
      $ brew unlink openssl
      $ brew install https://raw.githubusercontent.com/Homebrew/homebrew/62fc2a1a65e83ba9dbb30b2e0a2b7355831c714b/Library/Formula/openssl.rb
      $ brew link --force openssl && brew switch openssl 1.0.1j_1
      $ brew install python --with-brewed-openssl --build-from-source
      $ pip install virtualenv

  .. tip::

      If you encounter trouble using `Homebrew <http://brew.sh/>`_ to install these dependencies, run the following command in the Terminal:

      ::

          $ brew doctor

      This will generate a list of suggestions for remedying your `Homebrew <http://brew.sh/>`_ installation.

2. Create Virtual Environment and Install Tethys Platform
---------------------------------------------------------

Python virtual environments are used to create isolated Python installations to avoid conflicts with dependencies of other Python applications on the same system. Execute the following commands in Terminal.

a. Create a :term:`Python virtual environment` and activate it::

    $ sudo mkdir -p /usr/lib/tethys
    $ sudo chown `whoami` /usr/lib/tethys
    $ virtualenv --no-site-packages /usr/lib/tethys
    $ . /usr/lib/tethys/bin/activate


.. important::

    The final command above activates the Python virtual environment for Tethys. You will know the virtual environment is active, because the name of it will appear in parenthesis in front of your terminal cursor::

        (tethys) $ _

    The Tethys virtual environment must remain active for most of the installation. If you need to logout or close the terminal in the middle of the installation, you will need to reactivate the virtual environment. This can be done at anytime by executing the following command (don't forget the dot)::

        $ . /usr/lib/tethys/bin/activate

    As a reminder, the commands requiring your Tethys virtual environment be active will show the cursor with "(tethys)" next to it.

b. Install Tethys Platform into the virtual environment with the following command::

    (tethys) $ git clone https://github.com/CI-WATER/tethys /usr/lib/tethys/src

.. tip::

    If you would like to install a different version of Tethys Platform, you can use git to checkout the tagged release branch. For example, to checkout version 1.0.0:

    ::

        cd /usr/lib/tethys/src
        git checkout tags/1.0.0

    For a list of all tagged releases, see `Tethys Platform Releases <https://github.com/CI-WATER/tethys/releases>`_. Depending on the version you intend to install, you may need to delete your entire virtual environment (i.e.: the ``/usr/lib/tethys`` directory) to start fresh.


c. Install the Python modules that Tethys requires::

    (tethys) $ pip install --upgrade -r /usr/lib/tethys/src/requirements.txt
    (tethys) $ python /usr/lib/tethys/src/setup.py develop

d. Restart the Python virtual environment::

    (tethys) $ deactivate
             $ . /usr/lib/tethys/bin/activate


3. Install Tethys Software Suite Using Docker
---------------------------------------------

Tethys Platform provides a software suite that addresses the unique needs of water resources web app development (see :doc:`../features` for more details). To make installation of the software easy, each software has been provided as Docker container. The following instructions will walk you through installation of these software using Docker. See the `Docker Documentation <https://docs.docker.com/>`_ for more information about Docker.

a. Install Boot2Docker version 1.6 using the `Install Docker on Mac OSX instructions <https://docs.docker.com/v1.6/installation/mac/>`_. Look for the heading titled *Install Boot2Docker*. Verify the installation using the instructions using the instructions under the *Start the Boot2Docker Application* heading.

b. Close the Boot2Docker terminal and open a new one. Initialize the Tethys Docker containers with the following command:

  ::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys docker init

  Follow the interactive prompts to customize your Docker installations. To accept the default value shown in square brackets, simply press ``enter``. **Take note of any passwords you are prompted to create.**

  .. note::

      The first time you initialize the Docker containers, the images for each container will need to be downloaded. These images are large and it may take a long time for them to download.

c. Start the docker containers with the following command:

  ::

    (tethys) $ tethys docker start

  After running the `tethys docker start` command, you will have the following software running:

    * PostgreSQL with PostGIS
    * 52 North WPS
    * GeoServer

  If you would like to test the Docker containers, see the :doc:`../supplementary/docker_testing` article.

  .. note::

      Although each Docker container appears to start instantaneously, it may take several minutes for the started containers to be fully up and running.

4. Install HTCondor (Optional)
------------------------------

HTCondor is a job scheduling and resource management system that is used by the Tethys Compute module. Distributed computing can be configured without installing HTCondor. For more information on how HTCondor is used for distributed computing in Tethys and the different configuration options see :doc:`../tethys_sdk/cloud_computing`.

a. Use a browser to download the HTCondor tarball from the `HTCondor downloads page. <http://research.cs.wisc.edu/htcondor/downloads/>`_ Click the link next to the version you wish to install. Select condor-X.X.X-x86_64_MacOSX-stripped.tar.gz, complete the rest of the form to submit your download request. This should redirect you to a page with a link to download the tarball.

b. In a terminal change directories to the location of the tarball, untar it, and change into the new directory::

    $ tar xzf condor-X.X.X-x86_64_MacOSX-stripped.tar.gz
    $ cd condor-X.X.X-x86_64_MacOSX7-stripped

c. Run the perl script condor_install with the following options to install condor

  ::

    $ perl condor_install --install --install-dir /usr/local/condor

d. Add an environmental variable to point to the location of the global condor_config file, and add the condor bin and sbin directories to PATH. This can be done by executing the condor.sh script that was generated when condor was installed::

    . /usr/local/condor/condor.sh

  .. tip::

        To have these environmental variables exported automatically when a terminal is started add the previous command to the .bash_profile.

        ::

            echo '. /usr/local/condor/condor.sh' >> ~/.bash_profile

e. Start condor::

    $ condor_master

f. Check that condor is running::

    $condor_status

    Name               OpSys      Arch   State     Activity LoadAv Mem   ActvtyTime

            slot1@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:05
            slot2@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.660 1024  0+00:50:06
            slot3@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:07
            slot4@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:08
            slot5@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:09
            slot6@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:10
            slot7@ciwater-1.lo OSX        X86_64 Unclaimed Idle      0.000 1024  0+00:50:11
            slot8@ciwater-1.lo OSX        X86_64 Unclaimed Idle      1.000 1024  0+00:50:04
                                 Total Owner Claimed Unclaimed Matched Preempting Backfill

                      X86_64/OSX     8     0       0         8       0          0        0

                           Total     8     0       0         8       0          0        0

5. Create Settings File and Configure Settings
----------------------------------------------

Create a settings file for your Tethys Platform installation using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli`. Execute the following command in the terminal::

    (tethys) $ tethys gen settings -d /usr/lib/tethys/src/tethys_apps

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_apps`. Open the :file:`settings.py` file and make the following modifications.

.. note::

    Accessing the :file:`settings.py` file can be done by opening a new Finder Window and selecting ``Go > Go to Folder...`` from the menu. Enter :file:`/usr/lib/tethys/src/tethys_apps` in the text box and press ``Go`` to browse to directory. From here you can open the :file:`settings.py` file using your favorite text editor.

a. Run the following command to obtain the host and port for the Docker running the database:

  ::

    (tethys) $ tethys docker ip

    PostGIS/Database:
      Host: 192.168.59.103
      Port: 5435
    ...

b. Open the :file:`settings.py` and locate the ``DATABASES`` setting. Replace the password for **tethys_default**, with the password you created when initializing the Docker containers. Also set the host and port to match those given from the ``tethys docker ip`` command:

  ::

    DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2',
          'NAME': 'tethys_default',
          'USER': 'tethys_default',
          'PASSWORD': 'pass',
          'HOST': '192.168.59.103',
          'PORT': '5435'
          }
    }

c. Find the TETHYS_DATABASES setting near the bottom of the :file:`settings.py` file and set the passwords for the **tethys_db_manager** and **tethys_super** database users. If necessary, also change the HOST and PORT to match the host and port given by the ``tethys docker ip`` command::

    TETHYS_DATABASES = {
        'tethys_db_manager': {
            'NAME': 'tethys_db_manager',
            'USER': 'tethys_db_manager',
            'PASSWORD': 'pass',
            'HOST': '192.168.59.103',
            'PORT': '5435'
        },
        'tethys_super': {
            'NAME': 'tethys_super',
            'USER': 'tethys_super',
            'PASSWORD': 'pass',
            'HOST': '192.168.59.103',
            'PORT': '5435'
        }
    }


d. Save your changes and close the :file:`settings.py` file.

6. Create Database Tables
-------------------------

Execute the :command:`tethys manage syncdb` command from the Tethys :doc:`../tethys_sdk/tethys_cli` to create the database tables. In the terminal:

::

    (tethys) $ tethys manage syncdb


.. important::

    When prompted to create a system administrator enter 'yes'. Take note of the username and password, as this will be the administrator user you will use to manage your Tethys Platform installation.

7. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Platform. In the terminal, execute the following command from the Tethys :doc:`../tethys_sdk/tethys_cli`::

    (tethys) $ tethys manage start


Tethys Platform provides a web interface that is called the Tethys Portal. You can access your Tethys Portal by opening `<http://localhost:8000/>`_ in a new tab in your web browser.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

8. Web Admin Setup
------------------

You are now ready to configure your Tethys Platform installation using the web admin interface. Follow the :doc:`./web_admin_setup` tutorial to finish setting up your Tethys Platform.















