"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import logging
import os
import sys
import traceback
from collections import OrderedDict as SortedDict

from django.conf.urls import url
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from past.builtins import basestring
from tethys_apps import tethys_log
from tethys_apps.app_harvester import SingletonAppHarvester
from tethys_apps.base import permissions
from tethys_apps.models import TethysApp

log = logging.getLogger('tethys.tethys_apps.utilities')


def register_app_permissions():
    """
    Register and sync the app permissions.
    """
    from guardian.shortcuts import assign_perm, remove_perm, get_perms
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission, Group

    # Get the apps
    harvester = SingletonAppHarvester()
    apps = harvester.apps
    all_app_permissions = {}
    all_groups = {}

    for app in apps:
        perms = app.permissions()

        # Name spaced prefix for app permissions
        # e.g. my_first_app:view_things
        # e.g. my_first_app | View things
        perm_codename_prefix = app.package + ':'
        perm_name_prefix = app.package + ' | '

        if perms is not None:
            # Thing is either a Permission or a PermissionGroup object

            for thing in perms:
                # Permission Case
                if isinstance(thing, permissions.Permission):
                    # Name space the permissions and add it to the list
                    permission_codename = perm_codename_prefix + thing.name
                    permission_name = perm_name_prefix + thing.description
                    all_app_permissions[permission_codename] = permission_name

                # PermissionGroup Case
                elif isinstance(thing, permissions.PermissionGroup):
                    # Record in dict of groups
                    group_permissions = []
                    group_name = perm_codename_prefix + thing.name

                    for perm in thing.permissions:
                        # Name space the permissions and add it to the list
                        permission_codename = perm_codename_prefix + perm.name
                        permission_name = perm_name_prefix + perm.description
                        all_app_permissions[permission_codename] = permission_name
                        group_permissions.append(permission_codename)

                    # Store all groups for all apps
                    all_groups[group_name] = {'permissions': group_permissions, 'app_package': app.package}

    # Get the TethysApp content type
    tethys_content_type = ContentType.objects.get(
        app_label='tethys_apps',
        model='tethysapp'
    )

    # Remove any permissions that no longer exist
    db_app_permissions = Permission.objects.filter(content_type=tethys_content_type).all()

    for db_app_permission in db_app_permissions:
        # Delete the permission if the permission is no longer required by an app
        if db_app_permission.codename not in all_app_permissions:
            db_app_permission.delete()

    # Create permissions that need to be created
    for perm in all_app_permissions:
        # Create permission if it doesn't exist
        try:
            # If permission exists, update it
            p = Permission.objects.get(codename=perm)

            p.name = all_app_permissions[perm]
            p.content_type = tethys_content_type
            p.save()

        except Permission.DoesNotExist:
            p = Permission(
                name=all_app_permissions[perm],
                codename=perm,
                content_type=tethys_content_type
            )
            p.save()

    # Remove any groups that no longer exist
    db_groups = Group.objects.all()
    db_apps = TethysApp.objects.all()
    db_app_names = [db_app.package for db_app in db_apps]

    for db_group in db_groups:
        db_group_name_parts = db_group.name.split(':')

        # Only perform maintenance on groups that belong to Tethys Apps
        if (len(db_group_name_parts) > 1) and (db_group_name_parts[0] in db_app_names):

            # Delete groups that is no longer required by an app
            if db_group.name not in all_groups:
                db_group.delete()

    # Create groups that need to be created
    for group in all_groups:
        # Look up the app
        db_app = TethysApp.objects.get(package=all_groups[group]['app_package'])

        # Create group if it doesn't exist
        try:
            # If it exists, update the permissions assigned to it
            g = Group.objects.get(name=group)

            # Get the permissions for the group and remove all of them
            perms = get_perms(g, db_app)

            for p in perms:
                remove_perm(p, g, db_app)

            # Assign the permission to the group and the app instance
            for p in all_groups[group]['permissions']:
                assign_perm(p, g, db_app)

        except Group.DoesNotExist:
            # Create a new group
            g = Group(name=group)
            g.save()

            # Assign the permission to the group and the app instance
            for p in all_groups[group]['permissions']:
                assign_perm(p, g, db_app)


def generate_app_url_patterns():
    """
    Generate the url pattern lists for each app and namespace them accordingly.
    """

    # Get controllers list from app harvester
    harvester = SingletonAppHarvester()
    apps = harvester.apps
    app_url_patterns = dict()

    for app in apps:
        if hasattr(app, 'url_maps'):
            url_maps = app.url_maps()
        elif hasattr(app, 'controllers'):
            url_maps = app.controllers()
        else:
            url_maps = None

        if url_maps:
            for url_map in url_maps:
                app_root = app.root_url
                app_namespace = app_root.replace('-', '_')

                if app_namespace not in app_url_patterns:
                    app_url_patterns[app_namespace] = []

                # Create django url object
                if isinstance(url_map.controller, basestring):
                    controller_parts = url_map.controller.split('.')
                    module_name = '.'.join(controller_parts[:-1])
                    function_name = controller_parts[-1]
                    try:
                        module = __import__(module_name, fromlist=[function_name])
                    except ImportError:
                        error_msg = 'The following error occurred while trying to import the controller function ' \
                                    '"{0}":\n {1}'.format(url_map.controller, traceback.format_exc(2))
                        log.error(error_msg)
                        sys.exit(1)
                    try:
                        controller_function = getattr(module, function_name)
                    except AttributeError as e:
                        error_msg = 'The following error occurred while tyring to access the controller function ' \
                                    '"{0}":\n {1}'.format(url_map.controller, traceback.format_exc(2))
                        log.error(error_msg)
                        sys.exit(1)
                else:
                    controller_function = url_map.controller
                django_url = url(url_map.url, controller_function, name=url_map.name)

                # Append to namespace list
                app_url_patterns[app_namespace].append(django_url)

    return app_url_patterns


def get_directories_in_tethys_apps(directory_names, with_app_name=False):
    # Determine the tethysapp directory
    tethysapp_dir = safe_join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')

    # Assemble a list of tethysapp directories
    tethysapp_contents = os.listdir(tethysapp_dir)
    tethysapp_match_dirs = []

    for item in tethysapp_contents:
        item_path = safe_join(tethysapp_dir, item)

        # Check each directory combination
        for directory_name in directory_names:
            # Only check directories
            if os.path.isdir(item_path):
                match_dir = safe_join(item_path, directory_name)

                if match_dir not in tethysapp_match_dirs and os.path.isdir(match_dir):
                    if not with_app_name:
                        tethysapp_match_dirs.append(match_dir)
                    else:
                        tethysapp_match_dirs.append((item, match_dir))

    return tethysapp_match_dirs


class TethysAppsStaticFinder(BaseFinder):
    """
    A static files finder that looks in each app in the tethysapp directory for static files.
    This finder search for static files in a directory called 'public' or 'static'.
    """

    def __init__(self, apps=None, *args, **kwargs):
        # List of locations with static files
        self.locations = get_directories_in_tethys_apps(('static', 'public'), with_app_name=True)

        # Maps dir paths to an appropriate storage instance
        self.storages = SortedDict()

        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage

        super(TethysAppsStaticFinder, self).__init__(*args, **kwargs)

    def find(self, path, all=False):
        """
        Looks for files in the Tethys apps static or public directories
        """
        matches = []
        for prefix, root in self.locations:
            matched_path = self.find_location(root, path, prefix)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path, prefix=None):
        """
        Finds a requested static file in a location, returning the found
        absolute path (or ``None`` if no match).
        """
        if prefix:
            prefix = '%s%s' % (prefix, os.sep)
            if not path.startswith(prefix):
                return None
            path = path[len(prefix):]
        path = safe_join(root, path)
        if os.path.exists(path):
            return path

    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage


def sync_tethys_app_db():
    """
    Sync installed apps with database.
    """
    from django.conf import settings

    # Get the harvester
    harvester = SingletonAppHarvester()

    try:
        # Make pass to remove apps that were uninstalled
        db_apps = TethysApp.objects.all()
        installed_app_packages = [app.package for app in harvester.apps]

        for db_apps in db_apps:
            if db_apps.package not in installed_app_packages:
                db_apps.delete()

        # Make pass to add apps to db that are newly installed
        installed_apps = harvester.apps

        for installed_app in installed_apps:
            # Query to see if installed app is in the database
            db_apps = TethysApp.objects. \
                filter(package__exact=installed_app.package). \
                all()

            # If the app is not in the database, then add it
            if len(db_apps) == 0:
                app = TethysApp(
                    name=installed_app.name,
                    package=installed_app.package,
                    description=installed_app.description,
                    enable_feedback=installed_app.enable_feedback,
                    feedback_emails=installed_app.feedback_emails,
                    index=installed_app.index,
                    icon=installed_app.icon,
                    root_url=installed_app.root_url,
                    color=installed_app.color,
                    tags=installed_app.tags
                )
                app.save()

                # custom settings
                app.add_settings(installed_app.custom_settings())
                # dataset services settings
                app.add_settings(installed_app.dataset_service_settings())
                # spatial dataset services settings
                app.add_settings(installed_app.spatial_dataset_service_settings())
                # wps settings
                app.add_settings(installed_app.web_processing_service_settings())
                # persistent store settings
                app.add_settings(installed_app.persistent_store_settings())

                app.save()

            # If the app is in the database, update developer-first attributes
            elif len(db_apps) == 1:
                db_app = db_apps[0]
                db_app.index = installed_app.index
                db_app.icon = installed_app.icon
                db_app.root_url = installed_app.root_url
                db_app.color = installed_app.color
                db_app.save()

                if hasattr(settings, 'DEBUG') and settings.DEBUG:
                    db_app.name = installed_app.name
                    db_app.description = installed_app.description
                    db_app.tags = installed_app.tags
                    db_app.enable_feedback = installed_app.enable_feedback
                    db_app.feedback_emails = installed_app.feedback_emails
                    db_app.save()

                    # custom settings
                    db_app.add_settings(installed_app.custom_settings())
                    # dataset services settings
                    db_app.add_settings(installed_app.dataset_service_settings())
                    # spatial dataset services settings
                    db_app.add_settings(installed_app.spatial_dataset_service_settings())
                    # wps settings
                    db_app.add_settings(installed_app.web_processing_service_settings())
                    # persistent store settings
                    db_app.add_settings(installed_app.persistent_store_settings())
                    db_app.save()

            # More than one instance of the app in db... (what to do here?)
            elif len(db_apps) >= 2:
                continue
    except Exception as e:
        log.error(e)


def get_active_app(request=None, url=None):
    """
    Get the active TethysApp object based on the request or URL.
    """
    apps_root = 'apps'

    if request is not None:
        the_url = request.path
    elif url is not None:
        the_url = url
    else:
        return None

    url_parts = the_url.split('/')
    app = None

    # Find the app key
    if apps_root in url_parts:
        # The app root_url is the path item following (+1) the apps_root item
        app_root_url_index = url_parts.index(apps_root) + 1
        app_root_url = url_parts[app_root_url_index]

        if app_root_url:
            try:
                # Get the app from the database
                app = TethysApp.objects.get(root_url=app_root_url)
            except ObjectDoesNotExist:
                tethys_log.warning('Could not locate app with root url "{0}".'.format(app_root_url))
            except MultipleObjectsReturned:
                tethys_log.warning('Multiple apps found with root url "{0}".'.format(app_root_url))
    return app


def create_ps_database_setting(app_package, name, description='', required=False, initializer='', initialized=False,
                               spatial=False, dynamic=False):
    from cli.cli_colors import pretty_output, FG_RED, FG_GREEN
    from tethys_apps.models import PersistentStoreDatabaseSetting

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A Tethys App with the name "{}" does not exist. Aborted.'.format(app_package))
        return False

    try:
        setting = PersistentStoreDatabaseSetting.objects.get(name=name)
        if setting:
            with pretty_output(FG_RED) as p:
                p.write('A PersistentStoreDatabaseSetting with name "{}" already exists. Aborted.'.format(name))
            return False
    except ObjectDoesNotExist:
        pass

    try:
        ps_database_setting = PersistentStoreDatabaseSetting(
            tethys_app=app,
            name=name,
            description=description,
            required=required,
            initializer=initializer,
            initialized=initialized,
            spatial=spatial,
            dynamic=dynamic
        )
        ps_database_setting.save()
        with pretty_output(FG_GREEN) as p:
            p.write('PersistentStoreDatabaseSetting named "{}" for app "{}" created successfully!'.format(name,
                                                                                                          app_package))
        return True
    except Exception as e:
        print e
        with pretty_output(FG_RED) as p:
            p.write('The above error was encountered. Aborted.'.format(app_package))
        return False


def remove_ps_database_setting(app_package, name, force=False):
    from cli.cli_colors import pretty_output, FG_RED, FG_GREEN
    from tethys_apps.models import PersistentStoreDatabaseSetting

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A Tethys App with the name "{}" does not exist. Aborted.'.format(app_package))
        return False

    try:
        setting = PersistentStoreDatabaseSetting.objects.get(tethys_app=app, name=name)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('An PersistentStoreDatabaseSetting with the name "{}" for app "{}" does not exist. Aborted.'
                    .format(name, app_package))
        return False

    if not force:
        proceed = raw_input('Are you sure you want to delete the PersistentStoreDatabaseSetting named "{}"? [y/n]: '
                            .format(name))
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = raw_input('Please enter either "y" or "n": ')

        if proceed in ['y', 'Y']:
            setting.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed PersistentStoreDatabaseSetting with name "{0}"!'.format(name))
            return True
        else:
            with pretty_output(FG_RED) as p:
                p.write('Aborted. PersistentStoreDatabaseSetting not removed.')
    else:
        setting.delete()
        with pretty_output(FG_GREEN) as p:
            p.write('Successfully removed PersistentStoreDatabaseSetting with name "{0}"!'.format(name))
        return True


def link_service_to_app_setting(service_type, service_uid, app_package, setting_type, setting_uid):
    """
    Links a Tethys Service to a TethysAppSetting.
    :param service_type: The type of service being linked to an app. Must be either 'spatial' or 'persistent'.
    :param service_uid: The name or id of the service being linked to an app.
    :param app_package: The package name of the app whose setting is being linked to a service.
    :param setting_type: The type of setting being linked to a service. Must be one of the following: 'ps_database',
    'ps_connection', or 'ds_spatial'.
    :param setting_uid: The name or id of the setting being linked to a service.
    :return: True if successful, False otherwise.
    """
    from cli.cli_colors import pretty_output, FG_GREEN, FG_RED
    from tethys_sdk.app_settings import (SpatialDatasetServiceSetting, PersistentStoreConnectionSetting,
                                         PersistentStoreDatabaseSetting)
    from tethys_services.models import (SpatialDatasetService, PersistentStoreService)

    service_type_to_model_dict = {
        'spatial': SpatialDatasetService,
        'persistent': PersistentStoreService
    }

    setting_type_to_link_model_dict = {
        'ps_database': {
            'setting_model': PersistentStoreDatabaseSetting,
            'service_field': 'persistent_store_service'
        },
        'ps_connection': {
            'setting_model': PersistentStoreConnectionSetting,
            'service_field': 'persistent_store_service'
        },
        'ds_spatial': {
            'setting_model': SpatialDatasetServiceSetting,
            'service_field': 'spatial_dataset_service'
        }
    }

    service_model = service_type_to_model_dict[service_type]

    try:
        try:
            service_uid = int(service_uid)
            service = service_model.objects.get(pk=service_uid)
        except ValueError:
            service = service_model.objects.get(name=service_uid)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A {0} with ID/Name "{1}" does not exist.'.format(str(service_model), service_uid))
        return False

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A Tethys App with the name "{}" does not exist. Aborted.'.format(app_package))
        return False

    try:
        linked_setting_model_dict = setting_type_to_link_model_dict[setting_type]
    except KeyError:
        with pretty_output(FG_RED) as p:
            p.write('The setting_type you specified ("{0}") does not exist.'
                    '\nChoose from: "ps_database|ps_connection|ds_spatial"'.format(setting_type))
        return False

    linked_setting_model = linked_setting_model_dict['setting_model']
    linked_service_field = linked_setting_model_dict['service_field']

    try:
        try:
            setting_uid = int(setting_uid)
            setting = linked_setting_model.objects.get(tethys_app=app, pk=setting_uid)
        except ValueError:
            setting = linked_setting_model.objects.get(tethys_app=app, name=setting_uid)

        setattr(setting, linked_service_field, service)
        setting.save()
        with pretty_output(FG_GREEN) as p:
            p.write('{} with name "{}" was successfully linked to "{}" with name "{}" of the "{}" Tethys App'
                    .format(str(service_model), service_uid, linked_setting_model, setting_uid, app_package))
        return True
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A {0} with ID/Name "{1}" does not exist.'.format(str(linked_setting_model), setting_uid))
        return False
