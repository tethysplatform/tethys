**********
What's New
**********

**Last Updated:** January 19, 2016

Refer to this article for information about each new release of Tethys Platform.

Release 1.3.0
=============

Tethys Portal
-------------

* Open account signup disabled by default
* New setting in `settings.py` that allows open signup to be enabled

See: :doc:`./tethys_portal/customize`

Map View
--------

* Feature selection enabled for ImageWMS layers
* Clicking on features highlights them when enabled
* Callback functions can be defined in JavaScript to trap on the feature selection change event
* Custom styles can be applied to highlighted features
* Basemap can be disabled
* Layer attributes can be set in MVLayer (e.g. visibility and opacity)
* Updated to use OpenLayers 3.10.1

See: :doc:`./tethys_sdk/gizmos/map_view`

Plot View
---------

* D3 plotting implemented as a free alternative to Highcharts for line plot, pie plot, scatter plot, bar plot, and timeseries plot.

See: :doc:`./tethys_sdk/gizmos/plot_view`

Spatial Dataset Services
------------------------

* Upgraded gsconfig dependency to version 1.0.0
* Provide two new methods on the geoserver engine to create SQL views and simplify the process of linking PostGIS databases with GeoServer.

See: :doc:`./tethys_sdk/spatial_dataset_service/geoserver_reference`

App Feedback
------------

* Places button on all app pages that activates a feedback form
* Sends app-users comments to specified developer emails
* Includes user and app specific information

See: :doc:`./tethys_portal/feedback`

Handoff
-------

* Handoff Manager now available, which can be used from controllers to handoff from one app to another on the same Tethys portal (without having to use the REST API)
* The way handoff handler controllers are specified was changed to be consistent with other controllers

See: :doc:`./tethys_sdk/handoff`

Jobs Table Gizmo
----------------

* The refresh interval for job status and runtime is configurable

See: :doc:`./tethys_sdk/gizmos/jobs_table`

Social Authentication
---------------------

* Support for HydroShare added

See: :doc:`./tethys_portal/social_auth`

Dynamic Persistent Stores
-------------------------

* Persistent stores can now be created dynamically (at runtime)
* Helper methods to list persistent stores for the app and check whether a store exists.

See: :doc:`./tethys_sdk/persistent_store`

App Descriptions
----------------

* Apps now feature optional descriptions.
* An information icon appears on the app icon when descriptions are available.
* When the information icon is clicked on the description is shown.

See: :doc:`./tethys_sdk/app_class`

Bugs
----

* Missing initial value parameter was added to the select and select2 gizmos.
* Addressed several cases of mixed content warnings when running behind HTTPS.
* The disconnect social account buttons are now disabled if your account doesn't have a password or there is only one social account associated with the account.
* Fixed issues with some of the documentation not being generated.
* Fixed styling issues that made the Message Box gizmo unusable.
* Normalized references to controllers, persistent store initializers, and handoff handler functions.
* Various docs typos were fixed.

Patches
-------

* 1.3.1
   * Updated dependency for condorpy to fix status for muti-process jobs on the jobs table.
* 1.3.2
   * Documentation update to reference new tutorial. See :doc:`./tutorials/dam_break`.
* 1.3.3
   * Locked down Python Social Auth dependency to version 0.2.13. Versions after this one break social authentication.

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
