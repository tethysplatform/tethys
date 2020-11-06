.. _whats_new:

**********
What's New
**********

**Last Updated:** November 2020

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Multi-Factor Authentication
===========================

* Implemented Multi Factor Authentication via the `Django MFA2 app <https://pypi.org/project/django-mfa2/>`_.
* Time-based One Time Password (TOTP) method is enabled by default, but users must opt-in.
* Added MFA settings to User Profile Pages
* The Email OTP method has also been tested extensively and verified to work.
* Other methods have not been tested.

See: :ref:`multi_factor_auth_config`

Additional Single Sign-On Backends
==================================

* Added four new officially supported Single Sign-On/Social Authentication Methods.
* Renamed Documentation for "Social Authentication" to the more general "Single Sign On".
* New methods include: :ref:`social_auth_azuread`, :ref:`social_adfs`, :ref:`social_auth_onelogin`, and :ref:`social_auth_okta`.

See: :ref:`single_sign_on_config`

Automatic Lockout
=================

* Tethys Portal can now be configured to automatically lockout users after multiple failed login attempts.
* This feature is opt-in.

See: :ref:`advanced_config_lockout`


Jobs Table
==========

* The Status and Actions Columns have been revamped to simplify the Jobs Table.
* All action buttons (Delete, Resubmit, View Logs, etc.) have been moved into a drop down menu in the actions column.
* Simple versions of each status are now shown for single-status jobs instead of a filled progress bar.
* The progress bar is still used to show the status of multiple-status jobs (i.e. workflows).
* Several arguments for the Jobs Table are now deprecated in favor of a simpler method.
* Gizmo Showcase was updated for the Jobs Table.

See: :ref:`jobs-table`

Cesium Map View
===============

* Added support for ENV and VIEWPARAMS when using MVLayer with Cesium Map View.

See: :ref:`cesium-map-view`

jQuery
======

* Updated jQuery to 3.5.1 to address known vulnerability in previous version.

Documentation
-------------

* Added documentation that describes how to configure Tethys Platform to use REDIS as a Channels backend for production.

See: :ref:`production_channels_config` and :ref:`production_official_docker`

Bug Fixes
=========

* Fixed an issue with the tethys command line interface not working on systems without Docker installed.
* Fixed issue with Add User admin page that would prevent adding additional users after the first user was added.
* Modified the Condor Scheduler admin pages to use the PasswordInput field for the password fields.
* Updated the default ASGI configuration file so that it can be killed properly by supervisor when stopped.

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
