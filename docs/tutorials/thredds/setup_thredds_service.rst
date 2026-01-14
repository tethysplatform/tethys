*********************
Setup THREDDS Service
*********************

**Last Updated:** July 2024

In this tutorial you will register a THREDDS server as a Tethys Spatial Dataset **Service** so it can be more easily used by the app. You will also create a Spatial Dataset Service **Setting** in the app to allow it to consume this service. The following topics will be covered in this tutorial:

* Tethys Services
* Tethys Service App Settings

.. figure:: ./resources/setup_thredds_service_solution.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial
    cd tethysapp-thredds_tutorial
    git checkout -b new-app-project-solution new-app-project-solution-|version|


1. Create a Spatial Dataset Service App Setting
===============================================

Service settings are a special class of setting for Tethys Apps that allow you to specify an external service (e.g. THREDDS, GeoServer, PostGIS) as a requirement of your app. Portal administrators can then either setup a new service or assign an existing service of that type to the app for it to consume.

This app will need a THREDDS service, so add the following method to the :term:`app class` to define a new THREDDS Spatial Dataset Service Setting for the app:

.. code-block:: python

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

.. code-block:: python

    class App(TethysAppBase):
        ...

        THREDDS_SERVICE_NAME = 'thredds_service'

        def spatial_dataset_service_settings(self):
            """
            Example spatial_dataset_service_settings method.
            """
            sds_settings = (
                SpatialDatasetServiceSetting(
                    name=self.THREDDS_SERVICE_NAME,
                    description='THREDDS service for app to use',
                    engine=SpatialDatasetServiceSetting.THREDDS,
                    required=True,
                ),
            )

            return sds_settings

.. note::

    The name of the setting is used as a key for retrieving the service assigned to the setting. If you are not careful, the name of the setting could end up hard-coded all over the app, making it difficult to change in the future. In this example, the name of the setting is saved as a class property of the app class: ``THREDDS_SERVICE_NAME``. The class property can be used for look-up operations rather than the hard-coded string:

    .. code-block:: python

        engine = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_engine=True)

2. Create THREDDS Spatial Dataset Service
=========================================

For this tutorial you'll be using the publicly accesible UCAR THREDDS Data Server: `<https://thredds.ucar.edu/thredds/catalog/catalog.html>`_. Complete the following steps to register the service as a Tethys Spatial Dataset Service:

1. Exit the app and navigate to the **Site Administration** page by selecting ``Site Admin`` from the drop down menu located to the right of your user name.

2. Scroll down to the **TETHYS SERVICES** section of the page.

3. Click on the ``Spatial Dataset Services`` link.

4. Click on the ``ADD SPATIAL DATASET SERVICE`` button to create a new Spatial Dataset Service.

5. Enter the following information for the new Spatial Dataset Service:

    * Name: Global_0p5deg
    * Engine: THREDDS
    * Endpoint: https://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p5deg/
    * Public Endpoint: https://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p5deg/
    * ApiKey: (LEAVE BLANK)
    * Username: (LEAVE BLANK)
    * Password: (LEAVE BLANK)

    .. important::

         For the purposes of this tutorial, the Public Endpoint is the same as the (internal) Endpoint. However, in a production deployment of Tethys Platform, **the Public Endpoint needs to be the publicly accessible address** of the THREDDS server.

    .. tip::

        The UCAR THREDDS server is open access, so no **username** or **password** is required. To use a private THREDDS server, enter the **username** and **password**. Currently, only simple authentication is supported for THREDDS services in Tethys.

6. Press the ``Save`` button to save the new Spatial Dataset Service.

.. tip::

    The ``Endpoint`` and ``Public Endpoint`` do not necessarily need to be the root endpoint. They can be any THREDDS endpoint, at any depth, containing a catalog.xml.

3. Assign THREDDS Service to App Setting
========================================

1. Navigate back to the **Site Administration** page (see step 4.1).

2. Scroll down to the **TETHYS APPS** section of the page.

3. Click on the ``Installed Apps`` link.

4. Click on the ``THREDDS Tutorial`` link.

5. Scroll down to the **SPATIAL DATASET SERVICE SETTINGS** section.

6. Select the ``Global_0p5deg`` as the spatial dataset service for the ``thredds_service`` app setting.


.. note::

    This app is meant to be somewhat of a THREDDS dataset browser. It should be able to support other THREDDS services provided the following services are enabled on the datasets you wish to view: (1) WMS and (2) NCSS.

    To use the app with other THREDDS services, repeat steps 2 to create additional Spatial Dataset Services for each additional THREDDS service. Then repeat step 3 to swap out the THREDDS service that the app is using.

4. Solution
===========

This concludes the New App Project portion of the THREDDS Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-thredds_tutorial/tree/thredds-service-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial
    cd tethysapp-thredds_tutorial
    git checkout -b thredds-service-solution thredds-service-solution-|version|