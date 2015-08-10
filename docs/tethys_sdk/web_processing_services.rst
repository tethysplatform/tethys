***************************
Web Processing Services API
***************************

**Last Updated:** May 13, 2015

Web Processing Services (WPS) are web services that can be used perform geoprocessing and other processing activities for apps. The Open Geospatial Consortium (OGC) has created the `WPS interface standard <http://www.opengeospatial.org/standards/wps>`_ that provides rules for how inputs and outputs for processing services should be handled. Using the Web Processing Services API, you will be able to provide processing capabilities for your apps using any service that conforms to the OGC WPS standard. For convenience, the 52 North WPS is provided as part of the Tethys Platform software suite. Refer to the :doc:`../installation` documentation to learn how to install Tethys Platform with 52 North WPS enabled.

Configuring WPS Services
========================

Before you can start using WPS services in your apps, you will need link your Tethys Platform to a valid WPS. This can be done either at a sitewide level or at an app specific level. When a WPS is configured at the sitewide level, all apps that are installed on that Tethys Platform instance will be able to access the WPS. When installed at an app specific level, the WPS will only be accessible to the app that it is linked to. The following sections will describe how to configure a WPS to be used at both of these levels.

Register New WPS Service
------------------------

Sitewide configuration is performed using the System Admin Settings.

1. Login to your Tethys Platform instance as an administrator.
2. Select "Site Admin" from the user drop down menu.

  .. figure:: ../images/site_admin/select_site_admin.png
      :width: 600px
      :align: center


3. Select "Web Processing Services" from the "Tethys Services" section.


  .. figure:: ../images/site_admin/home.png
      :width: 600px
      :align: center


4. Select an existing Web Processing Service configuration from the list to edit it OR click on the "Add Web Processing Service" button to create a new one.

  .. figure:: ../images/site_admin/wps_services.png
      :width: 600px
      :align: center

5. Give the Web Processing Service configuration a name and specify the endpoint. The name must be unique, because it is used to connect to the WPS. The endpoint is a URL pointing to the WPS. For example, the endpoint for the 52 North WPS demo server would be:

  ::

    http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService

If authentication is required, specify the username and password.

  .. figure:: ../images/site_admin/wps_service_edit.png
      :width: 600px
      :align: center

6. Press "Save" to save the WPS configuration.


.. note::

  Prior to version Tethys Platform 1.1.0, it was possible to register WPS services using a mechanism in the :term:`app configuration file`. This mechanism has been deprecated due to security concerns.

Working with WPS Services in Apps
=================================

The Web Processing Service API is powered by `OWSLib <http://geopython.github.io/OWSLib/#wps>`_, a Python client that can be used to interact with OGC web services. For detailed explanations the WPS client provided by OWSLib, refer to the `OWSLib WPS Documentation <http://geopython.github.io/OWSLib/#wps>`_. This article only provides a basic introduction to working with the OWSLib WPS client.

Get a WPS Engine
----------------

Anytime you wish to use a WPS service in an app, you will need to obtain an ``owslib.wps.WebProcessingService`` engine object. The Web Processing Service API provides a convenience function for retrieving ``owslib.wps.WebProcessingService`` engine objects called ``get_wps_service_engine``. Basic usage involves calling the function with the name of the WPS service that you wish to use. For example:

::

  from tethys_sdk.services import get_wps_service_engine

  wps_engine = get_wps_service_engine(name='example')

Alternatively, you may retrieve a list of all the dataset engine objects that are registered using the ``list_wps_service_engines`` function:

::

  from tethys_sdk.services import list_wps_service_engines

  wps_engines = list_wps_service_engines()

You can also create an ``owslib.wps.WebProcessingService`` engine object directly without using the convenience function. This can be useful if you want to vary the credentials for WPS service access frequently (e.g.: using user specific credentials).

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


It is also possible to perform requests using data that are hosted on WFS servers, such as the GeoServer that is provided as part of the Tethys Platform software suite. See the `OWSLib WPS Documentation <http://geopython.github.io/OWSLib/#wps>`_ for more details on how this is to be done.

Web Processing Service Developer Tool
=====================================

Tethys Platform provides a developer tool that can be used to browse the sitewide WPS services and the processes that they provide. This tool is useful for formulating new process requests. To use the tool:

1. Browse to the Developer Tools page of your Tethys Platform by selecting the "Developer" link from the menu at the top of the page.

2. Select the tool titled "Web Processing Services".

  .. figure:: ../images/wps_tool/developer_tools_wps.png
      :width: 600px
      :align: center

3. Select a WPS service from the list of services that are linked with your Tethys Instance. If no WPS services are linked to your Tethys instance, follow the steps in Sitewide Configuration, above, to setup a WPS service.

  .. figure:: ../images/wps_tool/wps_tool_services.png
      :width: 600px
      :align: center

4. Select the process you wish to view.

  .. figure:: ../images/wps_tool/wps_tool_processes.png
      :width: 600px
      :align: center

A description of the process and the inputs and outputs will be displayed.

  .. figure:: ../images/wps_tool/wps_tool_buffer.png
      :width: 600px
      :align: center