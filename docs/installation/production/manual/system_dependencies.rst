.. _production_system_dependencies:

***************************
Install System Dependencies
***************************

**Last Updated:** September 2022

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

  **CentOS**:

  .. code-block:: bash

      sudo yum install -y vim nano

wget
----

Wget is used during the installation to download files needed for the installation, like the install script for Miniconda.

  **Ubuntu**:

  .. code-block:: bash

      sudo apt install -y wget

  **CentOS**:

  .. code-block:: bash

      sudo yum install -y wget

PostgreSQL
==========

1. A `PostgreSQL <https://www.postgresql.org/>`_ database is required for a Tethys Portal installation. For a production installation we recommend that you DO NOT use the database that is installed via conda. Instead install PostgreSQL using the system package manager as follows:

    **Ubuntu**:

        .. code-block:: bash

            sudo apt install -y postgresql postgresql-contrib

    **CentOS**:

        .. code-block:: bash

            sudo yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm

        .. code-block:: bash

            sudo dnf -qy module disable postgresql
            sudo dnf -y install postgresql12 postgresql12-server

        Initialize the database:

        .. code-block:: bash

            # Initialize the database
            sudo /usr/pgsql-12/bin/postgresql-12-setup initdb

        Start PostgreSQL and enable it so it starts up automatically when the server restarts:

        .. code-block:: bash

            sudo systemctl start postgresql-12
            sudo systemctl enable postgresql-12
            
.. note::

    You may be wondering why you didn't need to initialize the database and start/enable it when installing PostgreSQL on Ubuntu. This has to do with the differing philosophies between CentOS and Ubuntu. Ubuntu packages are usually installed with a reasonable default configurtaion and already enabled and running, whereas CentOS only installs the binaries and leaves the configurtaion and enabling up to you.


2. Verify that PostgreSQL is Running:

    **Ubuntu**:

        .. code-block:: bash

            sudo systemctl status postgresql

    **CentOS**:

        .. code-block:: bash

            sudo systemctl status postgresql-12

.. note::

    Install PostgreSQL using these instructions if you plan on having the database on the same server as your Tethys Portal. If you plan to use a separate server for your database, you may also use these instructions to install PostgreSQL on that server, but do not run these installation commands on the Tethys Portal server.  These instructions are based on `How To Install and Use PostgreSQL on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04>`_ and `How To Install PostgreSQL 12 on CentOS 7 / CentOS 8 <https://computingforgeeks.com/how-to-install-postgresql-12-on-centos-7/>`_.

Set ``postgres`` Password
-------------------------

1. The ``postgres`` user is the default superuser account that comes installed with PostgreSQL. In this step assign the ``postgres`` user a password so that we can initialize it.

    .. code-block:: bash

        sudo su - postgres
        psql -c "alter user postgres with password '<POSTGRES_PASSWORD>'"
        exit

    .. note::

        Replace ``<POSTGRES_PASSWORD>`` with the password you created during the :ref:`production_preparation` step.

2. On CentOS it is also necessary to enable password authentication for local connections. This is done in the :file:`pg_hba.conf` file as follows:

    **CentOS**:

        .. code-block:: bash

            sudo vim /var/lib/pgsql/12/data/pg_hba.conf

        Change:

        .. code-block:: bash

            # "local" is for Unix domain socket connections only
            local   all             all                                     peer
            # IPv4 local connections:
            host    all             all             127.0.0.1/32            ident
            # IPv6 local connections:
            host    all             all             ::1/128                 ident

        To:

        .. code-block::

            # "local" is for Unix domain socket connections only
            local   all             all                                     md5
            # IPv4 local connections:
            host    all             all             127.0.0.1/32            md5
            # IPv6 local connections:
            host    all             all             ::1/128                 md5

        Then restart PostgreSQL:

        .. code-block::

            sudo systemctl restart postgresql-12

3. Verify that password authentication is working by opening a connection to the database using the commandline client ``psql``:

    .. code-block::

        PGPASSWORD=<POSTGRES_PASSWORD> psql -U postgres

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

            sudo apt install -y postgis postgresql-12-postgis-3

    **CentOS**:

        .. code-block:: bash

            sudo yum install -y epel-release
            sudo dnf config-manager --set-enabled PowerTools
            sudo yum install -y postgis30_12

    .. note::

        These instructions are based on `How To Install PostGIS on Ubuntu 20.04/18.04 | Debian 10 <https://computingforgeeks.com/how-to-install-postgis-on-ubuntu-debian/>`_ and `How To Install PostGIS on CentOS 8 <https://computingforgeeks.com/how-to-install-postgis-on-centos-8-linux/>`_.


NGINX
=====

`NGINX <https://www.nginx.com/resources/wiki/>`_ (pronounced "N-gin-X") is a free and open-source HTTP server and reverse proxy. It is known for its high performance, stability, rich feature set, simple configuration, and low resource consumption. NGINX is used in combination with Daphne as an HTTP server to host Tethys Portal in production.

    Install NGINX as follows:

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo apt install -y nginx

        Disable and stop NGINX because it will be managed with Supervisor

        .. code-block:: bash

            sudo systemctl stop nginx  # Will manage w/ supervisor
            sudo systemctl disable nginx  # Will manage w/ supervisor

    
    **CentOS**:
    
        .. code-block:: bash
        
            sudo yum install -y nginx

    .. note::

        These instructions are based on `How To Install Nginx on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04>`_ and `How to Install Nginx on CentOS 8 <https://linuxize.com/post/how-to-install-nginx-on-centos-8/>`_.

Supervisor
==========

`Supervisor <http://supervisord.org/>`_ is a process control system. It allows users to control and monitor many processes on UNIX-like operating systems. Supervisor is used in the Tethys Portal production deployment to control the NGINX and Daphne server processes.

    1. Install Supervisor as follows:

    **Ubuntu**:

        .. code-block:: bash

            # It is not required to start and enable supervisor when installing from apt on Ubuntu
            sudo apt update
            sudo apt install -y supervisor

    **CentOS**:

        .. code-block:: bash

            sudo yum install -y epel-release

        .. code-block:: bash

            sudo yum update
            sudo yum install -y supervisor

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

        These instructions are based on `Installing Supervisor <http://supervisord.org/installing.html>`_, `Install EPEL <https://fedoraproject.org/wiki/EPEL>`_, and `Installing Supervisor on CentOS 7 <https://cloudwafer.com/blog/how-to-install-and-configure-supervisor-on-centos-7/>`_.


Postfix (Optional)
==================

`Postfix <http://www.postfix.org/>`_ is an email server. You should install Postfix if you plan to support the "forgotten password" feature of Tethys Portal.

    Install Postfix as follows:

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo apt install -y postfix libsasl2-modules
    
    **CentOS**:
    
        .. code-block:: bash
        
            sudo yum install -y postfix cyrus-sasl-plain cyrus-sasl-md5

        Start Postfix and enable it so it starts up automatically when the server restarts:

        .. code-block:: bash

            sudo systemctl enable postfix
            sudo systemctl start postfix
