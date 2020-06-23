.. _installing_apps_production:

*****************************
Installing Apps in Production
*****************************

**Last Updated:** May 2020

Installing apps in a Tethys Portal configured for production can be challenging. Most of the difficulties arise, because Tethys is served by NGINX in production and all the files need to be owned by the NGINX user. The following instructions for installing apps in a production environment are provided to aid administrators of Tethys Portals.

Activate the Tethys Environment
===============================

    .. code-block:: bash
    
        conda activate tethys

Setup App Directory (First Time Only)
=====================================

Decide on a location to download the app code. We recommend creating a :file:`/var/www/tethys/apps` directory:
    
    .. code-block:: bash
    
        sudo mkdir -p /var/www/tethys/apps
        sudo chown $USER /var/www/tethys/apps

Download App Source Code
========================
    
You will need to copy the source code of the app to the server. There are many methods for accomplishing this, but one way is to create a repository for your code in GitHub, BitBucket, or another Git repository. To download the source from a Git repository, change into the app directory and then clone it as follows:
    
    .. code-block:: bash
    
        cd /var/www/tethys/apps

    .. code-block:: bash

        sudo git clone <CLONE_URL>
    
    .. note::
    
        Replace ``<CLONE_URL>`` with the URL for your repository. These URLs generally look something like this: ``https://<host>/<username>/<repository_name>.git``.

Install the App
===============

Execute the install command in the app directory to make Python aware of the app and install any of its dependencies:

    .. code-block:: bash
    
        cd /var/www/tethys/apps/<APP_DIR>

    .. code-block:: bash

        tethys install
    
    .. seealso::
    
        :doc:`../application` for more information on the installation process.

Collect and Static Files and Workspaces
=======================================

You will need to collect the workspaces and static files from the new app to the ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` directories. This is easily done using the ``collectall`` command. However, you will need to change ownership the ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` directories to your user before you can successfully run ``collectall``. Don't forget to change ownership of these files back to the ``NGINX_USER`` after you are done.

1. Change the Ownership of Files to the Current User
    
    .. code-block:: bash
    
        sudo chown -R $USER <STATIC_ROOT>
        sudo chown -R $USER <TETHYS_WORKSPACES_ROOT>
    
    .. note::
    
        Replace ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` with the paths to the directories you set up in the :ref:`production_static_workspaces_dirs` step.

2. Run ``collectall`` Command
    
    .. code-block:: bash
    
        tethys manage collectall

3. Change the Ownership of Files Back to the NGINX User

    .. code-block:: bash


        sudo chown -R <NGINX_USER>: <STATIC_ROOT>
        sudo chown -R <NGINX_USER>: <TETHYS_WORKSPACES_ROOT>

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in the :ref:`production_nginx_config` step. Replace ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` with the paths to the directories you set up in the :ref:`production_static_workspaces_dirs` step.

.. tip::

    If you setup the shortcuts earlier, you can use them now to make installation of new apps a little easier (see: :ref:`setup_file_permissions_shortcuts`):

    .. code-block:: bash

        tethys_user_own
        collectall
        tethys_server_own

Restart ASGI and NGINX
=======================

Restart ASGI and NGINX services to effect the changes:

    .. code-block:: bash

        sudo supervisorctl restart all

Configure Additional App Settings
=================================

Set any additional required settings on the app settings page in the Tethys Portal admin pages (see :doc:`../../tethys_portal/admin_pages`).

Initialize Persistent Stores
============================

If your app requires a database via the persistent stores API, you will need to initialize it:

    .. code-block:: bash

        tethys syncstores all
