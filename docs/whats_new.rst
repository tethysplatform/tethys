.. _whats_new:

**********
What's New
**********

**Last Updated:** December 2021

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Production Installation Docs
============================

* Expanded the docs for manual production installation
* Added a tutorial and documentation for using the Tethys Docker for production releases
* Added documentation explaining the new Microsoft Azure Tethys Platform Image

Cesium Map View Gizmo
=====================

* Added support for Cesium Ion Primitives
* Added JavaScript API for the `CesiumMapView` to allow loading with Ajax

Dockerfile
==========

* Added build args to Dockerfile to allow Python version to be specified

Tethys CLI
==========

* Added support for specifying the type of spatial service (e.g. GeoServer or THREDDS) in the `tethys services create spatial` command
* Added support for setting custom settings via the `tethys app_settings` command

Bug Fixes
=========

- Pinned version of psycopg2 to be compatible with Django 2.2
- Fixed Plotly tests for compatibility with newer version
- Updated CDN URL for compatibility
- Updated tests to be compatible with Bokeh 2.4.0

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
