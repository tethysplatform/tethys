******************
App Base Class API
******************

**Last Updated:** May 2017

Tethys apps are configured via the :term:`app class`, which is contained in the :term:`app configuration file` (:file:`app.py`) of the :term:`app project`. The :term:`app class` must inherit from the ``TethysAppBase`` class to be loaded properly into CKAN. The following article contains the API documentation for the ``TethysAppBase`` class.

.. autoclass:: tethys_apps.base.app_base.TethysAppBase
    :members: url_maps, permissions, custom_settings, get_custom_setting, persistent_store_settings, get_persistent_store_connection, get_persistent_store_database, dataset_services_settings, get_dataset_service, spatial_dataset_services_settings, get_spatial_dataset_service, web_processing_services_settings, get_web_processing_service, handoff_handlers, get_handoff_manager, job_templates, get_job_manager, get_app_workspace, get_user_workspace,  list_persistent_store_connections, list_persistent_store_databases, persistent_store_exists, create_persistent_store, drop_persistent_store
