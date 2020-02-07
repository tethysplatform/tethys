***********************
Production Installation
***********************

**Last Updated:** January 2020

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. Currently production installation of Tethys is only supported on Linux. Some parts of these instructions are optimized for Ubuntu, though installation on other Linux distributions will be similar.

1. Install Tethys Platform Configured for Production
====================================================

Follow these steps to install Tethys Portal with the following considerations:

* Make sure to install the correct version.
* Assign strong passwords to the database users.
* You must edit the :file:`portal_config.yml` file to ensure production settings (i.e. ``DEBUG: False``, etc.).
* Optionally, Follow the :doc:`./distributed` instructions to install Docker and the components of the software suite on separate servers.
* For Linux distributions with SELinux enabled (e.g.: CentOS, RedHat, Fedora), set correct SELinux permissions.

1) Install Tethys Platform using the Conda package.


    To install ``tethys-platform`` into a new conda environment then run the following commands:

    .. code-block:: bash

        conda create -n tethys -c tethysplatform -c conda-forge tethys-platform
        conda activate tethys

2) Install Additional Software:

    The method of installing each of the following software is dependent on the specific Linux distribution you are using. Please refer to the installation instructions for each software to find instructions appropriate for your Linux distribution.

    * Supervisor (**install using system package if possible**, see `<http://supervisord.org/installing.html>`_).
        .. note::

            On **CentOS** run the following after installing to get supervisor running:

            .. code-block::

                sudo systemctl enable supervisord
                sudo systemctl start supervisord

    * NGINX (See `<https://www.nginx.com/resources/wiki/start/topics/tutorials/install/>`_).
    * Install Docker (**Optional**, see `<https://docs.docker.com/install/>`_).
    * Install PostgresSQL

        We recommend not using the Postgresql database installed in the Tethys Conda environment for production installations. Instead, use one of these methods:

        1. System installation: see `<https://www.postgresql.org/download/>`_ to find instructions for your Linux distribution.
        2. Docker Alternative (*requires previous Docker installation*): Get Postgres Docker image with the PostGIS extension from `<https://hub.docker.com/r/mdillon/postgis/>`_

        .. tip::

            The tethys Docker command can be used to get the PostGIS Docker image

            .. code-block:: bash

                tethys docker init -c postgis

3) Create :file:`portal_config.yml`:

    Generate the portal configuration file with the following command:

    .. code-block::

        tethys gen portal_config

    .. note::

        This file is generated in your ``TETHYS_HOME`` directory. It can be edited directly or using the ``tethys settings`` command. See: :ref:`tethys_configuration` and :ref:`tethys_settings_cmd`.

4) Note the Location of ``TETHYS_HOME``

    The directory where the :file:`portal_config.yml` is generated is the ``TETHYS_HOME`` directory for your installation.

    The default location of ``TETHYS_HOME`` is :file:`~/.tethys/` if your environment is named Tethys, otherwise it is :file:`~/.tethys/<env_name>/`.

    **Note this location and use it in the following steps where you see ``<TETHYS_HOME>``.**

5) Configure Settings for Production:

    Use the ``tethys settings`` command to set the following settings (see :ref:`tethys_settings_cmd`). **DO NOT EDIT settings.py DIRECTLY IN TETHYS 3+**.

    * Set Allowed Hosts:

        .. code-block::

            tethys settings --set ALLOWED_HOSTS "['my.example.host', 'localhost']"

        .. note::

            The first entry in ``ALLOWED_HOSTS`` will be used to set the server name in the nginx configuration file.

    * Set Database Parameters:

        .. code-block::

            tethys settings --set DATABASES.default.USER <TETHYS_DB_USERNAME> --set DATABASES.default.PASSWORD <TETHYS_DB_PASSWORD> --set DATABASES.default.HOST <TETHYS_DB_HOST> --set DATABASES.default.PORT <TETHYS_DB_PORT>

        .. important::

            Do not use the default username or password for the production Tethys database. Also ensure the host and port match the host and port that your database is running on.

    * Disable Debug:

        .. code-block::

            tethys settings --set DEBUG False

6) Setup Tethys Database:

    Create the Tethys Database using the ``tethys db`` command (see :ref:`tethys_db_cmd`):

    .. code-block::

        tethys db configure --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>

    .. tip::

        The ``TETHYS_DB_USERNAME`` and ``TETHYS_DB_PASSWORD`` need to be the same as those set in the portal config (see pervious step).

    .. note::

        Running ``tethys db configure`` is equivalent of running the following commands:

        * ``tethys db init`` (skip if using a Docker or system database)
        * ``tethys db start`` (skip if using a Docker or system database)
        * ``tethys db create --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD>``
        * ``tethys db migrate``
        * ``tethys db createsuperuser --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>``

    .. tip::

        You need to prepend the ``tethys db`` commands with the password for the postgres user of the database when using a Docker or a system install:

        .. code-block:: bash

            $ PGPASSWORD="<POSTGRES_PASSWORD>" tethys db configure --username <USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>

7) Make Directories for Workspaces and Static Files

    Get the values of the static and workspace directories in settings:

    .. code-block::

        tethys settings --get STATIC_ROOT
        tethys settings --get TETHYS_WORKSPACES_ROOT

    Create the directories if they do not already exist

    .. code-block::

        mkdir -p <STATIC_ROOT>
        mkdir -p <TETHYS_WORKSPACE_ROOT>

8) Collect Static Files and App Workspaces:

    .. code-block::

        tethys manage collectall --noinput

    .. tip::

        The ``tethys manage collectall`` command is equivalent of:

        .. code-block::

            tethys manage collectstatic
            tethys manage collectworkspaces

9) Note ``nginx`` User for Permissions


    Get the ``nginx`` user for permissions changes in the follow steps.

    .. code-block::

        grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}'

    Note this user and use it in the following steps where you see ``<NGINX_USER>``.

10) Setup Log File

    This is the file to which Tethys logs will be written.

    .. code-block::

        sudo mkdir -p /var/log/tethys
        sudo touch /var/log/tethys/tethys.log

    .. code-block::

        sudo chown -R <NGINX_USER>: /var/log/tethys

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

11) Setup ASGI Run Directory

    This directory is used for housing the socket files for the Daphne/ASGI processes.

    .. code-block::

        sudo mkdir -p /run/asgi

    .. code-block::

        sudo chown -R <NGINX_USER>: /run/asgi

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

12) Generate ``nginx`` and ``supervisor`` Configuration Files:

    Generate and review the contents of the following configuration files for ``nginx`` and ``supervisor``. Adjust to match your deployment's needs if necessary.

    .. code-block::

        tethys gen nginx --overwrite
        tethys gen nginx_service --overwrite
        tethys gen asgi_service --overwrite

    .. tip::

        These files are generated in the ``TETHYS_HOME`` directory.

13) Configure ``nginx`` and ``supervisor`` to Use Tethys Configurations:

    Creates symbolic links to configuration file in the appropriate ``/etc`` directories:

    Debian and Ubuntu:

    .. code-block::

        sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisor/conf.d/asgi_supervisord.conf
        sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisor/conf.d/nginx_supervisord.conf
        sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/sites-enabled/tethys_nginx.conf

        # Remove the default nginx configuration
        sudo rm /etc/nginx/sites-enabled/default

    Fedora, CentOS, RedHat

    .. code-block::

        sudo sed -i '$ s@$@ /etc/supervisord.d/*.conf@' "/etc/supervisord.conf"
        sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisord.d/asgi_supervisord.conf
        sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisord.d/nginx_supervisord.conf
        sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/conf.d/tethys_nginx.conf

14) Change Permissions of Tethys Directories

    Many of the directories and files need to be owned by the ``nginx`` user for Tethys to access them while running in production.

    .. code-block::

        sudo chown -R <NGINX_USER>: <STATIC_ROOT>
        sudo chown -R <NGINX_USER>: <TETHYS_WORKSPACE_ROOT>

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

    Change access to the home directory to full access for owners, no access for group, and read execute for other:

    .. code-block::

        sudo chmod 705 ~

    .. tip::

        You will often need to change the permissions of ``TETHYS_HOME``, ``STATIC_ROOT``, and ``TETHYS_WORKSPACES_ROOT`` to your user and back to the ``nginx`` user when performing maintenance operations. Define these aliases in the activate script of your environment to make it easier:

        .. code-block::

            export ACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/activate.d/tethys-activate.sh"
            export DEACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/deactivate.d/tethys-deactivate.sh"
            export STATIC_ROOT="<STATIC_ROOT>"
            export TETHYS_WORKSPACE_ROOT="<TETHYS_WORKSPACE_ROOT>"
            export TETHYS_HOME="<TETHYS_HOME>"
            export NGINX_USER="<NGINX_USER>"

            echo "alias tethys_user_own='sudo chown -R \${USER} \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"
            echo "alias tethys_server_own='sudo chown -R ${NGINX_USER}: \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"
            echo "alias tethys_server_restart='tso; sudo supervisorctl restart all;'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tsr=tethys_server_restart" >> "${ACTIVATE_SCRIPT}"

            echo "unalias tethys_user_own" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tethys_server_restart" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tsr" >> "${DEACTIVATE_SCRIPT}"

15) Reload and Update ``supervisor`` configuration:

    .. code-block::

        sudo supervisorctl reread
        sudo supervisorctl update

    .. note::

        This step needs to be performed anytime you make changes to the ``nginx_supervisord.conf`` or ``asgi_supervisord.conf``

16) Open HTTP Port on Firewall (if applicable)

    If your server employs a firewall, open the HTTP port like so:

    .. code-block::

        sudo firewall-cmd --permanent --zone=public --add-service=http
        sudo firewall-cmd --reload

    .. note::

        The commands to manage your firewall may differ. Ensure the HTTP port (80) is open.

17) Configure SELinux (CentOS, RedHat, Fedora)

    If your server is running Security Enhanced Linux, you will need to create a security policy for Tethys. This is typically the case on CentOS, RedHat, and Fedora systems. The following is what the installation script does to configure SELinux, but you should not rely on this for your own deployment without understanding what it is doing (see: `Security-Enhanced Linux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `CentOS SELinux <https://wiki.centos.org/HowTos/SELinux>`_, `RedHat SELinux <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/ch-selinux>`_). **USE AT YOUR OWN RISK**:

    .. code-block::

        sudo chown ${USER} <TETHYS_HOME>
        sudo yum install setroubleshoot -y
        sudo semanage fcontext -a -t httpd_config_t <TETHYS_HOME>/tethys_nginx.conf
        sudo restorecon -v <TETHYS_HOME>/tethys_nginx.conf
        sudo semanage fcontext -a -t httpd_sys_content_t "<TETHYS_HOME>(/.*)?"
        sudo semanage fcontext -a -t httpd_sys_content_t "<STATIC_ROOT>(/.*)?"
        sudo semanage fcontext -a -t httpd_sys_rw_content_t "<TETHYS_WORKSPACE_ROOT>(/.*)?"
        sudo restorecon -R -v <TETHYS_HOME> > /dev/null
        echo $'module tethys-selinux-policy 1.0;\nrequire {type httpd_t; type init_t; class unix_stream_socket connectto; }\n#============= httpd_t ==============\nallow httpd_t init_t:unix_stream_socket connectto;' > <TETHYS_HOME>/tethys-selinux-policy.te

        checkmodule -M -m -o <TETHYS_HOME>/tethys-selinux-policy.mod <TETHYS_HOME>/tethys-selinux-policy.te
        semodule_package -o <TETHYS_HOME>/tethys-selinux-policy.pp -m <TETHYS_HOME>/tethys-selinux-policy.mod
        sudo semodule -i <TETHYS_HOME>/tethys-selinux-policy.pp
        sudo chown <NGINX_USER> <TETHYS_HOME>

2. Review the Django Deployment Checklist
=========================================

.. important::

    Review the `Django Deployment Checklist <https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/>`_ carefully. Remember, do not edit the settings.py file directly, instead use the ``tethys settings`` command or edit the ``settings`` section of the :file:`portal_config.yml` to change Django settings.

3. Additional Installation and Configuration:
=============================================

You may wish to complete the following optional steps as part of your setup:

.. toctree::
    :maxdepth: 1

    ssl_config
    email_config

4. Install Apps
===============

Download and install any apps that you want to host using this installation of Tethys Platform. For more information see: :doc:`./app_installation`.


.. tip::

    **Troubleshooting**: If you are experiencing problems please search for a solution or post a question on the `Tethys Platform Forum <https://groups.google.com/forum/#!forum/tethysplatform>`_.


