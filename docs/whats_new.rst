**********
What's New
**********

**Last Updated:** August 11, 2015

Refer to this article for information about each new release of Tethys Platform.


Release 1.2.0
=============

Social Authentication
---------------------

* Social login supported
* Google, LinkedIn, and Facebook
* HydroShare coming soon
* New controls on User Profile page to manage social accounts

See: :doc:`./tethys_portal/social_auth`


D3 Plotting Gizmos
------------------

* D3 alternatives for all the HighCharts plot views
* Use the same plot objects to define both types of charts
* Simplified and generalized the mechanism for declaring plot views

See: :doc:`./tethys_sdk/gizmos_api`

Job Manager Gizmo
-----------------

* New Gizmo that will show the status of jobs running with the Job Manager

Job Manager Updates
-------------------


Workspaces
----------

* SDK methods for creating and managing workspaces for apps
* List files and directories in workspace directory
* Clear and remove files and directories in workspace

See: :doc:`./tethys_sdk/workspaces`

Handoff
-------

* Use handoff to launch one app from another
* Pass arguments via GET parameters that can be used to retrieve data from the sender app

See: :doc:`./tethys_sdk/handoff`

Video Tutorials
---------------

* New video tutorials have been created
* The videos highlight working with different software suite elements
* CKAN, GeoServer, PostGIS
* Advanced user input forms
* Advanced Mapping and Plotting Gizmos

See: :doc:`./tutorials/video_tutorials`

New Location for Tethys SDK
---------------------------

* Tethys SDK methods centralized to a new convenient package: tethys_sdk

See: :doc:`./tethys_sdk`

Persistent Stores Changes
-------------------------

* Moved the get_persistent_stores_engine() method to the TethysAppBase class.
* To call the method import your :term:`app class` and call it on the class.
* The old get_persistent_stores_engine() method has been flagged for deprecation.

See: :doc:`./tethys_sdk/persistent_store`

Command Line Interface
----------------------

* New management commands including ``createsuperuser``, ``collectworkspaces``, and ``collectall``
* Modified behavior of ``syncdb`` management command, which now makes and then applies migrations.

See: :doc:`./tethys_sdk/tethys_cli`


Release 1.1.0
=============

Gizmos
------

* Options objects for configuring gizmos (see :doc:`./tethys_sdk/gizmos` and :doc:`./tethys_sdk/gizmos_api` for more details).
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






