*****************************
Installing Apps in Production
*****************************

**Last Updated:** August 10, 2015

Installing apps in a Tethys Platform configured for production can be challenging. Most of the difficulties arise, because Tethys is served by Apache in production and all the files need to be owned by the Apache user. The following instructions for installing apps in a production environment are provided to aid administrators of a Tethys Portal.

1. Create a Directory for App Source
====================================

Create a directory on your server that will store the source code for the apps that are installed on your server. For example:

::

    $ sudo mkdir -p /var/www/tethys/apps/

2. Download App Source Code
===========================

You will need to copy the source code of the app to the server. There are many methods for accomplishing this, but one way is to create a repository for your code in GitHub. To download the source from GitHub, clone it as follows:

::

    $ cd /var/www/tethys/apps/
    $ sudo git clone https://github.com/username/tethysapp-my_first_app.git

.. tip::

    Substitute "username" for your GitHub username or organization and substitute "tethysapp-my_first_app" for the name of the repository with your app source code.

3. Install the App
==================

Execute the setup script (``setup.py``) with the ``install`` command to make Python aware of the app and install any of its dependencies:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ cd /var/www/tethys/apps/tethysapp-my_first_app
    (tethys) $ python setup.py install
    (tethys) $ exit

.. tip::

    If you plan to execute the commands in steps 4 - 6, do not run the ``exit`` until after you have completed the commands in these steps. That way you will not need to run the ``sudo su`` and `` . /usr/lib/tethys/bin/activate`` commands multiple times.

4. Collect and Static Files
===========================

The static files for apps are hosted by Apache, which necessitates collecting all of the static files to a single directory. This directory is configured through the ``STATIC_ROOT`` setting in the ``settings.py`` script. Collect the static files with this command:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys manage collectstatic
    (tethys) $ exit


5. Collect Workspaces (optional)
================================

As a means of optimizing storage on the server, the workspaces of apps can be collected to a central location. This location is configured through the ``TETHYS_WORKSPACES_ROOT`` setting in the ``settings.py`` script. Collect the workspaces with this command:

::

    $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys manage collectworkspaces
    (tethys) $ exit

.. tip::

    The ``collectall`` command provides a shortcut for running both ``collectstatic`` and ``collectworkspaces`` commands:

    ::

                 $ sudo su
                 $ . /usr/lib/tethys/bin/activate
        (tethys) $ tethys manage collectall
        (tethys) $ exit

6. Initialize Persistent Stores (optional)
==========================================

If your app requires a database via the persistent stores API, you will need to initialize it:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys syncstores my_first_app
    (tethys) $ exit

7. Change the Ownership of Files to the Apache User
===================================================

The Apache user must own any files that it Apache is serving. This includes the source files, static files, and any workspaces that your app may have. Assuming the sources files, static files, and workspaces are all located in the ``/var/www/tethys/`` directory, the following command will accomplish the change in ownership that is required:

::

    $ sudo chown -R www-data:www-data /var/www/tethys/ /usr/lib/tethys/src/tethys_app/tethysapp/

.. note::

    The name of the Apache user in RedHat or CentOS flavored systems is ``apache``, not ``www-data``.

8. Restart Apache
=================

Restart Apache to effect the changes:

::

    $ sudo service apache2 restart

.. note::

   The command for managing Apache on CentOS or RedHat flavored systems is ``httpd``. Restart as follows:

   ::

       $ sudo service httpd restart

