*******************************
The Model and Persistent Stores
*******************************

**Last Updated:** November 11, 2014

In this part of the tutorial you'll learn about the Model component of MVC. The Model represents the data of your app
and the code used to manage it. The data of your app can take many forms. It can be generated on-the-fly and stored in
Python data structures (e.g.: lists, dictionaries, and NumPy arrays), stored in databases, or contained in files via
a dataset service.

In this tutorial you will learn how to use the `SQLAlchemy <http://www.sqlalchemy.org/>`_ object relational mapper
(ORM). You will also use the :doc:`../tethys_api/persistent_store` to create a spatially enabled database for your app.

Register a Persistent Store
===========================

To register a new persistent store database add the ``persistent_stores()`` method of your :term:`app class`, which is
located in your :term:`app configuration file`. This method must return a list or tuple of ``PersistentStore`` objects.
Open the app configuration file for your app located at :file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/app.py`.
Import the ``PersistentStore`` objects and add the ``persistent_stores()`` method to your app class as follows:

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



A persistent store database will be created for each ``PersistentStore`` object that is returned by the ``persistent_stores()``
method. In this case, your app will have a persistent store named "stream_gage_db". The ``initializer`` argument
points to a function that you define that will be called to initialize the persistent store database. This will be
discussed in more detail after the data model has been created. The ``spatial`` argument can be used to add spatial
capabilities to your persistent store. Tethys Platform provides PostgreSQL databases for persistent stores and PostGIS
for the spatial database capabilities.

.. note::

    Read more about persistent stores in the :doc:`../tethys_api/persistent_store` documentation.

Create an SQLAlchemy Data Model
===============================

SQLAlchemy provides an Object Relational Mapper (ORM) that allows you to create data models using Python code and issue
queries using an object-oriented approach. In other words, you are able to harness the power of SQL databases without
writing SQL. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Object Relational Tutorial <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html>`_.

You will use SQLAlchemy to create a data model for the tables that will be store the data for your app. Open the
:file:`model.py` file located at :file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/model.py`.

First, add the following import statements to your :file:`model.py` file:

::

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.orm import sessionmaker

    from .utilities import get_persistent_store_engine


Next, add these lines to your :file:`model.py` file:

::

    # DB Engine, sessionmaker and base
    engine = get_persistent_store_engine('stream_gage_db')
    SessionMaker = sessionmaker(bind=engine)
    Base = declarative_base()

The ``get_persistent_store_engine()`` method accepts the name of a persistent store as an argument and returns and
SQLAlchemy engine object. The engine object contains all the connection information need to connect to the persistent
store database. Anytime you want to query or modify your persistent store data, you will do so with an SQLAlchemy
``session`` object. As the name implies, the ``SessionMaker`` can be used to create new ``session`` objects. The
``Base`` object is used in the next step when we define our data model.

Finally, add these lines to your :file:`model.py` file:

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

        @classmethod
        def get_gages_as_geojson(cls):
            '''
            Returns a GeoJSON object representing all gages in db
            '''
            # Create a session
            session = SessionMaker()

            # Query DB for gage objects
            gages = session.query(cls).all()

            # Create geojson object
            geojson_gages = {"type": "GeometryCollection",
                             "geometries": []}
            geometries = []

            # Create geometry objects for each gage
            for gage in gages:
                gage_geometry = dict(type="Point",
                					 coordinates=[gage.latitude, gage.longitude],
                                     properties={"value": gage.value})
                geometries.append(gage_geometry)

            geojson_gages['geometries'] = geometries
            return geojson_gages

The database model is defined by the ``StreamGage`` class. Each class of an SQLAlchemy data model defines a table in
the database. Currently the model consists of a single table called "stream_gages", as denoted by the ``__tablename__``
property.

Notice that the ``StreamGage`` class inherits from the ``Base`` class that we created in the previous lines. The class
also has four other properties that are SQLAlchemy ``Column`` objects: *id*, *latitude*, *longitude*, and *value*.
These properties define the columns of the "stream_gages" table. The column type and options are defined by the
arguments passed to the ``Column`` constructor. For example, the *latitude* column is of type ``Float`` while the *id*
column is of type ``Integer`` and is also flagged as the primary key for the table. The ``StreamGage`` class also has a
simple constructor method called ``__init__()`` and a class method called ``get_gages_as_geojson()``.

This class is not only used to define the tables for your persistent store, it will also be used to create objects for
interacting with your data. Each instance of the ``StreamGage`` class will represent one row or record in the
"stream_gages" table and the properties of the instance be populated with the values of the columns in that record.
You will learn how to use these objects for interacting the database in the next section.

Create an Initialization Function
=================================

Now that you have created a data model, the next step is to write a database initialization function. This function will
use the database model from the previous section to create all the tables. We'll also use this function to add some
dummy data for testing.

1. Create a new file called     :file:`init_stream_gages_db.py` in your :term:`app package` :file:`lib` directory (:file:`~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/lib`).

2. Add the following lines to your     :file:`init_stream_gages_db.py` script:

::

    from tethysapp.my_first_app.stream_gage_model import Base, engine, StreamGage, SessionMaker

    Base.metadata.create_all(engine)

Believe it or not, these two lines are all that is needed to create all of the tables in your persistent store. The ``Base`` object that our model class inherits from contains a ``metadata`` object. The ``metadata`` object collects all of the information about the tables in our data model from the classes that inherit ``Base``. We call the ``metadata.create_all()`` to create the tables and we give it the ``engine`` object from our :file:`stream_gages_model.py` file to point it at the right database. After the tables are created, let's have the initialization script load some dummy data into our database so we can make sure everything is working properly.

3. First, we need to create a ``session`` object to interact with the database. We will use the ``SessionMaker`` object that we created in our :file:`stream_gages_model.py` to create a new ``session``. Add these lines to your :file:`init_stream_gages_db.py` script:

::

    # Create a Session
    session = SessionMaker()

4. Next, we need to add some dummy data. To do so, we create several instances of the ``StreamGage`` class. Each instance will represent a new row in our "stream_gages" table. Copy and paste the following line of code into your :file:`init_stream_gages_db.py` script:

::

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

Notice that everytime we create a new ``StreamGage`` object, we add it to the ``session`` object using the ``session.add()`` method. Finally, when we are ready to persist the data, we call the ``session.commit()`` method. Querying using SQLAlchemy will be covered in the :doc:`./controller` tutorial.


Register Initialization Script
==============================

Now that you have created a database initialization script, we can register it to be run automatically when the app is installed. To do so, modify the ``registerPersistentStores()`` method in your :term:`app configuration file` so it looks like this:

::

    def registerPersistentStores(self, persistentStores):
        '''
        Add one or more persistent stores
        '''
        persistentStores.addPersistentStore('stream_gage_db')
        persistentStores.addInitializationScript('my_first_app.lib.init_stream_gages_db')


Reinstall App
=============

Everytime you add a new persistent store to your app, you will need to reinstall the app to have it created. Everytime you make changes to your data model (i.e.: edit the tables and columns), you will need to reinstall the app or rerun your database initialization script. The app can be reinstalled like so:

::

    $ . /usr/lib/ckan/default/bin/activate
    $ cd ~/tethydev/tethysapp-my_first_app
    $ python setup.py develop

.. note::

    If you want to hard install your app (which is not recommended under development) use the :command:`install` command instead of :command:`develop`. See :doc:`../working_with_apps`.


Data Model Under Development
============================

While you are developing your database model, you will likely make changes to the tables and columns frequently. To create updated tables and columns, you will first need to drop the old tables. Add the following line to your database initialization script just before the line that calls ``Base.metadata.create_all()``:

::

    Base.metadata.drop_all(engine)

This will have the effect of dropping all the tables and then creating them again everytime you run the initialization script. **Don't forget to take this line out when your distribute your app**. Leaving it in could have confusing consequences and lead to loss of data.
    

.. _enable-persistent-store-legacy-apps:

Enabling Persistent Store for Legacy Apps
=========================================

If you are working with an app that was generated with the scaffold prior to version 0.3 of the Tethys Apps plugin, you will need to follow these steps to enable automatic persistent stores:

Modify the Setup Script
-----------------------

1. Add the following import statements to the **top** of your app's :term:`setup script` (:file:`setup.py`):

::

    from ckanext.tethys_apps.lib.persistent_store import provision_persistent_stores
    from ckanext.tethys_apps.lib import get_tethysapp_directory


2. Add these lines to the **bottom** of your app's :term:`setup script` (:file:`setup.py`):

::

    # Provision tethys databases for app
    provision_persistent_stores(<your.app.class>)

Replace <your.app.class> with the path to your app class using dot notation. For example, for the ``my_first_app`` example, the path to the app class would be:

::


    'my_first_app.app:MyFirstAppApp'


Modify the App Configuration File
---------------------------------

Add the ``registerPersistentStores()`` method to the bottom of your :term:`app class` in the :term:`app configuration file` (:file:`app.py`):

::

    def registerPersistentStores(self, persistentStores):
        '''
        Add one or more persistent stores
        '''
        # persistentStores.addPersistentStore('example_db')
        # persistentStores.addInitializationScript('example.lib.init_db')

Add Method to App Lib
---------------------

Finally, add this method to your ``lib.__init__.py`` file:

::

    import os
    from ckanext.tethys_apps.lib.persistent_store import get_persistent_store_engine as gpse

    def get_persistent_store_engine(persistent_store_name):
        '''
        Wrapper for the get_persistent_store_engine method that makes it easier to use
        '''
        # Derive app name
        app_name = os.path.split(os.path.dirname(os.path.dirname(__file__)))[1]
        
        # Get engine
        return gpse(app_name, persistent_store_name)

Install the Latest Version of Tethys Apps Plugin
------------------------------------------------

Follow the instructions at :doc:`../installation` to install the latest version of Tethys Apps. There are a few additional steps to Tethys Apps installation that are necessary (e.g.: setting up a database user for database provisioning).








