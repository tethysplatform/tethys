**********
What's New
**********

**Last Updated:** December 14, 2015

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

Spatial Dataset Services
------------------------

* Upgraded gsconfig dependency to version 1.0.0
* Provide two new methods on the geoserver engine to create SQL views and simplify the process of linking PostGIS databases with GeoServer.

See: :doc:`./tethys_sdk/spatial_dataset_service/geoserver_reference`

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

Bugs
----

* Missing initial value parameter was added to the select and select2 gizmos.
* Addressed several cases of mixed content warnings when running behind HTTPS.
* The disconnect social account buttons are now disabled if your account doesn't have a password or there is only one social account associated with the account.
* Fixed issues with some of the documentation not being generated.
* Fixed styling issues that made the Message Box gizmo unusable.
* Normalized references to controllers, persistent store initializers, and handoff handler functions.
* Various docs typos were fixed.
* Plot view was fixed to allow parameter overwriting as was intended.

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
