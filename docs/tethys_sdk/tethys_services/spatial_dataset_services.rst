.. _spatial_dataset_services_api:


****************************
Spatial Dataset Services API
****************************

**Last Updated:** December 2019

.. important::

    This feature requires the ``tethys_dataset_services`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``tethys_dataset_services`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge tethys_dataset_services

        # pip
        pip install tethys_dataset_services

Spatial dataset services are web services that can be used to store and publish file-based :term:`spatial datasets` (e.g.: Shapefile, GeoTiff, NetCDF). The spatial datasets published using spatial dataset services are made available in a variety of formats, many of which or more web friendly than the native format (e.g.: PNG, JPEG, GeoJSON, OGC Services).

One example of a spatial dataset service is `GeoServer <https://geoserver.org/>`_, which is capable of storing and serving vector and raster datasets in several popular formats including Shapefiles, GeoTiff, ArcGrid and others. GeoServer serves the data in a variety of formats via the `Open Geospatial Consortium (OGC) <https://www.ogc.org/>`_ standards including `Web Feature Service (WFS) <https://www.ogc.org/publications/standard/wfs/>`_, `Web Map Service (WMS) <https://www.ogc.org/publications/standard/wms/>`_, and `Web Coverage Service (WCS) <https://www.ogc.org/publications/standard/wcs/>`_.

Another supported spatial dataset service is the `THREDDS Data Server (TDS) <https://docs.unidata.ucar.edu/tds/current/userguide/index.html>`_, which is a web server that specializes in serving gridded datasets using common protocols including `OPeNDAP <https://www.opendap.org/>`_, OGC WMS, OGC WCS, and HTTP. Examples of data formats supported by THREDDS include NetCDF, HDF5, GRIB, and NEXRAD.

Tethys app developers can use this Spatial Dataset Services API to store and access :term:` spatial datasets` for use in their apps and publish any resulting :term:`datasets` their apps may produce.

Spatial Dataset Engine References
=================================

The engines for some spatial dataset service engines in Tethys implement the ``SpatialDatasetEngine`` interface, which means they implement a common set of base methods for interacting with the service. The ``GeoServerSpatialDatasetEngine`` is an example of this pattern. Other engines are powered by excellent 3rd-party libraries, such as `Siphon <https://unidata.github.io/siphon/latest/examples/Basic_Usage.html>`_ for THREDDS spatial dataset services. Refer to the following references for the APIs that are available for each spatial dataset service supported by Tethys.

.. toctree::
    :maxdepth: 1

    spatial_dataset_service/base_reference
    spatial_dataset_service/geoserver_reference
    spatial_dataset_service/thredds_reference


Spatial Dataset Service Settings
================================

Using dataset services in your app is accomplished by adding the ``spatial_dataset_service_settings()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method should return a list or tuple of ``SpatialDatasetServiceSetting`` objects. For example:

::

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

    class App(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...
        def spatial_dataset_service_settings(self):
            """
            Example spatial_dataset_service_settings method.
            """
            sds_settings = (
                SpatialDatasetServiceSetting(
                    name='primary_geoserver',
                    description='GeoServer service for app to use.',
                    engine=SpatialDatasetServiceSetting.GEOSERVER,
                    required=True,
                ),
                SpatialDatasetServiceSetting(
                    name='primary_thredds',
                    description='THREDDS service for the app to use.',
                    engine=SpatialDatasetServiceSetting.THREDDS,
                    required=True
                ),
            )

            return sds_settings

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

.. _assign_spatial_dataset_service:

Assign Spatial Dataset Service
==============================

The ``SpatialDatasetServiceSetting`` can be thought of as a socket for a connection to a ``SpatialDatasetService``. Before we can do anything with the ``SpatialDatasetServiceSetting`` we need to "plug in" or assign a ``SpatialDatasetService`` to the setting. The ``SpatialDatasetService`` contains the connection information and can be used by multiple apps. Assigning a ``SpatialDatasetService`` is done through the Admin Interface of Tethys Portal as follows:

1. Create ``SpatialDatasetService`` if one does not already exist

    a. Access the Admin interface of Tethys Portal by clicking on the drop down menu next to your user name and selecting the "Site Admin" option.

    b. Scroll down to the **Tethys Services** section of the Admin Interface and select the link titled **Spatial Dataset Services**.

    c. Click on the **Add Spatial Dataset Service** button.

    d. Fill in the connection information to the database server.

    e. Press the **Save** button to save the new ``SpatialDatasetService``.

    .. tip::

        You do not need to create a new ``SpatialDatasetService`` for each ``SpatialDatasetServiceSetting`` or each app. Apps and ``SpatialDatasetServiceSettings`` can share ``DatasetServices``.

2. Navigate to App Settings Page

    a. Return to the Home page of the Admin Interface using the **Home** link in the breadcrumbs or as you did in step 1a.

    b. Scroll to the **Tethys Apps** section of the Admin Interface and select the **Installed Apps** link.

    c. Select the link for your app from the list of installed apps.

3. Assign ``SpatialDatasetService`` to the appropriate ``SpatialDatasetServiceSetting``

    a. Scroll to the **Spatial Dataset Services Settings** section and locate the ``SpatialDatasetServiceSetting``.

    .. note::

        If you don't see the ``SpatialDatasetServiceSetting`` in the list, uninstall the app and reinstall it again.

    b. Assign the appropriate ``SpatialDatasetService`` to your ``SpatialDatasetServiceSetting`` using the drop down menu in the **Spatial Dataset Service** column.

    c. Press the **Save** button at the bottom of the page to save your changes.

.. note::

    During development you will assign the ``SpatialDatasetService`` setting yourself. However, when the app is installed in production, this steps is performed by the portal administrator upon installing your app, which may or may not be yourself.

Working with Spatial Dataset Services
=====================================

After spatial dataset services have been properly configured, you can use the services to store, publish, and retrieve data for your apps. This process typically involves the following steps:


1. Get an Engine for the Spatial Dataset Service
------------------------------------------------

Call the ``get_spatial_dataset_service()`` method of the app class to get the engine for the Spatial Dataset Service:

.. code-block:: python

    from .app import App

    geoserver_engine = App.get_spatial_dataset_service('primary_geoserver', as_engine=True)

You can also create a ``SpatialDatasetEngine`` object directly. This can be useful if you want to vary the credentials for dataset access frequently (e.g.: using user specific credentials):

.. code-block:: python

  from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine

  spatial_dataset_engine = GeoServerSpatialDatasetEngine(endpoint='http://www.example.com/geoserver/rest', username='admin', password='geoserver')

.. caution::

  Take care not to store API keys, usernames, or passwords in the source files of your app--especially if the source code is made public. This could compromise the security of your app and the spatial dataset service.

2. Use the Spatial Dataset Engine
---------------------------------

After you have an engine object, simply call the desired methods on it. Consider the following example for uploading a shapefile to a GeoServer spatial dataset service:

::

    from .app import App

    # First get an engine
    engine = App.get_spatial_dataset_service('primary_geoserver', as_engine=True)

    # Create a workspace named after our app
    engine.create_workspace(workspace_id='my_app', uri='http://www.example.com/apps/my-app')

    # Path to shapefile base for foo.shp, side cars files (e.g.: .shx, .dbf) will be
    # gathered in addition to the .shp file.
    shapefile_base = '/path/to/foo'

    # Notice the workspace in the store_id parameter
    result = dataset_engine.create_shapefile_resource(store_id='my_app:foo', shapefile_base=shapefile_base)

    # Check if it was successful
    if not result['success']:
        raise

.. note::

    The type of engine object returned and the methods available vary depending on the type of spatial dataset service.
