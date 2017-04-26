*********************************
Installation on Linux and Mac OSX
*********************************

**Last Updated:** April 2017

Use these instructions to install a development environment on Mac OSX or Linux systems.

.. tip::

    To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. For a quick introduction to the command line, see the :doc:`../supplementary/terminal_quick_guide` article.

1. Download and Run the Installation Script
-------------------------------------------

Run the following commands from a terminal to download and run the Tethys Platform install script.

For systems with `wget` (most Linux distributions):

.. parsed-literal::

      $ wget \https://raw.githubusercontent.com/tethysplatform/tethys/|branch|/scripts/install_tethys.sh
      $ . install_tethys.sh

For Systems with `curl` (e.g. Mac OSX and CentOS):

.. parsed-literal::

      $ curl \https://raw.githubusercontent.com/tethysplatform/tethys/|branch|/scripts/install_tethys.sh -o ./install_tethys.sh
      $ . install_tethys.sh

.. note::

    You can customize your tethys installation by passing command line options to the installation script. The available options can be listed by running::

         $ . install_tethys.sh --help

    Each option is also descriped here:

        * `-t, --tethys-home <PATH>`:
                Path for tethys home directory. Default is ~/tethys.
        * `-a, --allowed-host <HOST>`:
                Hostname or IP address on which to serve Tethys. Default is 127.0.0.1.
        * `-p, --port <PORT>`:
                Port on which to serve Tethys. Default is 8000.
        * `-b, --branch <BRANCH_NAME>`:
                Branch to checkout from version control. Default is 'master'.
        * `-c, --conda-home <PATH>`:
                Path to conda home directory where Miniconda will be installed. Default is ${TETHYS_HOME}/miniconda.
        * `-n, --conda-env-name <NAME>`:
                Name for tethys conda environment. Default is 'tethys'.
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
        * `--install-docker`:
                Flag to include Docker installation as part of the install script (Linux only). See `2. Install Docker (OPTIONAL)`_ for more details.
        * `--docker-options <OPTIONS>`:
                Command line options to pass to the `tethys docker init` call if --install-docker is used. Default is "'-d'".
                .. tip::

                    Note that the value for the `--docker-options` option must have nested quotes. For example "'-d -c geoserver'" or '"-d -c geoserver"'.
        * `-x`:
                Flag to turn on shell command echoing.
        * `-h, --help`:
                Print this help information.

    Here is an example of calling the installation script with customized options::

        $ . install_tethys.sh -t ~/Workspace/tethys -a localhost -p 8005 -c ~/miniconda3 --db-username tethys_db_user --db-password db_user_pass --db-port 5437 -S tethys -E email@example.com -P tpass


The installation script may take several minutes to run. Once it is completed the new conda environment will be left activated so you can start the Tethys development server by running::

    (tethys) $ tethys manage start

or simply just::

    (tethys) $ tms

.. tip::

    The installation script adds several environmental variables and aliases to help make using Tethys easier. Most of them are active only while the tethys conda environment is activated, however one alias to activate the tethys conda environment was added to your `.bashrc` or `bash_profile` file in your home directory and should be available from any terminal session:

     - `t`: Alias to activate the tethys conda environment. It is a shortcut for the command `source <CONDA_HOME>/bin/activate tethys` where <CONDA_HOME> is the value of the `--conda-home` option that was passed to the install script.

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

     When you start up a new terminal there are three steps to get the Tethys development server running again:

        1. Activate the Tethys conda environment
        2. Start the Tethys database server
        3. start the Tethys development server

    For convenience the Tethys database server is started automatically when the tethys conda environment is activated, and it is stopped when the environment is deactivated. So, using the supplied aliases, starting the Tethys development server from a fresh terminal can be done with the following two commands::

        $ t
        (tethys) $ tms

Congratulations! You now have Tethys Platform running a in a development server on your machine. Tethys Platform provides a web interface that is called the Tethys Portal. You can access your Tethys Portal by opening `<http://localhost:8000/>`_ (or if you provided custom host and port options to the install script then it will be `<HOST>:<PORT>`) in a new tab in your web browser.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px


2. Install Docker (OPTIONAL)
----------------------------

To facilitate leveraging the full capabilities of Tethys Platform Docker containers are provided to allow the :doc:`../software_suite` to be easily installed. To use these containers you must first install Docker. The Tethys installation script :file:`install_tethys.sh` will support installing the community edition of Docker on several Linux distributions. To install Docker when installing Tethys then add the `--install-docker` option. You can also add the `--docker-options` options to pass options to the `tethys docker init` command (see the :ref:`tethys_cli_docker` section of the :doc:`../tethys_sdk/tethys_cli` documentation).

To install Docker on other systems or to install the enterprise edition of Docker please refer to the `Docker installation documentation <https://docs.docker.com/engine/installation/>`_

Use the following Tethys command to start the Docker containers.

::

  tethys docker start

You are now ready to link your Tethys Portal with the Docker containers using the web admin interface. Follow the :doc:`./web_admin_setup` tutorial to finish setting up your Tethys Platform.

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.


3. Customize Settings (OPTIONAL)
--------------------------------

The Tethys installation script created a settings file called :file:`settings.py` in the directory :file:`$TETHYS_HOME/src/tethys_apps`. The installation script has defined the most essential settings that will allow the Tethys development server to function based on the options that were passed to the script or based on the default values of those options. If you would like to further customize the settings then open the :file:`settings.py` file and make any desired changes. Refer to the :doc:`settings` documentation for a description of each of the settings.
