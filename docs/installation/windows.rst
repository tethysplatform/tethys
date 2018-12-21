***********************
Installation on Windows
***********************

**Last Updated:** April 2017

Use these instructions to install a development environment on Windows systems.


1. Download the Installation Script and the Miniconda Installation Executable
-----------------------------------------------------------------------------

a. Download the Tethys installation batch script by right clicking on the following link and selecting `Save link as...`: :install_tethys:`install_tethys.bat <bat>`


b. Download the Miniconda installer from the `Conda site <https://conda.io/miniconda.html>`_ or by clicking on the following link: `<https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe>`_


2. Run the Tethys Installation Batch Script
-------------------------------------------

As long as the :file:`install_tethys.bat` and the :file:`Miniconda3-latest-Windows-x86_64.exe` files are in the same directory you can simply double click the :file:`install_tethys.bat` to perform a default installation. To pass in custom options to the installation scrip you must run the script for the command prompt:

.. parsed-literal::

    install_tethys.bat -b |branch|

.. note::

    You can customize your tethys installation by passing command line options to the installation script. The available options can be listed by running::

         > install_tethys.bat --help

    Each option is also descriped here:

        * `-t, --tethys-home <PATH>`:
                Path for tethys home directory. Default is C:\%HOMEPATH%\tethys.
        * `-s, --tethys-src <PATH>`:
                Path for tethys source directory. Default is %TETHYS_HOME%\src.
        * `-a, --allowed-host <HOST>`:
                Hostname or IP address on which to serve Tethys. Default is 127.0.0.1.
        * `-p, --port <PORT>`:
                Port on which to serve Tethys. Default is 8000.
        * `-b, --branch <BRANCH_NAME>`:
                Branch to checkout from version control. Default is 'release'.
        * `-c, --conda-home <PATH>`:
                Path to conda home directory where Miniconda will be installed, or to an existing installation of Miniconda. Default is %TETHYS_HOME%\miniconda.

                .. tip::

                    The conda home path cannot contain spaces. If the the tethys home path contains spaces then the `--conda-home` option must be specified and point to a path without spaces.

        * `-C, --conda-exe <PATH>`:
                Path to Miniconda installer executable. Default is '.\Miniconda3-latest-Windows-x86_64.exe'.
        * `-n, --conda-env-name <NAME>`:
                Name for tethys conda environment. Default is 'tethys'.
        * `--python-version <PYTHON_VERSION>` (deprecated):
                Main python version to install tethys environment into (2-deprecated or 3). Default is 3.
                .. note::

                    Support for Python 2 is deprecated and will be dropped in Tethys version 3.0.

        * `--db-username <USERNAME>`:
                Username that the tethys database server will use. Default is 'tethys_default'.
        * `--db-password <PASSWORD>`:
                Password that the tethys database server will use. Default is 'pass'.
        * `--db-port <PORT>`:
                Port that the tethys database server will use. Default is 5436.
        * `-S, --superuser <USERNAME>`:
                Tethys super user name. Default is 'admin'.
        * `-E, --superuser-email <EMAIL>`:
                Tethys super user email. Default is ''.
        * `-P, --superuser-pass <PASSWORD>`:
                Tethys super user password. Default is 'pass'.
        * `-x`:
                Flag to echo all commands.
        * `-h, --help`:
                Print this help information.

    Here is an example of calling the installation script with customized options::

        > install_tethys.bat -t C:\tethys -a localhost -p 8005 -c C:\Miniconda3 --db-username tethys_db_user --db-password db_user_pass --db-port 5437 -S tethys -E email@example.com -P tpass


The installation script may take several minutes to run. Once it is completed the new conda environment will be left activated so you can start the Tethys development server by running::

    (tethys) > tethys manage start

or simply just::

    (tethys) > tms

.. tip::

    The installation script adds several environmental variables and aliases to help make using Tethys easier, which are active only while the tethys conda environment is activated. To facilitate activating the environment a batch file was added to the TETHYS_HOME directory called :file:`tethys_cmd.bat`. Double clicking that file will open a command prompt with the tethys conda environment activated.

    The following environmental variables are available once the tethys conda environment is activated:

    - `TETHYS_HOME`:
            The directory where the Tethys source code and other Tethys resources are. It is set from the value of the `--tethys-home` option that was passed to the install script.
    - `TETHYS_PORT`:
            The port that the Tethys development server will be served on. Set from the `--port` option.
    - `TETHYS_DB_PORT`:
            The port that the Tethys local database server is running on. Set from the `--db-port` option.

    Also, the following aliases are available:

    - `tethys_start_db`:
            Starts the local Tethys database server
    - `tstartdb`:
            Another alias for `tethys_start_db`
    - `tethys_stop_db`:
            Stops the localTethys database server
    - `tstopdb`:
            Another alias for `tethys_stop_db`
    - `tms`:
            An alias to start the Tethys development server. It calls the command `tethys manage start -p <HOST>:${TETHYS_PORT}` where `<HOST>` is the value of the `--allowed-host` option that was passed to the install script and `${TETHYS_PORT}` is the value of the environmental variable which is set from the `--port` option of the install script.
    - `tstart`:
            Combines the `tethys_start_db` and the `tms` commands.

     When you start up a new terminal there are three steps to get the Tethys development server running again:

        1. Activate the Tethys conda environment
        2. Start the Tethys database server
        3. start the Tethys development server

    Using the supplied aliases, starting the Tethys development server can be done by running the :file:`tethys_cmd.bat` file and then executing the following command::

        (tethys) > tstart

Congratulations! You now have Tethys Platform running a in a development server on your machine. Tethys Platform provides a web interface that is called the Tethys Portal. You can access your Tethys Portal by opening `<http://localhost:8000/>`_ (or if you provided custom host and port options to the install script then it will be `<HOST>:<PORT>`) in a new tab in your web browser.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px

To log in, use the credentials that you specified with the `-S` or `--superuser` and the `-P` or `--superuser-pass` options. If you did not specify these options then the default credentials are:

    * username: `admin`
    * password:  `pass`


2. Install Docker (OPTIONAL)
----------------------------

To facilitate leveraging the full capabilities of Tethys Platform Docker containers are provided to allow the :doc:`../software_suite` to be easily installed. To use these containers you must first install Docker. To install Docker on Windows please refer to the `Docker installation documentation <https://docs.docker.com/docker-for-windows/>`_

Use the following Tethys command to start the Docker containers.

::

  tethys docker start

You are now ready to link your Tethys Portal with the Docker containers using the web admin interface. Follow the :doc:`./web_admin_setup` tutorial to finish setting up your Tethys Platform.

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.


3. Customize Settings (OPTIONAL)
--------------------------------

The Tethys installation script created a settings file called :file:`settings.py` in the directory :file:`$TETHYS_HOME/src/tethys_apps`. The installation script has defined the most essential settings that will allow the Tethys development server to function based on the options that were passed to the script or based on the default values of those options. If you would like to further customize the settings then open the :file:`settings.py` file and make any desired changes. Refer to the :doc:`./platform_settings` documentation for a description of each of the settings.

