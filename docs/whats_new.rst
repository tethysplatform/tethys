**********
What's New
**********

**Last Updated:** September 2019

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

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

See: :doc:`./installation`

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

See: :doc:`./tutorials/websockets`

Bokeh Integration
-----------------

* Bokeh's functionality to link backend Python objects to frontend JavaScript objects has been added.

See: :ref:`bokeh_integration`

See: :doc:`./tutorials/bokeh`

URL Maps API
------------

* Documentation for Tethys ``url_maps`` and ``UrlMap`` has been added. This includes a description of the newly added ``UrlMap`` parameters with ``Websockets`` and ``Bokeh Integration``.

See: :doc:`./tethys_sdk/url_maps`

Django Analytical
-----------------

* Tethys comes with `Django Analytical <https://django-analytical.readthedocs.io/en/latest/>`_ installed to enable support form a number of analytics and tracking services.
* You can now enable analytics tracking (e.g. Google Analytics) to every page of your apps and portal with a few settings in the settings file.

See: :doc:`./tethys_portal/webanalytics`

Tethys Quotas
-------------

* Tethys Quotas allow portal administrators to have better control over the resources being used by users and apps (e.g. disk storage).
* Tethys ships with quotas for workspace storage implemented, but it is disabled by default. When enabled, portal administrators can set limits on the storage users or apps are able to use.
* Tethys Quotas are completely extensible, allowing developer to create custom quotas for other resources (e.g. memory usage, database storage, wall time hours, etc.).

See: :doc:`./tutorials/quotas` and :doc:`./tethys_sdk/tethys_quotas`

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

See: :doc:`./tethys_cli`

Automatic Application Installation
----------------------------------

* App now require an ``install.yml`` file which allows dependencies to be installed using conda or pip.
* Apps can also use an optional ``services.yml`` portal specific file that will automatically link services.
* The CLI has a new command for installing apps: `tethys install`.

See: :doc:`./installation/application`, :ref:`tethys_install_yml`, :ref:`tethys_services_yml`, and :ref:`Install Command <tethys_cli_install>`


New App Installation Approach
-----------------------------

* The structure of apps and the way they are installed has changed.
* The changes will allow Tethys to be updated in the future without the need to reinstall apps afterward.
* Tethys 2 Apps will need to be migrated to work in Tethys 3.

.. toctree::
   :maxdepth: 2

   whats_new/app_migration

Dask Job Type
-------------

* New TethysJob types for submitting and managing Dask Jobs.
* Dask allows pure Python code to be automagically parallelized and executed accross a distributed cluster of nodes.

See: :doc:`./tethys_sdk/jobs/dask_job_type` API documentation and the :doc:`./tutorials/dask` tutorial

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


Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
