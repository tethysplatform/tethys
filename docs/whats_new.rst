**********
What's New
**********

**Last Updated:** December 2018

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

Python 3 Support
----------------

* Python 3 officially supported in Tethys Platform.
* Python 2 support officially deprecated and will be dropped when Tethys Platform 3.0 is released.
* Tethys needs to migrate to Python 3 only so we can upgrade to Django 2.0, which only supports Python 3.

.. important::

    Migrate your apps to Python 3. After Tethys Platform 3.0 is released, Python 2 will no longer be supported by Tethys Platform.


100% Unit Test Coverage
-----------------------

* Tests pass in Python 2 and Python 3.
* Unit tests cover 100% of testable code.
* Code base linted using flake8 to enforce PEP-8 and other Python coding best practices.
* Automated test execution on Travis-CI and Stickler-CI whenever a Pull Request is submitted.
* Added badges to the README to display build/testing, coverage, and docs status on github repository.
* All of this will lead to increased stability in this and future releases.

See: `Tethys Platform Repo <https://github.com/tethysplatform/tethys>`_ for build and coverage information.

Tethys Extensions
-----------------

* Customize Tethys Platform functionality.
* Create your own gizmos.
* Centralize app logic that is common to multiple apps in an extension.

See: :doc:`./tethys_sdk/extensions`

Map View Gizmo
--------------

* Added support for many more basemaps.
* Added Esri, Stamen, CartoDB.
* Support for custom XYZ services as basemaps.
* User can set OpenLayers version.
* Uses jsdelivr to load custom versions (see: `<https://cdn.jsdelivr.net/npm/openlayers>`_)
* Default OpenLayers version updated to 5.3.0.

See: :doc:`tethys_sdk/gizmos/map_view`

Class-based Controllers
-----------------------

* Added ``TethysController`` to SDK to support class-based views in Tethys apps.
* Inherits from django ``View`` class.
* Includes ``as_controller`` method, which is a thin wrapper around ``as_view`` method to better match Tethys terminology.
* UrlMaps can take class-based Views as the controller argument: ``MyClassBasedController.as_controller(...)``
* More to come in the future.

See: `Django Class-based views <https://docs.djangoproject.com/en/2.1/topics/class-based-views/>`_ to get started.

Partial Install Options
-----------------------

* The Tethys Platform installation scripts now allow for partial installation.
* Install in existing Conda environment or against existing database.
* Upgrade using the install script!
* Linux and Mac only.

See: :doc:`./installation/linux_and_mac` and :doc:`./installation/update`

Commandline Interface
---------------------

* New commands to manage app settings and services.
* ``tethys app_settings`` - List settings for an app.
* ``tethys services`` - List, create, and remove Tethys services (only supports persistent store services and spatial dataset services for now).
* ``tethys link`` - Link/Assign a Tethys service to a corresponding app setting.
* ``tethys schedulers`` - List, create, and remove job Schedulers.
* ``tethys manage sync`` - Sync app and extensions with Tethys database without a full Tethys start.

See: :ref:`tethys_cli_app_settings`, :ref:`tethys_cli_services`, :ref:`tethys_cli_link`, :ref:`tethys_cli_schedulers`, and :ref:`tethys_manage_cmd`

Dockerfile
----------

* New Dockerfile for Tethys Platform.
* Use it to build Docker images.
* Use it as a base for your own Docker images that have your apps installed.
* Includes supporting salt files.
* Dockerfile has been optimized to minimize the size of the produced image.
* Threading is enabled in the Docker container.

See: `Docker Documentation <https://docs.docker.com/get-started/>`_ to learn how to use Docker in your workflows.

API Tokens for Users
--------------------
* API tokens are automatically generated for users when they are created.
* Use User API tokens to access protected REST API views.

Documentation
-------------
* Added SSL setup instruction to Production Installation (see: :ref:`production_installation_ssl`)

Bugs
----

* Fixed grammar in forget password link.
* Refactored various methods and decorators to use new way of using Django methods ``is_authenticated`` and ``is_anonymous``.
* Fixed bug with Gizmos that was preventing errors from being displayed when in debug mode.
* Fixed various bugs with uninstalling apps and extensions.
* Fixed bugs with get_persistent_store_setting methods.
* Fixed a naming conflict in the SelectInput gizmo.
* Fixed numerous bugs identified by new tests.

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
