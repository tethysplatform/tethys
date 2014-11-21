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

Registering new :term:`persistent stores` is accomplished by adding the ``persistent_stores()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method must return a list or tuple of ``PersistentStore`` objects. The following example illustrates what an :term:`app class` with the ``persistent_stores()`` method would look like:

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

Up to 5 databases can be created for an app using the Persistent Store API. Databases follow a specific naming convention that is essentially a combination of the app name and the name that is provided during registration. For example, the database for the example above may have a name "my_first_app_example_db". To register another database, add another ``Persistent Store`` object to the tuple that is returned by the ``persistent_stores()`` method.

Data Model Definition
=====================

The tables for a persistent store should be defined using an SQLAlchemy data model. The recommended location for data model code is :file:`model.py` file that is generated with the scaffold. If your data model requires multiple files, it is recommended that you replace the :file:`model.py` module with a package called :file:`model` and store all of the model related modules in this package. The following example illustrates what a typical SQLAlchemy data model may consist of:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, Float
    from sqlalchemy.orm import sessionmaker

    from .utilities import get_persistent_store_engine

    # DB Engine, sessionmaker, and base
    engine = get_persistent_store_engine('example_db')
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


Object Relational Mapping
-------------------------
Each class in an SQLAlchemy data model defines a table in the database. Each object instantiated using an SQLAlchemy class represents individual rows or records in the table. The entire contents of a table could be represented as a list of SQLAlchemy objects. This pattern for interacting between database tables using objects in code is called Object Relational Mapping or ORM.

The example above consists of a single table called "stream_gages", as denoted by the ``__tablename__`` property of the ``StreamGage`` class. The ``StreamGage`` class is defined as an SQLAlchemy data model class because it inherits from the ``Base`` class that was created in the previous lines using the ``declarative_base()`` function provided by SQLAlchemy.This inheritance notifies SQLAlchemy that the ``StreamGage`` class is part of the data model. All tables belonging to the same data model should inherit from the same ``Base`` class.

The columns of tables defined using SQLAlchemy classes are defined by properties that contain ``Column`` objects. The class in the example above defines four columns for the "stream_gages" table: ``id``, ``latitude``, ``longitude``, and ``value``. The column type and options are defined by the arguments passed to the ``Column`` constructor. For example, the ``latitude`` column is of type ``Float`` while the ``id`` column is of type ``Integer`` and is also flagged as the primary key for the table.

Engine Object
-------------

Anytime you wish to query a persistent store database, you will need to connect to it. In SQLAlchemy, the connection to a database is provided via an ``engine`` objects. You can retrieve the SQLAlchemy ``engine`` object for a persistent store database using the ``get_persistent_store_engine()`` function provided by the Persistent Store API. The example above shows how the ``get_persistent_store_engine()`` function should be used. Provide the name of the persistent store to the function and it will return the ``engine`` object for that store.

.. note::

    Although the full name of the persistent store database follows the app-database naming convention described in `Persistent Store Registration`_, you need only use the name you provided during registration to retrieve the engine using ``get_persistent_store_engine()``.

Session Object
--------------

Database queries are issued using SQLAlchemy ``session`` objects. You need to create new session objects each time you perform a new set of queries (i.e.: in each controller). Creating ``session`` objects is done via a ``SessionMaker``. In the example above, the ``SessionMaker`` is created using the ``sessionmaker()`` function provided by SQLAlchemy. The ``SessionMaker`` is bound to the ``engine`` object. This means that anytime a ``session`` is created using that ``SessionMaker`` it will automatically be connected to the database that the ``engine`` provides a connection to. You should create a ``SessionMaker`` for each persistent store that you create. An example of how to use ``session`` and ``SessionMaker`` objects is shown in the `Initialization Function`_ section.

SQLAlchemy ORM is a powerful tool for working with SQL databases. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Object Relational Tutorial <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html>`_.

Initialization Function
=======================

The code for initializing a persistent store database should be defined in an initialization function. The recommended location for initialization functions is the :file:``init_stores.py`` file that is generated with the scaffold. In most cases, each persistent store should have it's own initialization function. The initialization function makes use of the SQLAlchemy data model to create the tables and load any initial data the database may need. The following example illustrates a typical initialization function for a persistent store database:

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

Create Tables
-------------

The SQLAlchemy ``Base`` class defined in the data model is used to create the tables. Every class that inherits from the ``Base`` class is tracked by a ``metadata`` object. As the name implies, the ``metadata`` object collects metadata about each table defined by the classes in the data model. This information used to create the tables when the ``metadata.create_all()`` method is called. In other words, the tables for persistent stores are created using a single line of code:

::

    Base.metadata.create_all(engine)

.. note::

    The ``metadata.create_all()`` method accepts the ``engine`` object for connection information.

Initial Data
------------

The initialization functions should also be used to add any initial data to persistent store databases. The ``first_time`` parameter is provided to all initialization functions as an aid to adding initial data. It is a boolean that is ``True`` if the function is being called after the tables have been created for the first time. This is provided as a mechanism for adding initial data only the first time the initialization function is run. Notice the code that adds initial data to the persistent store database in the example above is wrapped in a conditional statement that uses the ``first_time`` parameter.

Example SQLAlchemy Query
------------------------

This initial data code uses an SQLAlchemy data model to add four stream gages to the persistent store database. A new ``session`` object is created using the ``SessionMaker`` that was defined in the model. Creating a new record in the database using SQLAlchemy is achieved by creating a new ``StreamGage`` object and adding it to the ``session`` object using the ``session.add()`` method. The ``session.commit()`` method is called, to persist the new records to the persistent store database.

Managing Persistent Stores
==========================

Persistent store management is handled via the :command:`syncstores` command provided by the Tethys Command Line Interface (Tethys CLI). This command is used to create the persistent stores of apps during installation. It should also be used anytime you make changes to persistent store registration, data models, or initialization functions. For example, after performing the registration, creating the data model, and defining the initialization function in the example above, the :command:`syncstores` command would need to be called from the command line to create the new persistent store:

::

    $ tethys syncstores my_first_app

This command would create all the non-existent persistent stores that are registered for ``my_first_app`` and run the initialization functions for them. This is the most basic usage of the :command:`syncstores` command. A detailed description of the :command:`syncstores` command can be found in the :doc:`./tethys_cli` documentation.


API Documentation
=================

.. autoclass:: tethys_apps.base.persistent_store.PersistentStore

.. automethod:: tethys_apps.base.persistent_store.get_persistent_store_engine

See :doc:`./app_class` for an explanation of the ``TethysAppBase.persistent_stores()`` method.


.. note::

    Tethys app projects generated using the scaffold include a function in the :file:`utilities.py` called ``get_persistent_store_engine()``. This function is a wrapper for the function defined above and it allows the omission of the  ``app_name`` parameter for simplicity. The example above uses the ``utilities.get_persistent_store_engine()`` function.




