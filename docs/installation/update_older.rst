.. _update_tethys_older:

***************************
Upgrade from Older Versions
***************************

**Last Updated:** July 2022

This document provides instructions for upgrading from versions of Tethys Platform prior to |version|.

Upgrading 3.X Versions
======================

Use these instructions to update Tethys 3.X installations to other versions of Tethys 3 (3.1, 3.2, 3.3, and 3.4). Tethys Platform has become much more stable as of version 3.0 and you shouldn't expect many major breaking changes between different minor versions (e.g. 3.1, 3.2, 3.3). In other words, apps that work in 3.0 should work in 3.1 without any changes. The following steps can be used as a general guide, but additional steps may be required for your specific installation.

Upgrade Steps
-------------

1. Review the :ref:`whats_new` documentation before attempting any upgrade, especially on production servers.

2. :ref:`activate_environment`

3. Update the Tethys Platform package and dependencies by installing the new version of Tethys Platform

    .. tabs::

      .. tab:: Conda

        .. code-block:: bash

          conda install -c conda-forge tethys-platform=3.*
      
      .. tab:: Pip

        .. code-block:: bash

          pip install tethys-platform==3.*

4. Migrate the Tethys Platform database tables::

    tethys db migrate

5. Make any changes to your apps if necessary. This should only be the case when upgrading between major versions (e.g. 3.0 to 4.0). See the :ref:`whats_new` documentation for detailed notes on what changes occur in each release.

.. note::

    In previous versions of Tethys Platform it was required to backup the :file:`settings.py` file before upgrading and then copy your custom settings from the backup to the new :file:`settings.py` file after upgrading. As of version 3.0, this should no longer be the case. All custom settings should be defined in the :file:`portal_config.yml`, which is preserved during upgrades. See: :ref:`tethys_configuration` for more details.

Additional Upgrade Steps for Production Installations
-----------------------------------------------------

The following additional steps may be required for production server upgrades.

1. Collect static files::

    tethys manage collectstatic

2. Restart Daphne and NGINX servers::

    sudo supervisorctl restart all

Upgrading from 2.1 to 3.X
=========================

Many significant changes were made since Tethys Platform 2.1. Please note the following differences:

Source Code
-----------

Tethys in now a conda package! This means that when installing tethys you will no longer clone the source code into TETHYS_HOME. Now Tethys will be installed in your conda environment instead.

TETHYS_HOME
-----------

In 2.1 ``TETHYS_HOME`` by default was located at :file:`~/tethys/`. As of 3.0 ``TETHYS_HOME`` is now, by default at :file:`~/.tethys/`

.. note::

  If your tethys conda environment is named something other than ``tethys`` then ``TETHYS_HOME`` will be at :file:`~/.tethys/<ENV_NAME>/`. For example if your conda environment were named ``tethys-dev`` then ``TETHYS_HOME`` would be at :file:`~/.tethys/tethys-dev/`

Settings
--------

In 2.1 custom settings were specified directly in the :file:`settings.py` file. Now settings must be configured in the :file:`portal_config.yml` file which is generated in ``TETHYS_HOME``

Upgrade Steps
=============

1. :ref:`activate_environment` and uninstall the previous version of ``tethys-platform``::

    pip uninstall tethys-platform

2. Install the new conda packaged version of ``tethys-platform``::

    conda install -c tethysplatform -c conda-forge tethys-platform


3. Rename :file:`~/tethys/` to :file:`~/.tethys/`::

    mv ~/tethys ~/.tethys

4. Generate a :file:`portal_config.yml` file::

    tethys gen portal_config


5.  Port any custom settings from your old :file:`settings.py` to the new :file:`portal_config.yml`:

    Common settings that need to be copied include:
      * DEBUG
      * ALLOWED_HOSTS
      * DATABASES
      * STATIC_ROOT, TETHYS_WORKSPACES_ROOT
      * EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, DEFAULT_FROM_EMAIL
      * SOCIAL_OAUTH_XXXX_KEY, SOCIAL_OAUTH_XXXX_SECRET
      * BYPASS_TETHYS_HOME_PAGE

    Refer to :ref:`tethys_configuration` for more details on specifying settings in the :file:`portal_config.yml` file.

6.  Migrate the database:

    If you have a locally installed database then you will need to add a ``DIR`` setting in the ``DATABASES`` setting of the :file:`portal_config.yml` file:
      ::

        DATABASES:
          default:
            NAME: tethys_platform
            USER: tethys_default
            PASSWORD: pass
            HOST: localhost
            PORT: 5436
            DIR: psql

    .. note::

      The ``DIR`` setting is relative to ``TETHYS_HOME``. By default the locally installed database would have been at :file:`~/tethys/psql/`, but now that ``TETHYS_HOME`` has moved the default location is :file:`~/.tethys/psql/`.

    .. tip::

      If you have a locally installed database server then you need to downgrade postgresql to the version that the database was created with.
      ::

        t
        conda install -c conda-forge postgresql=9.5

    Once you have the database settings and dependencies configured properly then you can migrate the database by running:
      ::

        tethys db migrate


    .. tip::

      Refer to the :ref:`tethys_db_cmd` docs for more information on how to use the new ``tethys db`` command.
