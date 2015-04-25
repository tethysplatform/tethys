**********************
Update from 1.0 to 1.1
**********************


**Last Updated:** April 24, 2015

The following article describes how to update your Tethys Platform installation from version 1.0.X to 1.1.0. There are two methods that can be used to update to 1.1.0:

1. Delete Tethys Virtual Environment
====================================

Use the following command to delete the Tethys Platform virtual environment:

::

   $ sudo rm -rf /usr/lib/tethys

2. Reinstall Tethys Platform for Production
===========================================

Follow the :doc:`./installation` instructions to reinstall Tethys Platform for production. Do not update the Docker images unless you want to loose all data in databases.

.. warning::

    Updating the Docker containers will result in the loss of all data.

3. Reinstall Apps
=================

Reinstall any apps that you wish to have installed on Tethys Platform. Refer to the documentation for each app for specific installation instructions, but generally apps can be installed as follows:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ cd /path/to/tethysapp-my_first_app
    (tethys) $ python setup.py install
    (tethys) $ tethys syncstores my_first_app

The databases for the apps should have been retained unless you updated the Docker containers.