*******************
Prior Release Notes
*******************

**Last Updated:** August 2020

Information about prior releases is shown here.

Release 3.2
===========

Multi-Factor Authentication
===========================

* Implemented Multi Factor Authentication via the `Django MFA2 app <https://pypi.org/project/django-mfa2/>`_.
* Time-based One Time Password (TOTP) method is enabled by default, but users must opt-in.
* Added MFA settings to User Profile Pages
* The Email OTP method has also been tested extensively and verified to work.
* Other methods have not been tested.

See: :ref:`multi_factor_auth_config`

Additional Single Sign-On Backends
==================================

* Added four new officially supported Single Sign-On/Social Authentication Methods.
* Renamed Documentation for "Social Authentication" to the more general "Single Sign On".
* New methods include: :ref:`social_auth_azuread`, :ref:`social_adfs`, :ref:`social_auth_onelogin`, and :ref:`social_auth_okta`.

See: :ref:`single_sign_on_config`

Automatic Lockout
=================

* Tethys Portal can now be configured to automatically lockout users after multiple failed login attempts.
* This feature is opt-in.

See: :ref:`advanced_config_lockout`


Jobs Table
==========

* The Status and Actions Columns have been revamped to simplify the Jobs Table.
* All action buttons (Delete, Resubmit, View Logs, etc.) have been moved into a drop down menu in the actions column.
* Simple versions of each status are now shown for single-status jobs instead of a filled progress bar.
* The progress bar is still used to show the status of multiple-status jobs (i.e. workflows).
* Several arguments for the Jobs Table are now deprecated in favor of a simpler method.
* Gizmo Showcase was updated for the Jobs Table.

See: :ref:`jobs-table`

Cesium Map View
===============

* Added support for ENV and VIEWPARAMS when using MVLayer with Cesium Map View.

See: :ref:`cesium-map-view`

jQuery
======

* Updated jQuery to 3.5.1 to address known vulnerability in previous version.

Documentation
-------------

* Added documentation that describes how to configure Tethys Platform to use REDIS as a Channels backend for production.

See: :ref:`production_channels_config` and :ref:`production_official_docker`

Bug Fixes
=========

* Fixed an issue with the tethys command line interface not working on systems without Docker installed.
* Fixed issue with Add User admin page that would prevent adding additional users after the first user was added.
* Modified the Condor Scheduler admin pages to use the PasswordInput field for the password fields.
* Updated the default ASGI configuration file so that it can be killed properly by supervisor when stopped.

Release 3.1
===========

App Permissions Assigned to Groups
----------------------------------

* App permissions can now be assigned directly to permission Groups in the admin pages.
* Adding an app to the permission Group will reveal a dialog to select which of the app permissions to also assign.
* Assign users to the permission Group to grant them those permissions within the app.
* This is an opt-in feature: set ENABLE_RESTRICTED_APP_ACCESS to True in portal_config.yml to use this feature.

See: :ref:`tethys_portal_app_permission_groups`

App Access Permissions
----------------------

* Apps now have an access permission that can be used to grant access to specific users or groups.
* When a users does not have access to an app it will be hidden in the apps library.
* If a user without permission to access an app enters one of the app URLs, they will see a 404 page.
* Configure access to apps by creating a permission Group with access to the App and then assign any number of users to that group.
* The access permission is automatically enforced for all views of apps.
* This is an opt-in feature: set ENABLE_RESTRICTED_APP_ACCESS to True in portal_config.yml to use this feature.

See: :ref:`tethys_portal_app_permission_groups`

Custom Home and App Library Styles and Templates
------------------------------------------------

* Portal admins can now customize the Home or App library pages with custom CSS or HTML.
* Two new settings groups in Site Settings section of admin pages.
* Specify CSS directly into the setting or reference a file in a discoverable Static path.
* Specify the path to custom templates in a discoverable Templates path.

See: :ref:`production_customize_theme`

Additional Base Templates for Apps
----------------------------------

* There are 9 new base templates for Apps that simplify implementing common layouts.
* Specify the desired base template in the ``extends`` tag of the app template.

See: :ref:`additional_base_templates`

New Features for Jobs Table
---------------------------

* Logs action that displays job logs while job is running.
* Monitor job action that can be implemented to display live results of job as it runs.
* Jobs can be grouped and filtered by permission Groups in addition to User.
* Resubmit job action.

See: :ref:`jobs-table`

Official Docker Image Improvements
----------------------------------

* Additional options added to ``run.sh`` to allow it to be run in different modes (daemon, test, etc.) to facilitate testing.
* Adds two new Salt Scripts to make it easier to extend without duplicating steps.
* ``pre_tethys.sls``: prepares static and workspace directories in persistent volume location.
* ``post_app.sls``: runs ``collectstatic`` and ``collectall`` and syncs configuration files to persistent volume location.
* New documentation for using the Official Docker Image

See: :ref:`production_official_docker`

Tethys Portal Configuration
---------------------------

* Fixed inconsistencies with documentation and behavior.
* Fixed issues with some of the groups that weren't working.
* The way logging settings are specified is more straight-forward now.

See: :ref:`tethys_configuration`

Install Command
---------------

* New ``--no-db-sync`` option to ``tethys install`` command to allow for installing the app code without the database sync portion.
* This is helpful in contexts where the database is unavailable during installation such as in a Docker build.

See: :ref:`tethys_cli_install`

Collectstatic Command
---------------------

* Behavior of ``collectstatic`` command changed to copy the static directory instead of link it to be more consistent with how other static files are handled.
* Alleviates a workaround that was necessary in SE Linux environments (the links couldn't be followed).
* Old linking behavior still available via the ``--link`` option.

See: :ref:`tethys_manage_cmd`

Expanded Earth Engine Tutorials
-------------------------------

* Two additional follow-on tutorials to the Earth Engine tutorial.
* Part 2 - add additional pages to app, layout with Bootstrap grid system, upload files, add REST API.
* Part 3 - prepare app for production deployment and publishing on GitHub, deploy to production server.

See: :ref:`tutorial_google_earth_engine`

All New Production Installation Guide
-------------------------------------

* Near complete rewrite of the production installation documentation.
* Examples shown for both Ubuntu and CentOS.
* Expanded from a 1 page document to 25+ documents.
* Moved many documents that were in Tethys Portal to configuration section of production installation docs.
* All existing documentation was updated.

See: :ref:`production_installation`

Docs Fixes
----------

* Added example for SSL firewall configuration.
* Various fixes to make THREDDS and GEE tutorials more clear.
* Tethys Portal Configuration documentation fixed.


Bug Fixes
---------

* Fixed bug with scaffolding extensions.
* Compatibility changes for Bokeh 2.0.0.
* Fixes broken URIs for password reset capability.

Security Updates
----------------

* Return 404 instead of 403 on pages that require login to prevent directory mapping.
* Disable caching on login and register pages.

Release 3.0
===========

.. tip::

    Use this presentation in workshops and training courses to provide an overview of the latest features in Tethys Platform 3.0: `Tethys Platform 3.0 Overview Presentation <https://docs.google.com/presentation/d/1e1pVLDFBJMA2FXryFHo2TdhYGwUUVnPsVHW75i6QhVo/edit>`_.

Django 2.2
----------

* Django was updated to version 2.2, the next LTS version of Django.
* It will be supported until April 2022.
* Includes the latest security updates.

See: `Django Supported Versions <https://www.djangoproject.com/download/#supported-versions>`_

Python 3 Only
-------------

* Tethys Platform no longer supports Python 2.
* This is in large part because Django no longer supports Python 2 as of version 2.0.
* Python 2 is also reaching its `end of life in 2020 <https://pythonclock.org/>`_ (supposedly).

See: `Automated Python 2 to 3 code translation <https://docs.python.org/3.7/library/2to3.html>`_ and `Should I use Python 2 or Python 3 for my development activity? <https://wiki.python.org/moin/Python2orPython3>`_

Conda Package
-------------

* Tethys has been Conda packaged
* It can be installed from our `Conda channel <https://anaconda.org/tethysplatform/tethysplatform>`_.

See: :doc:`../installation`

Upgraded JQuery and Bootstrap
-----------------------------

* The JQuery and Bootstrap libraries that Tethys provides were upgraded to address known security vulnerabilities (see: https://snyk.io/test/npm/bootstrap/3.2.0 and https://snyk.io/test/npm/jquery/1.11.1).
* Bootstrap has been upgraded to version 3.4.1 (not 4 yet, sorry).
* Coincidentally, JQuery was also upgraded to version 3.4.1.

Django Channels
---------------

* Tethys comes with `Django Channels <https://channels.readthedocs.io/en/latest/>`_
* Django Channels wraps the synchronous Django process in an asynchronous process, allowing developers to use modern web protocols like WebSockets.
* WebSockets allow for a bidirectional, long-lived connections between the server and client.

See: :doc:`../tutorials/websockets`

Bokeh Integration
-----------------

* Bokeh's functionality to link backend Python objects to frontend JavaScript objects has been added.

See: :ref:`bokeh_integration`

See: :doc:`../tutorials/bokeh`

URL Maps API
------------

* Documentation for Tethys ``url_maps`` and ``UrlMap`` has been added. This includes a description of the newly added ``UrlMap`` parameters with ``Websockets`` and ``Bokeh Integration``.

See: :doc:`../tethys_sdk/url_maps`

Django Analytical
-----------------

* Tethys comes with `Django Analytical <https://django-analytical.readthedocs.io/en/latest/>`_ installed to enable support form a number of analytics and tracking services.
* You can now enable analytics tracking (e.g. Google Analytics) to every page of your apps and portal with a few settings in the settings file.

See: :doc:`../installation/production/configuration/advanced/webanalytics`

Tethys Quotas
-------------

* Tethys Quotas allow portal administrators to have better control over the resources being used by users and apps (e.g. disk storage).
* Tethys ships with quotas for workspace storage implemented, but it is disabled by default. When enabled, portal administrators can set limits on the storage users or apps are able to use.
* Tethys Quotas are completely extensible, allowing developer to create custom quotas for other resources (e.g. memory usage, database storage, wall time hours, etc.).

See: :doc:`../tutorials/quotas` and :doc:`../tethys_sdk/tethys_quotas`

Workspace Storage Management Pages
----------------------------------

* The User Profile now includes a page for managing storage in the user's workspace accross all apps in the portal. Users can choose to clear the storage in their workspace for an app.
* The App Settings page now includes information about storage in the app's workspace and provides a method for clearing that workspace.
* New endpoints on the App class allow app developers to respond to requests to clear storage from users.

See: :ref:`admin_pages_tethys_quotas`

New Portal Configuration File
-----------------------------

* Tethys will now use a new configuration file: ``portal_config.yml``
* The ``portal_config.yml`` will store information about which services should be used for installed apps and the portal settings
* Tethys Portal settings will now be configured in the new ``portal_config.yml`` file, rather than the ``settings.py``
* This will allow for the local settings to be retained when Tethys is updated in the future (no more regenerating the ``settings.py`` file when you update).
* Site settings will also be able to be configured via the ``portal_config.yml`` (e.g. primary color, logo, home page content).

See:

``tethys db`` command
---------------------

* The CLI has a new command for managing the Tethys database.
* It includes subcommands for initializing the tethys database, starting and stopping the local database, migrating the database between releases, and creating the tethys superuser.

See: :ref:`tethys_db_cmd`

Updated the ``tethys docker`` command
-------------------------------------

* The ``tethys docker`` command now uses the latest version of the Docker Python API.

See: :ref:`tethys_cli_docker`

Extended Services and Link Commands
-----------------------------------

* The ``tethys services`` command has been extended to support creating all Tethys services programatically.
* The ``tethys link`` command has been extended to support link all types of Tethys services to applicable App Settings programatically.

See: :ref:`tethys_cli_services` and :ref:`tethys_cli_link`

Improved CLI Documentation
--------------------------

* The documentation for the command line interface has moved to a new location.
* The CLI documenation is automatically generated from the code to ensure accuracy.

See: :doc:`../tethys_cli`

Automatic Application Installation
----------------------------------

* App now require an ``install.yml`` file which allows dependencies to be installed using conda or pip.
* Apps can also use an optional ``services.yml`` portal specific file that will automatically link services.
* The CLI has a new command for installing apps: `tethys install`.

See: :doc:`../installation/application`, :ref:`tethys_install_yml`, :ref:`tethys_services_yml`, and :ref:`Install Command <tethys_cli_install>`


New App Installation Approach
-----------------------------

* The structure of apps and the way they are installed has changed.
* The changes will allow Tethys to be updated in the future without the need to reinstall apps afterward.
* Tethys 2 Apps will need to be migrated to work in Tethys 3.

.. toctree::
   :maxdepth: 2

   ./app_migration

Dask Job Type
-------------

* New TethysJob types for submitting and managing Dask Jobs.
* Dask allows pure Python code to be automagically parallelized and executed accross a distributed cluster of nodes.

See: :doc:`../tethys_sdk/jobs/dask_job_type` API documentation and the :doc:`../tutorials/dask` tutorial

CesiumMapView Gizmo
-------------------

* New Gizmo for adding Cesium 3D globes to Tethys Apps.
* The initial view can be configured almost entirely using Python in the controller.
* The JavaScript API for the Gizmo allows full access to the underlying Cesium objects to all developers to fully customize.

See: :ref:`cesium-map-view`

MapView Gizmo
-------------

* The MapView Gizmo now includes an overview map control.
* Features on the drawing layer can no be made selectable.
* Initial features can now be specified for the drawing layer.
* New snapping capabilities: a layer can be specified as the layer to snap to.
* Adds full API support for styles on vector-based MVLayers.

See: :ref:`map-view`

JobsTable Gizmo
---------------

* Fixed an issue that prevented the DAG view of Condor Workflow jobs from working with jobs submitted to a remote Condor Scheduler.
* Improved usability of JobsTable in general.
* Changes to allow the JobsTable to work with custom TethysJobs.

See: :ref:`jobs-table`

Open Portal Mode
----------------

* Adds setting to allow Tethys to be run in an open-portal mode.
* When running in open-portal mode, no login will be required, even for views decorated with the ``login_required`` decorator.
* Note: you should use the ``login_required`` decorator provided by Tethys.

Updated PostGIS Docker Image
----------------------------

* We have retired the custom PostGIS image that Tethys has been using since it's first release.
* The ``tethys docker`` command will now install the excellent ``mdillon/postgis`` image.

See: `Docker Hub: mdillon/postgis <https://hub.docker.com/r/mdillon/postgis/>`_

THREDDS Integration as Tethys Service
-------------------------------------

* THREDDS is now supported as a Tethys Spatial Dataset Service.
* A `Siphon <https://unidata.github.io/siphon/latest/index.html>`_ `TDSCatalog <https://unidata.github.io/siphon/latest/api/catalog.html#siphon.catalog.TDSCatalog>`_ object is returned as the engine.
* The official `Unidata THREDDS docker <https://hub.docker.com/r/unidata/thredds-docker>`_ can be installed with the Tethys docker command.

See: :ref:`spatial_dataset_services_api`, :ref:`thredds_engine_reference`, and :ref:`tethys_cli_docker`

Official Tethys Docker Image
----------------------------

* Tethys now builds and maintains an official Docker image on Docker Hub.

See: `Tethys Platform Docker Image <https://hub.docker.com/r/tethysplatform/tethys-core>`_

Tethys Apps Settings
--------------------

* The icon for an app can now be set and overriden by portal admins via the App Settings page.

Bug Fixes
---------

* Several bugs with the JobsTable gizmo (see above).
* The ``tethys docker ip`` command returning the incorrect port for GeoServer.
* The ``tethys uninstall`` command would not remove the database entry if the files were removed manually.
* Removed hardcoded "src" directory to allow tethys to be installed in directories of any name.
* Fixed issue where tags for disabled or not shown apps were still showing up.

Release 2.1.0
=============

Python 3 Support
----------------

* Python 3 officially supported in Tethys Platform.
* Python 2 support officially deprecated and will be dropped when Tethys Platform 3.0 is released.
* Tethys needs to migrate to Python 3 only so we can upgrade to Django 2.0, which only supports Python 3.

.. important::

    Migrate your apps to Python 3. After Tethys Platform 3.0 is released, Python 2 will no longer be supported by Tethys Platform.


100% Unit Test Coverage
-----------------------

* Tests pass in Python 2 and Python 3.
* Unit tests cover 100% of testable code.
* Code base linted using flake8 to enforce PEP-8 and other Python coding best practices.
* Automated test execution on Travis-CI and Stickler-CI whenever a Pull Request is submitted.
* Added badges to the README to display build/testing, coverage, and docs status on github repository.
* All of this will lead to increased stability in this and future releases.

See: `Tethys Platform Repo <https://github.com/tethysplatform/tethys>`_ for build and coverage information.

Tethys Extensions
-----------------

* Customize Tethys Platform functionality.
* Create your own gizmos.
* Centralize app logic that is common to multiple apps in an extension.

See: :doc:`../tethys_sdk/extensions`

Map View Gizmo
--------------

* Added support for many more basemaps.
* Added Esri, Stamen, CartoDB.
* Support for custom XYZ services as basemaps.
* User can set OpenLayers version.
* Uses jsdelivr to load custom versions (see: `<https://cdn.jsdelivr.net/npm/openlayers>`_)
* Default OpenLayers version updated to 5.3.0.

See: :doc:`../tethys_sdk/gizmos/map_view`

Class-based Controllers
-----------------------

* Added ``TethysController`` to SDK to support class-based views in Tethys apps.
* Inherits from django ``View`` class.
* Includes ``as_controller`` method, which is a thin wrapper around ``as_view`` method to better match Tethys terminology.
* UrlMaps can take class-based Views as the controller argument: ``MyClassBasedController.as_controller(...)``
* More to come in the future.

See: `Django Class-based views <https://docs.djangoproject.com/en/2.2/topics/class-based-views/>`_ to get started.

Partial Install Options
-----------------------

* The Tethys Platform installation scripts now allow for partial installation.
* Install in existing Conda environment or against existing database.
* Upgrade using the install script!
* Linux and Mac only.

See: :doc:`../installation/developer_installation` and :doc:`../installation/update`

Command Line Interface
----------------------

* New commands to manage app settings and services.
* ``tethys app_settings`` - List settings for an app.
* ``tethys services`` - List, create, and remove Tethys services (only supports persistent store services and spatial dataset services for now).
* ``tethys link`` - Link/Assign a Tethys service to a corresponding app setting.
* ``tethys schedulers`` - List, create, and remove job Schedulers.
* ``tethys manage sync`` - Sync app and extensions with Tethys database without a full Tethys start.

See: :ref:`tethys_cli_app_settings`, :ref:`tethys_cli_services`, :ref:`tethys_cli_link`, :ref:`tethys_cli_schedulers`, and :ref:`tethys_manage_cmd`

Dockerfile
----------

* New Dockerfile for Tethys Platform.
* Use it to build Docker images.
* Use it as a base for your own Docker images that have your apps installed.
* Includes supporting salt files.
* Dockerfile has been optimized to minimize the size of the produced image.
* Threading is enabled in the Docker container.

See: `Docker Documentation <https://docs.docker.com/get-started/>`_ to learn how to use Docker in your workflows.

API Tokens for Users
--------------------
* API tokens are automatically generated for users when they are created.
* Use User API tokens to access protected REST API views.

Documentation
-------------
* Added SSL setup instruction to Production Installation

Bugs
----

* Fixed grammar in forget password link.
* Refactored various methods and decorators to use new way of using Django methods ``is_authenticated`` and ``is_anonymous``.
* Fixed bug with Gizmos that was preventing errors from being displayed when in debug mode.
* Fixed various bugs with uninstalling apps and extensions.
* Fixed bugs with get_persistent_store_setting methods.
* Fixed a naming conflict in the SelectInput gizmo.
* Fixed numerous bugs identified by new tests.

Release 2.0.0
=============

Powered by Miniconda Environment
--------------------------------

* Tethys Platform is now installed in a Miniconda environment.
* Using the Miniconda includes Conda, an open source Python package management system
* Conda can be used to install Python dependencies as well as system dependencies
* Installing packages like GDAL or NetCDF4 are as easy as ``conda install gdal``
* Conda is cross platform: it works on Windows, Linux, and MacOS

See: `Miniconda <https://conda.io/miniconda.html>`_ and `Conda <https://conda.io/docs/>`_

Cross Platform Support
----------------------

* Develop natively on Windows, Mac, or Linux!
* No more virtual machines.
* Be careful with your paths.

See: :doc:`../installation`

Installation Scripts
--------------------

* Completely automated installation of Tethys
* Scripts provided for Mac, Linux, and Windows.

See: :doc:`../installation`

Python 3
--------

* Experimental Python 3 Support in 2.0.0
* Tethys Dataset Services is not completely Python 3 compatible
* Use ``--python-version 3`` option on the installation script
* Python 2 support will be dropped in version 2.1

See: :doc:`../installation`

Templating API
--------------

* Leaner, updated theme for app base template.
* New ``header_buttons`` block for adding custom buttons to app header.

See: :doc:`../tethys_sdk/templating`

App Settings
------------

* Developers can create App Settings, which are configured in the admin interface of the Tethys Portal.
* Types of settings that can be created include Custom Settings, Persistent Store Settings, Dataset Service Settings, Spatial Dataset Service Settings, and Web Processing Service Settings.
* The way Tethys Services are allocated to apps is now done through App Settings.
* All apps using the Persistent Stores APIs, Dataset Services APIs, or Web Processing Services APIs prior to version 2.0.0 will need to be refactored to use the new App settings approach.

See: :doc:`../tethys_sdk/app_settings`

Commandline Interface
---------------------

* Added ``tethys list`` command that lists installed apps.
* Completely overhauled scaffold command that works cross-platform.
* New options for scaffold command that allow automatically accepting the defaults and overwriting project if it already exists.

See: :ref:`tethys_list_cmd` and :ref:`tethys_scaffold_cmd`

Tutorials
---------

* Brand new Getting Started Tutorial
* Demonstration of most Tethys SDK APIs

See: :ref:`key_concepts_tutorial`

Gizmos
------

* New way to call them
* New load dependencies Method
* Updated select_gizmo to allow Select2 options to be passed in.

See: :doc:`../tethys_sdk/gizmos`

Map View
--------

* Updated OpenLayers libraries to version 4.0
* Fixes to make MapView compatible with Internet Explorer
* Can configure styling of MVDraw overlay layer
* New editable attribute for MVLayers to lock layers from being edited
* Added data attribute to MVLayer to allow passing custom attributes with layers for use in custom JavaScript
* A basemap switcher tool is now enabled on the map with the capability to configure multiple basemaps, including turning the basemap off.
* Added the ability to customize some styles of vector MVLayers.

See: :doc:`../tethys_sdk/gizmos/map_view`

Esri Map View
-------------

* New map Gizmo that uses ArcGIS for JavaScript API.

See: :doc:`../tethys_sdk/gizmos/esri_map`

Plotly View and Bokeh View Gizmos
---------------------------------

* True open source options for plotting in Tethys

See: :doc:`../tethys_sdk/gizmos/bokeh_view` and :doc:`../tethys_sdk/gizmos/plotly_view`

DataTable View Gizmos
---------------------

* Interactive table gizmo based on Data Tables.

See: :doc:`../tethys_sdk/gizmos/datatable_view`

Security
--------

* Sessions will now timeout and log user out after period of inactivity.
* When user closes browser, they are automatically logged out now.
* Expiration times can be configured in settings.

HydroShare OAuth Backend and Helper Function
--------------------------------------------

* Refactor default HydroShare OAuth backend; Token refresh is available; Add backends for HydroShare-beta and HydroShare-playground.
* Include hs_restclient library in requirements.txt; Provide a helper function to help initialize the ``hs`` object based on HydroShare social account.
* Update python-social-auth to 0.2.21.



Bugs
----

* Fixed issue where ``tethys uninstall <app>`` command was not uninstalling fully.


Release 1.4.0
=============

App Permissions
---------------

* There is now a formalized mechanism for creating permissions for apps.
* It includes a `permission_required` decorator for controllers and a `has_permission` method for checking permissions within controllers.

Tags for Apps
-------------

* Apps can be assigned tags via the "tags" property in app.py.
* App tags can be overriden by portal admins using the ``Installed Apps`` settings in the admin portal.
* If there are more than 5 app tiles in the apps library, a list of buttons, one for each tag, will be displayed at the top of the Apps Library page.
* Clicking on one of the tag buttons, will filter the list of displayed apps to only those with the selected tag.

Terms and Conditions Management
-------------------------------

* Portal Admins can now manage and enforce portal-wide terms and conditions and other legal documents.
* Documents are added via the admin interface of the portal.
* Documents can be versioned and dates at which they become active can be set.
* Once the date passes, all users will be prompted to accept the terms of the new documents.

GeoServer
---------

* The GeoServer docker was updated to version 2.8.3
* It can be configured to run in clustered mode (multiple instances of GeoServer running inside the container) for greater stability and performance
* Several extensions are now included:

   * `JMS Clustering <http://docs.geoserver.org/2.8.x/en/user/community/jms-cluster/index.html>`_
   * `Flow Control <http://docs.geoserver.org/2.8.x/en/user/extensions/css/index.html>`_
   * `CSS Styles <http://docs.geoserver.org/2.8.x/en/user/extensions/controlflow/index.html>`_
   * `NetCDF <http://docs.geoserver.org/2.8.x/en/user/extensions/netcdf/netcdf.html>`_
   * `NetCDF Output <http://docs.geoserver.org/2.8.x/en/user/extensions/netcdf-out/index.html>`_
   * `GDAL WCS Output <http://docs.geoserver.org/2.8.x/en/user/community/gdal/index.html>`_
   * `Image Pyramid <http://docs.geoserver.org/2.8.x/en/user/tutorials/imagepyramid/imagepyramid.html>`_

Tethys Docker CLI
-----------------

* Modified behaviour of "-c" option to accept a list of containers names so that commands can be performed on subsets of the containers
* Improved behaviour of "start" and "stop" commands such that they will start/stop all installed containers if some are not installed
* Improved behaviour of the "remove" command to skip containers that are not installed

Select2 Gizmo
-------------

* Updated the Select2 Gizmo libraries to version 4.0.
* Not changes should be necessary for basic usage of the Select2 Gizmo.
* If you are using advanced features of Select2, you will likely need to migrate some of your code.
* Refer to `<https://select2.github.io/announcements-4.0.html#migrating-from-select2-35>`_ for migration help.

MapView Gizmo
-------------

* New JavaScript API endpoints for the MapView.
* Use the `TETHYS_MAP_VIEW.getSelectInteraction()` method to have more control over items that are selected.
* MVLayer Select Features now supports selection of vector layers in addition to the WMS Layers.
* Added support for images in the legend including support for GeoServer GetLegendGraphic requests.

PlotView Gizmo
--------------

* New JavaScript API endpoints for initializing PlotViews dynamically.

Workflow Job Type
-----------------

* New Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single job.
* The hierarchical relationships are defined as parent-child relationships between jobs.
* As part of this addition the original Condor Job type was refactored and, while backwards compatibility is maintained in version 1.4, several aspects of how job templates are defined have been deprecated.

Testing Framework
-----------------

* New Tethys CLI command to run tests on Tethys and apps.
* Tethys SDK now provides a TethysTestCase to streamlines app testing.
* Persistent stores is supported in testing.
* Tethys App Scaffold now includes testing module with example test code.

Installation
------------

* Installation Instructions for Ubuntu 16.04

Bug Fixes
---------

* Fixed an issue with URL mapping that was masking true errors with contollers (see: `Issue #177 <https://github.com/tethysplatform/tethys/issues/177>`_)
* Fixed an issue with syncstores that use the string version of the path to the intializer function (see: `Issue #185 <https://github.com/tethysplatform/tethys/issues/185>`_)
* Fixed an issue with syncstores that would cause it to fail the first time (see: `Issue #194 <https://github.com/tethysplatform/tethys/issues/194>`_)

Release 1.3.0
=============

Tethys Portal
-------------

* Open account signup disabled by default
* New setting in `settings.py` that allows open signup to be enabled

Map View
--------

* Feature selection enabled for ImageWMS layers
* Clicking on features highlights them when enabled
* Callback functions can be defined in JavaScript to trap on the feature selection change event
* Custom styles can be applied to highlighted features
* Basemap can be disabled
* Layer attributes can be set in MVLayer (e.g. visibility and opacity)
* Updated to use OpenLayers 3.10.1

Plot View
---------

* D3 plotting implemented as a free alternative to Highcharts for line plot, pie plot, scatter plot, bar plot, and timeseries plot.

Spatial Dataset Services
------------------------

* Upgraded gsconfig dependency to version 1.0.0
* Provide two new methods on the geoserver engine to create SQL views and simplify the process of linking PostGIS databases with GeoServer.

App Feedback
------------

* Places button on all app pages that activates a feedback form
* Sends app-users comments to specified developer emails
* Includes user and app specific information

Handoff
-------

* Handoff Manager now available, which can be used from controllers to handoff from one app to another on the same Tethys portal (without having to use the REST API)
* The way handoff handler controllers are specified was changed to be consistent with other controllers

Jobs Table Gizmo
----------------

* The refresh interval for job status and runtime is configurable

Social Authentication
---------------------

* Support for HydroShare added

Dynamic Persistent Stores
-------------------------

* Persistent stores can now be created dynamically (at runtime)
* Helper methods to list persistent stores for the app and check whether a store exists.

App Descriptions
----------------

* Apps now feature optional descriptions.
* An information icon appears on the app icon when descriptions are available.
* When the information icon is clicked on the description is shown.

Bugs
----

* Missing initial value parameter was added to the select and select2 gizmos.
* Addressed several cases of mixed content warnings when running behind HTTPS.
* The disconnect social account buttons are now disabled if your account doesn't have a password or there is only one social account associated with the account.
* Fixed issues with some of the documentation not being generated.
* Fixed styling issues that made the Message Box gizmo unusable.
* Normalized references to controllers, persistent store initializers, and handoff handler functions.
* Various docs typos were fixed.

Release 1.2.0
=============

Social Authentication
---------------------

* Social login supported
* Google, LinkedIn, and Facebook
* HydroShare coming soon
* New controls on User Profile page to manage social accounts


D3 Plotting Gizmos
------------------

* D3 alternatives for all the HighCharts plot views
* Use the same plot objects to define both types of charts
* Simplified and generalized the mechanism for declaring plot views

Job Manager Gizmo
-----------------

* New Gizmo that will show the status of jobs running with the Job Manager

Workspaces
----------

* SDK methods for creating and managing workspaces for apps
* List files and directories in workspace directory
* Clear and remove files and directories in workspace

Handoff
-------

* Use handoff to launch one app from another
* Pass arguments via GET parameters that can be used to retrieve data from the sender app

Video Tutorials
---------------

* New video tutorials have been created
* The videos highlight working with different software suite elements
* CKAN, GeoServer, PostGIS
* Advanced user input forms
* Advanced Mapping and Plotting Gizmos

New Location for Tethys SDK
---------------------------

* Tethys SDK methods centralized to a new convenient package: tethys_sdk

Persistent Stores Changes
-------------------------

* Moved the get_persistent_stores_engine() method to the TethysAppBase class.
* To call the method import your :term:`app class` and call it on the class.
* The old get_persistent_stores_engine() method has been flagged for deprecation.

Command Line Interface
----------------------

* New management commands including ``createsuperuser``, ``collectworkspaces``, and ``collectall``
* Modified behavior of ``syncdb`` management command, which now makes and then applies migrations.


Release 1.1.0
=============

Gizmos
------

* Options objects for configuring gizmos
* Many improvements to Map View

  * Improved layer support including GeoJSON, KML, WMS services, and ArcGIS REST services
  * Added a mechanism for creating legends
  * Added drawing capabilities
  * Upgraded to OpenLayers version 3.5.0

* New objects for simplifying Highcharts plot creation

  * HighChartsLinePlot
  * HighChartsScatterPlot
  * HighChartsPolarPlot
  * HighChartsPiePlot
  * HighChartsBarPlot
  * HighChartsTimeSeries
  * HighChartsAreaRange

* Added the ability to draw a box on Google Map View

Tethys Portal Features
----------------------

* Reset forgotten passwords
* Bypass the home page and redirect to apps library
* Rename the apps library page title
* The two mobile menus were combined into a single mobile menu
* Dataset Services and Web Processing Services admin settings combined into a single category called Tethys Services
* Added "Powered by Tethys Platform" attribution to footer

Job Manager
-----------

* Provides a unified interface for all apps to create submit and monitor computing jobs
* Abstracts the CondorPy module to provide a higher-level interface with computing jobs
* Allows definition of job templates in the app.py module of apps projects


Documentation Updates
---------------------

* Added documentation about the Software Suite and the relationship between each software component and the APIs in the SDK is provided
* Documentation for manual download and installation of Docker images
* Added system requirements to documentation

Bug Fixes
---------

* Naming new app projects during scaffolding is more robust
* Fixed bugs with fetch climate Gizmo
* Addressed issue caused by usernames that included periods (.) and other characters
* Made header more responsive to long names to prevent header from wrapping and obscuring controls
* Fixed bug with tethys gen apache command
* Addressed bug that occurred when naming WPS services with uppercase letters

Other
-----

* Added parameter of UrlMap that can be used to specify custom regular expressions for URL search patterns
* Added validation to service engines
* Custom collectstatic command that automatically symbolically links the public/static directories of Tethys apps to the static directory
* Added "list" methods for dataset services and web processing services to allow app developers to list all available services registered on the Tethys Portal instance
