******************
Start and Register
******************

**Last Updated:** May 2017


Scaffold New App
================

Create a new app, but don't install it yet:

::

    $ t
    (tethys) $ tethys scaffold geoserver_app

Create Spatial Dataset Service Setting
======================================

Open the ``app.py`` and add the following method to the ``GeoserverApp`` class:

::

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

    class GeoserverApp(TethysAppBase):
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




Install GeoServer and Start Tethys Development Server
=====================================================

::

    (tethys) $ cd tethysapp-geoserver_app
    (tethys) $ tethys install -d
    (tethys) $ tethys manage start


Start GeoServer
===============

If you are using the Docker containers, start up your :doc:`../../software_suite/geoserver` container:

::

	(tethys) $ tethys docker start -c geoserver

Otherwise ensure that you have GeoServer installed and running. Refer to the `GeoServer Installation Guide <http://docs.geoserver.org/stable/en/user/installation/>`_ for system specific instructions.



Create GeoServer Spatial Dataset Service
========================================

Register the GeoServer with Tethys Portal admin page by creating a Spatial Dataset Service:

1. Select the "Site Admin" link from the drop down menu by your username.
2. Scroll to the "Tethys Services" section and select the "Spatial Dataset Services" link.
3. Create a new Spatial Dataset Service named "primary_geoserver" of type GeoServer.
4. Enter the endpoint and public endpoint as the same (e.g.: http://localhost:8181/geoserver/rest/ if using Docker or http://localhost:8080/geoserver/rest/ if using a default installation of GeoServer).
5. Fill out the username and password (default username and password is "admin" and "geoserver", respectively.
6. No API Key is required.
7. Press "Save".

Assign Spatial Dataset Service to App Setting
=============================================

Assign the "primary_geoserver" Spatial Dataset Service to the "main_geoserver" setting for the app.

1. Select the "Site Admin" link from the drop down menu by your username.
2. Scroll to the "Tethys Apps" section and select the "Installed Apps" link.
3. Select the "Geoserver App" link.
4. Scroll down to the "Spatial Dataset Service Settings" section and assign the "primary_geoserver" to the Spatial Dataset Service property of the "main_geoserver" setting for the app.
5. Press "Save".

.. tip::

	If you don't see the "main_geoserver" setting in the "Spatial Dataset Service Settings" section try restarting the Tethys development server. If it still doesn't show up, then stop the Tethys development server, uninstall the app, reinstall it, and start the Tethys server again:

    ::

        (tethys) $ tethys uninstall geoserver_app
        (tethys) $ cd tethysapp-geoserver_app
        (tethys) $ tethys install -d
        (tethys) $ tethys manage start


GeoServer Web Admin Interface
=============================

Explore the GeoServer web admin interface by visiting link: `<http://\<host\>:\<port\>/geoserver/web/>`_.


Download Test Files
===================

Download the sample shapefiles that you will use to test your app:

:download:`geoserver_app_data.zip`

