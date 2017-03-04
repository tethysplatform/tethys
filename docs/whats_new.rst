**********
What's New
**********

**Last Updated:** December 10, 2016

Refer to this article for information about each new release of Tethys Platform.

Release 1.5.0
=============

Install With Miniconda
----------------------

TODO

See:

HydroShare OAuth Backend and Helper Function
--------------------------------------------

* Refactor default HydroShare OAuth backend; Token refresh is available; Add backends for HydroShare-beta and HydroShare-playground.
* Include hs_restclient library in requirements.txt; Provide a helper function to help initialize the ``hs`` object based on HydroShare social account.
* Update python-social-auth to 0.2.21.

See: :doc:`tethys_portal/social_auth`

Map View
--------

* Updated OpenLayers libraries to version 4.0.1
* Can configure styling of MVDraw layer
* New editable attribute for MVLayers to lock layers from being edited
* Added data attribute to MVLayer to allow passing custom attributes with layers for use in custom JavaScript

See: :doc:`tethys_sdk/gizmos/map_view`

Esri Map View
-------------

TODO

See:

Gizmos
------

TODO

* New way to call them
* New load dependencies Method
* Updated select_gizmo to allow Select2 options to be passed in.

See:

Plotly and Bokeh Gizmos
-----------------------

* True open source options for plotting in Tethys

See:



Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
