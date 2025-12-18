.. _whats_new:

**********
What's New
**********

**Last Updated:** November 2024

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Major Features
--------------

Django 4/5 Support
..................

* Tethys Platform 4.3 is compatible with Django versions 4.2 - 5.x. It is now recommended to explicitly specify the version of Django that you want when you create your tethys environment.

See: :ref:`development_installation`

New Logo
........

* The new logo design that is on the `Tethys Platform <https://www.tethysplatform.org/>`_ website is now in the default configuration of the Tethys Portal.

Single App Mode
...............

* Tethys can now be used to deploy just a single app by setting the new `MULTIPLE_APP_MODE` setting to `False`.

See: :ref:`tethys_portal_config_settings`

Paths API
.........

* The new Paths API replaces the Workspaces API (which will still be supported until version 5.0) and provides access to the new Media directories and the App Resources directory. It also makes better use of the Python `pathlib` library.

See: :ref:`tethys_paths_api`

Async Support for the Jobs Table Gizmo
......................................

* Jobs Table actions callbacks are now asynchronous enabling them to run without blocking the webserver. Custom actions can also be `async`.

See: :ref:`jobs-table`

Multi-Tenancy Support
.....................

* Tethys Platform now supports multi-tenancy using the third-party `django-tenants` library. This allows you to run multiple isolated configurations of Tethys Portal within a single portal.
See: :ref:`Multi Tenancy <multi_tenancy_config>`

For a full list of changes in version 4.4 refer to `<https://github.com/tethysplatform/tethys/releases/tag/4.4.0>`_

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
