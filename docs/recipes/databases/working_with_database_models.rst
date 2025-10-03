.. _working_with_database_models_recipe:

Working with Database models
#############################

**Last Updated:** September 2025

This recipe will show you how to interact and work with database models. For more information on how to create database models, check out :ref:`Creating Database Models <create_database_models_recipe>`

There are a few different ways to interact with data from the database:

* **Creating**: Writing to the database
* **Retreiving**: Extracting existing information
* **Updating**: Modifying existing records
* **Deleting**: Removing data from the table

Below are examples for each of these interactions.

For these examples, we'll use the Dam model defined in the :ref:`Creating Database Models <create_database_models_recipe>` recipe.

In order to interact with the database in any way, you'll need to initiate a session to connect to it

**Note:** 'primary_db' should be replaced with the name of your persistent store service setting. 

.. code-block:: python

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

If you are making any changes or updates to the database (creating, updating, or deleting), you'll need to **commit** your changes or they won't be saved.

.. code-block:: python

    session.commit()

After you're done interacting with the database, **always** make sure to close the session:

.. code-block:: python

    session.close()

Creating
+++++++++

To create a new Dam in the database:

.. code-block:: python

    from .model import Dam

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    new_dam = Dam(
        latitude=36.016,
        longitude=-114.737,
        river="Colorado River",
        name="Hoover Dam",
        owner=""
    )

    session.add(new_dam)
    session.commit()
    session.close()

Retreiving
++++++++++

To retreive all the instances of a model or in other words, all the rows in a table:

.. code-block:: python

    from .model import Dam

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    dams = session.query(Dam).all()
    for dam in dams:
        print(f"Name: {dam.name} - River: {dam.river}")

    # Close the session
    session.close()


To retrieve a dam with a specific id:

.. code-block:: python

    from .model import Dam

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    # Access the dam with id 123
    dam = session.query(Dam).get(123)
    print(f"This dam's name is {dam.name} on the {dam.river}")

    session.close()

To retrieve all dams on a certain river:

.. code-block:: python

    from .model import Dam

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    
    dams = session.query(Dam).filter(Dam.river=="Columbia River")
    
    print("All dams on the columbia river: ")
    for dam in dams:
        print(dam.name)

    session.close()

To retrieve a dam by name:

.. code-block:: python

    from .model import Dam  

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    dam = session.query(Dam).filter(Dam.name=="Hoover Dam").first()

    print(f"The Hoover Dam is on the {dam.river}")

Updating
++++++++

Here is how to update an entry of a dam in the database:

.. code-block:: python

    from .model import Dam  

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    dam = session.query(dam).filter_by(name="Hoover Dam").first()

    if dam:
        dam.owner = "U.S. Bureau of Reclamation" # Update owner
        session.commit() # Save changes
    
    session.close()


Deleting
++++++++

Here is how to delete an entry from the database:

.. code-block:: python

    from .model import Dam  

    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    dam = session.query(dam).filter_by(name="Hoover Dam").first()

    if dam:
        session.delete(dam)
        session.commit() # Save changes
    
    session.close()

        
For more information on working with databases using SQLAlchemy, check out the `SQLAlchemy Unified Tutorial <https://docs.sqlalchemy.org/en/20/tutorial/index.html#unified-tutorial>`_