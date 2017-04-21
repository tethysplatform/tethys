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
from django.core.exceptions import ObjectDoesNotExist

from tethys_apps.base.workspace import TethysWorkspace
from tethys_apps.base.handoff import HandoffManager
from tethys_apps.exceptions import TethysAppSettingDoesNotExist, TethysAppSettingNotAssigned


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
      tag [string]: A string for filtering apps.
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
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def __unicode__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

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

            from tethys_sdk.base import url_map_maker

            def url_maps(self):
                \"""
                Example url_maps method.
                \"""
                # Create UrlMap class that is bound to the root url.
                UrlMap = url_map_maker(self.root_url)

                url_maps = (UrlMap(name='home',
                                   url='my-first-app',
                                   controller='my_first_app.controllers.home',
                                   ),
                )

                return url_maps
        """
        raise NotImplementedError()

    def custom_settings(self):
        """
        Use this method to define custom settings for use in your app.

        Returns:
          iterable: A list or tuple of ``CustomTethysAppSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import CustomTethysAppSetting

            def custom_settings(self):
                \"""
                Example custom_settings method.
                \"""
                custom_settings = (
                    CustomTethysAppSetting(
                           name='example',
                           description='custom setting for this app.',
                           required=True,
                    ),
                )

                return custom_settings
        """
        return None

    def persistent_store_settings(self):
        """
        Define this method to define a persistent store service connections for your app.

        Returns:
          iterable: A list or tuple of ``PersistentStoreServiceSettings`` objects. A persistent store database will be created for each object returned.

        **Example:**

        ::

            from tethys_sdk.settings import PersistentStoreServiceSetting

            def persistent_stores(self):
                \"""
                Example persistent_store_service_settings method.
                \"""

                stores = (
                    PersistentStoreServiceSetting(
                        name='example_ps_service',
                        description='',
                        engine='postgres',
                        required=True
                    ),
                )

                return stores
        """
        #TODO: REDO THIS DOCUMENTATION
        return None

    def dataset_services_settings(self):
        """
        Use this method to define dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``DatasetServiceSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.settings import DatasetServiceSetting
            def dataset_services_settings(self):
                \"""
                Example dataset_services_settings method.
                \"""
                dataset_services_settings = (
                    DatasetServiceSetting(
                        name='example',
                        description='dataset service for app to use',
                        engine='ckan',
                        required=True,
                    ),
                )

                return dataset_services_settings
        """
        return None

    def spatial_dataset_services_settings(self):
        """
        Use this method to define spatial dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``SpatialDatasetServiceSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.settings import SpatialDatasetServiceSetting
            def spatial_dataset_services_settings(self):
                \"""
                Example spatial_dataset_services_settings method.
                \"""
                spatial_dataset_services_settings = (
                    SpatialDatasetServiceSetting(
                        name='example',
                        description='spatial dataset service for app to use',
                        engine='geoserver',
                        required=True,
                    ),
                )

                return spatial_dataset_services_settings
        """
        return None

    def wps_services_settings(self):
        """
        Use this method to define web processing service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``WpsService`` objects.

        **Example:**

        ::

            from tethys_sdk.settings import WebProcessingServiceSetting
            def wps_services(self):
                \"""
                Example wps_services method.
                \"""
                wps_services = (
                    WebProcessingServiceSetting(
                        name='example',
                        description='WPS service for app to use',
                        required=True,
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

            from tethys_sdk.handoff import HandoffHandler

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

    def permissions(self):
        """
        Use this method to define permissions for your app.

        Returns:
          iterable: A list or tuple of ``Permission`` or ``PermissionGroup`` objects.

        **Example:**

        ::

            from tethys_sdk.permissions import Permission, PermissionGroup

            def permissions(self):
                \"""
                Example permissions method.
                \"""
                # Viewer Permissions
                view_map = Permission(
                    name='view_map',
                    description='View map'
                )

                delete_projects = Permission(
                    name='delete_projects',
                    description='Delete projects'
                )

                create_projects = Permission(
                    name='create_projects',
                    description='Create projects'
                )

                admin = PermissionGroup(
                    name='admin',
                    permissions=(delete_projects, create_projects)
                )


                permissions = (admin, view_map)

                return permissions
        """
        return None

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
    def get_handoff_manager(cls):
        """
        Get the handoff manager for the app.
        """
        app = cls()
        handoff_manager = HandoffManager(app)
        return handoff_manager



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
    def get_custom_setting(cls, name):
        """
        Retrieves general for app
        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        custom_settings = db_app.custom_settings
        try:
            custom_setting = custom_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('CustomTethysAppSetting named "{0}" does not exist.'.format(name))

        return custom_setting.value

    @classmethod
    def get_dataset_service(cls, name, request=None, as_endpoint=False,
                            as_engine=False):
        """
        Retrieves dataset engine for app
        """
        from tethys_apps.models import TethysApp
        app = cls()
        db_app = TethysApp.objects.get(package=app.package)
        dataset_services_settings = db_app.dataset_services_settings
        try:
            dataset_services_settings = dataset_services_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('DatasetServiceSetting named "{0}" does not exist.'.format(name))
        dataset_service = dataset_services_settings.dataset_service
        if as_endpoint:
            return dataset_service.endpoint
        elif as_engine:
            return dataset_service.get_engine(request=request)
        return dataset_service

    @classmethod
    def get_spatial_dataset_service(cls, name, as_endpoint=False, as_wms=False,
                                    as_wfs=False, as_engine=False):
        """
        Retrieves spatial dataset engine for app
        """
        from tethys_apps.models import TethysApp
        app = cls()
        db_app = TethysApp.objects.get(package=app.package)
        spatial_dataset_services_settings = db_app.spatial_dataset_services_settings
        try:
            spatial_dataset_service_setting = spatial_dataset_services_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('SpatialDatasetServiceSetting named "{0}" does not exist.'.format(name))

        spatial_dataset_service = spatial_dataset_service_setting.spatial_dataset_service
        if as_endpoint:
            return spatial_dataset_service.endpoint
        elif as_wms:
            return spatial_dataset_service.endpoint.split('/rest')[0] + '/wms'
        elif as_wfs:
            return spatial_dataset_service.endpoint.split('/rest')[0] + '/ows'
        elif as_engine:
            return spatial_dataset_service.get_engine()
        return spatial_dataset_service

    @classmethod
    def get_wps_service(cls, name, as_endpoint=False, as_engine=False):
        """
        Retrieves wps engine for app
        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        wps_services_settings = db_app.wps_services_settings
        try:
            wps_service_setting = wps_services_settings.objects.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('WebProcessingServiceSetting named "{0}" does not exist.'.format(name))
        wps_service = wps_service_setting.web_processing_service
        if as_endpoint:
            return wps_service.endpoint
        elif as_engine:
            return wps_service.get_engine()
        return wps_service

    @classmethod
    def get_persistent_store_connection(cls, name, as_url=False):
        """
        Creates an SQLAlchemy Engine or URL object for the named persistent store connection.

        Args:
          name(string): Name of the persistent store database for which to retrieve the engine.
          as_url(bool): Return SQLAlchemy URL object instead of engine object if True. Defaults to False.

        Returns:
          sqlalchemy.Engine or sqlalchemy.URL: An SQLAlchemy Engine or URL object for the persistent store requested.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            engine = app.get_persistent_store_connection('primary')
            url = app.get_persistent_store_database('primary', as_url=True

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_connection_settings = db_app.persistent_store_connection_settings

        try:
            ps_connection_setting = ps_connection_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreConnectionSetting named "{0}" does not exist.'.format(name))

        ps_connection_service = ps_connection_setting.persistent_store_service

        # Validate connection service
        if ps_connection_service is None:
            raise TethysAppSettingNotAssigned('Cannot create engine or url for PersistentStoreConnection "{0}" for app '
                                              '"{1}": no PersistentStoreService assigned.'.format(name, db_app.package))

        if as_url:
            return ps_connection_service.get_url()

        # Return SQLAlchemy Engine
        return ps_connection_service.get_engine()

    @classmethod
    def get_persistent_store_database(cls, name, as_url=False):
        """
        Creates an SQLAlchemy Engine or URL object for the app and persistent store given.

        Args:
          name(string): Name of the persistent store database for which to retrieve the engine.
          as_url(bool): Return SQLAlchemy URL object instead of engine object if True. Defaults to False.

        Returns:
          sqlalchemy.Engine or sqlalchemy.URL: An SQLAlchemy Engine or URL object for the persistent store requested.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            engine = app.get_persistent_store_database('example_db')
            url = app.get_persistent_store_database('example_db', as_url=True)

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings
        try:
            ps_database_setting = ps_database_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreDatabaseSetting named "{0}" does not exist.'.format(name))

        # Get the assigned connection setting
        ps_connection_service = ps_database_setting.persistent_store_service

        # Validate connection service
        if ps_connection_service is None:
            raise TethysAppSettingNotAssigned('Cannot create engine or url for PersistentStoreDatabase "{0}" for app '
                                              '"{1}": no PersistentStoreService found.'.format(name, db_app.package))

        # If testing environment, the engine for the "test" version of the persistent store should be fetched
        if hasattr(settings, 'TESTING') and settings.TESTING:
            name = 'test_{0}'.format(name)

        # Derive the unique store name
        unique_store_name = '_'.join([db_app.package, name])

        # Add database (only temporary, not persisted on connection service object)
        ps_connection_service.database = unique_store_name

        if as_url:
            return ps_connection_service.get_url()

        # Return SQLAlchemy Engine
        return ps_connection_service.get_engine()

    @classmethod
    def create_persistent_store(cls, db_name, connection_name, spatial=False):
        """
        Creates a new persistent store database for this app.

        Args:
          db_name(string): Name of the persistent store that will be created.
          connection_name(string): Name of persistent store connection.
          spatial(bool): Enable spatial extension on the database being created.

        Returns:
          bool: True if successful.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            result = app.create_persistent_store('example_db', 'primary')

            if result:
                engine = app.get_persistent_store_engine('example_db')

        """
        # Validate
        if cls.persistent_store_exists(db_name):
            raise NameError('Database with name "{0}" for app "{1}" already exists.'.format(
                db_name,
                cls.package
            ))
            return False

        # Get named persistent store service connection
        from tethys_apps.models import TethysApp
        from tethys_apps.models import PersistentStoreDatabaseSetting
        db_app = TethysApp.objects.get(package=cls.package)

        # Get connection service
        ps_connection_settings = db_app.persistent_store_connection_settings

        try:
            ps_connection_setting = ps_connection_settings.get(name=connection_name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist(
                'PersistentStoreConnectionSetting named "{0}" does not exist.'.format(connection_name))

        ps_connection_service = ps_connection_setting.persistent_store_service

        # Create new PersistentStoreDatabaseSetting
        new_db_setting = PersistentStoreDatabaseSetting(
            name=db_name,
            description='',
            required=True,
            initializer='',
            spatial=spatial
        )

        new_db_setting.persistent_store_service = ps_connection_service
        db_app.add_settings((new_db_setting,))

        # Compose full name spaced db name
        full_db_name = '_'.join((db_app.package, db_name))

        # Get engine for new database
        engine = ps_connection_service.get_engine()

        # Cannot create databases in a transaction: connect and commit to close transaction
        create_connection = engine.connect()

        # Create db
        # TODO: Can I create spatial using a template?
        # Options are:
        # 1. Use CREATE EXTENSION on existing database - requires superuser
        #    Problem: all spatial databases would be required to have superuser connections = vulnerability
        #    Possible Solution: still require super user in settings.py and use this user for creating stores
        #                       access to the store would be dictated by the connection specified when created
        # 2. Use a template that has postgis extension enabled - superuser not required
        #    Problem: no default postgis template is provided, needs to be provided in database, requiring special
        #             setup of databases used by persistent stores. Template db cannot be connected to.
        #    Possible Solution: Provide template in Docker and/or provide instructions for preparing database for
        #                       use as persistent store. Maybe provide script that creates template?
        create_db_statement = """
                              CREATE DATABASE {0}
                              WITH OWNER {1}
                              TEMPLATE template0
                              ENCODING 'UTF8'
                              """.format(full_db_name, engine.url.username)

        # Close transaction first by committing and then execute statement
        create_connection.execute('commit')
        create_connection.execute(create_db_statement)
        create_connection.close()

        # Enable PostGIS extension
        if spatial:
            # Connect to new database
            ps_connection_service.database = full_db_name
            extension_engine = ps_connection_service.get_engine()
            extension_connection = extension_engine.connect()

            # Notify user
            enable_postgis_statement = 'CREATE EXTENSION IF NOT EXISTS postgis'

            # Execute postgis statement
            extension_connection.execute(enable_postgis_statement)
            extension_connection.close()

        # Save database entry
        db_app.save()

        return True

    @classmethod
    def destroy_persistent_store(cls, name):
        """
        Destroys (drops) a persistent store database from this app.

        Args:
          name(string): Name of the persistent store that will be created.

        Returns:
          bool: True if successful.


        **Example:**

        ::

            from .app import MyFirstApp

            result = MyFirstApp.destroy_persistent_store('example_db')

            if result:
                # App database 'example_db' was successfuly destroyed and no longer exists
                pass

        """
        if not cls.persistent_store_exists(name):
            raise NameError('Database with name "{0}" for app "{1}" does not exists.'.format(
                name,
                cls.package
            ))

        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings
        try:
            ps_database_setting = ps_database_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist(
                'PersistentStoreDatabaseSetting named "{0}" does not exist.'.format(name))

        # Get the assigned connection setting
        ps_connection_service = ps_database_setting.persistent_store_service

        # Validate connection service
        if ps_connection_service is None:
            raise TethysAppSettingNotAssigned('Cannot create engine or url for PersistentStoreDatabase "{0}" for app '
                                              '"{1}": no PersistentStoreService found.'.format(name, db_app.package))

        # Compose db name
        full_db_name = '_'.join((db_app.package, name))

        # Create db engine
        engine = ps_connection_service.get_engine()

        # Create db
        drop_db_statement = 'DROP DATABASE IF EXISTS {0}'.format(full_db_name)

        # Connection variable
        drop_connection = None

        try:
            drop_connection = engine.connect()
            drop_connection.execute('commit')
            drop_connection.execute(drop_db_statement)
        except Exception as e:
            if 'being accessed by other users' in str(e):

                # Force disconnect all other connections to the database
                disconnect_sessions_statement = '''
                                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                FROM pg_stat_activity
                                                WHERE pg_stat_activity.datname = '{0}'
                                                AND pg_stat_activity.pid <> pg_backend_pid();
                                                '''.format(full_db_name)
                drop_connection.execute(disconnect_sessions_statement)

                # Try again to drop the databse
                drop_connection.execute('commit')
                drop_connection.execute(drop_db_statement)
                drop_connection.close()
            else:
                raise e
        finally:
            drop_connection.close()

        # Remove the database setting
        ps_database_setting.delete()

        return True

    @classmethod
    def list_persistent_store_databases(cls):
        """
        Returns a list of existing persistent store databases for this app.

        Returns:
          list: A list of persistent store database names.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            ps_databases = app.list_persistent_store_databases()

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings
        return [ps_database_setting.name for ps_database_setting in ps_database_settings]

    @classmethod
    def list_persistent_store_connections(cls):
        """
        Returns a list of existing persistent store connections for this app.

        Returns:
          list: A list of persistent store connection names.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            ps_connections = app.list_persistent_store_connections()

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_connection_settings = db_app.persistent_store_connection_settings
        return [ps_connection_setting.name for ps_connection_setting in ps_connection_settings]

    @classmethod
    def persistent_store_exists(cls, name):
        """
        Returns True if a persistent store with the given name exists for this app.

        Args:
          name(string): Name of the persistent store that will be created.

        Returns:
          bool: True if persistent store exists.


        **Example:**

        ::

            from .app import MyFirstApp

            result = MyFirstApp.persistent_store_exists('example_db')

            if result:
                engine = MyFirstApp.get_persistent_store_engine('example_db')

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings
        try:
            # If it exists return True
            ps_database_setting = ps_database_settings.get(name=name)
        except ObjectDoesNotExist:
            # Else return False
            return False

        # Get the assigned connection setting
        ps_connection_service = ps_database_setting.persistent_store_service

        # Validate connection service
        if ps_connection_service is None:
            raise TethysAppSettingNotAssigned(
                'Cannot create engine or url for PersistentStoreDatabase "{0}" for app '
                '"{1}": no PersistentStoreService found.'.format(name, db_app.package))

        # Database setting existing doesn't mean the database exists necessarily,
        # Attempt to connect to database to verify that it exists.
        # Derive the unique store name
        unique_store_name = '_'.join([db_app.package, name])

        # Add database (only temporary, not persisted on connection service object)
        ps_connection_service.database = unique_store_name

        # Get engine
        engine = ps_connection_service.get_engine()

        try:

            # Attempt to connect
            connection = engine.connect()

        except Exception:
            # Orphaned connection, can be caused by database being deleted but corresponding setting not being deleted.
            # Remove orphaned db setting entries
            ps_database_setting.delete()
            return False

        # Able to connect means it exists in db
        connection.close()
        return True
