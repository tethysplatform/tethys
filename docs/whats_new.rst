.. _whats_new:

**********
What's New
**********

**Last Updated:** May 2023

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Python 3.11
-----------

* Verified Tethys Platform works using Python 3.11

Secret and JSON Custom Settings
-------------------------------

* Added two new types of Custom App Settings: Secret and JSON.
* The values of Secret Custom settings are encrypted for additional security of sensitive data (e.g. passwords, API keys, etc.).
* JSON Custom settings store JSON strings and can be initialized from a JSON file.
* The app settings page provides an embedded JSON editor for JSON Custom settings.

See: :ref:`app_settings_custom_settings`,  :ref:`tethys_portal_secret_settings`, and :ref:`tethys_portal_json_settings`

Tethys CLI
----------

* Added Docker image (``-i``) name and tag (``-t``) options to the ``tethys docker`` command to allow users to override the default images installed by the ``init`` and ``update`` command.
* Added port (``-o``) option to tethys scheduler create-condor CLI command.
* Link Schedulers to App Settings using the ``tethys link`` command.

See: :ref:`tethys_cli_docker`, :ref:`tethys_cli_schedulers`, and :ref:`tethys_cli_link`

Support for Other Databases
---------------------------

* Removed PostgreSQL specific model code for the primary Tethys Platform database to allow using other database engines (MySQL, Microsoft SQL, SQLite, etc.).
* Made SQLite the default database engine for the Tethys Platform database.
* Note: Persistent stores still require PostgreSQL, but work is being done to all support for more datbase engines.


Miscellaneous Changes
---------------------

* Removed unused site settings.
* Refactored base templates for user and account pages to allow for separation and more control with custom CSS settings.
* Various improvements for Production deployments (See `Pull Request 942 <https://github.com/tethysplatform/tethys/pull/942>`_).

Documentation
-------------

* Updated the Docker Production Deployment Tutorial for Tethys 4

Bug Fixes
---------

* Fix `Issue 931 Map Layout Bug Fixes <https://github.com/tethysplatform/tethys/pull/931>`_
* Fix `Issue 940 Update THREDDS Docker version (4.6.20 no longer published) <https://github.com/tethysplatform/tethys/pull/940>`_
* Fix `Issue 946 Fixed issue with tethys install when libmamba is set to default solver <https://github.com/tethysplatform/tethys/pull/946>`_

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
