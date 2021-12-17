.. _azure_vm_apps_manual:

*********************
Install Apps Manually
*********************

**Last Updated:** November 2021

Installing apps manually on an Azure VM is a similar process as described in :ref:`installing_apps_production` of the :ref:`manual_production_installation` guide, but there are some differences. Use the following steps to install apps on an Azure VM:

1. Login as Tethys User
=======================

Remember, to use the ``tethys`` command, you'll need to login as the ``tethys`` user:

.. code-block::

    sudo su - tethys

2. Activate the Tethys Conda Environment
========================================

.. code-block::

    conda activate tethys

3. Change into the Apps Directory
=================================

A directory for app source code has already been created at :file:`$TETHYS_HOME/apps`.

.. code-block::

    cd $TETHYS_HOME/apps

4. Download App Source Code
===========================

Clone the app source code as suggested in the :ref:`installing_apps_production_app_source` section of  :ref:`installing_apps_production`, using :file:`$TETHYS_HOME/apps` as the ``APP_SOURCES_ROOT``.

5. Install App
==============

Install the app as suggested in the :ref:`installing_apps_production_install_app` section of  :ref:`installing_apps_production`, using :file:`$TETHYS_HOME/apps` as the ``APP_SOURCES_ROOT``.

6. Collect Static Files and Workspaces
======================================

It is not necessary to change permissions to collect static files or workspaces in the Azure VM image if you are logged in as the ``tethys`` user. Simply run the following command after installing the app:

.. code-block::

    tethys manage collectall

7. Restart the Tethys Service
=============================

Restart the Tethys service for the new app to be loaded:

.. code-block::

    sudo systemctl restart tethys.service

8. Configure App Settings
=========================

Configure app settings in the Tethys Portal admin pages if required (see: :ref:`Admin Pages > Tethys Apps <tethys_portal_app_settings>`).

9. Initialize Persistent Stores
===============================

If your app requires a database via the persistent stores API, you will need to initialize it:

    .. code-block:: bash

        tethys syncstores all