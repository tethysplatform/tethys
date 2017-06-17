********************
Upgrade to |version|
********************

**Last Updated:** December 10, 2016

1. Get the Latest Version
=========================

When you installed Tethys Platform you did so using it's remote Git repository on GitHub. To get the latest version of Tethys Platform, you will need to pull the latest changes from this repository:

::

    $ cd /usr/lib/tethys/src
    $ git pull origin master

2. Install Requirements and Run Setup Script
============================================

Install new dependencies and upgrade old ones:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ pip install --upgrade -r /usr/lib/tethys/src/requirements.txt
    (tethys) $ python /usr/lib/tethys/src/setup.py develop

3. Generate New Settings Script
===============================

Backup your old settings script (``settings.py``) and generate a new settings file to get the latest version of the settings. Then copy any settings (like database usernames and passwords) from the backed up settings script to the new settings script.

::

    (tethys) $ mv /usr/lib/tethys/src/tethys_apps/settings.py /usr/lib/tethys/src/tethys_apps/settings.py_bak
    (tethys) $ tethys gen settings -d /usr/lib/tethys/src/tethys_apps

.. caution::

    Don't forget to copy any settings from the backup settings script (``settings.py_bak``) to the new settings script. Common settings that need to be copied include:

    * DEBUG
    * ALLOWED_HOSTS
    * DATABASES, TETHYS_DATABASES
    * STATIC_ROOT, TETHYS_WORKSPACES_ROOT
    * EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, DEFAULT_FROM_EMAIL
    * SOCIAL_OAUTH_XXXX_KEY, SOCIAL_OAUTH_XXXX_SECRET
    * BYPASS_TETHYS_HOME_PAGE

    After you have copied these settings, you can delete or archive the backup settings script.

4. Sync the Database
====================

Start the database docker if not already started and apply any changes to the database that may have been issued with the new release:

::

    (tethys) $ tethys docker start -c postgis
    (tethys) $ tethys manage syncdb

.. note::

    For migration errors use:

    ::

        $ cd ~/usr/lib/tethys/src
        $ python manage.py makemigrations --merge
        $ tethys manage syncdb
