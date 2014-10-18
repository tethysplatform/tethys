***********************
Setup with VMWare Image
***********************

**Last Updated:** May 30, 2014

If you have VMWare installed on your computer, you can make use of the VMWare image to have an instantly configured development environment. This image comes with a full Ubuntu installation with CKAN and Tethys Apps installed. This method is quick and painless. It will take some time to download the image, but then there is only minimal setup required after that.

1. Download the image `here <https://drive.google.com/file/d/0B6apBoh0rF2Ra0JSZEZ5NnJkem8/edit?usp=sharing>`_. 

2. Extract the file from the zip archive to a safe location and double-click to run it. If prompted whether you moved or copied the VM, select the **copied** option.

3. Login using the following credentials:

::

    diplay name: Tethys User
    username: user
    password: tethyspass

4. Pull the latest version of the Tethys Apps plugin:

::

    cd ~/tethysdev/ckanext-tethys_apps
    git pull

5. Customize Ubuntu to your liking. You are welcome to change the username, password, and any settings you would like after you start the VM.

.. note::
    The contained in the zip archive is the virtual machine. DO NOT DELETE THIS FILE. We recommend that you move the file to a safe location.

Useful Accounts
=============

There are several usernames and passwords that may be useful when using the VMWare image for developing Tethys apps. The image provides a system admin for the CKAN web site. The system admin can be used to manage users and datasets in CKAN. See the `Sysadmin Guide <http://docs.ckan.org/en/ckan-2.2/sysadmin-guide.html>`_ for more details. The credentials for the system admin are:

::

    username: tethysadmin
    password: tethyspass

Start Developing
================

Refer to the :doc:`./working_ckan` to learn how to start up CKAN and start developing.

