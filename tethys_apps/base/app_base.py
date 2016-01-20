"""
********************************************************************************
* Name: app_base.py
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""
import os
import sys

from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject
from django.conf import settings

from sqlalchemy import create_engine


from tethys_apps.base.workspace import TethysWorkspace
from tethys_apps.base.handoff import HandoffManager


class TethysAppBase(object):
    """
    Base class used to define the app class for Tethys apps.

    Attributes:
      name (string): Name of the app.
      index (string): Lookup term for the index URL of the app.
      icon (string): Location of the image to use for the app icon.
      package (string): Name of the app package.
      root_url (string): Root URL of the app.
      color (string): App theme color as RGB hexadecimal.
      description (string): Description of the app.
      enable_feedback (boolean): Shows feedback button on all app pages.
      feedback_emails (list): A list of emails corresponding to where submitted feedback forms are sent.

    """
    name = ''
    index = ''
    icon = ''
    package = ''
    root_url = ''
    color = ''
    description = ''
    enable_feedback = False
    feedback_emails = []

    def __repr__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

    def url_maps(self):
        """
        Use this method to define the URL Maps for your app. Your ``UrlMap`` objects must be created from a ``UrlMap`` class that is bound to the ``root_url`` of your app. Use the ``url_map_maker()`` function to create the bound ``UrlMap`` class. If you generate your app project from the scaffold, this will be done automatically.

        Returns:
          iterable: A list or tuple of ``UrlMap`` objects.

        **Example:**

        ::

            def url_maps(self):
                \"""
                Example url_maps method.
                \"""
                # Create UrlMap class that is bound to the root url.
                UrlMap = url_map_maker(self.root_url)

                url_maps = (UrlMap(name='home',
                                   url='my-first-app',
                                   controller='my_first_app.controllers.home'
                                   ),
                )

                return url_maps
        """
        raise NotImplementedError()
    
    def persistent_stores(self):
        """
        Define this method to register persistent store databases for your app. You may define up to 5 persistent stores for an app.

        Returns:
          iterable: A list or tuple of ``PersistentStore`` objects. A persistent store database will be created for each object returned.

        **Example:**

        ::

            def persistent_stores(self):
                \"""
                Example persistent_stores method.
                \"""

                stores = (PersistentStore(name='example_db',
                                          initializer='init_stores:init_example_db',
                                          spatial=True
                        ),
                )

                return stores
        """
        return None

    def dataset_services(self):
        """
        Use this method to define dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``DatasetService`` objects.

        **Example:**

        ::

            def dataset_services(self):
                \"""
                Example dataset_services method.
                \"""
                dataset_services = (DatasetService(name='example',
                                                   type='ckan',
                                                   endpoint='http://www.example.com/api/3/action',
                                                   apikey='a-R3llY-n1Ce-@Pi-keY'
                                                   ),
                )

                return dataset_services
        """
        return None

    def spatial_dataset_services(self):
        """
        Use this method to define spatial dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``SpatialDatasetService`` objects.

        **Example:**

        ::

            def spatial_dataset_services(self):
                \"""
                Example spatial_dataset_services method.
                \"""
                spatial_dataset_services = (SpatialDatasetService(name='example',
                                                                  type='geoserver',
                                                                  endpoint='http://www.example.com/geoserver/rest',
                                                                  username='admin',
                                                                  password='geoserver'
                                                                  ),
                )

                return spatial_dataset_services
        """
        return None

    def wps_services(self):
        """
        Use this method to define web processing service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``WpsService`` objects.

        **Example:**

        ::

            def wps_services(self):
                \"""
                Example wps_services method.
                \"""
                wps_services = (WpsService(name='example',
                                           endpoint='http://www.example.com/wps/WebProcessingService'
                                           ),
                )

                return wps_services
        """
        return None

    def handoff_handlers(self):
        """
        Use this method to define handoff handlers for use in your app.

        Returns:
          iterable: A list or tuple of ``HandoffHandler`` objects.

        **Example:**

        ::

            def handoff_handlers(self):
                \"""
                Example handoff_handlers method.
                \"""
                handoff_handlers = (HandoffHandlers(name='example',
                                                    handler='my_first_app.controllers.my_handler'),
                )

                return handoff_handlers
        """
        return None

    @classmethod
    def get_handoff_manager(cls):
        """
        Get the handoff manager for the app.
        """
        app = cls()
        handoff_manager = HandoffManager(app)
        return handoff_manager

    def job_templates(self):
        """
        Use this method to define job templates to easily create and submit jobs in your app.

        Returns:
            iterable: A list or tuple of ``JobTemplate`` objects.

        **Example:**

        ::

            from tethys_sdk.jobs import CondorJobTemplate
            from tethys_sdk.compute import list_schedulers

            def job_templates(cls):
                \"""
                Example job_templates method.
                \"""
                my_scheduler = list_schedulers()[0]

                job_templates = (CondorJobTemplate(name='example',
                                                   parameters={'executable': '$(APP_WORKSPACE)/example_exe.py',
                                                               'condorpy_template_name': 'vanilla_transfer_files',
                                                               'attributes': {'transfer_input_files': ('../input_1.in', '../input_2.in'),
                                                                              'transfer_output_files': ('example_output1.out', 'example_output2.out'),
                                                                             },
                                                               'scheduler': my_scheduler,
                                                               'remote_input_files': ('$(APP_WORKSPACE)/example_exe.py', '$(APP_WORKSPACE)/input_1.in', '$(USER_WORKSPACE)/input_2.in'),
                                                              }
                                                  ),
                                )

                return job_templates
        """
        return None

    @classmethod
    def get_job_manager(cls):
        """
        Get the job manager for the app
        """
        from tethys_sdk.jobs import JobManager
        app = cls()
        job_manager = JobManager(app)
        return job_manager

    @classmethod
    def get_user_workspace(cls, user):
        """
        Get the file workspace (directory) for a user.

        Args:
          user(User or HttpRequest): User or request object.

        Returns:
          tethys_apps.base.TethysWorkspace: An object representing the workspace.

        **Example:**

        ::

            import os
            from .app import MyFirstApp

            def a_controller(request):
                \"""
                Example controller that uses get_user_workspace() method.
                \"""
                # Retrieve the workspace
                user_workspace = MyFirstApp.get_user_workspace(request.user)
                new_file_path = os.path.join(user_workspace.path, 'new_file.txt')

                with open(new_file_path, 'w') as a_file:
                    a_file.write('...')

                context = {}

                return render(request, 'my_first_app/template.html', context)

        """
        username = ''

        from django.contrib.auth.models import User
        if isinstance(user, User) or isinstance(user, SimpleLazyObject):
            username = user.username
        elif isinstance(user, HttpRequest):
            username = user.user.username
        elif user is None:
            pass
        else:
            raise ValueError("Invalid type for argument 'user': must be either an User or HttpRequest object.")

        if not username:
            username = 'anonymous_user'

        project_directory = os.path.dirname(sys.modules[cls.__module__].__file__)
        workspace_directory = os.path.join(project_directory, 'workspaces', 'user_workspaces', username)
        return TethysWorkspace(workspace_directory)

    @classmethod
    def get_app_workspace(cls):
        """
        Get the file workspace (directory) for the app.

        Returns:
          tethys_apps.base.TethysWorkspace: An object representing the workspace.

        **Example:**

        ::

            import os
            from .app import MyFirstApp

            def a_controller(request):
                \"""
                Example controller that uses get_app_workspace() method.
                \"""
                # Retrieve the workspace
                app_workspace = MyFirstApp.get_app_workspace()
                new_file_path = os.path.join(app_workspace.path, 'new_file.txt')

                with open(new_file_path, 'w') as a_file:
                    a_file.write('...')

                context = {}

                return render(request, 'my_first_app/template.html', context)

        """
        # Find the path to the app project directory
        ## Hint: cls is a child class of this class.
        ## Credits: http://stackoverflow.com/questions/4006102/is-possible-to-know-the-_path-of-the-file-of-a-subclass-in-python
        project_directory = os.path.dirname(sys.modules[cls.__module__].__file__)
        workspace_directory = os.path.join(project_directory, 'workspaces', 'app_workspace')
        return TethysWorkspace(workspace_directory)

    @classmethod
    def get_persistent_store_engine(cls, persistent_store_name):
        """
        Creates an SQLAlchemy engine object for the app and persistent store given.

        Args:
          persistent_store_name(string): Name of the persistent store for which to retrieve the engine.

        Returns:
          object: An SQLAlchemy engine object for the persistent store requested.


        **Example:**

        ::

            from .app import MyFirstApp

            engine = MyFirstApp.get_persistent_store_engine('example_db')

        """
        # Create the unique store name
        app_name = cls.package
        unique_store_name = '_'.join([app_name, persistent_store_name])

        # Get database manager
        database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']
        database_manager_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager',
                                                                         database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
                                                                         database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
                                                                         database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
                                                                         database_manager_db['NAME'] if 'NAME' in database_manager_db else 'tethys_db_manager')

        # Create connection engine
        engine = create_engine(database_manager_url)
        connection = engine.connect()

        # Check for Database
        existing_dbs_statement = '''
                                 SELECT d.datname as name
                                 FROM pg_catalog.pg_database d
                                 LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
                                 ORDER BY 1;
                                 '''

        existing_dbs = connection.execute(existing_dbs_statement)

        # Compile list of db names
        existing_db_names = []

        for existing_db in existing_dbs:
            existing_db_names.append(existing_db.name)

        # Check to make sure that the persistent store exists
        if unique_store_name in existing_db_names:
            # Retrieve the database manager url.
            # The database manager database user is the owner of all the app databases.
            database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']

            # Assemble url for persistent store with that name
            persistent_store_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager',
                                                                             database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
                                                                             database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
                                                                             database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
                                                                             unique_store_name)

            # Return SQLAlchemy Engine
            return create_engine(persistent_store_url)

        else:
            print('WARNING: No persistent store "{0}" for app "{1}". Make sure you register the persistent store in app.py '
                  'and run "tethys syncstores {1}".'.format(persistent_store_name, app_name))
            return None

    @classmethod
    def create_persistent_store(cls, persistent_store_name, spatial=False):
        """
        Creates a new persistent store database for this app.

        Args:
          persistent_store_name(string): Name of the persistent store that will be created.
          spatial(bool): Enable spatial extension on the database being created.

        Returns:
          bool: True if successful.


        **Example:**

        ::

            from .app import MyFirstApp

            result = MyFirstApp.create_persistent_store('example_db')

            if result:
                engine = MyFirstApp.get_persistent_store_engine('example_db')

        """
        # Get database manager url from the config
        database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']
        database_manager_name = database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager'

        database_manager_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            database_manager_name,
            database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
            database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
            database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
            database_manager_db['NAME'] if 'NAME' in database_manager_db else 'tethys_db_manager'
        )

        # Compose db name
        full_db_name = '_'.join((cls.package, persistent_store_name))
        engine = create_engine(database_manager_url)

        if cls.persistent_store_exists(persistent_store_name):
            raise NameError('Database with name "{0}" for app "{1}" already exists.'.format(
                persistent_store_name,
                cls.package
            ))

        # Cannot create databases in a transaction: connect and commit to close transaction
        create_connection = engine.connect()

        # Create db
        create_db_statement = '''
                              CREATE DATABASE {0}
                              WITH OWNER {1}
                              TEMPLATE template0
                              ENCODING 'UTF8'
                              '''.format(full_db_name, database_manager_name)

        # Close transaction first and then execute
        create_connection.execute('commit')
        create_connection.execute(create_db_statement)
        create_connection.close()

        # Enable PostGIS extension
        if spatial:
            # Get URL for Tethys Superuser to enable extensions
            super_db = settings.TETHYS_DATABASES['tethys_super']

            new_db_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
                super_db['USER'] if 'USER' in super_db else 'tethys_super',
                super_db['PASSWORD'] if 'PASSWORD' in super_db else 'pass',
                super_db['HOST'] if 'HOST' in super_db else '127.0.0.1',
                super_db['PORT'] if 'PORT' in super_db else '5435',
                full_db_name
            )

            # Connect to new database
            new_db_engine = create_engine(new_db_url)
            new_db_connection = new_db_engine.connect()

            # Notify user
            enable_postgis_statement = 'CREATE EXTENSION IF NOT EXISTS postgis'

            # Execute postgis statement
            new_db_connection.execute(enable_postgis_statement)
            new_db_connection.close()

        return True

    @classmethod
    def list_persistent_stores(cls):
        """
        Returns a list of existing persistent stores for this app.

        Returns:
          list: A list of persistent store names.


        **Example:**

        ::

            from .app import MyFirstApp

            persistent_stores = MyFirstApp.list_persistent_stores()

        """
        # Get database manager url from the config
        database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']
        database_manager_name = database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager'

        database_manager_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            database_manager_name,
            database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
            database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
            database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
            database_manager_db['NAME'] if 'NAME' in database_manager_db else 'tethys_db_manager'
        )

        # Check conflicting database with name
        engine = create_engine(database_manager_url)

        # Cannot create databases in a transaction: connect and commit to close transaction
        connection = engine.connect()

        existing_dbs_statement = "SELECT d.datname as name " \
                                 "FROM pg_catalog.pg_database d " \
                                 "LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid " \
                                 "WHERE d.datname LIKE '" + cls.package + "_%%' " \
                                 "ORDER BY 1;"

        existing_dbs = connection.execute(existing_dbs_statement)
        connection.close()

        persistent_stores = []
        for existing_db in existing_dbs:
            persistent_stores.append(existing_db.name.replace(cls.package + '_', ''))

        return persistent_stores

    @classmethod
    def persistent_store_exists(cls, persistent_store_name):
        """
        Returns True if a persistent store with the given name exists for this app.

        Args:
          persistent_store_name(string): Name of the persistent store that will be created.

        Returns:
          bool: True if persistent store exists.


        **Example:**

        ::

            from .app import MyFirstApp

            result = MyFirstApp.persistent_store_exists('example_db')

            if result:
                engine = MyFirstApp.get_persistent_store_engine('example_db')

        """
        # Get database manager url from the config
        database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']
        database_manager_name = database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager'

        database_manager_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            database_manager_name,
            database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
            database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
            database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
            database_manager_db['NAME'] if 'NAME' in database_manager_db else 'tethys_db_manager'
        )

        # Compose db name
        full_db_name = '_'.join((cls.package, persistent_store_name))
        engine = create_engine(database_manager_url)

        # Cannot create databases in a transaction: connect and commit to close transaction
        connection = engine.connect()

        existing_dbs_statement = "SELECT d.datname as name " \
                                 "FROM pg_catalog.pg_database d " \
                                 "LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid " \
                                 "WHERE d.datname = '{0}';".format(full_db_name)

        existing_dbs = connection.execute(existing_dbs_statement)
        connection.close()

        for existing_db in existing_dbs:
            if existing_db.name == full_db_name:
                return True

        return False
