*****************
Working with Apps
*****************

**Last Updated:** May 21, 2014

Apps Project Scaffold
=====================

CKAN apps are developed as Python packages. The package includes the :file:`apps.py` configuration file, Python scripts for the model, views, and controllers of the app, dynamic HTML templates, static resources such as images, and JavaScript and CSS libraries for style and app functionality. The structure and organization of all these parts of an app is very important. Failure to follow the guidelines outlined in :doc:`./app_project` page could result in an app that does not work properly. Conveniently, the Tethys Apps plugin includes a command-line tool for generating the scaffolding of an app package. We strongly encourage developers to use the scaffold every time they start a new app. To create a new app using the scaffold, open a terminal and change to the directory where you would like to create the app package. Execute the following commands:

::

	$ mkdir ~/tethysdev
	$ cd ~/tethysdev
	$ paster create -t ckanapp ckanapp-example

Replace ckanapp-example with the name of your app. Tethys Apps projects must begin with the 'ckanapp-' prefix followed by a *unique* name. Follow the interactive prompts to fill in the metadata about your app. The only required field is the *proper_name* field.

.. hint::

	Only alphanumeric characters and underscores are allowed for app names. The name may not have spaces.

Installing Apps in Production
=============================

Tethys App projects are structured similarly to ckan plugin projects. In fact, it is useful to think of a Tethys App as a plugin for the Tethys Apps plugin. Always refer to the documentation for an app for specific installation requirments. Generally, installation will include the following steps:

1. Run the Setup Script with Install Command
--------------------------------------------

Run the setup script (:file:`setup.py`) using your CKAN Python environment. The setup script will automatically install any dependencies the app may have and copy the app source to the Python path (:file:`site-packages`). Continuing the example above:

::

	$ . /usr/lib/ckan/default/bin/activate
	$ cd ~/tethysdev/ckanapp-example
	$ python setup.py install

2. Restart CKAN Server to Load Apps
-----------------------------------

Apps are loaded into CKAN on startup, so the CKAN server must be restarted whenever apps are added or removed.

Linking Apps during Development
===============================

During development of an app, you will make frequent changes to source. If you used the directions from the previous section for installation, you would need to reinstall the app everytime you made a change to see the updated app. This is not very practical for development. Instead, use the following steps to install a Tethys App during the development phase:

1. Run the Setup Script with Develop Command
--------------------------------------------

Rather than using the :command:`install` command on the setup script, use the :command:`develop` command. This will install any dependencies for the app and link to your working copy of the source to the Python path, rather than hard copying your source to the Python :file:`site-packages` directory. Thus, as you make changes to your source, they will automatically be updated for Python without the need to rerun the setup script.

::

	$ . /usr/lib/ckan/default/bin/activate
	$ cd ~/tethysdev/ckanapp-example
	$ python setup.py develop

2. Restart the CKAN Server to Load Apps
---------------------------------------

Just as before, the CKAN server must be restarted to load the apps the first time.


3. Use Paster Server for Development
------------------------------------

We recommend using the Paster server for during app development. When you start the Paster server, start it using :option:`--reload` option. This will cause the server to reload automatically anytime one of your files is saved/changed.

::

	$ . /usr/lib/ckan/default/bin/activate
	$ paster serve --reload /etc/ckan/default/development.ini

Additional Steps for Installing Legacy Apps
===========================================

Prior to version 0.3 of Tethys Apps it was necessary to also copy or symbolically link the your :term:`app package` into the :file:`ckanapp` directory of the Tethys Apps source. This process is automatically performed for apps created with the scaffold after version 0.3. If you generated a new app project using the scaffold from an early version of the Tethys Apps plugin, the following steps may be necessary.

Production
----------

For production installations, it will be necessary to copy the :term:`app package` of your app into the :file:`ckanapp` directory. This can be done like so:

::

	$ cp ~/tethysdev/ckanapp-example/ckanapp/example /usr/lib/ckan/default/src/ckan/ckanext/tethys_app/ckanapp/

Development
-----------

For installing your app during installation, it is preferrable to symbolically link your :term:`app package` into the :file:`ckanapp` directory:

::

	$ ln -s ~/tethysdev/ckanapp-example/ckanapp/example /usr/lib/ckan/default/src/ckan/ckanext/apps/ckanapp/example

Uninstalling Apps
=================

Use the following steps to uninstall an app.

1. Remove Source Package or Symbolic Link from :file:`ckanapp` Directory
------------------------------------------------------------------------

You may not have been aware of it, but when you install an app, the source code is automatically copied or symbolically linked into the :file:`ckanapp` directory. If all you want is to remove the app from CKAN, the only necessary step is to remove the source package for the app from this directory. This can be done like so:

::

	$ rm -rf /usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/ckanapp/example

2. Uninstall Python Installation using PIP
------------------------------------------

If you want to remove the Python installation of an app, use :command:`pip` to uninstall it.

::

	$ . /usr/lib/ckan/default/bin/activate
	$ pip uninstall ckanapp-example







