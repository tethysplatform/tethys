.. _production_system_dependencies:

***************************
Install System Dependencies
***************************

**Last Updated:** September 2024

This guide describes how to install the necessary system dependencies. You will need ``sudo`` or root access on the server to complete these steps.

Tools
=====

The following applications will be used during the installation process, but not necessarily needed by Tethys Portal.

Text Editor
-----------

You will need a text editor to modify the configuration files during the installation.

  **Ubuntu**:

  .. code-block:: bash

      sudo apt install -y vim nano

  **Rocky Linux**:

  .. code-block:: bash

      sudo dnf install -y vim nano

wget
----

Wget is used during the installation to download files needed for the installation, like the install script for Miniconda.

  **Ubuntu**:

  .. code-block:: bash

      sudo apt install -y wget

  **Rocky Linux**:

  .. code-block:: bash

      sudo dnf install -y wget

PostgreSQL
==========

1. A `PostgreSQL <https://www.postgresql.org/>`_ database is required for a Tethys Portal installation. For a production installation we recommend that you DO NOT use the database that is installed via conda. Instead install PostgreSQL using the system package manager as follows:

    **Ubuntu**:

        .. code-block:: bash

            sudo apt install -y postgresql postgresql-contrib

    **Rocky Linux**:

        .. code-block:: bash

            sudo dnf install -y postgresql-server glibc-all-langpacks

        Initialize the database:

        .. code-block:: bash

            # Initialize the database
            sudo postgresql-setup --initdb

        Start PostgreSQL and enable it so it starts up automatically when the server restarts:

        .. code-block:: bash

            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
.. note::

    You may be wondering why you didn't need to initialize the database and start/enable it when installing PostgreSQL on Ubuntu. This has to do with the differing philosophies between Rocky Linux and Ubuntu. Ubuntu packages are usually installed with a default configurtaion and already enabled and running, whereas Rocky Linux only installs the binaries and leaves the configurtaion and enabling up to you.


2. Verify that PostgreSQL is Running:

    **Both**:

        .. code-block:: bash

            sudo systemctl status postgresql

.. note::

    Install PostgreSQL using these instructions if you plan on having the database on the same server as your Tethys Portal. If you plan to use a separate server for your database, you may also use these instructions to install PostgreSQL on that server, but do not run these installation commands on the Tethys Portal server. These instructions are based on `How To Install and Use PostgreSQL on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04>`_ and `How To Install and Use PostgreSQL on Rocky Linux 9 <https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-rocky-linux-9>`_.

Set ``postgres`` Password
-------------------------

1. The ``postgres`` user is the default superuser account that comes installed with PostgreSQL. In this step assign the ``postgres`` user a password so that we can initialize it.

    .. code-block:: bash

        sudo su - postgres
        psql -c "alter user postgres with password '<POSTGRES_PASSWORD>'"
        exit

    .. note::

        Replace ``<POSTGRES_PASSWORD>`` with the password you created during the :ref:`production_preparation` step.

2. On Rocky Linux it is also necessary to enable password authentication for local IP connections. This is done in the :file:`pg_hba.conf` file as follows:

    **Rocky Linux**:

        .. code-block:: bash

            sudo vim /var/lib/pgsql/data/pg_hba.conf

    **pg_hba.conf**:

        Change:

        .. code-block:: bash

            # "local" is for Unix domain socket connections only
            local   all             all                                     peer
            # IPv4 local connections:
            host    all             all             127.0.0.1/32            ident
            # IPv6 local connections:
            host    all             all             ::1/128                 ident
            # Allow replication connections from localhost, by a user with the
            # replication privilege.
            local   replication     all                                     peer
            host    replication     all             127.0.0.1/32            ident
            host    replication     all             ::1/128                 ident

        To:

        .. code-block:: bash

            # "local" is for Unix domain socket connections only
            local   all             all                                     peer
            # IPv4 local connections:
            host    all             all             127.0.0.1/32            md5
            # IPv6 local connections:
            host    all             all             ::1/128                 md5
            # Allow replication connections from localhost, by a user with the
            # replication privilege.
            local   replication     all                                     peer
            host    replication     all             127.0.0.1/32            md5
            host    replication     all             ::1/128                 md5


    **Rocky Linux**:

    Then restart PostgreSQL:

        .. code-block::

            sudo systemctl restart postgresql

3. Verify that password authentication is working by opening a connection to the database using the commandline client ``psql``:

    .. code-block::

        PGPASSWORD=<POSTGRES_PASSWORD> psql -U postgres -h localhost

    To quit ``psql`` type ``\q`` and press ``Enter``.

    .. tip::

        If authentication isn't working, try rebooting the system and trying again. This can be done by running:

        .. code-block::

            sudo shutdown -r now

        For more information on this topic see: `Solution of psql: FATAL: Peer authentication failed for user “postgres” (or any user) <https://gist.github.com/AtulKsol/4470d377b448e56468baef85af7fd614>`_


PostGIS Extension (Optional)
----------------------------

`PostGIS <https://postgis.net/>`_ is an extension for PostgreSQL that adds spatial data types and functions. Using PostGIS you can create databases with columns that can store features and rasters similar to ArcGIS geodatabases. You can also perform common geoprocessing analyses using the spatial database functions.

    If the app(s) you plan to install on this server require a spatial persistent store, then install PostGIS as follows:

    **Ubuntu**:

        .. code-block:: bash

            sudo apt install -y postgis postgresql-16-postgis-3

    **Rocky Linux**:

        .. code-block:: bash

            # Install the Postgresql repository
            sudo yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

            # Install EPEL repo RPM:
            sudo dnf -y install epel-release

            # Enable additional repositories to resolve dependencies
            sudo dnf config-manager --enable crb

            # Disable default PostgreSQL AppStream repository.
            sudo dnf -qy module disable postgresql

            # Select the right PostGIS and PostgreSQL versions
            sudo yum -y install postgis32_13

            # Restart postgresql
            systemctl restart postgresql

    .. note::

        These instructions are based on `Users Wiki: Ubuntu Install Guide <https://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS3UbuntuPGSQLApt>`_ and `Install PostGIS on Rocky Linux 8|CentOS 8|AlmaLinux 8 <https://computingpost.medium.com/install-postgis-on-rocky-linux-8-centos-8-almalinux-8-fa384a6ee920>`_.


NGINX (Recommended)
===================

`NGINX <https://docs.nginx.com>`_ (pronounced "N-gin-X") is a free and open-source HTTP server and reverse proxy. It is known for its high performance, stability, rich feature set, simple configuration, and low resource consumption. NGINX is used in combination with Daphne as an HTTP server to host Tethys Portal in production.

    Install NGINX as follows:

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo apt install -y nginx

        Disable and stop NGINX because it will be managed with Supervisor

        .. code-block:: bash

            sudo systemctl stop nginx
            sudo systemctl disable nginx

    
    **Rocky Linux**:
    
        .. code-block:: bash
        
            sudo dnf install -y nginx

    .. note::

        These instructions are based on `How To Install Nginx on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04>`_ and `How To Install Nginx on Rocky Linux 9 <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-rocky-linux-9>`_.

Apache (Optional)
=================

`Apache <https://httpd.apache.org/>`_ is a free and open-source cross-platform web server software. If you prefer to use Apache instead of NGINX, you can install it as follows:

    **Ubuntu**:

        .. code-block:: bash

            sudo apt install -y apache2

        Disable and stop Apache because it will be managed with Supervisor

        .. code-block:: bash

            sudo systemctl stop apache2
            sudo systemctl disable apache2

    **Rocky Linux**:

        .. code-block:: bash

            sudo dnf install -y httpd

    .. note::

        These instructions are based on `How To Install the Apache Web Server on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-20-04>`_ and `How to install Apache on Rocky Linux 9 <https://www.linuxteck.com/how-to-install-apache-on-rocky-linux/>`_.

Supervisor
==========

`Supervisor <https://supervisord.org/>`_ is a process control system. It allows users to control and monitor many processes on UNIX-like operating systems. Supervisor is used in the Tethys Portal production deployment to control the NGINX and Daphne server processes.

    1. Install Supervisor as follows:

    **Ubuntu**:

        .. code-block:: bash

            # It is not required to start and enable supervisor when installing from apt on Ubuntu
            sudo apt update
            sudo apt install -y supervisor

    **Rocky Linux**:

        .. code-block:: bash

            # If you haven't already, install the EPEL repository
            sudo dnf install -y epel-release

        .. code-block:: bash

            # Install supervisor
            sudo dnf install -y supervisor

        Start Supervisor and enable it so it starts up automatically when the server restarts:

        .. code-block:: bash

            sudo systemctl start supervisord
            sudo systemctl enable supervisord

    2. Use these commands to start, stop, and restart Supervisor:

    .. code-block:: bash

        sudo systemctl start supervisord
        sudo systemctl stop supervisord
        sudo systemctl restart supervisord

    .. note::

        These instructions are based on `Installing Supervisor <https://supervisord.org/installing.html>`_, `Install EPEL <https://docs.fedoraproject.org/en-US/epel/>`_, and `How to install Supervisor on RHEL/CentOS/AlmaLinux/RockyLinux <https://www.hostround.com/one/knowledgebase/100/How-to-install-Supervisor-on-RHELorCentOSorAlmaLinuxorRockyLinux.html>`_.


Postfix (Optional)
==================

`Postfix <http://www.postfix.org/>`_ is an email server. You should install Postfix if you plan to support the "forgotten password" feature of Tethys Portal.

    Install Postfix as follows:

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo apt install -y postfix libsasl2-modules
    
    **Rocky Linux**:
    
        .. code-block:: bash
        
            sudo dnf install -y postfix cyrus-sasl-plain cyrus-sasl-md5

        Start Postfix and enable it so it starts up automatically when the server restarts:

        .. code-block:: bash

            sudo systemctl enable postfix
            sudo systemctl start postfix
