.. _update_tethys:

********************
Upgrade to |version|
********************

**Last Updated:** July 2022

This document provides a recommendation for how to upgrade Tethys Platform to new versions.

Upgrading 3.X to 4.X and 4.X Versions
=====================================

The following instructions can be used for both upgrading from Tethys Platform 3.X to 4.X and updating to new minor versions of 4.X (e.g. 4.1, 4.2, 4.3) when they are released.

Upgrading 3.X to 4.X Notes
--------------------------

You need to have at least Tethys Platform 3.0 installed to use these instructions to upgrade to Tethys 4.X. Apps that were developed with Tethys 3.X will need to be updated to function properly in Tethys 4.X.

Upgrading 4.X Notes
-------------------

After upgrading to Tethys 4.0, there shouldn't be many major breaking changes between minor versions (e.g. 4.1, 4.2, 4.3). In other words, apps that work in Tethys Platform 4.0 should work in 4.1, 4.2, etc. without any changes. The following steps can be used as a general guide, but additional steps may be required for your specific installation.

Upgrade Steps
-------------

1. Review the :ref:`whats_new` documentation before attempting any upgrade, especially on production servers.

2. :ref:`activate_environment`

3. Update the Tethys Platform conda package and dependencies by installing the new version of Tethys Platform:

    .. tabs::

      .. tab:: Conda

        .. code-block:: bash

          conda install -c conda-forge -c tethysplatform tethys-platform=4.*
        
        .. note::

            The order of the channels matters here. In Tethys 3, the ``tethysplatform`` channel was listed before (higher priority) ``conda-forge``. For Tethys 4, this is reversed so that ``conda-forge`` has higher priority.
      
      .. tab:: Pip

        .. code-block:: bash

          pip install tethys-platform==4.*

4. Migrate the Tethys Platform database tables::

    tethys db migrate

5. Make any changes to your apps if necessary. This should only be the case when upgrading between major versions (e.g. 3.0 to 4.0). See the :ref:`whats_new` and :ref:`migrate_3_to_4` documentation for detailed notes on what changes occur in each release.

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
