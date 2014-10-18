******************************
Setup from Source Installation
******************************

**Last Updated:** May 30, 2014

This method of setting up the development environment for Tethys Apps involves setting up a computer with the Ubuntu (Linux) operating system and installing CKAN and the Tethys Apps plugin from the source code. This is the most difficult method and can be time intensive if you are not familiar with Linux. That said, the installation instructions provided are very well written fairly staight forward. Plan on spending at least 2-3 hours to get setup using this method.

.. _install_ubuntu:

Install Ubuntu
==============

Ubuntu Desktop can be downloaded at the `Download Ubuntu <http://www.ubuntu.com/desktop>`_ page. There are three ways you can install Ubuntu on your computer. The first option is to overwrite whatever operating system you are running with Ubuntu.This can be done using either a USB or DVD. Use the `Install Ubuntu <http://www.ubuntu.com/download/desktop/install-ubuntu-desktop>`_ instructions to do so (Note: these instructions are for Ubuntu 14.04, but they should work for Ubuntu 12.04 as well). This method is not usually preferable or recommended, because most users still want to retain use of their Windows or Mac operating systems. The next two options accomodate this need.

The second options is to install Ubuntu in a dual boot configuration. This will let you choose to either run Ubuntu or Windows/Mac OSX when you start your computer. Follow the instructions provided by Ubuntu for `Windows Dual Boot <https://help.ubuntu.com/community/WindowsDualBoot>`_ if on a Windows computer or the `Intel Mac Dual Boot <https://help.ubuntu.com/community/MactelSupportTeam/AppleIntelInstallation>`_ if on a Mac computer.

The third option is to install Ubuntu as a virtual machine using virtualization software such as `VirtualBox <https://www.virtualbox.org/>`_. If you are running Mac OSX you can also use `VMWare <https://www.vmware.com/>`_ or `Parallels <http://www.parallels.com/>`_. Follow the instructions for creating a new Ubuntu virtual machine for the software you are running.

After installing Ubuntu, be sure to install any updates using the Update Manager and restart. 

Install CKAN from Source
========================

When Ubuntu is up and running, the next step is to install CKAN. CKAN runs on top of the Pylons Python web framework, thus CKAN will use Python to run. We recommend using Python 2.7.3. Please note that Python 3.x will not work. You can check the version of Python running on your Ubuntu machine by executing the following command on the terminal:

::

    $ python -V

To install CKAN, follow the excellent source installation instructions found `here <http://docs.ckan.org/en/ckan-2.2/install-from-source.html>`_. Use all of the default directories and names specified in the instructions for your development environment.

Next, configure your CKAN installation with FileStore enabled. You will not be able to upload or store files in your CKAN installation without enabling FileStore. Follow `these <http://docs.ckan.org/en/ckan-2.2/filestore.html?highlight=filestore>`_ instructions to setup FileStore. Optinally, you may also enable the DataStore using `these <http://docs.ckan.org/en/ckan-2.2/datastore.html>`_ instructions.

.. note::

    If you decide you would like to install CKAN on another Linux operating system, `this <https://github.com/ckan/ckan/wiki/How-to-Install-CKAN>`_ link may be helpful. It provides intructions for several other operating systems. However, all the instructions for setting up the development environment are written for Ubuntu.

.. caution::

    Some of the instructions for installing CKAN require you to change a few lines in various configuration files. Some of these lines are commented out by default. **Make sure all these lines are uncommented.**

CKAN Installation Troubleshooting
---------------------------------

A recent change to the ``libtomcat6-java`` library has caused some issues with Solr running through Jetty. If you encounter these issues (i.e.: some error about a tomcat library), Solr can be configured to run through Tomcat instead. To use Tomcat instead of Jetty, execute the following commands:

::

    $ sudo apt-get remove solr-jetty
    $ sudo apt-get install solr-tomcat

Next, open the tomcat configuration file (/etc/tomcat6) and change the port attribute of the Connector to **8983**. Start tomcat like so:

::

    $ sudo service tomcat6 start

If you get an error like *Permission denied:'/var/lib/ckan/default/storage'* run the following commands:

::

    $ sudo chown -R `whoami` /var/lib/ckan/default
    $ sudo chmod -R u+rwx /var/lib/ckan/default

Tethys Apps
===========

Follow the instructions for installing the Tethys Apps plugin found :doc:`../installation`. Be sure to use the modified instructions for installing during development.

CI-Water Theme
==============

Optionally, you may wish to install the CI-Water Theme to give your CKAN installation a different look. This can be done by installing the ``ci-water_theme`` plugin:

::

    $ cd ~/tethysdev
    $ git clone https://swainn@bitbucket.org/swainn/ckanext-ciwater_theme.git

After downloading the source code, change into the :file:`ckanext-ciwater_theme` directory and perform the installation. Be sure your CKAN python environment is activated before running the install command. Finally, copy the :file:`ciwater_theme` source into the :file:`ckanext` directory.

::

    $ . /usr/lib/ckan/default/bin/activate
    $ cd ~/tethysdev/ckanext-ciwater_theme
    $ python setup.py install
    $ cp ~/tethysdev/ckanext-ciwater_theme/ckanext/ciwater_theme /usr/lib/ckan/default/src/ckan/ckanext/

Add *"ciwater_theme"* to the **ckan.plugins** parameter of CKAN configuration file (e.g.: :file:`development.ini`). Be sure the *"ciwater_theme"* plugin is listed **after** the *"tethys_apps"* plugin.

::

    ckan.plugins = tethys_apps ciwater_theme

Just like the Tethys Apps plugin, the CI-Water Theme plugin is under heavy development. You may wish to modify your installation to use links instead of hard copying. To do so, execute the following commands instead of the above: 

::

    $ . /usr/lib/ckan/default/bin/activate
    $ cd ~/tethysdev/ckanext-ciwater_theme
    $ python setup.py develop
    $ ln -s ~/tethysdev/ckanext-ciwater_theme/ckanext/ciwater_theme /usr/lib/ckan/default/src/ckan/ckanext/ciwater_theme

Start Developing
================

Refer to the :doc:`./working_ckan` to learn how to start up CKAN and start developing.
