.. _azure_vm_apps_app_store:

************************
Install Tethys App Store
************************

**Last Updated:** November 2021

The Tethys App Store is a Tethys app that can be used to publish and install Tethys apps. It can install Tethys apps from its catalog of published apps or directly from GitHub repositories. To learn more about the Tethys App Store, see `Community Apps | Tethys Platform <http://www.tethysplatform.org/community-apps>`_. This section will describe how to install and use the Tethys App Store on the Tethys Platform Azure VM.

.. figure:: ../images/apps--app-store.png
    :width: 800px
    :alt: Screenshot of the Tethys App Store

    **Figure 1.** Screenshot of the Tethys App Store.

1. Login as Tethys User
=======================

Remember, to use the ``tethys`` command, you'll need to login as the ``tethys`` user:

.. code-block::

    sudo su - tethys

2. Activate the Tethys Conda Environment
========================================

.. code-block::

    conda activate tethys

3. Change into the Tethys Home Directory
========================================

.. code-block::

    cd $TETHYS_HOME

4. Install Tethys App Store
===========================

Complete the instructions in the **Install using Miniconda** section of `Installation | Tethys App Store <https://tethys-app-store.readthedocs.io/en/latest/install.html#install-using-miniconda-recommended>`_.

5. Collect Static Files and Workspaces
======================================

It is not necessary to change permissions to collect static files or workspaces in the Azure VM image if you are logged in as the ``tethys`` user. Simply run the following command after installing the app:

.. code-block::

    tethys manage collectall

6. Restart the Tethys Service
=============================

Restart the Tethys service for the new app to be loaded:

.. code-block::

    sudo systemctl restart tethys.service

7. Enable WebSocket Support
===========================

Modify the :file:`tethys_nginx.conf` as follows to enable web socket support:

1. Open the :file:`$TETHYS_HOME/config/tethys_nginx.conf` with your favorite text editor.
2. Add the following lines to the top of the file, above the ``upstream`` section:

    .. code-block::

        # top-level http config for websocket headers
        # If Upgrade is defined, Connection = upgrade
        # If Upgrade is empty, Connection = close
        map $http_upgrade $connection_upgrade {
            default upgrade;
            ''      close;
        }

3. Change the following line:

    from:

    .. code-block::

        proxy_set_header Connection "upgrade";

    to:

    .. code-block::

        proxy_set_header Connection $connection_upgrade;

8. Restart the NGINX Service
============================

Restart NGINX to enable changes made to :file:`tethys_nginx.conf`.

.. code-block::

    sudo systemctl restart nginx

9. Add Password to Root User
============================

Run the following command to create a password for the root user. Use a password generator like `xkpasswd <https://xkpasswd.net/s/>`_ or similar to create strong and unique password.

.. code-block::

    sudo -i passwd

10. Login to Tethys Portal with a Portal Admin Account
======================================================

Navigate to the Tethys Portal (see :ref:`View the Tethys Portal <azure_vm_create_view_portal>`) and login with the Portal Admin account.

11. Navigate to Tethys App Store Settings
=========================================

Launch the Tethys App Store app and press the **Settings** button (gear icon) in the top right-hand corner of the page.

12. Set ``sudo_server_pass`` Setting
====================================

Set the value of the ``sudo_server_pass`` setting to the root password you set in step 9. Press the **Save** button to save the settings.

.. figure:: ../images/apps--root-pass-setting.png
    :width: 800px
    :alt: Screenshot of the Tethys App Store Settings.

    **Figure 2.** Screenshot of the Tethys App Store Settings.

13. Install Apps
================

To use the Tethys App Store app to install an app, simply search for the app and press the **Install** button next to it. To submit an app to the Tethys App Store catalog follow these instructions: `Application Submission | Tethys App Store <https://tethys-app-store.readthedocs.io/en/latest/app-submit.html>`_.