****************************************
GeoServer SpatialDatasetEngine Reference
****************************************

**Last Updated**: December 2019

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

API
===

The following reference provides a summary the class used to define the ``GeoServerSpatialDatasetEngine`` objects.

.. autoclass:: tethys_dataset_services.engines.GeoServerSpatialDatasetEngine
    :members:
