************************
Application Installation
************************

**Last Updated:** March 13, 2019

Once you have the portal configured and setup with all the required services, the next step is to install Tethys applications on to your portal.

1. Navigate to App Directory
============================

Within the command line interface, navigate to the directory of the app you wish to install (this directory must contain the app's ``setup.py`` file).

::

    $ cd /directory/of/app

2. Install the App
==================

Using Install (Recommended):
----------------------------

Using the ``install`` cli command, you can install the application in one quick step. The ``install`` command will install all the dependencies, link any services that you might need for your application and can also rely on the portal configuration to link default services to your application (as configured by the portal administrator).

::

    # Run Init
    $ tethys install

    # Tethys install with custom options
    $ tethys install -f ../install.yml -p $TETHYS_HOME/src/configs/portal.yml


The install command uses three configuration files:

.. _tethys_install_yml:

install.yml 
-----------

This file is generated with your application scaffold. Please do NOT list any dependencies in setup.py. Instead list them in the :file:`install.yml` file. This file should be committed with your application code in order to aid installation on a Tethys Portal

.. code-block:: python

	# This file may be committed to your app code.
	version: 1.0
	# This should match the app - package name in your setup.py
	name: hydroexplorer

	conda:
	  # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
	  skip: false
	  channels:
	  	- conda-forge
	  dependencies:
	    - pyshp=2.0.0
	    - geojson
	    - shapely

	pip:
	  - see

	post:
  	  - test.sh

**install.yml Options:**

* **version**: Indicated the version of the :file:`install.yml` file. Current default : 1.0
* **name**: This should match the app-package name in your setup.py

* **conda/skip**: If enabled, it will skip the installation of dependencies and channels. This option is set to `False` by default. 

* **conda/channels**: List of conda channels that need to be searched for dependency installation. Only specify any conda channels that are apart from the default. 

* **conda/dependencies**: List of python dependencies that need to be installed by conda. These may be entered in the format ``pyshp=2.0.0`` to download a specific version.

* **pip**: A list of python dependencies that need to be installed by pip.

* **post**: A list of shell scripts that you would want to run after the installation is complete. This option can be used to initialize workspaces/databases etc. These shell scripts should be present in the same directory as setup.py

.. tip::

    Run ``tethys gen install`` to create a blank template of this file. By default the file will be saved to the current working directory.

.. _tethys_services_yml:

services.yml 
------------

This file will be created by the portal administrator who has created/has access to all the service in the portal. This file will only be run by default if there is no portal services config file present (see :ref:`tethys_portal_yml`). However you can force the use of this file over the portal config by specifying the `--force-services` tag on the install command.

.. code-block:: python

	# Do not commit this file. This file is portal specific.
	version: 1.0
	skip: false
	interactive: false

	# Set service params in the following format :
	# app_service_setting_name(from your app.py): <service_name or id from list of installed services>
	persistent:
  	 catalog_db: hydroexplorer-persistent
  	 second_db: main-persistent
	wps:
  	 wps_main: testWPS
  	dataset:
  	spatial:

**services.yml Options:**

* **version**: Indicated the version of the :file:`services.yml` file. Current default : 1.0
* **skip**: If enabled, it will skip the installation of services. This option is set to `False` by default. 
* **interactive**: If enabled, it will start an interactive mode that will let you select from existing portal services. This option is set to `False` by default. 


* **persistent** : List of persistent store settings in the app and the service to link to each.
* **dataset** : List of dataset settings in the app and the service to link to each.
* **spatial** : List of spatial persistent store settings in the app and the service to link to each.
* **wps** : List of Web Processing service settings in the app and the service to link to each. 

Settings in each of the service sections above will need to be listed in the following format::

	<app_service_setting_name> : <service_name or id>

In the above example, ``catalog_db`` is the name of the service in your :file:`app.py` and ``hydroexplorer-persistent`` is the name of the service on the portal. 

.. tip::

    Run ``tethys gen services`` to create a blank template of this file. By default the file will be saved to the current working directory.

.. _tethys_portal_yml:

portal.yml 
------------

The file is designed to be maintained by the server administrator who can provide incoming apps with default services. 

.. code-block:: python

	# Portal Level Config File

	version: 1.0
	name: Tethys Main Portal
	apps:
	 hydroexplorer:
	  services:
	   persistent:
	    catalog_db: test
	   spatial:
	   dataset:
	   wps:


**portal.yml Options:**

* **version**: Indicated the version of the :file:`portal.yml` file. Current default : 1.0
* **name**: Name of the portal

* **apps/<app-name>/services/persistent** : List of persistent store settings in the app and the service to link to each.
* **apps/<app-name>/services/dataset** : List of dataset settings in the app and the service to link to each.
* **apps/<app-name>/services/spatial** : List of spatial persistent store settings in the app and the service to link to each.
* **apps/<app-name>/services/wps** : List of Web Processing service settings in the app and the service to link to each. 

Settings in each of the service sections above will need to be listed in the following format::

	<app_service_setting_name> : <service_name or id>

In the above example, ``catalog_db`` is the name of the service in your :file:`app.py` and ``test`` is the name of the service on the portal.

.. tip::

    Run ``tethys gen portal`` to create a blank template of this file. By default the file will be saved to ``$TETHYS_SRC/tethy_portal``.


3. Restart Tethys Server
==========================

Restart tethys portal to effect the changes::

    (tethys) $ tethys manage start

.. tip::

    Use the alias `tms` as a shortcut

4. Configure Additional App Settings
====================================

Set any additional required settings on the application settings page in the Tethys Portal admin pages (see :doc:`../../tethys_portal/admin_pages`).

5. Initialize Persistent Stores
===============================

If your application requires a database via the persistent stores API, you will need to initialize it::

    $ t
    (tethys) $ tethys syncstores all