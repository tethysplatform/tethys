.. _whats_new:

**********
What's New
**********

**Last Updated:** March 2026

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

Tethys Run (Express Mode)
-------------------------

* The new ``tethys run`` command runs a single-file component app with zero configuration — no portal configuration, no database setup, no ``pip install``, and no login required.
* Inspired by tools like Shiny and Streamlit, it lowers the barrier to entry for building Tethys apps: write one Python file and run it with one command.
* Apps developed this way run on the standard portal machinery and can be installed in a full Tethys Portal without modification.

See: :ref:`tethys_run_cmd`

New Recipes
-----------

* Tethys Platform has introduced new Recipes, which are step-by-step guides for common tasks and workflows.
* Recipes are designed to help both new and experienced users quickly find and implement solutions for various Tethys Platform functionalities.
* Recipes for MapLayout and using GeoServer in Tethys have been added. More recipes will be added over time.

See: :ref:`recipes`

SQLite Persistent Stores
------------------------

* Tethys Platform now supports SQLite persistent stores, allowing for lightweight, file-based database storage for Tethys apps.
* This feature is particularly useful for development and testing environments where a full database server is not required.
* When running Tethys Platform migrations, all existing persistent stores will be updated to PostgreSQL persistent stores.

See: :ref:`persistent_stores_api`

Buy Me a Soda
-------------
* Tethys Platform has added a "Buy Me a Soda" button to the documentation, allowing users to support the project financially.
* This is a way for users to contribute to the ongoing development and maintenance of Tethys

See: :ref:`contribute_documentation`

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases