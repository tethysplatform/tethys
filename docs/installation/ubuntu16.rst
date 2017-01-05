****************************
Installation on Ubuntu 16.04
****************************

**Last Updated:** January 5, 2017

.. warning::

    These installation instructions have been tested for Ubuntu 16.04 only. It is likely that you will encounter problems if you try to use these instructions on any other Linux distribution (e.g. RedHat, CentOS) or even other versions of Ubuntu.

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.
    
    Also, check to make sure that your installation of Ubuntu = version 16.04. The following steps are likely not to work with other versions.

1. Install Miniconda (or Anaconda)
----------------------------------

a. Installers can be found on the `Miniconda website <http://conda.pydata.org/miniconda.html>`_. Or to perform a silent installation of Miniconda (which assumes you accept the `terms and conditions <https://docs.continuum.io/anaconda/eula>`_), open a terminal and execute the following commands:

  ::

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"

2. Clone the Tethys Platform Repository
---------------------------------------

a. Create a directory for the source code with the proper permissions and clone the code into that directory.

  ::

    sudo mkdir -p /usr/lib/tethys
    sudo chown $USER /usr/lib/tethys
    conda install --yes git
    git clone https://github.com/tethysplatform/tethys /usr/lib/tethys/src
    cd /usr/lib/tethys/src
    git checkout dev

.. tip::

    The last line that was executed checks out the development branch of Tethys Platform. If you would like to install a different version, you can use git to checkout the tagged release branch. For example, to checkout version 1.4.0:

    ::

        $ cd /usr/lib/tethys/src
        $ git checkout tags/1.4.0

    For a list of all tagged releases, see `Tethys Platform Releases <https://github.com/tethysplatform/tethys/releases>`_. Depending on the version you intend to install, you may need to delete your entire virtual environment (i.e.: the ``/usr/lib/tethys`` directory) to start fresh.

.. note::

    The source code can be placed into any directory, however it is recommended that you use `/usr/lib/tethys/src` for consistency with the documentation.

c. Create a Conda environment with the Tethys dependencies and install Tethys into that environment.

  ::

    conda env create -f tethys_conda_env.yml
    . activate tethys
    python setup.py develop

.. important::

    The final command above activates the Python virtual environment for Tethys. You will know the virtual environment is active, because the name of it will appear in parenthesis in front of your terminal cursor::

        (tethys) $ _

    The Tethys virtual environment must remain active for the entire installation. If you need to logout or close the terminal in the middle of the installation, you will need to reactivate the virtual environment. To activate the environment you first need to add the miniconda `bin` directory to your path::

        export PATH="$HOME/miniconda/bin:$PATH"

    Then you can activate the tethys environment by executing the following command (don't forget the dot)::

        . activate tethys

    If you get tired of going through these steps to activate your environment, you can add an alias to your ``.bashrc`` file::

        echo "alias t='. $HOME/miniconda/bin/activate tethys'" >> ~/.bashrc

    Execute the ``.bashrc`` file to effect the changes. (This file is automatically executed when a new terminal is opened)::

        . ~/.bashrc

    Now, to activate your virtual environment all you have to do is use the alias ``t``::

        t
        (tethys) $ _

3. Install Docker
-----------------

Docker needs to be installed to install the Tethys Software Suite. These instructions are adapted from the `Installation on Ubuntu <https://docs.docker.com/engine/installation/linux/ubuntulinux/>`_ Docker tutorial and the `How to Install and Use Docker on Ubuntu 16.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04>`_ Digital Ocean tutorial.

a. Add the GPG key for the official Docker repository:

  ::

    sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
  
b. Add the Docker repository to APT sources:

  ::

    echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
  
c. Update APT sources again and install Docker engine:

  ::

    sudo apt-get update
    sudo apt-get install -y docker-engine

d. Add your user to the Docker group. This is necessary to use the Tethys Docker commandline tools. In a command prompt execute:

  ::

    sudo gpasswd -a $USER docker
    sudo service docker restart
    newgrp docker

.. warning::

    Adding a user to the Docker group is the equivalent of declaring a user as root. See `Giving non-root access <https://docs.docker.com/installation/ubuntulinux/#giving-non-root-access>`_ for more details.

4. Install Tethys Software Suite Docker Containers
--------------------------------------------------

Execute the following Tethys commands using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli` to initialize the Docker containers:

::

  tethys docker init

You will be prompted to enter various parameters needed to customize your instance of the software. **Take note of the usernames and passwords that you specify**. You will need them to complete the installation.

.. tip::

    Running into errors with this command? Try logging out and logging back in to reinitialize the docker group permissions for you user.

    Occasionally, you may encounter an error due to poor internet connection. Run the ``tethys docker init`` command repeatedly. It will pick up where it left off and eventually lead to success. When in doubt, try, try again.



5. Start the Docker Containers
------------------------------

Use the following Tethys command to start the Database Docker container for the next steps:

::

  tethys docker start -c postgis

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.

6. Create Settings File and Configure Settings
----------------------------------------------

In the next steps you will configure your Tethys Platform and link it to each of the software in the software suite. Create a new settings file for your Tethys Platform installation using the :command:`tethys` :doc:`../tethys_sdk/tethys_cli`. Execute the following command in the terminal::

    tethys gen settings -d /usr/lib/tethys/src/tethys_apps

This will create a file called :file:`settings.py` in the directory :file:`/usr/lib/tethys/src/tethys_apps`. As the name suggests, the :file:`settings.py` file contains all of the settings for the Tethys Platform. There are a few settings that need to be configured in this file.

.. note::

    The :file:`usr` directory is located in the root directory which can be accessed using a file browser and selecting :file:`Computer` from the menu on the left.

Open the :file:`settings.py` file that you just created (:file:`/usr/lib/tethys/src/tethys_apps/settings.py`) in a text editor and modify the following settings appropriately.

a. Run the following command to obtain the host and port for Docker running the database (PostGIS). You will need these in the following steps:

  ::

    tethys docker ip

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

Execute the following command to initialize the database tables::

    tethys manage syncdb

8. Create a Superuser
---------------------

Create a superuser/website administrator for your Tethys Portal:

::

    tethys manage createsuperuser

9. Start up the Django Development Server
-----------------------------------------

You are now ready to start the development server and view your instance of Tethys Platform. The website that ships with Tethys Platform is called :doc:`../tethys_portal`. In the terminal, execute the following command to start the development server::

    tethys manage start

Open `<http://localhost:8000/>`_ in a new tab in your web browser and you should see the default :doc:`../tethys_portal` landing page.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

.. tip::

    Whenever you need to start the Tethys development server you must (1) activate the environment, (2) start the dockers, and (3) start the server. To facilitate these steps you can add another alias to your ``.bashrc`` file::

        echo "alias tstart='. $HOME/miniconda/bin/activate tethys; tethys docker start; tethys manage start'" >> ~/.bashrc

    Now to start the development server all you need to do is type::

        tstart

9. Web Admin Setup
------------------

You are now ready to configure your Tethys Platform installation using the web admin interface. Follow the :doc:`./web_admin_setup` instructions to finish setting up your Tethys Platform.

.. tip::

    If you are already familiar with all of the installation steps and just need to quickly install Tethys with the default settings, then you can just copy and paste the following command blocks in succession into your terminal::

        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
        bash ~/miniconda.sh -b -p $HOME/miniconda
        export PATH="$HOME/miniconda/bin:$PATH"
        conda install --yes git
        sudo mkdir -p /usr/lib/tethys
        sudo chown $USER /usr/lib/tethys
        git clone https://github.com/tethysplatform/tethys /usr/lib/tethys/src
        cd /usr/lib/tethys/src
        git checkout dev
        conda env create -f tethys_conda_env.yml
        . activate tethys
        python setup.py develop
        sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    ::

        echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
        sudo apt-get update

    ::

        sudo apt-get install -y docker-engine
        sudo gpasswd -a $USER docker
        sudo service docker restart
        newgrp docker
    ::

        tethys docker init -d
        tethys docker start -c postgis
        tethys gen settings -d /usr/lib/tethys/src/tethys_apps
        tethys manage syncdb
        tethys manage createsuperuser