**********************
Update from 1.0 to 1.1
**********************


**Last Updated:** April 24, 2015

The following article describes how to update your Tethys Platform installation from version 1.0.X to 1.1.0. There are two methods that can be used to update to 1.1.0:

1. **Fresh Install**: Purge existing installation and reinstall
2. **Modify**: Modify the existing installation to preserve existing data and configuration

Method 1 is much easier than method 2, but it results in loss of data and starting from scratch. If you are not concerned about losing data such as user account information, site configuration, and app data, then method 1 is recommended. This is often the case with development installations. If you need to preserve existing user accounts and site configuration, then method 2 is recommended. This is usually the case for production installations. Whatever method you choose, it is a good idea to backup your database before you proceed.

Method 1: Fresh Install
=======================

To install a fresh copy of Tethys Platform, perform the following steps:


1. Remove Dockers
-----------------

Run the following commands to delete your existing docker containers:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys docker remove
    (tethys) $ deactivate

.. warning::

    This command will result in the loss of the data in all of your databases and the other dockers like GeoServer.

2. Delete Tethys Virtual Environment
------------------------------------

Use the following command to delete the Tethys virtual environment:

::

   $ sudo rm -rf /usr/lib/tethys

3. Reinstall Tethys Platform
----------------------------

Follow the normal :doc:`./linux` or :doc:`./mac` instructions to reinstall Tethys Platform.

4. Reinstall Apps
-----------------

Reinstall any apps that you wish to have installed on Tethys Platform. For example, to install an app called *my_first_app*:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ cd /path/to/tethysapp-my_first_app
    (tethys) $ python setup.py install
    (tethys) $ tethys syncstores my_first_app

Refer to the documentation for each app for specific instructions.


Method 2: Modify
================

To upgrade the existing installation of Tethys Platform, perform the following steps:

1. Remove Tables to Be Updated
------------------------------

We recommend the use of `PGAdminIII <http://www.pgadmin.org/>`_ as a graphical client for modifying the database. Refer to the :doc:`../supplementary/pgadmin` for help.

a. Using the PGAdminIII database client, connect to the database using the credentials for your *tethys_super* database user (see Figure 1).

  .. figure:: ../images/pgadmin_tutorial_2.png
        :width: 550px

        **Figure 1.** Connect to the database using the credentials for your *tethys_super* database user.

b. Locate the *tethys_default* database, right click on it, and select **Delete/Drop...** from the context menu that appears.

c. From the **edit** menu select New Object >> New Database...

.. note::

    Your database is likely located in one of the Tethys docker containers, so be sure they are running before you attempt these steps:

    ::

        $ tethys docker start


