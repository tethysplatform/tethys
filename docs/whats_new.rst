**********
What's New
**********

**Last Updated:** May 2017

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

Powered by Miniconda Environment
--------------------------------

* Tethys Platform is now installed in a Miniconda environment.
* Using the Miniconda includes Conda, an open source Python package management system
* Conda can be used to install Python dependencies as well as system dependencies
* Installing packages like GDAL or NetCDF4 are as easy as ``conda install gdal``
* Conda is cross platform: it works on Windows, Linux, and MacOS

See: `Miniconda <https://conda.io/miniconda.html>`_ and `Conda <https://conda.io/docs/>`_

App Settings
------------

* Developers can create App Settings, which are configured in the admin interface of the Tethys Portal.
* Types of settings that can be created include Custom Settings, Persistent Store Settings, Dataset Service Settings, Spatial Dataset Service Settings, and Web Processing Service Settings.
* The way Tethys Services are allocated to apps is now done through App Settings.
* All apps using the Persistent Stores APIs, Dataset Services APIs, or Web Processing Services APIs prior to version 2.0.0 will need to be refactored to use the new App settings approach.

See: :doc:`./tethys_sdk/app_settings`

Gizmos
------

* New way to call them
* New load dependencies Method
* Updated select_gizmo to allow Select2 options to be passed in.

See: :doc:`tethys_sdk/gizmos`

Map View
--------

* Updated OpenLayers libraries to version 4.0
* Can configure styling of MVDraw layer
* New editable attribute for MVLayers to lock layers from being edited
* Added data attribute to MVLayer to allow passing custom attributes with layers for use in custom JavaScript

See: :doc:`tethys_sdk/gizmos/map_view`

Esri Map View
-------------

* New map Gizmo that uses ArcGIS for JavaScript API.

See: :doc:`tethys_sdk/gizmos/esri_map`

Plotly and Bokeh Gizmos
-----------------------

* True open source options for plotting in Tethys

See: :doc:`tethys_sdk/gizmos/bokeh_view` and :doc:`tethys_sdk/gizmos/plotly_view`

Commandline Interface
---------------------

* Added ``tethys list`` command that lists installed apps.

See: :ref:`tethys_list_cmd`

Templating API
--------------

* Leaner, updated theme for app base template.
* New ``header_buttons`` block for adding custom buttons to app header.

See: :doc:`tethys_sdk/templating`

HydroShare OAuth Backend and Helper Function
--------------------------------------------

* Refactor default HydroShare OAuth backend; Token refresh is available; Add backends for HydroShare-beta and HydroShare-playground.
* Include hs_restclient library in requirements.txt; Provide a helper function to help initialize the ``hs`` object based on HydroShare social account.
* Update python-social-auth to 0.2.21.

See: :doc:`tethys_portal/social_auth`

Bugs
----

* Fixed issue where ``tethys uninstall <app>`` command was not uninstalling fully.

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
