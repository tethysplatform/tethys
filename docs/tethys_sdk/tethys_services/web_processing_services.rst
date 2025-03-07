***************************
Web Processing Services API
***************************

**Last Updated:** May 2017

Web Processing Services (WPS) are web services that can be used perform geoprocessing and other processing activities for apps. The Open Geospatial Consortium (OGC) has created the `WPS interface standard <https://www.ogc.org/publications/standard/wps/>`_ that provides rules for how inputs and outputs for processing services should be formatted. Using the Web Processing Services API, you will be able to provide processing capabilities for your apps using any service that conforms to the OGC WPS standard. For convenience, the 52 North WPS is provided as part of the Tethys Platform software suite.

Web Processing Service Settings
===============================

Using web processing services in your app is accomplished by adding the ``web_processing_service_settings()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method should return a list or tuple of ``WebProcessingServiceSetting`` objects. For example:

::

      from tethys_sdk.app_settings import WebProcessingServiceSetting

      class App(TethysAppBase):
          """
          Tethys App Class for My First App.
          """
          ...
          def web_processing_service_settings(self):
              """
              Example wps_services method.
              """
              wps_services = (
                  WebProcessingServiceSetting(
                      name='primary_52n',
                      description='WPS service for app to use',
                      required=True,
                  ),
              )

              return wps_services

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Assign Web Processing Service
-----------------------------

The ``WebProcessingServiceSetting`` can be thought of as a socket for a connection to a WPS. Before we can do anything with the ``WebProcessingServiceSetting`` we need to "plug in" or assign a ``WebProcessingService`` to the setting. The ``WebProcessingService`` contains the connection information and can be used by multiple apps. Assigning a ``WebProcessingService`` is done through the Admin Interface of Tethys Portal as follows:

1. Create ``WebProcessingService`` if one does not already exist

    a. Access the Admin interface of Tethys Portal by clicking on the drop down menu next to your user name and selecting the "Site Admin" option.

    b. Scroll to the **Tethys Service** section of the Admin Interface and select the link titled **Web Processing Services**.

    c. Click on the **Add Web Processing Services** button.

    d. Fill in the connection information to the WPS server.

    e. Press the **Save** button to save the new ``WebProcessingService``.

    .. tip::

        You do not need to create a new ``WebProcessingService`` for each ``WebProcessingServiceSetting`` or each app. Apps and ``WebProcessingServiceSettings`` can share ``WebProcessingServices``.

2. Navigate to App Settings Page

    a. Return to the Home page of the Admin Interface using the **Home** link in the breadcrumbs or as you did in step 1a.

    b. Scroll to the **Tethys Apps** section of the Admin Interface and select the **Installed Apps** linke.

    c. Select the link for your app from the list of installed apps.


3. Assign ``WebProcessingService`` to the appropriate ``WebProcessingServiceSetting``

    a. Scroll to the **Web Processing Service Settings** section and locate the ``WebProcessingServiceSetting``.

    .. tip::

        If you don't see the ``WebProcessingServiceSetting`` in the list, uninstall the app and reinstall it again.

    b. Assign the appropriate ``WebProcessingService`` to your ``WebProcessingServiceSetting`` using the drop down menu in the **Web Processing Service** column.

    c. Press the **Save** button at the bottom of the page to save your changes.

.. note::

    During development you will assign the ``WebProcessingService`` setting yourself. However, when the app is installed in production, this steps is performed by the portal administrator upon installing your app, which may or may not be yourself.

Working with WPS Services in Apps
=================================

.. important::

    This feature requires the ``owslib`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``owslib`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge owslib

        # pip
        pip install owslib

The Web Processing Service API is powered by `OWSLib <https://owslib.readthedocs.io/en/latest/usage.html#wps>`_, a Python client that can be used to interact with OGC web services. For detailed explanations the WPS client provided by OWSLib, refer to the `OWSLib WPS Documentation <https://owslib.readthedocs.io/en/latest/usage.html#wps>`_. This article only provides a basic introduction to working with the OWSLib WPS client.

Get a WPS Engine
----------------

Anytime you wish to use a WPS service in an app, you will need to obtain an ``owslib.wps.WebProcessingService`` engine object. This can be done by calling the ``get_web_processing_service()`` method of the app class:

::

    from .app import App

    wps_engine = App.get_web_processing_service('primary_52n', as_engine=True)

Alternatively, you can create an ``owslib.wps.WebProcessingService`` engine object directly without using the convenience function. This can be useful if you want to vary the credentials for WPS service access frequently (e.g.: to provide user specific credentials).

::

  from owslib.wps import WebProcessingService

  wps_engine = WebProcessingService('http://www.example.com/wps/WebProcessingService', verbose=False, skip_caps=True)
  wps_engine.getcapabilities()

Using the WPS Engine
--------------------

After you have retrieved a valid ``owslib.wps.WebProcessingService`` engine object, you can use it execute process requests. The following example illustrates how to execute the GRASS buffer process on a 52 North WPS:

::

  from owslib.wps import GMLMultiPolygonFeatureCollection

  polygon = [(-102.8184, 39.5273), (-102.8184, 37.418), (-101.2363, 37.418), (-101.2363, 39.5273), (-102.8184, 39.5273)]
  feature_collection = GMLMultiPolygonFeatureCollection( [polygon] )
  process_id = 'v.buffer'
  inputs = [ ('DISTANCE', 5.0),
             ('INPUT', feature_collection)
            ]
  output = 'OUTPUT'
  execution = wps_engine.execute(process_id, inputs, output)
  monitorExecution(execution)


It is also possible to perform requests using data that are hosted on WFS servers, such as the GeoServer that is provided as part of the Tethys Platform software suite. See the `OWSLib WPS Documentation <https://owslib.readthedocs.io/en/latest/usage.html#wps>`_ for more details on how this is to be done.
