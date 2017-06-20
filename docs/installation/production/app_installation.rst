*****************************
Installing Apps in Production
*****************************

**Last Updated:** June, 2017

Installing apps in a Tethys Platform configured for production can be challenging. Most of the difficulties arise, because Tethys is served by Nginx in production and all the files need to be owned by the Nginx user. The following instructions for installing apps in a production environment are provided to aid administrators of a Tethys Portal.

1. Change the Ownership of Files to the Current User
====================================================

During the production installation any Tethys related files were change to be owned by the Nginx user. To make any changes on the server it is easiest to change the ownership back to the current user. This is easily done with an alias that was created in the tethys environment during the production installation process::

    $ t
    (tethys) $ tethys_user_own

3. Download App Source Code
===========================

You will need to copy the source code of the app to the server. There are many methods for accomplishing this, but one way is to create a repository for your code in GitHub. To download the source from GitHub, clone it as follows::

    $ cd $TETHYS_HOME/apps/
    $ sudo git clone https://github.com/username/tethysapp-my_first_app.git

.. tip::

    Substitute "username" for your GitHub username or organization and substitute "tethysapp-my_first_app" for the name of the repository with your app source code.

4. Install the App
==================

Execute the setup script (:file:`setup.py`) with the ``install`` command to make Python aware of the app and install any of its dependencies::

    (tethys) $ cd cd $TETHYS_HOME/apps/tethysapp-my_first_app
    (tethys) $ python setup.py install

5. Collect and Static Files and Workspaces
==========================================

The static files and files in app workspaces are hosted by Nginx, which necessitates collecting all of the static files to a single directory and all workspaces to another single directory. These directory is configured through the ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` setting in the :file:`settings.py` file. Collect the static files and workspaces with this command::

    (tethys) $ tethys manage collectall

6. Change the Ownership of Files to the Nginx User
==================================================

The Nginx user must own any files that Nginx is serving. This includes the source files, static files, and any workspaces that your app may have. The following alias will accomplish the change in ownership that is required::

    (tethys) $ tethys_server_own

7. Restart uWSGI and Nginx
==========================

Restart uWSGI and Nginx services to effect the changes::

    $ sudo systemctl restart tethys.uwsgi.service
    $ sudo systemctl restart nginx

.. tip::

    Use the alias `trestart` as a shortcut to doing both steps 6 and 7.

8. Configure App Settings
=========================

Set all required settings on the app settings page in the Tethys Portal admin pages (see :doc:`../../tethys_portal/admin_pages`).

9. Initialize Persistent Stores
===============================

If your app requires a database via the persistent stores API, you will need to initialize it::

    $ t
    (tethys) $ tethys syncstores all

