******************
App Base Class API
******************

**Last Updated:** November 20, 2014

Tethys apps are configured via the :term:`app class`, which is contained in the :term:`app configuration file` (:file:`app.py`) of the :term:`app project`. The :term:`app class` must inherit from the ``TethysAppBase`` class to be loaded properly into CKAN. The following article contains the API documentation for the ``TethysAppBase`` class.

.. autoclass:: tethys_apps.base.app_base.TethysAppBase
    :members: url_map, persistent_stores, dataset_services