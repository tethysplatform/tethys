.. _production_backup:

**************
What to Backup
**************

**Last Updated:** May 2020

Backing up your production Tethys Portal will allow you to quickly recover from hardware failure or other outage. The purpose of this guide is not to provide instructions for setting up backup, but rather to point out the locations where data is stored on a Tethys Portal server.

App Workspaces
==============

The apps often write data to their workspaces that is either user data or critical to the functioning of the app. In a production deployment of Tethys Portal, all workspaces are collected to the ``TETHYS_WORKSPACES_ROOT`` directory. Including the ``TETHYS_WORKSPACES_ROOT`` directory in a backup should be sufficient to restore this data.

To restore lost workspaces from a backup, simply copy the backed-up directory to ``TETHYS_WORKSPACES_ROOT`` and run the ``tethys manage collectworkspaces`` command to relink the workspaces with the apps. 

.. note::

    By default, the ``tethys manage collectworkspaces`` command will not overwrite an app workspace if it is already present in ``TETHYS_WORKSPACES_ROOT``, which is helpful in a restore-from-backup situation.

Static Files
============

We do not recommend that you store dynamic data or user data in the static directories of your apps. This type of information should be stored in app workspaces if possible. However, if your app stores information in the static directory that needs to be backed up you should back up the ``STATIC_ROOT`` directory.

To restore lost static files from a backup, you should:

    1. Run ``tethys manage collectstatic`` to collect all static files.
    2. Copy your backed up static files into the ``STATIC_ROOT``, without replacing existing files if possible.


Database
========

The Tethys Portal database contains user account information and app and portal settings information that should be backed up.

You can backup this data using one of PostgreSQL's utilities like `pg_dump <https://www.postgresql.org/docs/12/app-pgdump.html>`_ or you can backup the data directory on the server directly. The data directory can be found at:

**Ubuntu**:

    .. code-block:: bash
    
        /var/lib/postgresql/<version>/main

**CentOS**:

    .. code-block:: bash
    
        /var/lib/pgsql/<version>/data


Configuration Files
===================

You will likely end up customizing the configuration files for your server beyond the default configuration covered in the installation guide. Backing up these files will save you time needing to reconfigure your Tethys Portal after a loss. At a minimum we recommend backing up the :file:`tethys_portal.yml`. Here is a list of configuration files you may consider backing up:

    * :file:`~/.tethys/portal_config.yml`
    * :file:`~/.tethys/asgi_supervisord.conf`
    * :file:`~/.tethys/nginx_supervisord.conf`
    * :file:`~/.tethys/tethys_nginx.conf`
    * :file:`~/.tethys/tethys-selinux.mod`
    * :file:`~/.tethys/tethys-selinux.te`
    * :file:`~/.tethys/tethys-selinux.pp`


Other App Files
===============

Your apps may store data in other locations on the system that need to be backed up. Don't forget to include these locations in your server backups.