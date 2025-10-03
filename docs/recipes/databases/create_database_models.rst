.. _create_database_models_recipe :


*************************
Creating a Database Model
*************************

**Last Updated:** September 2025

This recipe will show you how to create a database model. A database model represents a table in your database.


Defining a Model
++++++++++++++++

Define a table called dams by creating a new class in :file:`model.py` called Dam:

.. code-block:: python

    import json
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, Float, String
    from sqlalchemy.orm import sessionmaker

    from .app import App

    Base = declarative_base()


    # SQLAlchemy ORM definition for the dams table
    class Dam(Base):
        """
        SQLAlchemy Dam DB Model
        """
        __tablename__ = 'dams'

        # Columns
        id = Column(Integer, primary_key=True)
        latitude = Column(Float)
        longitude = Column(Float)
        name = Column(String)
        owner = Column(String)
        river = Column(String)
        date_built = Column(String)

This class defines a table for storing data on different Dams. Each member variable here represents an attribute of a dam, or a column of the database table.

.. tip::

    Always make sure to execute the syncstores command to add any new tables to the database or to update your tables with changes you've made to them.:

    .. code-block:: bash
        
        tethys syncstores your_app

Model Relationships
+++++++++++++++++++

Next, let's add some more models that **relate** to each other and to the Dam model.

.. code-block:: python

    class Hydrograph(Base):
        """
        SQLAlchemy Hydrograph DB Model
        """
        __tablename__ = 'hydrographs'

        # Columns
        id = Column(Integer, primary_key=True)
        dam_id = Column(ForeignKey('dams.id'))

        # Relationships
        dam = relationship('Dam', back_populates='hydrograph')
        points = relationship('HydrographPoint', back_populates='hydrograph')


    class HydrographPoint(Base):
        """
        SQLAlchemy Hydrograph Point DB Model
        """
        __tablename__ = 'hydrograph_points'

        # Columns
        id = Column(Integer, primary_key=True)
        hydrograph_id = Column(ForeignKey('hydrographs.id'))
        time = Column(Integer)  #: hours
        flow = Column(Float)  #: cfs

        # Relationships
        hydrograph = relationship('Hydrograph', back_populates='points')

Also add a relationship to your Dam model: 
 
.. code-block:: python
    :emphasize-lines: 16-17

    class Dam(Base):
        """
        SQLAlchemy Dam DB Model
        """
        __tablename__ = 'dams'

        # Columns
        id = Column(Integer, primary_key=True)
        latitude = Column(Float)
        longitude = Column(Float)
        name = Column(String)
        owner = Column(String)
        river = Column(String)
        date_built = Column(String)

        # Relationships
        hydrograph = relationship('Hydrograph', back_populates='dam', uselist=False)

The `dam_id` attribute in the Hydorgraph model and the `hydrograph_id` attribute in the HydrographPoint model serve as actual columns on those "tables". The relationships you've defined in your models are Python helpers that let you more easily move between and access related Dams and Hydrographs, and related Hydrographs and Hydrograph Points. See some examples below:

.. tip::

    Always make sure to execute the syncstores command to add any new tables to the database or to update your tables with changes you've made to them.:

    .. code-block:: bash
        
        tethys syncstores your_app

.. code-block:: python

    from .app import App
    from .model import Dam

    def get_hydrograph_points(dam_id):
        Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
        session = Session()

        dam = session.query(Dam).get(int(dam_id))

        hydrograph = dam.hydrograph

        points = hydrograph.points

        for point in points:
            print(f"Time: {point.time}, Flow: {point.flow}")

        session.close()

.. code-block:: python

        from .app import App
        from .model import Hydrograph

        def get_dam(hydrograph_id):
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()

            hydrograph = session.query(Hydrograph).get(int(hydrograph_id))

            dam = hydrograph.dam

            print(f"This hydrograph's dam's name is: {dam.name}, and it is located on the {dam.river} river.")

            session.close()


Now that you've learned how to create your own database models, it may be useful to look at how to work with database models in other ways: :ref:`Working with Database Models <working_with_database_models_recipe>`

