****************************
Spatial Dataset Services API
****************************

**Last Updated:** July 17, 2015

Spatial dataset services are web services that can be used to store and publish file-based :term:`spatial datasets` (e.g.: Shapefile and GeoTiff). The spatial datasets published using spatial dataset services are made available in a variety of formats, many of which or more web friendly than the native format (e.g.: PNG, JPEG, GeoJSON, and KML). Tethys app developers can use this Spatial Dataset Services API to store and access :term:` spatial datasets` for use in their apps and publish any resulting :term:`datasets` their apps may produce.

Powered by GeoServer
====================

`GeoServer <http://geoserver.org/>`_ powers the Spatial Dataset Service capabilities of Tethys Platform. It is capable of storing and serving vector and raster datasets in several popular formats including Shapefiles, GeoTiff, ArcGrid and others. GeoServer serves the data in a variety of formats via the `Open Geospatial Consortium (OGC) <http://www.opengeospatial.org/>`_ standards including `Web Feature Service (WFS) <http://www.opengeospatial.org/standards/wfs>`_, `Web Map Service (WMS) <http://www.opengeospatial.org/standards/wms>`_, and `Web Coverage Service (WCS) <http://www.opengeospatial.org/standards/wcs>`_.

Key Concepts
============

There are quite a few concepts that you should understand before working with GeoServer and spatial dataset services. Definitions of each are provided here for quick reference.

**Resources** are the spatial datasets. These can vary in format ranging from a single file or multiple files to database tables depending on the type resource.

**Feature Type**: is a type of *resource* containing vector data or data consisting of discreet features such as points, lines, or polygons and any tables of attributes that describe the features.

**Coverage**: is a type of *resource* containing raster data or numeric gridded data.

**Layers**: are *resources* that have been published. Layers associate styles and other settings with the *resource* that are needed to generate maps of the *resource* via OGC services.

**Layer Groups**: are preset groups of *layers* that can be served as WMS services as though they were one *layer*.

**Stores**: represent repositories of spatial datasets such as database tables or directories of shapefiles. A *store* containing only *feature types* is called a **Data Store** and a *store* containing only *coverages* is called a **Coverage Store**.

**Workspaces**: are arbitrary groupings of data to help with organization of the data. It would be a good idea to store all of the spatial datasets for your app in a workspace resembling the name of your app to avoid conflicts with other apps.

**Styles**: are a set of rules that dictate how a *layer* will be rendered when accessed via WMS. A *layer* may be associated with many styles and a style may be associated with many *layers*. Styles on GeoServer are written in `Styled Layer Descriptor (SLD) <http://www.opengeospatial.org/standards/sld>`_ format.

**Styled Layer Descriptor (SLD)**:  An XML-based markup language that can be used to specify how spatial datasets should be rendered. See GeoServer's `SLD Cookbook <http://docs.geoserver.org/stable/en/user/styling/sld-cookbook/index.html#sld-cookbook>`_ for a good primer on SLD.

**Web Feature Service (WFS)**: An OGC standard for exchanging vector data (i.e.: feature types) over the internet. WFS can be used to not only query for the features (points, lines, and polygons) but also the attributes associated with the features.

**Web Coverage Service (WCS)**: An OGC standard for exchanging raster data (i.e.: coverages) over the internet. WCS is roughly the equivalent of WFS but for *coverages*, access to the raw coverage information, not just the image.

**Web Mapping Service (WMS)**: An OGC standard for generating and exchanging maps of spatial data over the internet. WMS can be used to compose maps of several different spatial dataset sources and formats.

Spatial Dataset Engine References
=================================

All ``SpatialDatasetEngine`` objects implement a minimum set of base methods. However, some ``SpatialDatasetEngine`` objects may include additional methods that are unique to that ``SpatialDatasetEngine`` implementation and the arguments that each method accepts may vary slightly. Refer to the following references for the methods that are offered by each ``SpatailDatasetEngine``.

.. toctree::
    :maxdepth: 1

    spatial_dataset_service/base_reference
    spatial_dataset_service/geoserver_reference

Register New Spatial Dataset Services
=====================================

Registering new spatial dataset services is performed using the System Admin Settings.

1. Login to your Tethys Platform instance as an administrator.
2. Select "Site Admin" from the user drop down menu.

  .. figure:: ../../images/site_admin/select_site_admin.png
      :width: 600px
      :align: center


3. Select "Spatial Dataset Services" from the "Tethys Services" section.

  .. figure:: ../../images/site_admin/home.png
      :width: 600px
      :align: center


4. Select an existing Spatial Dataset Service configuration from the list to edit it OR click on the "Add Spatial Dataset Service" button to create a new one.

  .. figure:: ../../images/site_admin/spatial_dataset_services.png
      :width: 600px
      :align: center

5. Give the Spatial Dataset Service configuration a name, select an appropriate engine, specify the endpoint, and provide a username and password. The name of the configuration must be unique, because it is used to retrieve the Spatial Dataset Service connection object. The endpoint is a URL pointing to the GeoServer REST endpoint. This endpoint can be for **any** GeoServer. If you want to use the built-in GeoServer installation, you can obtain the endpoint by running ``tethys docker ip`` in a terminal:

  ::

    $ tethys docker ip
    ...

    GeoServer:
      Host: localhost
      Port: 8181
      Endpoint: http://localhost:8181/geoserver/rest

    ...


  When you are done, your Spatial Dataset Service configuration should look similar to this:

  .. figure:: ../../images/site_admin/spatial_dataset_service_edit.png
      :width: 600px
      :align: center

6. Press "Save" to save the Dataset Service configuration.


.. note::

  Prior to version Tethys Platform 1.1.0, it was possible to register spatial dataset services using a mechanism in the :term:`app configuration file`. This mechanism has been deprecated due to security concerns.

Working with Spatial Dataset Services
=====================================

After spatial dataset services have been properly configured, you can use the services to store, publish, and retrieve data for your apps. This process typically involves the following steps:


1. Get a Spatial Dataset Engine
-------------------------------

The Spatial Dataset Services API provides a convenience function called ``get_spatial_dataset_engine``. To retrieve and engine for a sitewide configuration, call ``get_spatial_dataset_engine`` with the name of the configuration::

  from tethys_sdk.services import get_spatial_dataset_engine

  dataset_engine = get_dataset_engine(name='example')

It will return the first service with a matching name or raise an exception if the service cannot be found with the given name. Alternatively, you may retrieve a list of all the spatial dataset engine objects that are registered using the ``list_spatial_dataset_engines`` function:

::

  from tethys_sdk.services import list_spatial_dataset_engines

  dataset_engines = list_spatial_dataset_engines()

You can also create a ``SpatialDatasetEngine`` object directly without using the convenience function. This can be useful if you want to vary the credentials for dataset access frequently (e.g.: using user specific credentials). Simply import it and instantiate it with valid credentials::

  from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine

  spatial_dataset_engine = GeoServerSpatialDatasetEngine(endpoint='http://www.example.com/geoserver/rest', username='admin', password='geoserver')

.. caution::

  Take care not to store API keys, usernames, or passwords in the source files of your app--especially if the source code is made public. This could compromise the security of the spatial dataset service.

2. Use the Spatial Dataset Engine
---------------------------------

After you have a ``SpatialDatasetEngine`` object, simply call the desired method on it. All ``SpatialDatasetEngine`` methods return a dictionary with an item named 'success' that contains a boolean. If the operation was successful, 'success' will be true, otherwise it will be false. If 'success' is true, the dictionary will have an item named 'result' that will contain the results. If it is false, the dictionary will have an item named 'error' that will contain information about the error that occurred. This can be very useful for debugging and error catching purposes.

Consider the following example for uploading a shapefile to spatial dataset services:


::

  from tethys_sdk.services import get_spatial_dataset_engine

  # First get an engine
  engine = get_spatial_dataset_engine(name='example')

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


A new shapefile Data Store will be created called 'foo' in workspace 'my_app' and a resource will be created for the shapefile called 'foo'. A layer will also automatically be configured for the new shapefile resource.

.. tip::

    When you are learning how to use the spatial dataset engine methods, run the commands with the debug parameter set to true. This will automatically pretty print the result dictionary to the console so that you can inspect its contents:

    ::

      # Example method with debug option
      engine.list_layers(debug=True)


3. Get OGC Web Service URL
--------------------------

Publishing the spatial dataset with a spatial dataset service would be pointless without using the service to render the data on a map. This can be done by querying the data using the OGC web services WFS, WCS, or WMS. The dictionary that is returned when retrieving layers, layer groups, or resources will include a key for appropriate OGC services for the object returned. Feature type resources will provide a "wfs" key, coverage resources will provide a "wcs" key, and layers and layergroups will provide a "wms" key. The value will be another dictionary of OGC queries for different endpoints. For example:

::

    # Get a feature type layer
    response = engine.get_layer(layer_id='sf:roads', debug=True)

    # Response dictionary includes "wms" key with links to maps in various formats
    {'result': {'advertised': True,
                'attribution': None,
                'catalog': 'http://localhost:8181/geoserver/',
                'default_style': 'simple_roads',
                'enabled': None,
                'href': 'http://localhost:8181/geoserver/rest/layers/sf%3Aroads.xml',
                'name': 'sf:roads',
                'resource': 'sf:roads',
                'resource_type': 'layer',
                'styles': ['sf:line'],
                'wms': {'georss': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=rss',
                        'geotiff8': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/geotiff8',
                        'geptiff': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/geotiff',
                        'gif': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/gif',
                        'jpeg': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/jpeg',
                        'kml': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=kml',
                        'kmz': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=kmz',
                        'openlayers': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=application/openlayers',
                        'pdf': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=application/pdf',
                        'png': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/png',
                        'png8': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/png8',
                        'svg': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/svg',
                        'tiff': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/tiff',
                        'tiff8': 'http://localhost:8181/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sf:roads&styles=simple_roads&transparent=true&tiled=no&srs=EPSG:26713&bbox=589434.8564686741,4914006.337837095,609527.2102150217,4928063.398014731&width=731&height=512&format=image/tiff8'}},
     'success': True}

These links could be passed on to a web mapping client like OpenLayers or Google Maps to render the map interactively on a web page. Note that the OGC mapping services are very powerful and the links provided represent only a simple query. You can construct custom OGC URLs queries without much difficulty. For excellent primers on WFS, WCS, and WMS with GeoServer, visit these links:

* `GeoServer Web Feature Service Overview <http://docs.geoserver.org/stable/en/user/services/wfs/index.html>`_
* `GeoServer Web Coverage Service Overview <http://docs.geoserver.org/stable/en/user/services/wcs/index.html>`_
* `GeoServer Web Map Service Overview <http://docs.geoserver.org/stable/en/user/services/wms/index.html>`_




