******
Models
******

**Last Updated:** February 22, 2018

Extensions are not able to be linked to databases, but they can be used to store SQLAlchemy models that are used by multiple apps. Define the SQLAlchemy model as you would normally:

::

    import datetime
    from sqlalchemy import Column
    from sqlalchemy.types import Integer, String, DateTime
    from sqlalchemy.ext.declarative import declarative_base


    MyFirstExtensionBase = declarative_base()


    class Project(MyFirstExtensionBase):
        """
        SQLAlchemy interface for projects table
        """
        __tablename__ = 'projects'

        id = Column(Integer, autoincrement=True, primary_key=True)
        name = Column(String)
        description = Column(String)
        date_created = Column(DateTime, default=datetime.datetime.now(datetime.UTC))


To initialize the tables using a model defined in an extension, import the declarative base from the extension in the initializer function for the persistent store database you'd like to initialize:

::

    from tethyext.my_first_extension.models import MyFirstExtensionBase


    def init_primary_db(engine, first_time):
        """
        Initializer for the primary database.
        """
        # Create all the tables
        MyFirstExtensionBase.metadata.create_all(engine)

To use the extension models to query the database, import them from the extension and use like usual:

::

    from tethysapp.my_first_app.app import App
    from tethysext.my_first_extension.models import Project


    def my_controller(request, project_id):
        """
        My app controller.
        """
        SessionMaker = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
        session = SessionMaker()
        project = session.query(Project).get(project_id)

        context = {
            'project': project
        }

        return App.render(request, 'some_template.html', context)