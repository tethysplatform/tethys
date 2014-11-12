*******************************
The Model and Persistent Stores
*******************************

**Last Updated:** November 11, 2014

In this part of the tutorial you'll learn about the Model component of MVC development for Tethys apps. The Model represents the data of your app and the code used to manage it. The data of your app can take many forms. It can be generated on-the-fly and stored in Python data structures (e.g.: lists, dictionaries, and NumPy arrays), stored in databases, or contained in files via a :term:`dataset service`.

In this tutorial you will use the :doc:`../tethys_api/persistent_store` to create a spatially enabled database for your app and you will learn how to use the `SQLAlchemy <http://www.sqlalchemy.org/>`_ object relational mapper (ORM) to create a data model for your app.

Register a Persistent Store
===========================

To register a new :term:`persistent store` database add the ``persistent_stores()`` method to your :term:`app class`, which is located in your :term:`app configuration file`. This method must return a list or tuple of ``PersistentStore`` objects.

Open the app configuration file for your app located at :file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/app.py`. Import the ``PersistentStore`` object at the top and add the ``persistent_stores()`` method to your app class as follows:

::

    from tethys_apps.base import TethysAppBase, app_controller_maker
    from tethys_apps.base import PersistentStore


    class MyFirstApp(TethysAppBase):
        """
        Tethys App Class for My First App.
        """

        ...

        def persistent_stores(self):
            """
            Add one or more persistent stores
            """
            stores = (PersistentStore(name='stream_gage_db',
                                      initializer='init_stores:init_stream_gage_db',
                                      spatial=True
                    ),
            )

            return stores



A persistent store database will be created for each ``PersistentStore`` object that is returned by the ``persistent_stores()`` method. In this case, your app will have a persistent store named "stream_gage_db". The ``initializer`` argument points to a function that you will define in a later step. The ``spatial`` argument can be used to add spatial capabilities to your persistent store. Tethys Platform provides PostgreSQL databases for persistent stores and PostGIS for the spatial database capabilities.

.. note::

    Read more about persistent stores in the :doc:`../tethys_api/persistent_store` documentation.

Create an SQLAlchemy Data Model
===============================

SQLAlchemy provides an Object Relational Mapper (ORM) that allows you to create data models using Python code and issue queries using an object-oriented approach. In other words, you are able to harness the power of SQL databases without writing SQL. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Object Relational Tutorial <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html>`_.

You will use SQLAlchemy to create a data model for the tables that will store the data for your app. Open the :file:`model.py` file located at :file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/model.py`.

First, add the following import statements to your :file:`model.py` file:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, Float
    from sqlalchemy.orm import sessionmaker

    from .utilities import get_persistent_store_engine


Next, add these lines to your :file:`model.py` file:

::

    # DB Engine, sessionmaker and base
    engine = get_persistent_store_engine('stream_gage_db')
    SessionMaker = sessionmaker(bind=engine)
    Base = declarative_base()

The ``get_persistent_store_engine()`` method accepts the name of a persistent store as an argument and returns and SQLAlchemy engine object. The engine object contains the connection information needed to connect to the persistent store database. Anytime you want to query or modify your persistent store data, you will do so with an SQLAlchemy ``session`` object. As the name implies, the ``SessionMaker`` can be used to create new ``session`` objects. The ``Base`` object is used in the next step when we define our data model. Add these lines to your :file:`model.py` file:

::

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

Each class of an SQLAlchemy data model defines a table in the database. Currently the model consists of a single table called "stream_gages", as denoted by the ``__tablename__`` property of the ``StreamGage`` class. The ``StreamGage`` class inherits from the ``Base`` class that we created in the previous lines.

The class defines four other properties that are SQLAlchemy ``Column`` objects: *id*, *latitude*, *longitude*, and *value*. These properties define the columns of the "stream_gages" table. The column type and options are defined by the arguments passed to the ``Column`` constructor. For example, the *latitude* column is of type ``Float`` while the *id* column is of type ``Integer`` and is also flagged as the primary key for the table. The ``StreamGage`` class also has a simple constructor method called ``__init__()``.

This class is not only used to define the tables for your persistent store, it will also be used to create objects for interacting with your data.

Create an Initialization Function
=================================

Now that you have created a data model, the next step is to write a database initialization function. This function will be called during the initialization phase of your persistent store database and will be used to create the tables in your database and add any initial data that you may need in the database for your app to work.

Open the :file:`init_stores.py` file located at :file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/init_stores.py`. Import the ``engine``, ``SessionMaker``, ``Base``, and ``StreamGage`` from your data model::

    from .model import engine, SessionMaker, Base, StreamGage

Next, create a new function called ``init_stream_gage_db()`` with a single argument called ``first_time`` and the
following code::

    def init_stream_gage_db(first_time):
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

            # Gage 3
            gage3 = StreamGage(latitude=40.23650788415366,
                               longitude=-111.73278093338013,
                               value=3)

            session.add(gage3)

            # Gage 4
            gage4 = StreamGage(latitude=40.242519244799816,
                               longitude=-111.68254852294922,
                               value=4)

            session.add(gage4)

            session.commit()

The ``Base.metedata.create_all(engine)`` line is all that is needed to create the tables in your persistent store database. Every class that inherits from the ``Base`` class is tracked by the ``metadata`` object. The ``metadata.create_all()`` method issues the SQL that is needed to create the tables associated with the ``Base`` class. Notice that you must give it the ``engine`` object for connection information.

The ``first_time`` parameter that is passed to all persistent store initialization functions is a boolean that is ``True`` if the function is being called after freshly minted tables have been created for the first time. This is provided as a mechanism for adding initial data only once. Notice the code that adds initial data to your persistent store database is wrapped in a conditional statement that uses the ``first_time`` parameter.

This initial data code adds four stream gages to your persistent store database. Creating a new record in the database using SQLAlchemy is achieved by creating a new ``StreamGage`` object and adding it to the ``session`` object using the ``session.add()`` method. To persist the new records to the persistent store database, the ``session.commit()`` method is called. You will learn how to query the persistent store database using SQLAlchemy in the :doc:`./controller` tutorial.

.. tip::

    While you are developing your database model, you will likely make changes to the tables and columns frequently. To create updated tables and columns, you will first need to drop the old tables. Modify your database initialization function by adding the ``Base.metadata.drop_all(engine)`` line as follows:

    ::

        def init_function(first_time):
            """
            Persistent store initializer function
            """
            # Drop tables
            Base.metadata.drop_all(engine) # TODO: TAKE OUT BEFORE RELEASE

            # Create tables
            Base.metadata.create_all(engine)

            # Initial data
            if first_time:
                ...

    This will have the effect of dropping all the tables and then creating them again everytime the initialization script is executed. **Don't forget to take this line out when your distribute your app**. Leaving it in could have confusing consequences and lead to loss of data.



Register Initialization Function
================================

Recall that when you registered the persistent store in your app configuration file, you specified the ``initializer`` function for the persistent store. This argument accepts a string representing the path to the function using dot notation and a colon to delineate the function (e.g.: "foo.bar:function"). Check your app configuration file to ensure the path to the initializer function is correct: ``'init_stores:init_stream_gage_db'``.

Persistent Store Initialization
===============================

If you have not done so already, start your development server again using the ``tethys manage start`` command. The database will be initialized on start up. The information printed to the console will indicate this::

    Harvesting Apps:
    my_first_app

    Provisioning Persistent Stores:
    Creating database "stream_gage_db" for app "my_first_app"...
    Enabling PostGIS on database "stream_gage_db" for app "my_first_app"...
    Initializing database "stream_gage_db" for app "my_first_app"

If you have a graphical database client, you may wish to connect to your PostgreSQL database server and confirm that the database was created. You can use the credentials for ``tethys_super`` database user that you defined during installation to connect to the database. The name of the database will be a combination of the name of your app and the name of the persistent store: (i.e.: my_first_app_stream_gage_db).