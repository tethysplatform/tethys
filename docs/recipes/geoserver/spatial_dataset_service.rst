.. _spatial_dataset_service_recipe :


********************************
Set Up a Spatial Dataset Service
********************************

**Last Updated:** October 2025

In this recipe you will learn how to setup a Spatial Dataset Service with GeoServer.

Start geoserver
###############

If you want to use Docker containers, you can create and start a GeoServer container like so:

.. code-block:: bash

    tethys docker init -c geoserver

.. code-block:: bash

    tethys docker start -c geoserver

Create Spatial Dataset Service Setting
######################################

In order to use GeoServer resources in your app, you'll need to create a Spatial Dataset Service Setting. You can do by adding the following method to your ``App`` class in your ``app.py`` file:

.. code-block:: python

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

    class App(TethysAppBase):
        """
        Tethys app class for Geoserver App.
        """
        ...

        def spatial_dataset_service_settings(self):
            """
            Example spatial_dataset_service_settings method.
            """
            sds_settings = (
                SpatialDatasetServiceSetting(
                    name='main_geoserver',
                    description='spatial dataset service for app to use',
                    engine=SpatialDatasetServiceSetting.GEOSERVER,
                    required=True,
                ),
            )

            return sds_settings

Create GeoServer Spatial Dataset Service
#######################################

You can register and connect to your GeoServer in the Tethys Portal admin page by creating a Spatial Dataset Service:

1. Select the "Site Admin" link from the drop down menu by your username.

2. Scroll to the "Tethys Services" section and select the "Spatial Dataset Services" link.

3. Create a new Spatial Dataset Service named "primary_geoserver" of type GeoServer.

4. Enter the **endpoint** and **public endpoint** as the same (e.g.: http://localhost:8181/geoserver/rest/ if using Docker or http://localhost:8080/geoserver/rest/ if using a default installation of GeoServer).

5. Fill out the **username** and **password** (default username and password is "admin" and "geoserver", respectively).

6. No API Key is required.

7. Press "Save".

.. important::

    In a production deployment of Tethys, the public endpoint should point to the publicly accessible host and port of the geoserver (e.g.: http://www.example.com:8181/geoserver/rest/)

Assign Spatial Dataset Service to App Setting
#############################################

Next, you'll need to assign your service to your app setting.

1. Select the "Site Admin" link from the drop down menu by your username in the top right corner.--name
2. Scroll to the "Tethys Apps" section and select the "Installed Apps" link. 
3. Select your app.
4. Scroll down to the "Spatial Dataset Service Settings" section and assign the "primary_geoserver" to the Spatial Dataset Service property of the "main_geoserver" setting for your app.--name
5. Press "Save".

.. tip::

	If you don't see the "main_geoserver" setting in the "Spatial Dataset Service Settings" section try restarting the Tethys development server. If it still doesn't show up, then stop the Tethys development server, uninstall the app, reinstall it, and start the Tethys server again:

    .. code-block:: bash

        tethys uninstall geoserver_app
        cd tethysapp-geoserver_app
        tethys install -d
        tethys manage start

You've now started up your GeoServer container and connected it with your Tethys App. 

From here, you can explore your GeoServer web admin interface by going to `<http://localhost:8181/geoserver/web/>`_



