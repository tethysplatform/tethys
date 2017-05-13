"""
********************************************************************************
* Name: app_base.py
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""
import logging
import os
import sys

from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject
from django.core.exceptions import ObjectDoesNotExist
from sqlalchemy.orm import sessionmaker

from tethys_apps.base.workspace import TethysWorkspace
from tethys_apps.base.handoff import HandoffManager
from tethys_apps.exceptions import (TethysAppSettingDoesNotExist,
                                    TethysAppSettingNotAssigned)

tethys_log = logging.getLogger('tethys.app_base')

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
      tag (string): A string for filtering apps.
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

    _session_maker = sessionmaker()

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
        Override this method to define the URL Maps for your app. Your ``UrlMap`` objects must be created from a ``UrlMap`` class that is bound to the ``root_url`` of your app. Use the ``url_map_maker()`` function to create the bound ``UrlMap`` class. If you generate your app project from the scaffold, this will be done automatically.

        Returns:
          iterable: A list or tuple of ``UrlMap`` objects.

        **Example:**

        ::

            from tethys_sdk.base import url_map_maker

            class MyFirstApp(TethysAppBase):

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

    # TODO: ADD SETTING LINK TO TOP OF APP WHEN LOGGED IN AS STAFF
    def custom_settings(self):
        """
        Override this method to define custom settings for use in your app.

        Returns:
          iterable: A list or tuple of ``CustomSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import CustomSetting

            class MyFirstApp(TethysAppBase):

                def custom_settings(self):
                    \"""
                    Example custom_settings method.
                    \"""
                    custom_settings = (
                        CustomSetting(
                            name='default_name',
                            type=CustomSetting.TYPE_STRING
                            description='Default model name.',
                            required=True
                        ),
                        CustomSetting(
                            name='max_count',
                            type=CustomSetting.TYPE_INTEGER,
                            description='Maximum allowed count in a method.',
                            required=False
                        ),
                        CustomSetting(
                            name='change_factor',
                            type=CustomSetting.TYPE_FLOAT,
                            description='Change factor that is applied to some process.',
                            required=True
                        ),
                        CustomSetting(
                            name='enable_feature',
                            type=CustomSetting.TYPE_BOOLEAN,
                            description='Enable this feature when True.',
                            required=True
                        )
                    )

                    return custom_settings
        """
        return None

    def persistent_store_settings(self):
        """
        Override this method to define a persistent store service connections and databases for your app.

        Returns:
          iterable: A list or tuple of ``PersistentStoreDatabaseSetting`` or ``PersistentStoreConnectionSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, PersistentStoreConnectionSetting

            class MyFirstApp(TethysAppBase):

                def persistent_store_settings(self):
                    \"""
                    Example persistent_store_settings method.
                    \"""

                    ps_settings = (
                        # Connection only, no database
                        PersistentStoreConnectionSetting(
                            name='primary',
                            description='Connection with superuser role needed.',
                            required=True
                        ),
                        # Connection only, no database
                        PersistentStoreConnectionSetting(
                            name='creator',
                            description='Create database role only.',
                            required=False
                        ),
                        # Spatial database
                        PersistentStoreDatabaseSetting(
                            name='spatial_db',
                            description='for storing important spatial stuff',
                            required=True,
                            initializer='appsettings.model.init_spatial_db',
                            spatial=True,
                        ),
                        # Non-spatial database
                        PersistentStoreDatabaseSetting(
                            name='temp_db',
                            description='for storing temporary stuff',
                            required=False,
                            initializer='appsettings.model.init_temp_db',
                            spatial=False,
                        )
                    )

                    return ps_settings
        """
        return None

    def dataset_service_settings(self):
        """
        Override this method to define dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``DatasetServiceSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import DatasetServiceSetting

            class MyFirstApp(TethysAppBase):

                def dataset_service_settings(self):
                    \"""
                    Example dataset_service_settings method.
                    \"""
                    ds_settings = (
                        DatasetServiceSetting(
                            name='primary_ckan',
                            description='Primary CKAN service for app to use.',
                            engine=DatasetServiceSetting.CKAN,
                            required=True,
                        ),
                        DatasetServiceSetting(
                            name='hydroshare',
                            description='HydroShare service for app to use.',
                            engine=DatasetServiceSetting.HYDROSHARE,
                            required=False
                        )
                    )

                    return ds_settings
        """
        return None

    def spatial_dataset_service_settings(self):
        """
        Override this method to define spatial dataset service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``SpatialDatasetServiceSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import SpatialDatasetServiceSetting

            class MyFirstApp(TethysAppBase):

                def spatial_dataset_service_settings(self):
                    \"""
                    Example spatial_dataset_service_settings method.
                    \"""
                    sds_settings = (
                        SpatialDatasetServiceSetting(
                            name='primary_geoserver',
                            description='spatial dataset service for app to use',
                            engine=SpatialDatasetServiceSetting.GEOSERVER,
                            required=True,
                        ),
                    )

                    return sds_settings
        """
        return None

    def web_processing_service_settings(self):
        """
        Override this method to define web processing service connections for use in your app.

        Returns:
          iterable: A list or tuple of ``WebProcessingServiceSetting`` objects.

        **Example:**

        ::

            from tethys_sdk.app_settings import WebProcessingServiceSetting

            class MyFirstApp(TethysAppBase):

                def web_processing_service_settings(self):
                    \"""
                    Example wps_services method.
                    \"""
                    wps_services = (
                        WebProcessingServiceSetting(
                            name='primary_52n',
                            description='WPS service for app to use',
                            required=True,
                        ),
                    )

                    return wps_services
        """
        return None

    def handoff_handlers(self):
        """
        Override this method to define handoff handlers for use in your app.

        Returns:
          iterable: A list or tuple of ``HandoffHandler`` objects.

        **Example:**

        ::

            from tethys_sdk.handoff import HandoffHandler

            class MyFirstApp(TethysAppBase):

                def handoff_handlers(self):
                    \"""
                    Example handoff_handlers method.
                    \"""
                    handoff_handlers = (
                        HandoffHandlers(
                            name='example',
                            handler='my_first_app.controllers.my_handler'
                        ),
                    )

                    return handoff_handlers
        """
        return None

    def permissions(self):
        """
        Override this method to define permissions for your app.

        Returns:
          iterable: A list or tuple of ``Permission`` or ``PermissionGroup`` objects.

        **Example:**

        ::

            from tethys_sdk.permissions import Permission, PermissionGroup

            class MyFirstApp(TethysAppBase):

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
        Override this method to define job templates to easily create and submit jobs in your app.

        Returns:
            iterable: A list or tuple of ``JobTemplate`` objects.

        **Example:**

        ::

            from tethys_sdk.jobs import CondorJobTemplate
            from tethys_sdk.compute import list_schedulers

            class MyFirstApp(TethysAppBase):

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
        Get the HandoffManager for the app.
        """
        app = cls()
        handoff_manager = HandoffManager(app)
        return handoff_manager

    @classmethod
    def get_job_manager(cls):
        """
        Get the JobManager for the app.
        """
        from tethys_sdk.jobs import JobManager
        app = cls()
        job_manager = JobManager(app)
        return job_manager

    @classmethod
    def get_user_workspace(cls, user):
        """
        Get the file workspace (directory) for the given User.

        Args:
          user(User or HttpRequest): User or request object.

        Returns:
          tethys_apps.base.TethysWorkspace: An object representing the workspace.

        **Example:**

        ::

            import os
            from my_first_app.app import MyFirstApp as app

            def a_controller(request):
                \"""
                Example controller that uses get_user_workspace() method.
                \"""
                # Retrieve the workspace
                user_workspace = app.get_user_workspace(request.user)
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
            from my_first_app.app import MyFirstApp as app

            def a_controller(request):
                \"""
                Example controller that uses get_app_workspace() method.
                \"""
                # Retrieve the workspace
                app_workspace = app.get_app_workspace()
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
        Retrieves the value of a CustomSetting for the app.

        Args:
            name(str): The name of the CustomSetting as defined in the app.py.

        Returns:
            variable: Value of the CustomSetting or None if no value assigned.

        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            max_count = app.get_custom_setting('max_count')

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        custom_settings = db_app.custom_settings
        try:
            custom_setting = custom_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('CustomTethysAppSetting named "{0}" does not exist.'.format(name))

        return custom_setting.get_value()

    @classmethod
    def get_dataset_service(cls, name, as_public_endpoint=False, as_endpoint=False,
                            as_engine=False):
        """
        Retrieves dataset service engine assigned to named DatasetServiceSetting for the app.

        Args:
            name(str): name fo the DatasetServiceSetting as defined in the app.py.
            as_endpoint(bool): Returns endpoint url string if True, Defaults to False.
            as_public_endpoint(bool): Returns public endpoint url string if True. Defaults to False.
            as_engine(bool): Returns tethys_dataset_services.engine of appropriate type if True. Defaults to False.

        Returns:
            DatasetService: DatasetService assigned to setting if no other options are specified.

        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            ckan_engine = app.get_dataset_service('primary_ckan', as_engine=True)

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

        if not dataset_service:
            return None
        elif as_engine:
            return dataset_service.get_engine()
        elif as_endpoint:
            return dataset_service.endpoint
        elif as_public_endpoint:
            return dataset_service.public_endpoint
        return dataset_service

    @classmethod
    def get_spatial_dataset_service(cls, name, as_public_endpoint=False, as_endpoint=False, as_wms=False,
                                    as_wfs=False, as_engine=False):
        """
        Retrieves spatial dataset service engine assigned to named SpatialDatasetServiceSetting for the app.

        Args:
            name(str): name fo the SpatialDatasetServiceSetting as defined in the app.py.
            as_endpoint(bool): Returns endpoint url string if True, Defaults to False.
            as_public_endpoint(bool): Returns public endpoint url string if True. Defaults to False.
            as_wfs(bool): Returns OGC-WFS enpdoint url for spatial dataset service if True. Defaults to False.
            as_wms(bool): Returns OGC-WMS enpdoint url for spatial dataset service if True. Defaults to False.
            as_engine(bool): Returns tethys_dataset_services.engine of appropriate type if True. Defaults to False.

        Returns:
            SpatialDatasetService: SpatialDatasetService assigned to setting if no other options are specified.

        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            geoserver_engine = app.get_spatial_dataset_engine('primary_geoserver', as_engine=True)

        """
        from tethys_apps.models import TethysApp
        app = cls()
        db_app = TethysApp.objects.get(package=app.package)
        spatial_dataset_service_settings = db_app.spatial_dataset_service_settings

        try:
            spatial_dataset_service_setting = spatial_dataset_service_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('SpatialDatasetServiceSetting named "{0}" does not exist.'.format(name))

        spatial_dataset_service = spatial_dataset_service_setting.spatial_dataset_service

        if not spatial_dataset_service:
            return None
        elif as_engine:
            return spatial_dataset_service.get_engine()
        elif as_wms:
            return spatial_dataset_service.endpoint.split('/rest')[0] + '/wms'
        elif as_wfs:
            return spatial_dataset_service.endpoint.split('/rest')[0] + '/ows'
        elif as_endpoint:
            return spatial_dataset_service.endpoint
        elif as_public_endpoint:
            return spatial_dataset_service.public_endpoint
        return spatial_dataset_service

    @classmethod
    def get_web_processing_service(cls, name, as_public_endpoint=False, as_endpoint=False, as_engine=False):
        """
        Retrieves web processing service engine assigned to named WebProcessingServiceSetting for the app.

        Args:
            name(str): name fo the WebProcessingServiceSetting as defined in the app.py.
            as_endpoint(bool): Returns endpoint url string if True, Defaults to False.
            as_public_endpoint(bool): Returns public endpoint url string if True. Defaults to False.
            as_engine(bool): Returns owslib.wps.WebProcessingService engine if True. Defaults to False.

        Returns:
            WpsService: WpsService assigned to setting if no other options are specified.

        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            wps_engine = app.get_web_processing_service('primary_52n')

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        wps_services_settings = db_app.wps_services_settings
        try:
            wps_service_setting = wps_services_settings.objects.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('WebProcessingServiceSetting named "{0}" does not exist.'.format(name))
        wps_service = wps_service_setting.web_processing_service

        if not wps_service:
            return None
        elif as_engine:
            return wps_service.get_engine()
        elif as_endpoint:
            return wps_service.endpoint
        elif as_public_endpoint:
            return wps_service.pubic_endpoint
        return wps_service

    @classmethod
    def get_persistent_store_connection(cls, name, as_url=False, as_sessionmaker=False):
        """
        Gets an SQLAlchemy Engine or URL object for the named persistent store connection.

        Args:
          name(string): Name of the PersistentStoreConnectionSetting as defined in app.py.
          as_url(bool): Return SQLAlchemy URL object instead of engine object if True. Defaults to False.
          as_sessionmaker(bool): Returns SessionMaker class bound to the engine if True.  Defaults to False.

        Returns:
          sqlalchemy.Engine or sqlalchemy.URL: An SQLAlchemy Engine or URL object for the persistent store requested.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            conn_engine = app.get_persistent_store_connection('primary')
            conn_url = app.get_persistent_store_connection('primary', as_url=True)
            SessionMaker = app.get_persistent_store_database('primary', as_sessionmaker=True)
            session = SessionMaker()

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_connection_settings = db_app.persistent_store_connection_settings

        try:
            ps_connection_setting = ps_connection_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreConnectionSetting named "{0}" does not exist.'.format(name))

        return ps_connection_setting.get_engine(as_url=as_url, as_sessionmaker=as_sessionmaker)

    @classmethod
    def get_persistent_store_database(cls, name, as_url=False, as_sessionmaker=False):
        """
        Gets an SQLAlchemy Engine or URL object for the named persistent store database given.

        Args:
          name(string): Name of the PersistentStoreConnectionSetting as defined in app.py.
          as_url(bool): Return SQLAlchemy URL object instead of engine object if True. Defaults to False.
          as_sessionmaker(bool): Returns SessionMaker class bound to the engine if True.  Defaults to False.

        Returns:
          sqlalchemy.Engine or sqlalchemy.URL: An SQLAlchemy Engine or URL object for the persistent store requested.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            db_engine = app.get_persistent_store_database('example_db')
            db_url = app.get_persistent_store_database('example_db', as_url=True)
            SessionMaker = app.get_persistent_store_database('example_db', as_sessionmaker=True)
            session = SessionMaker()

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings
        try:
            ps_database_setting = ps_database_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreDatabaseSetting named "{0}" does not exist.'.format(name))

        return ps_database_setting.get_engine(as_url=as_url, as_sessionmaker=as_sessionmaker)

    @classmethod
    def get_session(cls, name):
        """
        Gets an SQLAlchemy session object for the named persistent store database given.

        Args:
          name(string): Name of the PersistentStoreConnectionSetting as defined in app.py.

        Returns:
          sqlalchemy.sessionmaker: An SQLAlchemy sessionmaker object for the persistent store requested.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            SessionMaker = app.get_session('example_db')
        """
        cls._session_maker.configure(bind=cls.get_persistent_store_database(name))
        return cls._session_maker()

    @classmethod
    def create_persistent_store(cls, db_name, connection_name, spatial=False, initializer='', refresh=False,
                                force_first_time=False):
        """
        Creates a new persistent store database for the app. This method is idempotent.

        Args:
          db_name(string): Name of the persistent store that will be created.
          connection_name(string): Name of persistent store connection.
          spatial(bool): Enable spatial extension on the database being created when True. Connection must have superuser role. Defaults to False.
          initializer(string): Dot-notation path to initializer function (e.g.: 'my_first_app.models.init_db').
          refresh(bool): Drop database if it exists and create again when True. Defaults to False.
          force_first_time(bool): Call initializer function with "first_time" parameter forced to True, even if this is not the first time intializing the persistent store database. Defaults to False.

        Returns:
          bool: True if successful.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            result = app.create_persistent_store('example_db', 'primary')

            if result:
                engine = app.get_persistent_store_engine('example_db')

        """
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

        ps_service = ps_connection_setting.persistent_store_service

        # Check if persistent store database setting already exists before creating it
        try:
            db_setting = db_app.persistent_store_database_settings.get(name=db_name)
            db_setting.persistent_store_service = ps_service
            db_setting.initializer = initializer
            db_setting.save()
        except ObjectDoesNotExist:
            # Create new PersistentStoreDatabaseSetting
            db_setting = PersistentStoreDatabaseSetting(
                name=db_name,
                description='',
                required=False,
                initializer=initializer,
                spatial=spatial,
                dynamic=True
            )

            # Assign the connection service
            db_setting.persistent_store_service = ps_service
            db_app.add_settings((db_setting,))

            # Save database entry
            db_app.save()

        # Create the new database
        db_setting.create_persistent_store_database(refresh=refresh, force_first_time=force_first_time)
        return True

    @classmethod
    def drop_persistent_store(cls, name):
        """
        Drop a persistent store database for the app. This method is idempotent.

        Args:
          name(string): Name of the persistent store to be dropped.

        Returns:
          bool: True if successful.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            result = app.drop_persistent_store('example_db')

            if result:
                # App database 'example_db' was successfully destroyed and no longer exists
                pass

        """
        # Get the setting
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings

        try:
            ps_database_setting = ps_database_settings.get(name=name)
        except ObjectDoesNotExist:
            return True

        # Drop the persistent store
        ps_database_setting.drop_persistent_store_database()

        # Remove the database setting
        ps_database_setting.delete()
        return True

    @classmethod
    def list_persistent_store_databases(cls, dynamic_only=False, static_only=False):
        """
        Returns a list of existing persistent store databases for the app.

        Args:
            dynamic_only(bool): only persistent store created dynamically if True. Defaults to False.
            static_only(bool): only static persistent stores if True. Defaults to False.

        Returns:
          list: A list of all persistent store database names for the app.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            ps_databases = app.list_persistent_store_databases()

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        ps_database_settings = db_app.persistent_store_database_settings

        if dynamic_only:
            ps_database_settings = ps_database_settings.filter(persistentstoredatabasesetting__dynamic=True)
        elif static_only:
            ps_database_settings = ps_database_settings.filter(persistentstoredatabasesetting__dynamic=False)
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
        Returns True if a persistent store with the given name exists for the app.

        Args:
          name(string): Name of the persistent store database to check.

        Returns:
          bool: True if persistent store exists.


        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            result = app.persistent_store_exists('example_db')

            if result:
                engine = app.get_persistent_store_engine('example_db')

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

        # Check if it exists
        ps_database_setting.persistent_store_database_exists()
        return True
