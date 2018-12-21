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

      wget :install_tethys:`sh`
      bash install_tethys.sh -b |branch|

For Systems with `curl` (e.g. Mac OSX and CentOS):

.. parsed-literal::

      curl :install_tethys:`sh` -o ./install_tethys.sh
      bash install_tethys.sh -b |branch|


.. _install_script_options:

Install Script Options
......................

    You can customize your tethys installation by passing command line options to the installation script. The available options can be listed by running::

         $ bash install_tethys.sh --help

    Each option is also descriped here:

        * `-t, --tethys-home <PATH>`:
                Path for tethys home directory. Default is ~/tethys.
        * `-s, --tethys-src <PATH>`:
                Path to the tethys source directory. Default is ${TETHYS_HOME}/src.
        * `-a, --allowed-host <HOST>`:
                Hostname or IP address on which to serve Tethys. Default is 127.0.0.1.
        * `-p, --port <PORT>`:
                Port on which to serve Tethys. Default is 8000.
        * `-b, --branch <BRANCH_NAME>`:
                Branch to checkout from version control. Default is 'release'.
        * `-c, --conda-home <PATH>`:
                Path to conda home directory where Miniconda will be installed, or to an existing installation of Miniconda. Default is ${TETHYS_HOME}/miniconda.

                .. tip::

                    The conda home path cannot contain spaces. If the the tethys home path contains spaces then the `--conda-home` option must be specified and point to a path without spaces.

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
        * `--db-super-username <USERNAME>`:
                Username for super user on the tethys database server. Default is 'tethys_super'.
        * `--db-super-password <PASSWORD>`:
                Password for super user on the tethys database server. Default is 'pass'.
        * `--db-port <PORT>`:
                Port that the tethys database server will use. Default is 5436.
        * `--db-dir <PATH>`:
                Path where the local PostgreSQL database will be created. Default is ${TETHYS_HOME}/psql.
        * `-S, --superuser <USERNAME>`:
                Tethys super user name. Default is 'admin'.
        * `-E, --superuser-email <EMAIL>`:
                Tethys super user email. Default is ''.
        * `-P, --superuser-pass <PASSWORD>`:
                Tethys super user password. Default is 'pass'.
        * `--skip-tethys-install`:
                Flag to skip the Tethys installation so that the Docker installation or production installation can be added to an existing Tethys installation.

                .. tip::

                    If conda home is not in the default location then the `--conda-home` options must also be specified with this option.

        * `--partial-tethys-install <FLAGS>`:
                List of flags to indicate which steps of the installation to do.

                Flags:
                    * `m` - Install Miniconda
                    * `r` - Clone Tethys repository (the `--tethys-src` option is required if you omit this flag).
                    * `c` - Checkout the branch specified by the option `--branch` (specifying the flag `r` will also trigger this flag)
                    * `e` - Create Conda environment
                    * `s` - Create `settings.py` file
                    * `d` - Create a local database server
                    * `i` - Initialize database server with the Tethys database (specifying the flag `d` will also trigger this flag)
                    * `u` - Add a Tethys Portal Super User to the user database (specifying the flag `d` will also trigger this flag)
                    * `a` - Create activation/deactivation scripts for the Tethys Conda environment
                    * `t` - Create the `t` alias to activate the Tethys Conda environment

                For example, if you already have Miniconda installed and you have the repository cloned and have generated a `settings.py` file, but you want to use the install script to:

                    * create a conda environment,
                    * setup a local database server,
                    * create the conda activation/deactivation scripts, and
                    * create the `t` shortcut,

                then you can run the following command::

                    bash install_tethys.sh --partial-tethys-install edat

                .. warning::

                    If `--skip-tethys-install` is used then this option will be ignored.

        * `--install-docker`:
                Flag to include Docker installation as part of the install script (Linux only). See `2. Install Docker (OPTIONAL)`_ for more details.

        * `--docker-options <OPTIONS>`:
                Command line options to pass to the `tethys docker init` call if --install-docker is used. Default is "'-d'".

                .. tip::

                    The value for the `--docker-options` option must have nested quotes. For example "'-d -c geoserver'" or '"-d -c geoserver"'.
        * `--production`
                Flag to install Tethys in a production configuration.
        * `--configure-selinux`
                Flag to perform configuration of SELinux for production installation. (Linux only).
        * `-x`:
                Flag to turn on shell command echoing.
        * `-h, --help`:
                Print this help information.

    Here is an example of calling the installation script with customized options::

        $ bash install_tethys.sh -t ~/Workspace/tethys -a localhost -p 8005 -c ~/miniconda3 --db-username tethys_db_user --db-password db_user_pass --db-port 5437 -S tethys -E email@example.com -P tpass

The installation script may take several minutes to run. Once it is completed you will need to activate the new conda environment so you can start the Tethys development server. This is most easily done using an alias created by the install script. To enable the alias you need to open a new terminal or re-run the :file:`.bashrc` (Linux) or :file:`.bash_profile` (Mac) file.

For Linux::

    $ . ~/.bashrc

For Mac::

    $ . ~/.bash_profile

 You can then activate the Tethys conda environment and start the Tethys development server by running::

    $ t
    (tethys) $ tethys manage start

or simply just::

    $ t
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
    - `tstart`:
            Combines the `tethys_start_db` and the `tms` commands.

    When installing Tethys in production mode the following additional environmental variables and aliases are added:

    - `NGINX_USER`:
            The name of the Nginx user.
    - `NGINX_HOME`:
            The home directory of the Nginx user.
    - `tethys_user_own`:
            Changes ownership of relevant files to the current user by running the command `sudo chown -R ${USER} ${TETHYS_HOME}/src ${NGINX_HOME}/tethys`.
    - `tuo`:
            Another alias for `tethys_user_own`
    - `tethys_server_own`:
            Reverses the effects of `tethys_user_own` by changing ownership back to the Nginx user.
    - `tso`:
            Another alias for `tethys_server_own`

     When you start up a new terminal there are three steps to get the Tethys development server running again:

        1. Activate the Tethys conda environment
        2. Start the Tethys database server
        3. start the Tethys development server

    Using the supplied aliases, starting the Tethys development server from a fresh terminal can be done with the following two commands::

        $ t
        (tethys) $ tstart

Congratulations! You now have Tethys Platform running a in a development server on your machine. Tethys Platform provides a web interface that is called the Tethys Portal. You can access your Tethys Portal by opening `<http://localhost:8000/>`_ (or if you provided custom host and port options to the install script then it will be `<HOST>:<PORT>`) in a new tab in your web browser.

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px


To log in, use the credentials that you specified with the `-S` or `--superuser` and the `-P` or `--superuser-pass` options. If you did not specify these options then the default credentials are:

    * username: `admin`
    * password:  `pass`


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

The Tethys installation script created a settings file called :file:`settings.py` in the directory :file:`$TETHYS_HOME/src/tethys_apps`. The installation script has defined the most essential settings that will allow the Tethys development server to function based on the options that were passed to the script or based on the default values of those options. If you would like to further customize the settings then open the :file:`settings.py` file and make any desired changes. Refer to the :doc:`./platform_settings` documentation for a description of each of the settings.
