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
import traceback
import warnings
import uuid

from django.db.utils import ProgrammingError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject
from django.conf.urls import url

from tethys_apps.base.testing.environment import is_testing_environment, get_test_db_name, TESTING_DB_FLAG
from tethys_apps.base import permissions
from .handoff import HandoffManager
from .workspace import TethysWorkspace
from .mixins import TethysBaseMixin
from ..exceptions import TethysAppSettingDoesNotExist, TethysAppSettingNotAssigned

from bokeh.server.django.consumers import WSConsumer
from bokeh.server.django import autoload

from bokeh.server.django.consumers import AutoloadJsConsumer

tethys_log = logging.getLogger('tethys.app_base')


class TethysBase(TethysBaseMixin):
    """
    Abstract base class of app and extension classes.
    """
    name = ''
    package = ''
    root_url = ''
    description = ''

    def __init__(self):
        self._url_patterns = None
        self._handler_patterns = None
        self._namespace = None

    @staticmethod
    def _resolve_ref_function(ref, ref_type, is_extension):
        """
        This method retrieves a controller or handler function.

        Args:
            ref: The function of dot-formatted string path to the function
            ref_type: Handler or controller
            is_extension: Boolean. True if working with a Tethys Extension

        Returns:
            func: If the reference is a string returns the attribute value of the function.
            If the reference is a function returns the referenced function itself.

        Example:
            controller_function = self._resolve_ref_function(url_map.controller, 'controller', is_extension)
        """

        if isinstance(ref, str):
            root_controller_path = 'tethysext' if is_extension else 'tethysapp'
            full_controller_path = '.'.join([root_controller_path, ref])
            controller_parts = full_controller_path.split('.')
            module_name = '.'.join(controller_parts[:-1])
            function_name = controller_parts[-1]
            try:
                module = __import__(module_name, fromlist=[function_name])
            except Exception as e:
                error_msg = f'The following error occurred while trying to import the {ref_type} function ' \
                            f'"{ref}":\n {traceback.format_exc(2)}'
                tethys_log.error(error_msg)
                raise e
            try:
                ref_function = getattr(module, function_name)
            except AttributeError as e:
                error_msg = f'The following error occurred while trying to access the {ref_type} function ' \
                            f'"{ref}":\n {traceback.format_exc(2)}'
                tethys_log.error(error_msg)
                raise e
        else:
            ref_function = ref
        return ref_function

    def _resolve_bokeh_handler(self, namespace, url_map, handler_function, handler_patterns):
        """
        Create and add url patterns for bokeh handler

        Args:
            namespace: App name
            url_map: Mapping containing url name, controller, and handler information
            handler_function: The function returned by _resolve_ref_function
            handler_patterns: dictionary to add http and websocket patterns to

        Returns:
            None

        Example:
            self._resolve_bokeh_handler(namespace, url_map, handler_function, handler_patterns)
        """

        if url_map.url in [r'', r'/', r'^$', r'^/$']:
            app_endpoint = '/'.join(['apps', self.root_url])
        else:
            stripped_url = url_map.url.replace("^", "").replace("$", "")
            if stripped_url.endswith('/'):
                stripped_url = stripped_url[:-1]

            app_endpoint = '/'.join(['apps', self.root_url, stripped_url])
        bokeh_app = autoload(app_endpoint, handler_function)
        kwargs = dict(app_context=bokeh_app.app_context)

        def urlpattern(suffix=""):
            url_pattern = bokeh_app.url + suffix
            return f'^{url_pattern}$'

        http_url = url(urlpattern('/autoload.js'), AutoloadJsConsumer,
                       name=f'{url_map.name}_bokeh_autoload', kwargs=kwargs)
        ws_url = url(urlpattern('/ws'), WSConsumer, name=f'{url_map.name}_bokeh_ws', kwargs=kwargs)

        # Append to namespace list
        handler_patterns['http'][namespace].append(http_url)
        handler_patterns['websocket'][namespace].append(ws_url)

    def url_maps(self):
        """
        Override this method to define the URL Maps for your app. Your ``UrlMap`` objects must be created from a ``UrlMap`` class that is bound to the ``root_url`` of your app. Use the ``url_map_maker()`` function to create the bound ``UrlMap`` class. If you generate your app project from the scaffold, this will be done automatically. Starting in Tethys 3.0, the ``WebSocket`` protocol is supported along with the ``HTTP`` protocol. To create a ``WebSocket UrlMap``, follow the same pattern used for the ``HTTP`` protocol. In addition, provide a ``Consumer`` path in the controllers parameter as well as a ``WebSocket`` string value for the new protocol parameter for the ``WebSocket UrlMap``. Alternatively, Bokeh Server can also be integrated into Tethys using ``Django Channels`` and ``Websockets``. Tethys will automatically set these up for you if a ``handler`` and ``handler_type`` parameters are provided as part of the ``UrlMap``.

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

                    url_maps = (
                        UrlMap(name='home',
                            url='my-first-app',
                            controller='my_first_app.controllers.home',
                        ),
                        UrlMap(name='home_ws',
                            url='my-first-ws',
                            controller='my_first_app.controllers.HomeConsumer',
                            protocol='websocket'
                        ),
                        UrlMap(name='bokeh_handler',
                            url='my-first-app/bokeh-example',
                            controller='my_first_app.controllers.bokeh_example',
                            handler='my_first_app.controllers.bokeh_example_handler',
                            handler_type='bokeh'
                        ),
                    )

                    return url_maps
        """  # noqa: E501
        return []

    @property
    def url_patterns(self):
        """
        Generate the url pattern lists for  app and namespace them accordingly.
        """
        if self._url_patterns is None:
            is_extension = isinstance(self, TethysExtensionBase)

            url_patterns = {'http': dict(), 'websocket': dict()}

            if hasattr(self, 'url_maps'):
                url_maps = self.url_maps()

            for url_map in url_maps:
                namespace = self.namespace

                if namespace not in url_patterns[url_map.protocol]:
                    url_patterns[url_map.protocol][namespace] = []

                # Create django url object
                controller_function = self._resolve_ref_function(url_map.controller, 'controller', is_extension)
                django_url = url(url_map.url, controller_function, name=url_map.name)

                # Append to namespace list
                url_patterns[url_map.protocol][namespace].append(django_url)
            self._url_patterns = url_patterns

        return self._url_patterns

    @property
    def handler_patterns(self):
        """
        Generate the url pattern lists for  app and namespace them accordingly.
        """
        if self._handler_patterns is None:
            is_extension = isinstance(self, TethysExtensionBase)

            handler_patterns = {'http': dict(), 'websocket': dict()}

            if hasattr(self, 'url_maps'):
                url_maps = self.url_maps()

            for url_map in url_maps:
                if url_map.handler:
                    namespace = self.namespace

                    if namespace not in handler_patterns['http']:
                        handler_patterns['http'][namespace] = []

                    if namespace not in handler_patterns['websocket']:
                        handler_patterns['websocket'][namespace] = []

                    # Create django url routing objects
                    handler_function = self._resolve_ref_function(url_map.handler, 'handler', is_extension)
                    if url_map.handler_type == 'bokeh':
                        self._resolve_bokeh_handler(namespace, url_map, handler_function, handler_patterns)

            self._handler_patterns = handler_patterns

        return self._handler_patterns

    def sync_with_tethys_db(self):
        """
        Sync installed apps with database.
        """
        raise NotImplementedError

    def remove_from_db(self):
        """
        Remove the instance from the db.
        """
        raise NotImplementedError


class TethysExtensionBase(TethysBase):
    """
    Base class used to define the extension class for Tethys extensions.
    """

    def __str__(self):
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
        """  # noqa: E501
        return []

    def sync_with_tethys_db(self):
        """
        Sync installed apps with database.
        """
        from django.conf import settings
        from tethys_apps.models import TethysExtension
        try:
            # Query to see if installed extension is in the database
            db_extensions = TethysExtension.objects. \
                filter(package__exact=self.package). \
                all()

            # If the extension is not in the database, then add it
            if len(db_extensions) == 0:
                extension = TethysExtension(
                    name=self.name,
                    package=self.package,
                    description=self.description,
                    root_url=self.root_url,
                )
                extension.save()

            # If the extension is in the database, update developer-first attributes
            elif len(db_extensions) == 1:
                db_extension = db_extensions[0]
                db_extension.root_url = self.root_url
                db_extension.save()

                if hasattr(settings, 'DEBUG') and settings.DEBUG:
                    db_extension.name = self.name
                    db_extension.description = self.description
                    db_extension.save()
        except ProgrammingError:
            tethys_log.warning("Unable to sync extension with database. tethys_apps_tethysextension "
                               "table does not exist")
        except Exception as e:
            tethys_log.error(e)


class TethysAppBase(TethysBase):
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
    index = ''
    icon = ''
    color = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def __str__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

    def __repr__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

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
        """  # noqa: E501
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

    def register_app_permissions(self):
        """
        Register and sync the app permissions.
        """
        from guardian.shortcuts import assign_perm, remove_perm, get_perms
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission, Group
        from tethys_apps.models import TethysApp

        perms = self.permissions()
        # add default access_app permission
        app_permissions = {f'{self.package}:access_app': f'{self.package} | Can access app'}
        app_groups = dict()

        # Name spaced prefix for app permissions
        # e.g. my_first_app:view_things
        # e.g. my_first_app | View things
        perm_codename_prefix = self.package + ':'
        perm_name_prefix = self.package + ' | '

        if perms is not None:
            # Thing is either a Permission or a PermissionGroup object

            for thing in perms:
                # Permission Case
                if isinstance(thing, permissions.Permission):
                    # Name space the permissions and add it to the list
                    permission_codename = perm_codename_prefix + thing.name
                    permission_name = perm_name_prefix + thing.description
                    app_permissions[permission_codename] = permission_name

                # PermissionGroup Case
                elif isinstance(thing, permissions.PermissionGroup):
                    # Record in dict of groups
                    group_permissions = []
                    group_name = perm_codename_prefix + thing.name

                    for perm in thing.permissions:
                        # Name space the permissions and add it to the list
                        permission_codename = perm_codename_prefix + perm.name
                        permission_name = perm_name_prefix + perm.description
                        app_permissions[permission_codename] = permission_name
                        group_permissions.append(permission_codename)

                    # Store all groups for all apps
                    app_groups[group_name] = {'permissions': group_permissions, 'app_package': self.package}

        # Get the TethysApp content type
        tethys_content_type = ContentType.objects.get(
            app_label='tethys_apps',
            model='tethysapp'
        )

        # Remove any permissions that no longer exist
        db_app_permissions = Permission.objects.\
            filter(content_type=tethys_content_type).\
            filter(codename__icontains=perm_codename_prefix).\
            all()

        for db_app_permission in db_app_permissions:
            # Delete the permission if the permission is no longer required by this app
            if db_app_permission.codename not in app_permissions:
                db_app_permission.delete()

        # Create permissions that need to be created
        for perm in app_permissions:
            # Create permission if it doesn't exist
            try:
                # If permission exists, update it
                p = Permission.objects.get(codename=perm)

                p.name = app_permissions[perm]
                p.content_type = tethys_content_type
                p.save()

            except Permission.DoesNotExist:
                p = Permission(
                    name=app_permissions[perm],
                    codename=perm,
                    content_type=tethys_content_type
                )
                p.save()

        # Remove any groups that no longer exist
        db_groups = Group.objects.filter(name__icontains=perm_codename_prefix).all()
        db_apps = TethysApp.objects.all()
        db_app_names = [db_app.package for db_app in db_apps]

        for db_group in db_groups:
            db_group_name_parts = db_group.name.split(':')

            # Only perform maintenance on groups that belong to Tethys Apps
            if (len(db_group_name_parts) > 1) and (db_group_name_parts[0] in db_app_names):

                # Delete groups that is no longer required by this app
                if db_group.name not in app_groups:
                    db_group.delete()

        # Create groups that need to be created
        for group in app_groups:
            # Look up the app
            db_app = TethysApp.objects.get(
                package=app_groups[group]['app_package'])

            # Create group if it doesn't exist
            try:
                # If it exists, update the permissions assigned to it
                g = Group.objects.get(name=group)

                # Get the permissions for the group and remove all of them
                perms = get_perms(g, db_app)

                for p in perms:
                    remove_perm(p, g, db_app)

                # Assign the permission to the group and the app instance
                for p in app_groups[group]['permissions']:
                    assign_perm(p, g, db_app)

            except Group.DoesNotExist:
                # Create a new group
                g = Group(name=group)
                g.save()

                # Assign the permission to the group and the app instance
                for p in app_groups[group]['permissions']:
                    assign_perm(p, g, db_app)

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
        from tethys_compute.job_manager import JobManager
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
        warnings.warn('@user_workspace decorator is now the preferred method for getting user workspace', DeprecationWarning)  # noqa: E501
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
        warnings.warn('@app_workspace decorator is now the preferred method for getting app workspace', DeprecationWarning)  # noqa: E501
        # Find the path to the app project directory
        # Hint: cls is a child class of this class.
        # Credits: http://stackoverflow.com/questions/4006102/ is-possible-to-know-the-_path-of-the-file-of-a-subclass-in-python  # noqa: E501
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
            return custom_setting.get_value()
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('CustomTethysAppSetting', name, cls.name)

    @classmethod
    def set_custom_setting(cls, name, value):
        """
        Assign the value of a CustomSetting for the app.

        Args:
            name(str): The name of the CustomSetting as defined in the app.py.
            value(str/int/float/boolean/uuid.UUID): the value of the customSetting.

        **Example:**

        ::

            from my_first_app.app import MyFirstApp as app

            max_count = app.set_custom_setting('max_count', 5)

        """
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=cls.package)
        custom_settings = db_app.custom_settings
        try:
            custom_setting = custom_settings.get(name=name)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('CustomTethysAppSetting', name, cls.name)

        type_matches = False
        if custom_setting.type == 'STRING':
            type_matches = isinstance(value, str)
        elif custom_setting.type == 'INTEGER':
            type_matches = isinstance(value, int)
        elif custom_setting.type == 'FLOAT':
            type_matches = isinstance(value, float)
        elif custom_setting.type == 'BOOLEAN':
            type_matches = str(value).lower() in ['true', 'false', 'yes', 'no', 't', 'f', 'y', 'n', '1', '0']
        elif custom_setting.type == 'UUID':
            try:
                type_matches = bool(uuid.UUID(str(value)))
            except ValueError:
                pass

        if type_matches:
            custom_setting.value = value
            custom_setting.save()
        else:
            raise ValidationError(f'Value must be of type {custom_setting.type}.')

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
            dataset_services_setting = dataset_services_settings.get(name=name)
            dataset_services_setting.get_value(as_public_endpoint=as_public_endpoint, as_endpoint=as_endpoint,
                                               as_engine=as_engine)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('DatasetServiceSetting', name, cls.name)

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

            geoserver_engine = app.get_spatial_dataset_service('primary_geoserver', as_engine=True)


        """
        from tethys_apps.models import TethysApp
        app = cls()
        db_app = TethysApp.objects.get(package=app.package)
        spatial_dataset_service_settings = db_app.spatial_dataset_service_settings

        try:
            spatial_dataset_service_setting = spatial_dataset_service_settings.get(
                name=name)
            return spatial_dataset_service_setting.get_value(
                as_public_endpoint=as_public_endpoint,
                as_endpoint=as_endpoint,
                as_wms=as_wms, as_wfs=as_wfs,
                as_engine=as_engine
            )
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('SpatialDatasetServiceSetting', name, cls.name)

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
            return wps_service_setting.get_value(as_public_endpoint=as_public_endpoint,
                                                 as_endpoint=as_endpoint, as_engine=as_engine)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('WebProcessingServiceSetting', name, cls.name)

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
            # Return as_engine if the other two are False
            as_engine = not as_sessionmaker and not as_url
            ps_connection_setting = ps_connection_settings.get(name=name)
            return ps_connection_setting.get_value(as_url=as_url, as_sessionmaker=as_sessionmaker, as_engine=as_engine)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreConnectionSetting', name, cls.name)
        except TethysAppSettingNotAssigned:
            cls._log_tethys_app_setting_not_assigned_error('PersistentStoreConnectionSetting', name)

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

        verified_name = name if not is_testing_environment() else get_test_db_name(name)

        try:
            # Return as_engine if the other two are False
            as_engine = not as_sessionmaker and not as_url
            ps_database_setting = ps_database_settings.get(name=verified_name)
            return ps_database_setting.get_value(with_db=True, as_url=as_url, as_sessionmaker=as_sessionmaker,
                                                 as_engine=as_engine)
        except ObjectDoesNotExist:
            raise TethysAppSettingDoesNotExist('PersistentStoreDatabaseSetting', verified_name, cls.name)
        except TethysAppSettingNotAssigned:
            cls._log_tethys_app_setting_not_assigned_error('PersistentStoreDatabaseSetting', verified_name)

    @classmethod
    def create_persistent_store(cls, db_name, connection_name, spatial=False, initializer='', refresh=False,
                                force_first_time=False):
        """
        Creates a new persistent store database for the app. This method is idempotent.

        Args:
          db_name(string): Name of the persistent store that will be created.
          connection_name(string|None): Name of persistent store connection or None if creating a test copy of an existing persistent store (only while in the testing environment)
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

        """  # noqa: E501
        # Get named persistent store service connection
        from tethys_apps.models import TethysApp
        from tethys_apps.models import PersistentStoreDatabaseSetting
        db_app = TethysApp.objects.get(package=cls.package)

        # Get connection service
        ps_connection_settings = db_app.persistent_store_connection_settings

        if is_testing_environment():
            verified_db_name = get_test_db_name(db_name)
        else:
            verified_db_name = db_name
            if connection_name is None:
                raise ValueError('The connection_name cannot be None unless running in the testing environment.')

        try:
            if connection_name is None:
                ps_database_settings = db_app.persistent_store_database_settings
                ps_setting = ps_database_settings.get(name=db_name)
            else:
                ps_setting = ps_connection_settings.get(name=connection_name)
        except ObjectDoesNotExist:
            if connection_name is None:
                raise TethysAppSettingDoesNotExist(
                    'PersistentStoreDatabaseSetting named "{0}" does not exist.'.format(db_name),
                    connection_name, cls.name)
            else:
                raise TethysAppSettingDoesNotExist('PersistentStoreConnectionSetting ', connection_name, cls.name)

        ps_service = ps_setting.persistent_store_service

        # Check if persistent store database setting already exists before creating it
        try:
            db_setting = db_app.persistent_store_database_settings.get(name=verified_db_name)
            db_setting.persistent_store_service = ps_service
            db_setting.initializer = initializer
            db_setting.save()
        except ObjectDoesNotExist:
            # Create new PersistentStoreDatabaseSetting
            db_setting = PersistentStoreDatabaseSetting(
                name=verified_db_name,
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
        verified_name = name if not is_testing_environment() else get_test_db_name(name)

        try:
            ps_database_setting = ps_database_settings.get(name=verified_name)
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
        return [ps_database_setting.name for ps_database_setting in ps_database_settings
                if TESTING_DB_FLAG not in ps_database_setting.name]

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
        return [ps_connection_setting.name for ps_connection_setting in ps_connection_settings
                if TESTING_DB_FLAG not in ps_connection_setting.name]

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

        verified_name = name if not is_testing_environment() else get_test_db_name(name)

        try:
            # If it exists return True
            ps_database_setting = ps_database_settings.get(name=verified_name)
        except ObjectDoesNotExist:
            # Else return False
            return False

        # Check if it exists
        ps_database_setting.persistent_store_database_exists()
        return True

    def sync_with_tethys_db(self):
        """
        Sync installed apps with database.
        """
        from django.conf import settings
        from tethys_apps.models import TethysApp

        try:
            # Make pass to add apps to db that are newly installed
            # Query to see if installed app is in the database
            db_apps = TethysApp.objects.\
                filter(package__exact=self.package).all()

            # If the app is not in the database, then add it
            if len(db_apps) == 0:
                db_app = TethysApp(
                    name=self.name,
                    package=self.package,
                    description=self.description,
                    enable_feedback=self.enable_feedback,
                    feedback_emails=self.feedback_emails,
                    index=self.index,
                    icon=self.icon,
                    root_url=self.root_url,
                    color=self.color,
                    tags=self.tags
                )
                db_app.save()

                # custom settings
                db_app.add_settings(self.custom_settings())
                # dataset services settings
                db_app.add_settings(self.dataset_service_settings())
                # spatial dataset services settings
                db_app.add_settings(self.spatial_dataset_service_settings())
                # wps settings
                db_app.add_settings(self.web_processing_service_settings())
                # persistent store settings
                db_app.add_settings(self.persistent_store_settings())

                db_app.save()

            # If the app is in the database, update developer priority attributes
            elif len(db_apps) == 1:
                db_app = db_apps[0]
                db_app.index = self.index
                db_app.root_url = self.root_url

                # custom settings
                db_app.add_settings(self.custom_settings())
                # dataset services settings
                db_app.add_settings(self.dataset_service_settings())
                # spatial dataset services settings
                db_app.add_settings(self.spatial_dataset_service_settings())
                # wps settings
                db_app.add_settings(self.web_processing_service_settings())
                # persistent store settings
                db_app.add_settings(self.persistent_store_settings())
                db_app.save()

                # In debug mode, update all fields, not just developer priority attributes
                if hasattr(settings, 'DEBUG') and settings.DEBUG:
                    db_app.name = self.name
                    db_app.description = self.description
                    db_app.icon = self.icon
                    db_app.color = self.color
                    db_app.tags = self.tags
                    db_app.enable_feedback = self.enable_feedback
                    db_app.feedback_emails = self.feedback_emails
                    db_app.save()

            # More than one instance of the app in db... (what to do here?)
            elif len(db_apps) >= 2:
                pass
        except ProgrammingError:
            tethys_log.warning("Unable to sync app with database. tethys_apps_tethysapp "
                               "table does not exist")
        except Exception as e:
            tethys_log.error(e)

    def remove_from_db(self):
        """
        Remove the instance from the db.
        """
        from tethys_apps.models import TethysApp

        try:
            # Attempt to delete the object
            TethysApp.objects.filter(package__exact=self.package).delete()
        except Exception as e:
            tethys_log.error(e)

    @classmethod
    def _log_tethys_app_setting_not_assigned_error(cls, setting_type, setting_name):
        """
        Logs useful traceback and message without actually raising an exception when an attempt
        to access a non-existent setting is made.

        Args:
            setting_type (str, required):
                Name of specific settings class (e.g. CustomTethysAppSetting, PersistentStoreDatabaseSetting etc).
            setting_name (str, required):
                Name attribute of the setting.
        """
        tethys_log.warning('Tethys app setting is not assigned.\nTraceback (most recent call last):\n{0} '
                           'TethysAppSettingNotAssigned: {1} named "{2}" has not been assigned. '
                           'Please visit the setting page for the app {3} and assign all required settings.'
                           .format(traceback.format_stack(limit=3)[0], setting_type, setting_name,
                                   cls.name.encode('utf-8'))
                           )

    @classmethod
    def pre_delete_user_workspace(cls, user):
        """
        Override this method to pre-process a user's workspace before it is emptied

        Args:
            user (User, required):
                User that requested to clear their workspace
        """

    @classmethod
    def post_delete_user_workspace(cls, user):
        """
        Override this method to post-process a user's workspace after it is emptied

        Args:
            user (User, required):
                User that requested to clear their workspace
        """

    @classmethod
    def pre_delete_app_workspace(cls):
        """
        Override this method to pre-process the app workspace before it is emptied
        """

    @classmethod
    def post_delete_app_workspace(cls):
        """
        Override this method to post-process the app workspace after it is emptied
        """
