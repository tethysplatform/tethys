*********************
Setup THREDDS Service
*********************

**Last Updated:** December 2019

In this tutorial you will register a public THREDDS server as a Tethys Service so can be more easily used in the app. The following topics will be covered in this tutorial:

* Tethys Services
* Tethys Service App Settings

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b new-app-project-solution new-app-project-solution-|version|


1. Create a Spatial Dataset Service App Setting
===============================================

Add the following method to your :term:`app class` to define a new spatial dataset services setting for your app:

.. code-block:: python

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

    class ThreddsTutorial(TethysAppBase):
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


2. Create THREDDS Spatial Dataset Service
=========================================

For this tutorial you'll be using UCAR's THREDDS Data Server: `<http://thredds.ucar.edu/thredds>`_

1. Exit the app and navigate to the **Site Administration** page by selecting ``Site Admin`` from the drop down menu located to the right of your user name.

2. Scroll down to the **TETHYS SERVICES** section of the page.

3. Click on the ``Spatial Dataset Services`` link.

4. Click on the ``ADD SPATIAL DATASET SERVICE`` button to create a new Spatial Dataset Service.

5. Enter the following information for the new Spatial Dataset Service:

    * Name: Global_0p5deg
    * Engine: THREDDS
    * Endpoint: http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p5deg
    * Public Endpoint: http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p5deg
    * ApiKey: (LEAVE BLANK)
    * Username: (LEAVE BLANK)
    * Password: (LEAVE BLANK)

    .. important::

         For the purposes of this tutorial, the Public Endpoint is the same as the (internal) Endpoint. However, in a production deployment of Tethys Platform, **the Public Endpoint needs to be the publicly accessible address** of the THREDDS server.

6. Press the ``Save`` button to save the new Spatial Dataset Service.

.. todo:

    * Add screen capture of the filled out new sds form.

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

    This app is meant to be somewhat of a THREDDS datase browser. It should be able to support other THREDDS services provided the following services are enabled on the datasets you wish to view:

    * WMS
    * NCSS

    To use the app with other THREDDS services, repeat steps 2 to create additional Spatial Dataset Services for each additional THREDDS service. Then repeat step 3 to swap out the THREDDS service that the app is using.


4. Solution
===========

This concludes the New App Project portion of the THREDDS Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-thredds_tutorial/tree/thredds-service-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b thredds-service-solution thredds-service-solution-|version|