.. _installing_apps_production:

*****************************
Installing Apps in Production
*****************************

**Last Updated:** May 2020

Installing apps in a Tethys Portal configured for production can be challenging. Most of the difficulties arise, because Tethys is served by NGINX in production and all the files need to be owned by the NGINX user. The following instructions for installing apps in a production environment are provided to aid administrators of Tethys Portals.


.. _installing_apps_production_activate:

Activate the Tethys Environment
===============================

See :ref:`activate_environment`.

.. _installing_apps_production_app_dir:

Setup App Directory (First Time Only)
=====================================

Create the APP_SOURCES_ROOT directory that you decided on in the preparation section. We recommend creating this directory somewhere in the default web directory of the server (e.g. :file:`/var/www/tethys/apps`).
    
    .. code-block:: bash
    
        sudo mkdir -p <APP_SOURCES_ROOT>
        sudo chown $USER <APP_SOURCES_ROOT>

.. _installing_apps_production_app_source:

Download App Source Code
========================
    
You will need to copy the source code of the app to the server. There are many methods for accomplishing this, but one way is to create a repository for your code in GitHub, BitBucket, or another Git repository. To download the source from a Git repository, change into the app directory and then clone it as follows:
    
    .. code-block:: bash

        cd <APP_SOURCES_ROOT>

    .. code-block:: bash

        sudo git clone <CLONE_URL>
    
    .. note::
    
        Replace ``<CLONE_URL>`` with the URL for your repository. These URLs generally look something like this: ``https://<host>/<username>/<repository_name>.git``.

.. _installing_apps_production_install_app:

Install the App
===============

Execute the install command in the app directory to make Python aware of the app and install any of its dependencies:

    .. code-block:: bash
    
        cd <APP_SOURCES_ROOT>/<REPOSITORY_NAME>

    .. code-block:: bash

        tethys install
    
    .. important::
    
        Installing your app in development mode on a production server (i.e.: ``tethys install -d`` or ``pip install -e .``) is not recommended. Doing so has implications on file permissions that are not accounted for in these instructions. Do so at your own risk.

    .. seealso::
    
        :doc:`../../application` for more information on the installation process.

.. _installing_apps_production_collect:

Collect Static Files and Workspaces
===================================

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

.. _installing_apps_production_restart:

Restart ASGI and NGINX
=======================

Restart ASGI and NGINX services to effect the changes:

    .. code-block:: bash

        sudo supervisorctl restart all

.. _installing_apps_production_app_settings:

Configure Additional App Settings
=================================

Set any additional required settings on the app settings page in the Tethys Portal admin pages (see :ref:`Admin Pages > Tethys Apps <tethys_portal_app_settings>`).

.. _installing_apps_production_persistent_stores:

Initialize Persistent Stores
============================

If your app requires a database via the persistent stores API, you will need to initialize it:

    .. code-block:: bash

        tethys syncstores all
