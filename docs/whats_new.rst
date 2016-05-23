**********
What's New
**********

**Last Updated:** March 25, 2016

Refer to this article for information about each new release of Tethys Platform.

Release 1.4.0
=============

GeoServer
---------

* The GeoServer docker was updated to version 2.8.2
* It can be configured to run in clustered mode (multiple instances of GeoServer running inside the container) for greater stability and performance
* Several extensions are now included:

   * `JMS Clustering <http://docs.geoserver.org/stable/en/user/community/jms-cluster/index.html>`_
   * `Flow Control <http://docs.geoserver.org/2.8.x/en/user/extensions/css/index.html>`_
   * `CSS Styles <http://docs.geoserver.org/2.8.x/en/user/extensions/controlflow/index.html>`_
   * `NetCDF <http://docs.geoserver.org/2.8.x/en/user/extensions/netcdf/netcdf.html>`_
   * `NetCDF Output <http://docs.geoserver.org/2.8.x/en/user/extensions/netcdf-out/index.html>`_

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
* See: :doc:`tethys_sdk/gizmos/map_view`

PlotView Gizmo
--------------

* New JavaScript API endpoints for initializing PlotViews dynamically.
* See: :doc:`tethys_sdk/gizmos/plot_view`


Bug Fixes
---------

* Fixed various bugs...




Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
