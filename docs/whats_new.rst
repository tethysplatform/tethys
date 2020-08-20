.. _whats_new:

**********
What's New
**********

**Last Updated:** August 2020

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

App Permissions Assigned to Groups
----------------------------------

* App permissions can now be assigned directly to permission Groups in the admin pages.
* Adding an app to the permission Group will reveal a dialog to select which of the app permissions to also assign.
* Assign users to the permission Group to grant them those permissions within the app.
* This is an opt-in feature: set ENABLE_RESTRICTED_APP_ACCESS to True in portal_config.yml to use this feature.

See: :ref:`tethys_portal_app_permission_groups`

App Access Permissions
----------------------

* Apps now have an access permission that can be used to grant access to specific users or groups.
* When a users does not have access to an app it will be hidden in the apps library.
* If a user without permission to access an app enters one of the app URLs, they will see a 404 page.
* Configure access to apps by creating a permission Group with access to the App and then assign any number of users to that group.
* The access permission is automatically enforced for all views of apps.
* This is an opt-in feature: set ENABLE_RESTRICTED_APP_ACCESS to True in portal_config.yml to use this feature.

See: :ref:`tethys_portal_app_permission_groups`

Custom Home and App Library Styles and Templates
------------------------------------------------

* Portal admins can now customize the Home or App library pages with custom CSS or HTML.
* Two new settings groups in Site Settings section of admin pages.
* Specify CSS directly into the setting or reference a file in a discoverable Static path.
* Specify the path to custom templates in a discoverable Templates path.

See: :ref:`production_customize_theme`

Additional Base Templates for Apps
----------------------------------

* There are 9 new base templates for Apps that simplify implementing common layouts.
* Specify the desired base template in the ``extends`` tag of the app template.

See: :ref:`additional_base_templates`

New Features for Jobs Table
---------------------------

* Logs action that displays job logs while job is running.
* Monitor job action that can be implemented to display live results of job as it runs.
* Jobs can be grouped and filtered by permission Groups in addition to User.
* Resubmit job action.

See: :ref:`jobs-table`

Official Docker Image Improvements
----------------------------------

* Additional options added to ``run.sh`` to allow it to be run in different modes (daemon, test, etc.) to facilitate testing.
* Adds two new Salt Scripts to make it easier to extend without duplicating steps.
* ``pre_tethys.sls``: prepares static and workspace directories in persistent volume location.
* ``post_app.sls``: runs ``collectstatic`` and ``collectall`` and syncs configuration files to persistent volume location.
* New documentation for using the Official Docker Image

See: :ref:`production_official_docker`

Tethys Portal Configuration
---------------------------

* Fixed inconsistencies with documentation and behavior.
* Fixed issues with some of the groups that weren't working.
* The way logging settings are specified is more straight-forward now.

See: :ref:`tethys_configuration`

Install Command
---------------

* New ``--no-db-sync`` option to ``tethys install`` command to allow for installing the app code without the database sync portion.
* This is helpful in contexts where the database is unavailable during installation such as in a Docker build.

See: :ref:`tethys_cli_install`

Collectstatic Command
---------------------

* Behavior of ``collectstatic`` command changed to copy the static directory instead of link it to be more consistent with how other static files are handled.
* Alleviates a workaround that was necessary in SE Linux environments (the links couldn't be followed).
* Old linking behavior still available via the ``--link`` option.

See: :ref:`tethys_manage_cmd`

Expanded Earth Engine Tutorials
-------------------------------

* Two additional follow-on tutorials to the Earth Engine tutorial.
* Part 2 - add additional pages to app, layout with Bootstrap grid system, upload files, add REST API.
* Part 3 - prepare app for production deployment and publishing on GitHub, deploy to production server.

See: :ref:`tutorial_google_earth_engine`

All New Production Installation Guide
-------------------------------------

* Near complete rewrite of the production installation documentation.
* Examples shown for both Ubuntu and CentOS.
* Expanded from a 1 page document to 25+ documents.
* Moved many documents that were in Tethys Portal to configuration section of production installation docs.
* All existing documentation was updated.

See: :ref:`production_installation`

Docs Fixes
----------

* Added example for SSL firewall configuration.
* Various fixes to make THREDDS and GEE tutorials more clear.
* Tethys Portal Configuration documentation fixed.


Bug Fixes
---------

* Fixed bug with scaffolding extensions.
* Compatibility changes for Bokeh 2.0.0.
* Fixes broken URIs for password reset capability.

Security Updates
----------------

* Return 404 instead of 403 on pages that require login to prevent directory mapping.
* Disable caching on login and register pages.


Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
