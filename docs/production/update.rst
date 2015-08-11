**********************
Update from 1.1 to 1.2
**********************

**Last Updated:** August 11, 2015

1. Pull Repository
==================

When you installed Tethys Platform you did so using it's remote Git repository on GitHub. To get the latest version of Tethys Platform, you will need to pull the latest changes from this repository. However, the repository has moved from where it was for version 1.1.0, so first you need to set the URL of the remote repository to point its new location. All of this can be done as follows:

::

    $ sudo su
    $ cd /usr/lib/tethys/src
    $ git remote set-url https://github.com/tethysplatform/tethys
    $ git pull origin master
    $ exit

2. Install Requirements and Run Setup Script
============================================

Install new dependencies and upgrade old ones:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ pip install --upgrade -r /usr/lib/tethys/src/requirements.txt
    (tethys) $ python /usr/lib/tethys/src/setup.py develop
    (tethys) $ exit

3. Sync the Database
====================

Start the database docker if not already started and apply any changes to the database that may have been issued with the new release:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys docker start -c postgis
    (tethys) $ tethys manage syncdb

4. Generate New Settings Script
===============================

Backup your old settings script (``settings.py``) and generate a new settings file to get the latest version of the settings. Then copy any settings (like database usernames and passwords) from the backed up settings script to the new settings script.

::

             $ sudo su
    (tethys) $ mv /usr/lib/tethys/src/tethys_apps/settings.py /usr/lib/tethys/src/tethys_apps/settings.py_bak
    (tethys) $ tethys gen settings -d /usr/lib/tethys/src/tethys_apps
    (tethys) $ exit

.. tip::

    Don't forget to copy any settings that you have set from the backup version of the settings script (``settings.py_bak``) to the new one (e.g.: your database usernames and passwords). After you have copied these settings, you can remove the backup settings file.

6. Collect Static Files
=======================

Collect the new static files and update the old ones:

::

             $ sudo su
    (tethys) $ tethys manage collectstatic
    (tethys) $ exit

7. Change Permissions
=====================

Assign ownership of Tethys Platform files and resources to the Apache user:

::

    $ sudo chown -R www-data:www-data /usr/lib/tethys/src /var/www/tethys

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


