.. _app_base_class_api:

******************
App Base Class API
******************

**Last Updated:** January 2022

Tethys apps are configured via the :term:`app class`, which is contained in the :term:`app configuration file` (:file:`app.py`) of the :term:`app project`. The :term:`app class` must inherit from the ``TethysAppBase`` to be recognized by Tethys. This document contains API documentation for the ``TethysAppBase`` class.

Apps are configured in two ways using the :term:`app class` to configure your app:

* Properties
* Method Overrides

In addition, the :term:`app class` provides several class methods that can be used to get and set values of custom settings and connections to :ref:`Tethys Services <tethys_services_api>` that are assigned to the app (e.g THREDDS/GeoServer, database connections, and schedulers).

Properties
----------

Use these properties to set things like the display name, icon/logo, and theme color.

.. autoclass:: tethys_apps.base.TethysAppBase

Override Methods
----------------

Override these methods (add them to your app class) to define objects that are used by the app such as :ref:`Permissions <permissions_api>`, :ref:`CustomSettings <app_settings_custom_settings>`, and settings for :ref:`Tethys Services <tethys_services_api>` that are required by your app.

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

.. automethod:: tethys_apps.base.TethysAppBase.scheduler_settings
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.handoff_handlers

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_app_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_app_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_user_workspace

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_user_workspace

.. automethod:: tethys_apps.base.TethysAppBase.register_url_maps

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

.. automethod:: tethys_apps.base.TethysAppBase.get_scheduler
   :noindex:

.. automethod:: tethys_apps.base.TethysAppBase.list_persistent_store_connections

.. automethod:: tethys_apps.base.TethysAppBase.list_persistent_store_databases

.. automethod:: tethys_apps.base.TethysAppBase.persistent_store_exists

.. automethod:: tethys_apps.base.TethysAppBase.create_persistent_store

.. automethod:: tethys_apps.base.TethysAppBase.drop_persistent_store
