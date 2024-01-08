.. _whats_new:

**********
What's New
**********

**Last Updated:** November 2023

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Python 3.12
-----------

* Verified Tethys Platform works using Python 3.12

Conda Forge Package
-------------------

* Tethys Platform is now fully packaged on conda-forge!

See: :ref:`development_installation`

Optional Dependencies and Micro Tethys
--------------------------------------

* Made many of the dependencies of ``tethys-platform`` optional and released new ``micro-tethys-platform`` conda package on the ``tethysplatform`` channel with minimal dependencies
* Updated docs to reflect what features are now optional and what dependencies are needed to support those features

.. note::

    The ``tethys-platform`` conda package for version 4.2 will still install all of the optional dependencies for backwards compatibility. Starting with Tethys version 5.0 the ``tethys-platform`` package will only have required dependencies. The ``micro-tethys-platform`` package, available on the ``tethysplatform`` channel, will install only the required dependencies allowing for a smaller Tethys environment.

See: :ref:`optional_features`, :ref:`development_installation`

Map Layout
----------

* Add labeling support for geojson features in MapLayout and MapView Gizmo.

See: `label_options` in :ref:`map_layout`

Admin Pages
-----------

* Added ability to have an icon on proxy app cards in the apps library to distinguish from native apps

See: :ref:`portal_admin_proxy_apps`

Settings
--------

* Added new ``PREFIX_URL`` to enable modifying all portal URLs with a prefix
* Added new settings ``ADDITIONAL_URLPATTERNS`` and ``ADDITIONAL_TEMPLATE_DIRS`` to allow more flexibility for supporting Django plugins
* Replaced deprecated setting ``AXES_ONLY_USER_FAILURES`` with recommended setting ``AXES_LOCKOUT_PARAMETERS``

See: :ref:`tethys_configuration`

OAuth2 Provider
---------------

* Added support for the Django OAuth Toolkit plugin to allow a Tethys portal to be an OAuth provider.

See: :ref:`optional_features`

Tethys CLI
----------

* Added a ``--urls`` option to the ``tethys list`` command to list the ``UrlMaps`` for apps.

See: :ref:`tethys_list_cmd`

Bokeh
-----

* Added support for Bokeh version 3

Jobs Table Gizmo
----------------

* Added a ``cached_status`` property to Tethys Jobs and optimized how the ``JobsTable`` gizmo loads statuses
* Added ability to sort jobs in the ``JobsTable`` gizmo and specify sorting key

See: :ref:`jobs-table`

Bug Fixes
---------

* Fixed issue with the TethysJob update-status callback endpoint not updating job status
* Fixed issue with assigning Custom JSON setting error when installing from file
* Fixed `Issue 985  Remove References to UrlMaps in Gizmo Docs <https://github.com/tethysplatform/tethys/issues/985>`_
* Fixed `Issue 881 The OneLoginOIDC Oauth backend is not compatible with the latest version of social-auth-core <https://github.com/tethysplatform/tethys/issues/881>`_
* Fixed `Issue 976 Invalid Links for Map View Controls <https://github.com/tethysplatform/tethys/issues/976>`_

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
