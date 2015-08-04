**********
What's New
**********

**Last Updated:** August 4, 2015

Refer to this article for information about each new release of Tethys Platform.


Release 1.2.0
=============

Social Authentication
---------------------


D3 Plotting Gizmos
------------------


Job Manager Gizmo
-----------------


Job Manager Updates
-------------------


Workspaces
----------


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






