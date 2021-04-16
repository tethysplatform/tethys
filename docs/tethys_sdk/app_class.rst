.. _app_base_class_api:

******************
App Base Class API
******************

**Last Updated:** May 2017

Tethys apps are configured via the :term:`app class`, which is contained in the :term:`app configuration file` (:file:`app.py`) of the :term:`app project`. The :term:`app class` must inherit from the ``TethysAppBase`` to be recognized by Tethys. The following article contains the API documentation for the ``TethysAppBase`` class.

Properties
----------

.. autoclass:: tethys_apps.base.TethysAppBase

Override Methods
----------------

.. automethod:: tethys_apps.base.TethysAppBase.url_maps

.. automethod:: tethys_apps.base.TethysAppBase.permissions

.. automethod:: tethys_apps.base.TethysAppBase.custom_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.persistent_store_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.dataset_service_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.spatial_dataset_service_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.web_processing_service_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.handoff_handlers

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_app_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_app_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_user_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_user_workspace

Class Methods
-------------

.. automethod:: tethys_apps.base.TethysAppBase.get_custom_setting
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.set_custom_setting
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_persistent_store_connection
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_persistent_store_database
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_dataset_service
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_spatial_dataset_service
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_web_processing_service
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.get_handoff_manager

.. automethod:: tethys_apps.base.TethysAppBase.get_job_manager

.. deprecated:: 3.0
.. automethod:: tethys_apps.base.TethysAppBase.get_app_workspace
   :noindex:

.. deprecated:: 3.0
.. automethod:: tethys_apps.base.TethysAppBase.get_user_workspace
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.list_persistent_store_connections

.. automethod:: tethys_apps.base.TethysAppBase.list_persistent_store_databases

.. automethod:: tethys_apps.base.TethysAppBase.persistent_store_exists

.. automethod:: tethys_apps.base.TethysAppBase.create_persistent_store

.. automethod:: tethys_apps.base.TethysAppBase.drop_persistent_store

