.. _production_database:

*******************
Production Database
*******************

**Last Updated:** September 2023

In this part of the production deployment guide, you will learn how to initialize and configure the Tethys Portal database for production.

1. Install Python dependencies
==============================

Using a PostgreSQL database for production requires the ``psycopg2`` Python package. Also,  While we do not recommend having your database on the same server as Tethys Portal, the commands to automate setting up and configuring the database require that the PostgreSQL database and the ``psycopg2`` library be installed on the web server. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``postgresql`` and ``psycopg2`` using conda as follows:


    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge postgresql psycopg2

2. Set Database Settings
========================

Set the database settings in the :file:`portal_config.yml` using the ``tethys settings`` command:

    .. code-block:: bash

        tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql --set DATABASES.default.NAME tethys_platform --set DATABASES.default.USER <TETHYS_DB_USERNAME> --set DATABASES.default.PASSWORD <TETHYS_DB_PASSWORD> --set DATABASES.default.HOST <TETHYS_DB_HOST> --set DATABASES.default.PORT <TETHYS_DB_PORT>

    .. note::

        Replace ``<TETHYS_DB_USERNAME>`` and ``<TETHYS_DB_PASSWORD>`` with the values you determined during the :ref:`production_preparation` step. Replace ``<TETHYS_DB_HOST>`` and ``<TETHYS_DB_PORT>`` with the host and port of your database. If you installed the database on the same server as your Tethys Portal, these would be ``localhost`` and ``5432``, respectively.

    .. important::

        **DO NOT USE DEFAULT USERNAMES OR PASSWORDS FOR PRODUCTION DATABASE ACCOUNTS**

3. Create Tethys Database and Database Users
============================================

Use the ``tethys db create`` command to create the database users and tables required by Tethys Portal:

    .. code-block:: bash

        PGPASSWORD=<POSTGRES_PASSWORD> tethys db create --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD>

    .. note::

        Replace ``<TETHYS_DB_USERNAME>``, ``<TETHYS_DB_PASSWORD>``, ``<TETHYS_DB_SUPER_USERNAME>``, ``<TETHYS_DB_SUPER_PASSWORD>``, and ``<POSTGRES_PASSWORD>`` with the values you determined during the :ref:`production_preparation` step. The ``tethys db create`` command uses the :file:`portal_config.yml` to get the normal database user credentials, host, and port.

    .. important::

        **DO NOT USE DEFAULT USERNAMES OR PASSWORDS FOR PRODUCTION DATABASE ACCOUNTS**

4. Create Tethys Database Tables
================================

Run the following command to create the Tethys database tables:

  .. code-block:: bash

      tethys db migrate

5. Create Portal Admin User
===========================

You will need to create at least one Portal Admin account to allow you to login to your Tethys Portal. Create the account as follows:

    .. code-block:: bash

        tethys db createsuperuser --portal-superuser-name <PORTAL_SUPERUSER_USERNAME> --portal-superuser-email '<PORTAL_SUPERUSER_EMAIL>' --portal-superuser-pass <PORTAL_SUPERUSER_PASSWORD>

    .. note::

            Replace ``<PORTAL_SUPERUSER_USERNAME>``, ``<PORTAL_SUPERUSER_EMAIL>``, and ``<PORTAL_SUPERUSER_PASSWORD>`` with the values you determined during the :ref:`production_preparation` step.

    .. important::

        **DO NOT USE DEFAULT USERNAMES OR PASSWORDS FOR PRODUCTION PORTAL ADMIN ACCOUNTS**


Tip: One Command
================

You can accomplish the three steps above using the ``tethys db configure`` command. It is equivalent of running the following commands:

* ``tethys db init`` (skipped if using a Docker or system database)
* ``tethys db start`` (skipped if using a Docker or system database)
* ``tethys db create --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD>``
* ``tethys db migrate``
* ``tethys db createsuperuser --portal-superuser-name <PORTAL_SUPERUSER_USERNAME> --portal-superuser-email '<PORTAL_SUPERUSER_EMAIL>' --portal-superuser-pass <PORTAL_SUPERUSER_PASSWORD>``

Simply pass all arguments to the command:

.. code-block:: bash

    PGPASSWORD=<POSTGRES_PASSWORD> tethys db configure --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <PORTAL_SUPERUSER_USERNAME> --portal-superuser-email '<PORTAL_SUPERUSER_EMAIL>' --portal-superuser-pass <PORTAL_SUPERUSER_PASSWORD>

.. note::
    PostgreSQL is the most supported database backend for a production instance of Tethys Platform. However, it is possible to configure any database backend that is supported by Django (see `Django's Databases Documentation <https://docs.djangoproject.com/en/5.0/ref/databases/>`_). When using an alternative database backend, the Tethys database and database users must be created manually since the `tethys db create` command only supports PostgreSQL databases. The normal commands can still be used for configuring the database settings, and for migrating the tables and creating a superuser.


