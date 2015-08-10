*****************************
Spatial Persistent Stores API
*****************************

**Last Updated:** November 24, 2014

Persistent store databases can support spatial data types. The spatial capabilities are provided by the `PostGIS <http://postgis.net/>`_ extension for the `PostgreSQL <http://www.postgresql.org/>`_ database. PostGIS extends the column types of PostgreSQL databases by adding ``geometry``, ``geography``, and ``raster`` types. PostGIS also provides hundreds of database functions that can be used to perform spatial operations on data stored in spatial columns. For more information on PostGIS, see `<http://www.postgis.net>`_.

The following article details the the spatial capabilities of persistent stores in Tethys Platform. This article builds on the concepts and ideas introduced in the :doc:`./persistent_store` documentation. Please review it before continuing.

Register Spatial Persistent Store
---------------------------------

Registering spatially enabled persistent stores follows the same process as registering normal persistent stores. The only difference is that you will set the ``spatial`` attribute of the ``PersistentStore`` object to ``True``:

::

    from tethys_sdk.base import TethysAppBase, url_map_maker
    from tethys_sdk.stores import PersistentStore


    class MyFirstApp(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...

        def persistent_stores(self):
            """
            Add one or more persistent stores
            """
            stores = (PersistentStore(name='spatial_db',
                                      initializer='init_stores:init_spatial_db',
                                      spatial=True
                    ),
            )

            return stores

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Adding Spatial Columns to Model
-------------------------------

Working with the ``raster``, ``geometry``, and ``geography`` column types provided by PostGIS is not supported natively in SQLAlchemy. For this, Tethys Platform provides the `GeoAlchemy2 <https://geoalchemy-2.readthedocs.org/en/latest/index.html>`_, which extends SQLAlchemy to support spatial columns and database functions. A data model that uses a ``geometry`` column type to store the points for stream gages may look like this:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer
    from sqlalchemy.orm import sessionmaker

    from geoalchemy2 import Geometry

    from .utilities import get_persistent_store_engine

    # Spatial DB Engine, sessiomaker, and base
    spatial_engine = get_persistent_store_engine('spatial_db')
    SpatialSessionMaker = sessionmaker(bind=spatial_engine)
    SpatialBase = declarative_base()

    # SQLAlchemy ORM definition for the spatial_stream_gages table
    class SpatialStreamGage(SpatialBase):
        """
        Example of SQLAlchemy spatial DB model
        """
        __tablename__ = 'spatial_stream_gages'

        # Columns
        id = Column(Integer, primary_key=True)
        value = Column(Integer)
        geom = Column(Geometry('POINT'))

        def __init__(self, latitude, longitude, value):
            """
            Constructor for a gage
            """
            self.geom = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)
            self.value = value

This data model is very similar to the data model defined in the :doc:`./persistent_store` documentation. Rather than using ``Float`` columns to store the latitude and longitude coordinates, the spatial data model uses a GeoAlchemy2 ``Geometry`` column called "geom". Notice that the constructor (``__init__.py``) takes the ``latitude`` and ``longitude`` provided and sets the value of the ``geom`` column to a string with a special format called `Well Known Text <http://en.wikipedia.org/wiki/Well-known_text>`_. This is a common pattern when working with GeoAlchemy2 columns.

.. important::

    This article only briefly introduces the concepts of working with GeoAlchemy2. It is highly recommended that you complete the `GeoAlchemy ORM <https://geoalchemy-2.readthedocs.org/en/latest/orm_tutorial.html>`_ tutorial.


Initialization Function
-----------------------

Initializing spatial persistent stores is performed in exactly the same way as normal persistent stores. An initialization function for the example above, would look like this:

::

    from .model import spatial_engine, SpatialSessionMaker, SpatialBase, SpatialStreamGage

    def init_spatial_db(first_time):
        """
        An example persistent store initializer function
        """
        # Create tables
        SpatialBase.metadata.create_all(spatial_engine)

        # Initial data
        if first_time:
            # Make session
            session = SpatialSessionMaker()

            # Gage 1
            gage1 = SpatialStreamGage(latitude=40.23812952992122,
                                      longitude=-111.69585227966309,
                                      value=1)


            session.add(gage1)

            # Gage 2
            gage2 = SpatialStreamGage(latitude=40.238784729316215,
                                      longitude=-111.7101001739502,
                                      value=2)

            session.add(gage2)

            session.commit()

Using Spatial Database Functions
--------------------------------

One of the major advantages of storing spatial data in PostGIS is that the data is exposed to spatial querying. PostGIS includes over 400 database functions (not counting variants) that can be used to perform spatial operations on the data stored in the database. Refer to the `Geometry Function Reference <http://postgis.net/docs/reference.html>`_ and the `Raster Function Reference <http://postgis.net/docs/RT_reference.html>`_ in the PostGIS documentation for more details.

GeoAlchemy2 makes it easy to use the spatial functions provided by PostGIS to perform spatial queries. For example, the ``ST_Contains`` function can be used to determine if one geometry is contained inside another geometry. To perform this operation on the spatial stream gage model would look something like this:

::

    from sqlalchemy import func
    from .model import SpatialStreamGage, SpatialSessionMaker

    session = SpatialSessionMaker()
    query = session.query(SpatialStreamGage).filter(
                func.ST_Contains('POLYGON((0 0,0 1,1 1,0 1,0 0))', SpatialStreamGage.geom)
                )

.. important::

    This article only briefly introduces the concepts of working with GeoAlchemy2. It is highly recommended that you complete the `GeoAlchemy ORM <https://geoalchemy-2.readthedocs.org/en/latest/orm_tutorial.html>`_ tutorial.