*******************
Prior Release Notes
*******************

**Last Updated:** December 10, 2016

Information about prior releases is shown here.

Release 1.4.0
=============

App Permissions
---------------

* There is now a formalized mechanism for creating permissions for apps.
* It includes a `permission_required` decorator for controllers and a `has_permission` method for checking permissions within controllers.

See: :doc:`../tethys_sdk/permissions`

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

See: :ref:`tethys_portal_terms_and_conditions`

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

See: :doc:`../software_suite/geoserver`

Tethys Docker CLI
-----------------

* Modified behaviour of "-c" option to accept a list of containers names so that commands can be performed on subsets of the containers
* Improved behaviour of "start" and "stop" commands such that they will start/stop all installed containers if some are not installed
* Improved behaviour of the "remove" command to skip containers that are not installed

See: :ref:`tethys_cli_docker`

Select2 Gizmo
-------------

* Updated the Select2 Gizmo libraries to version 4.0.
* Not changes should be necessary for basic usage of the Select2 Gizmo.
* If you are using advanced features of Select2, you will likely need to migrate some of your code.
* Refer to `<https://select2.github.io/announcements-4.0.html#migrating-from-select2-35>`_ for migration help.

See: :doc:`../tethys_sdk/gizmos/select_input`

MapView Gizmo
-------------

* New JavaScript API endpoints for the MapView.
* Use the `TETHYS_MAP_VIEW.getSelectInteraction()` method to have more control over items that are selected.
* MVLayer Select Features now supports selection of vector layers in addition to the WMS Layers.
* Added support for images in the legend including support for GeoServer GetLegendGraphic requests.

See: :doc:`../tethys_sdk/gizmos/map_view`

PlotView Gizmo
--------------

* New JavaScript API endpoints for initializing PlotViews dynamically.

See: :doc:`../tethys_sdk/gizmos/plot_view`

Workflow Job Type
-----------------

* New Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single job.
* The hierarchical relationships are defined as parent-child relationships between jobs.
* As part of this addition the original Condor Job type was refactored and, while backwards compatibility is maintained in version 1.4, several aspects of how job templates are defined have been deprecated.

See: :doc:`../tethys_sdk/jobs/condor_workflow_type`

Testing Framework
-----------------

* New Tethys CLI command to run tests on Tethys and apps.
* Tethys SDK now provides a TethysTestCase to streamlines app testing.
* Persistent stores is supported in testing.
* Tethys App Scaffold now includes testing module with example test code.

See: :doc:`../tethys_sdk/testing` and :ref:`tethys_cli_testing`

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

See: :doc:`../tethys_portal/customize`

Map View
--------

* Feature selection enabled for ImageWMS layers
* Clicking on features highlights them when enabled
* Callback functions can be defined in JavaScript to trap on the feature selection change event
* Custom styles can be applied to highlighted features
* Basemap can be disabled
* Layer attributes can be set in MVLayer (e.g. visibility and opacity)
* Updated to use OpenLayers 3.10.1

See: :doc:`../tethys_sdk/gizmos/map_view`

Plot View
---------

* D3 plotting implemented as a free alternative to Highcharts for line plot, pie plot, scatter plot, bar plot, and timeseries plot.

See: :doc:`../tethys_sdk/gizmos/plot_view`

Spatial Dataset Services
------------------------

* Upgraded gsconfig dependency to version 1.0.0
* Provide two new methods on the geoserver engine to create SQL views and simplify the process of linking PostGIS databases with GeoServer.

See: :doc:`../tethys_sdk/spatial_dataset_service/geoserver_reference`

App Feedback
------------

* Places button on all app pages that activates a feedback form
* Sends app-users comments to specified developer emails
* Includes user and app specific information

See: :doc:`../tethys_portal/feedback`

Handoff
-------

* Handoff Manager now available, which can be used from controllers to handoff from one app to another on the same Tethys portal (without having to use the REST API)
* The way handoff handler controllers are specified was changed to be consistent with other controllers

See: :doc:`../tethys_sdk/handoff`

Jobs Table Gizmo
----------------

* The refresh interval for job status and runtime is configurable

See: :doc:`../tethys_sdk/gizmos/jobs_table`

Social Authentication
---------------------

* Support for HydroShare added

See: :doc:`../tethys_portal/social_auth`

Dynamic Persistent Stores
-------------------------

* Persistent stores can now be created dynamically (at runtime)
* Helper methods to list persistent stores for the app and check whether a store exists.

See: :doc:`../tethys_sdk/persistent_store`

App Descriptions
----------------

* Apps now feature optional descriptions.
* An information icon appears on the app icon when descriptions are available.
* When the information icon is clicked on the description is shown.

See: :doc:`../tethys_sdk/app_class`

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

See: :doc:`../tethys_portal/social_auth`


D3 Plotting Gizmos
------------------

* D3 alternatives for all the HighCharts plot views
* Use the same plot objects to define both types of charts
* Simplified and generalized the mechanism for declaring plot views

See: :doc:`../tethys_sdk/gizmos/plot_view`

Job Manager Gizmo
-----------------

* New Gizmo that will show the status of jobs running with the Job Manager

Workspaces
----------

* SDK methods for creating and managing workspaces for apps
* List files and directories in workspace directory
* Clear and remove files and directories in workspace

See: :doc:`../tethys_sdk/workspaces`

Handoff
-------

* Use handoff to launch one app from another
* Pass arguments via GET parameters that can be used to retrieve data from the sender app

See: :doc:`../tethys_sdk/handoff`

Video Tutorials
---------------

* New video tutorials have been created
* The videos highlight working with different software suite elements
* CKAN, GeoServer, PostGIS
* Advanced user input forms
* Advanced Mapping and Plotting Gizmos

See: :doc:`../tutorials/video_tutorials`

New Location for Tethys SDK
---------------------------

* Tethys SDK methods centralized to a new convenient package: tethys_sdk

See: :doc:`../tethys_sdk`

Persistent Stores Changes
-------------------------

* Moved the get_persistent_stores_engine() method to the TethysAppBase class.
* To call the method import your :term:`app class` and call it on the class.
* The old get_persistent_stores_engine() method has been flagged for deprecation.

See: :doc:`../tethys_sdk/persistent_store`

Command Line Interface
----------------------

* New management commands including ``createsuperuser``, ``collectworkspaces``, and ``collectall``
* Modified behavior of ``syncdb`` management command, which now makes and then applies migrations.

See: :doc:`../tethys_sdk/tethys_cli`


Release 1.1.0
=============

Gizmos
------

* Options objects for configuring gizmos (see :doc:`../tethys_sdk/gizmos` for more details).
* Many improvements to Map View (see :ref:`map-view`)

  * Improved layer support including GeoJSON, KML, WMS services, and ArcGIS REST services
  * Added a mechanism for creating legends
  * Added drawing capabilities
  * Upgraded to OpenLayers version 3.5.0

* New objects for simplifying Highcharts plot creation (see :ref:`plot-view`)

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
