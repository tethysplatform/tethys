******************
App Base Class API
******************

**Last Updated:** May 11, 2016

Tethys apps are configured via the :term:`app class`, which is contained in the :term:`app configuration file` (:file:`app.py`) of the :term:`app project`. The :term:`app class` must inherit from the ``TethysAppBase`` class to be loaded properly into CKAN. The following article contains the API documentation for the ``TethysAppBase`` class.

.. autoclass:: tethys_apps.base.app_base.TethysAppBase
    :members: url_maps, permissions, persistent_stores, handoff_handlers, get_handoff_manager, job_templates, get_job_manager, get_user_workspace, get_app_workspace, get_persistent_store_engine, create_persistent_store, list_persistent_stores, persistent_store_exists