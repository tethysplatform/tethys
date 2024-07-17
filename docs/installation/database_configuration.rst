.. _database_configuration:

**********************
Database Configuration
**********************

**Last Updated:** September 2023

Tethys Platform supports several options for setting up a DB server: local, docker, or remote. By default Tethys uses a local SQLite database. When using the default settings, setting up a database can be done with one simple command:

.. code-block:: bash

    tethys db configure

.. note::

    The tethys db command (:ref:`tethys_db_cmd`) will create a local database file in the location specified by the ``NAME`` setting in the ``DATABASES`` section of the :file:`portal_config.yml` file (by default ``tethys_platform.sqlite``). If the value of ``NAME`` is a relative path then the database file will be created relative to directory specified by the ``TETHYS_HOME`` environment variable. By default ``TETHYS_HOME`` is at `~/.tethys`.

For information on additional database settings refer to the :ref:`database_settings` setting.

Using PostreSQL
===============

.. important::

    This feature requires that the PostgreSQL database and the ``psycopg2`` library be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``postgresql`` and ``psycopg2`` using conda as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge postgresql psycopg2

While Tethys Platform uses the SQLite database by default for ease of use in development environments, it has excellent support for PostgreSQL (which is recommended for production). To use a local PostgreSQL database (for development) you will need to change the ``ENGINE`` setting in the ``DATABASES`` section of the :file:`portal_config.yml` file to ``django.db.backends.postgresql``, and you will need to add the ``DIR`` setting in the same section. This can easily be done using the :ref:`tethys_settings_cmd`:

.. code-block:: bash

    tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql --set DATABASES.default.DIR psql

.. note::

    The tethys db command (:ref:`tethys_db_cmd`) will create a local database server in the directory specified by the ``DIR`` setting in the ``DATABASES`` section of the :file:`portal_config.yml` file. If the value of ``DIR`` is a relative path then the database server will be created relative to directory specified by the ``TETHYS_HOME`` environment variable. By default ``TETHYS_HOME`` is at `~/.tethys`.

    As an alternative to creating a local database server you can also configure a Docker DB server (see :ref:`using_docker`). A local database server is only recommended for development environments. For production environments please refer to :ref:`production_installation`.


Using Other Databases
=====================

While many of the convenience tools that Tethys provides only support SQLite and PostgreSQL, Tethys can be configured with other Database engines. See `<https://docs.djangoproject.com/en/5.0/ref/databases/>`_ for more information.