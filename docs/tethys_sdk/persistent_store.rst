*********************
Persistent Stores API
*********************

**Last Updated:** November 12, 2014


The Persistent Store API streamlines the use of SQL databases in Tethys apps. Using this API, you can provision up to 5 SQL databases for your app. The databases that will be created are `PostgreSQL <http://www.postgresql.org/>`_ databases. Currently, no other databases are supported.

The process of creating a new persistent database can be summed up in the following steps:

1. register a new persistent store in the :term:`app configuration file`,
2. create a data model to define the table structure of the database,
3. write a persistent store initialization function, and
4. use the Tethys command line interface to create the persistent store.

More detailed descriptions of each step of the persistent store process will be discussed in this article.

Persistent Store Registration
=============================

To register a new :term:`persistent store` database add the ``persistent_stores()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method must return a list or tuple of ``PersistentStore`` objects. The following example illustrates what an :term:`app class` with the ``persistent_stores()`` method would look like:

::

    from tethys_apps.base import TethysAppBase, url_map_maker, PersistentStore


    class MyFirstApp(TethysAppBase):
        """
        Tethys App Class for My First App.
        """

        ...

        def persistent_stores(self):
            """
            Add one or more persistent stores
            """
            stores = (PersistentStore(name='example_db',
                                      initializer='init_stores:init_example_db'
                    ),
            )

            return stores

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

In this example, a database called "example_db" would be created for this app. It would be initialized by a function called "init_example_db", which is located in a Python module called :file:`init_stores.py`. Notice that the path to the initializer function is given using dot notation with a colon delineating the function (e.g.: ``'foo.bar:function'``).

Up to 5 databases can be created for an app using the Persistent Store API. To add another database, add another ``Persistent Store`` object to the tuple that is returned by the ``persistent_stores()`` method.

Data Model Definition
=====================

Creating the database is only half the battle. The next step is to create tables in the database. For persistent stores, this is done using an SQLAlchemy ORM data model. The recommended location for data model code is :file:`model.py` file. The following code illustrates how to create an SQLAlchemy ORM data model that contains a single table for storing stream gage information:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, Float
    from sqlalchemy.orm import sessionmaker

    from .utilities import get_persistent_store_engine

    # DB Engine, sessionmaker and base
    engine = get_persistent_store_engine('stream_gage_db')
    SessionMaker = sessionmaker(bind=engine)
    Base = declarative_base()

    # SQLAlchemy ORM definition for the stream_gages table
    class StreamGage (Base):
        '''
        Example SQLAlchemy DB Model
        '''
        __tablename__ = 'stream_gages'

        # Columns
        id = Column(Integer, primary_key=True)
        latitude = Column(Float)
        longitude = Column(Float)
        value = Column(Integer)

        def __init__(self, latitude, longitude, value):
            """
            Constructor for a gage
            """
            self.latitude = latitude
            self.longitude = longitude
            self.value = value

The ``get_persistent_store_engine()`` method is provided by Tethys Platform and it accepts the name of a persistent store as an argument and returns an SQLAlchemy engine object. The engine object contains the connection information needed to connect to the persistent store database. Anytime you want to query or modify your persistent store data, you will do so with an SQLAlchemy ``session`` object. As the name implies, the ``SessionMaker`` can be used to create new ``session`` objects.

Each class in an SQLAlchemy data model defines a table in the database. The example above consists of a single table called "stream_gages", as denoted by the ``__tablename__`` property of the ``StreamGage`` class. The ``StreamGage`` class inherits from the ``Base`` class that was created in the previous lines using the ``declarative_base()`` function provided by SQLAlchemy. This inheritance notifies SQLAlchemy that the ``StreamGage`` class is part of the data model.

The class in the example four other properties that are SQLAlchemy ``Column`` objects: *id*, *latitude*, *longitude*, and *value*. These properties define the columns of the "stream_gages" table. The column type and options are defined by the arguments passed to the ``Column`` constructor. For example, the *latitude* column is of type ``Float`` while the *id* column is of type ``Integer`` and is also flagged as the primary key for the table. The ``StreamGage`` class also has a simple constructor method called ``__init__()``.

This class is not only used to define the tables for your persistent store, it will also be used to create objects for interacting with your data.

SQLAlchemy ORM is a powerful tool for working with SQL databases. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Object Relational Tutorial <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html>`_.

Initialization Function
=======================

The code for initializing a persistent store database should be defined in a initialization function. The recommended location for initialization functions is the :file:``init_stores.py`` file. The initialization function makes use of the data model defined in the :file:`model.py` file. Here is an example of a typical initialization function for a persistent store database:

::

    from .model import engine, SessionMaker, Base, StreamGage

    def init_example_db(first_time):
        """
        An example persistent store initializer function
        """
        # Create tables
        Base.metadata.create_all(engine)

        # Initial data
        if first_time:
            # Make session
            session = SessionMaker()

            # Gage 1
            gage1 = StreamGage(latitude=40.23812952992122,
                               longitude=-111.69585227966309,
                               value=1)


            session.add(gage1)

            # Gage 2
            gage2 = StreamGage(latitude=40.238784729316215,
                               longitude=-111.7101001739502,
                               value=2)

            session.add(gage2)

            session.commit()

The ``init_example_db()`` initialization function creates the tables and then adds some initial data to the database. The ``Base.metedata.create_all(engine)`` line is all that is needed to create the tables in a persistent store database. Every class that inherits from the ``Base`` class is tracked by a ``metadata`` object. The ``metadata.create_all()`` method issues the SQL that is needed to create the tables associated with the ``Base`` class. Notice that you must give it the ``engine`` object for connection information.

The ``first_time`` parameter that is passed to all persistent store initialization functions is a boolean that is ``True`` if the function is being called after the tables have been created for the first time. This is provided as a mechanism for adding initial data only the first time. Notice the code that adds initial data to your persistent store database is wrapped in a conditional statement that uses the ``first_time`` parameter.

This initial data code adds four stream gages to your persistent store database. Creating a new record in the database using SQLAlchemy is achieved by creating a new ``StreamGage`` object and adding it to the ``session`` object using the ``session.add()`` method. To persist the new records to the persistent store database, the ``session.commit()`` method is called.

Spatial Database Features
=========================

Persistent store databases can support spatial data types. The spatial capabilities are provided by the `PostGIS <http://postgis.net/>`_ extension for `PostgreSQL <http://www.postgresql.org/>`_. PostGIS extends the column types of PostgreSQL databases by adding ``geometry``, ``geography``, and ``raster`` types. PostGIS also provides hundreds of database functions that can be used to perform spatial operations on data stored in spatial columns. For more information on PostGIS, see `<http://www.postgis.net>`_.

The following documentation will provide detailed documentation of the spatial capabilities of persistent stores.

.. warning::

    UNDER CONSTRUCTION

Register Spatial Persistent Store
---------------------------------

Adding Spatial Columns to Model
-------------------------------

Using Spatial Database Functions
--------------------------------


API Documentation
=================

get_persistent_store_engine()

TethysAppBase.persistent_stores()

PersistentStore
