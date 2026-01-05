.. _whats_new:

**********
What's New
**********

**Last Updated:** November 2025

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

Django 3.2 Support Dropped
--------------------------

* Tethys Platform has dropped support for Django 3.2 due to its end-of-life status.
* Users are encouraged to upgrade to Django 4.2 or later to take advantage of the latest features and security updates.
* Tethys Platform has been compatible with Django 4.2 and Django 5.x since version 4.3 allowing you to migrate before updating to Tethys Platform 4.4.

See: :ref:`development_installation` and `PR 1202 <https://github.com/tethysplatform/tethys/pull/1202>`_

Component Apps
--------------

* Build dynamic, pure-Python Tethys Apps using ReactPy--no JavaScript required.

See: :ref:`tethys_components`

Scaffold Apps Graphically
-------------------------

* Tethys Portal features an option to scaffold and import apps graphically.
* This feature is currently only supported for admin/staff users in development mode (i.e. DEBUG=True).

See: :ref:`scaffold_an_app_via_the_portal`

Cookie Privacy Consent
----------------------

* Tethys Portal now supports an optional cookie privacy consent management using the `django-cookie-consent <https://django-cookie-consent.readthedocs.io/en/latest/>`_ library.
* When enabled, end users will be presented with a cookie consent banner upon their first visit to the portal.
* App developers can add a new cookies.yaml file to their apps to declare and categorize cookies used by their apps.

See: :ref:`cookie_consent`

Paths API CLI
--------------

* Tethys Platform now includes a new CLI for the Paths API, allowing for easier management and interaction with paths in Tethys apps.
* Use the Paths CLI to find the location of the various workspaces and media directories associated with Tethys apps.
* Add files to app and user workspaces and media directories directly from the command line.

See: :ref:`paths_cmd` and :ref:`tethys_paths_cli`

Recipes
-------

* Introducing Recipes--a new documentation tool featuring condensed, step-by-step guides for common Tethys Platform tasks.
* Recipes are designed to help both new and experienced users quickly find and implement solutions for various Tethys Platform functionalities.
* Recipes are reference guides that complement the more detailed tutorials and reference documentation.
* More recipes will be added over time.

See: :ref:`recipes`

Multi-Tenancy Support
---------------------

* Tethys Platform now supports multi-tenancy using the third-party `django-tenants` library. 
* This allows you to run multiple isolated configurations of Tethys Portal within a single portal.

See: :ref:`Multi Tenancy <multi_tenancy_config>`

Automated PyPI Package Uploads
------------------------------

* Tethys Platform now features automated uploads to PyPI for new releases.
* This enables support for installing Tethys Platform with pip and other PyPI-based package managers.

See: The "Pip" tab on :ref:`quickstart` and :ref:`getting_started_install_tethys`

Container Scanning
------------------

* Tethys Platform Docker images are now automatically scanned for vulnerabilities.
* Many vulnerabilities have been identified and resolved in the official Docker images starting with version 4.4.
* For the most secure image, use images for the latest versions of Python and Django that are supported by Tethys Platform.

See: `PR 1197 <https://github.com/tethysplatform/tethys/pull/1197>`_

Clear Option for Collectstatic
------------------------------
* A new option has been added to the `tethys manage collectstatic` command to clear existing static files before collecting new ones.
* A new `STATIC_ROOT_CLEAR` environment variable (default "True") has been added to the Docker image to enable static files reset on every start-up.
* This prevents stale static files persisting across deployments when the static files are stored in a persistent volume.

See: :ref:`tethys_manage_cmd` and `PR 1188 <https://github.com/tethysplatform/tethys/pull/1188>`_

Bug Fixes
---------

* `Component App fixes <https://github.com/tethysplatform/tethys/pull/1206>`_
* `SINGLE_APP_MODE Url Fix with React App <https://github.com/tethysplatform/tethys/pull/1204>`_
* `Fix Conda deprecated API: conda.cli.python_api -> conda.testing.conda_cli <https://github.com/tethysplatform/tethys/pull/1198>`_
* `Quotas bug fix <https://github.com/tethysplatform/tethys/pull/1192>`_
* `Scaffold fixes <https://github.com/tethysplatform/tethys/pull/1182>`_
* `Updated MFA Admin placeholder name <https://github.com/tethysplatform/tethys/pull/1208>`_

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
