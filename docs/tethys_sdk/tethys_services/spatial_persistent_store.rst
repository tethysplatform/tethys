*****************************
Spatial Persistent Stores API
*****************************

**Last Updated:** May 2017

.. important::

    This feature requires the ``psycopg2``, ``sqlalchmey``, and ``geoalchemy2`` libraries to be installed. Starting with Tethys 5.0 or if you are using ```micro-tethys-platform``, you will need to install these libraries using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge psycopg2 "sqlalchemy<2" geoalchemy2

        # pip
        pip install psycopg2 "sqlalchemy<2" geoalchemy2

Persistent store databases can support spatial data types. The spatial capabilities are provided by the `PostGIS <http://postgis.net/>`_ extension for the `PostgreSQL <https://www.postgresql.org/>`_ database. PostGIS extends the column types of PostgreSQL databases by adding ``geometry``, ``geography``, and ``raster`` types. PostGIS also provides hundreds of database functions that can be used to perform spatial operations on data stored in spatial columns. For more information on PostGIS, see `<http://www.postgis.net>`_.

The following article details the the spatial capabilities of persistent stores in Tethys Platform. This article builds on the concepts and ideas introduced in the :doc:`./persistent_store` documentation. Please review it before continuing.

Spatial Persistent Store Settings
=================================

Registering spatially enabled persistent stores is the same process as registering normal persistent stores. The only difference is that you will set the ``spatial`` attribute of the ``PersistentStoreDatabaseSetting`` object to ``True``:

::

    from tethys_sdk.base import TethysAppBase
    from tethys_sdk.app_settings import PersistentStoreDatabaseSetting


    class App(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...

        def persistent_store_settings(self):
            ps_settings = (
                PersistentStoreDatabaseSetting(
                    name='spatial_db',
                    description='Primary spatially enabled database for my_first_app.',
                    initializer='my_first_app.model.init_spatial_db',
                    required=True,
                    spatial=True
                ),
            )

            return ps_settings

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Adding Spatial Columns to Model
-------------------------------

Working with the ``raster``, ``geometry``, and ``geography`` column types provided by PostGIS is not supported natively in SQLAlchemy. Tethys Platform includes `GeoAlchemy2 <https://geoalchemy-2.readthedocs.io/en/latest/index.html>`_, which extends SQLAlchemy to support spatial columns and database functions. The following example illustrates how a data model could be developed using SQLAlchemy and GeoAlchemy2:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer
    from sqlalchemy.orm import sessionmaker

    from geoalchemy2 import Geometry

    # Spatial DB Engine, sessiomaker, and base
    Base = declarative_base()

    # SQLAlchemy ORM definition for the spatial_stream_gages table
    class SpatialStreamGage(Base):
        """
        Example of SQLAlchemy spatial DB model
        """
        __tablename__ = 'stream_gages'

        # Columns
        id = Column(Integer, primary_key=True)
        value = Column(Integer)
        geometry = Column(Geometry('POINT'))

        def __init__(self, latitude, longitude, value):
            """
            Constructor for a gage
            """
            self.geometry = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)
            self.value = value

This data model is very similar to the data model defined in the :doc:`./persistent_store` documentation. Rather than using ``Float`` columns to store the latitude and longitude coordinates, the spatial data model uses a GeoAlchemy2 ``Geometry`` column called "geometry". Notice that the constructor (``__init__.py``) takes the ``latitude`` and ``longitude`` provided and sets the value of the ``geometry`` column to a string with a special format called `Well Known Text <https://en.wikipedia.org/wiki/Well-known_text>`_. This is a common pattern when working with GeoAlchemy2 columns.

Initialization Function
-----------------------

Initializing spatial persistent stores is performed in exactly the same way as normal persistent stores. An initialization function for the example above, would look like this:

::

    from sqlalchemy.orm import sessionmaker
    from .model import Base, SpatialStreamGage

    def init_spatial_db(engine, first_time):
        """
        An example persistent store initializer function
        """
        # Create tables
        Base.metadata.create_all(engine)

        # Initial data
        if first_time:
            # Make session
            SessionMaker = sessionmaker(bind=engine)
            session = SessionMaker()

            # Gage 1
            gage1 = SpatialStreamGage(
                latitude=40.23812952992122,
                longitude=-111.69585227966309,
                value=1
            )

            session.add(gage1)

            # Gage 2
            gage2 = SpatialStreamGage(
                latitude=40.238784729316215,
                longitude=-111.7101001739502,
                value=2
            )

            session.add(gage2)

            session.commit()
            session.close()

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

    This article only briefly introduces the concepts of working with GeoAlchemy2. It is highly recommended that you complete the `GeoAlchemy ORM <https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html>`_ tutorial.