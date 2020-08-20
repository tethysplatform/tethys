.. _update_tethys:

********************
Upgrade to |version|
********************

**Last Updated:** August 2020

This document provides a recommendation for how to upgrade Tethys Platform to new versions.

Upgrading 3.X Versions
======================

Tethys Platform has become much more stable as of version 3.0 and you shouldn't expect many major breaking changes between different minor versions (e.g. 3.0, 3.1, 3.2). In other words, apps that work in 3.0 should work in 3.1 without any changes. The following steps can be used as a general guide, but additional steps may be required for your specific installation.

Upgrade Steps
-------------

1. Review the :ref:`whats_new` documentation before attempting any upgrade, especially on production servers.

2. Activate the ``tethys`` conda environment::

    conda activate tethys

3. Update the Tethys Platform conda package and dependencies::

    conda update -c tethysplatform -c conda-forge tethys-platform

4. Migrate the Tethys Platform database tables::

    tethys db migrate

5. Make any changes to your apps if necessary. This should only be the case when upgrading between major versions (e.g. 3.0 to 4.0). See the :ref:`whats_new` documentation for detailed notes on what changes occur in each release.

.. note::

    In previous versions of Tethys Platform it was required to back up the :file:`settings.py` file before upgrading and then copy your custom settings from the backup to the new :file:`settings.py` file after upgrading. As of version 3.0, this should no longer be the case. All custom settings should be defined in the :file:`portal_config.yml`, which is preserved during upgrades. See: :ref:`tethys_configuration` for more details.

Additional Upgrade Steps for Production Installations
-----------------------------------------------------

The following additional steps may be required for production server upgrades.

1. Collect static files::

    tethys manage collectstatic

2. Restart Daphne and NGINX servers::

    sudo supervisorctl restart all

.. toctree::
    :maxdepth: 2

    update_older
