"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from __future__ import print_function
from builtins import input
import logging
import os

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils._os import safe_join
from tethys_apps.harvester import SingletonHarvester

tethys_log = logging.getLogger('tethys.' + __name__)


def get_tethys_src_dir():
    """
    Get/derive the TETHYS_SRC variable.

    Returns:
        str: path to TETHYS_SRC.
    """
    default = os.path.dirname(os.path.dirname(__file__))
    return os.environ.get('TETHYS_SRC', default)


def get_tethys_home_dir():
    """
    Get/derive the TETHYS_HOME variable.

    Returns:
        str: path to TETHYS_HOME.
    """
    default = os.path.dirname(get_tethys_src_dir())
    return os.environ.get('TETHYS_HOME', default)


def get_directories_in_tethys(directory_names, with_app_name=False):
    """
    # Locate given directories in tethys apps and extensions.
    Args:
        directory_names: directory to get path to.
        with_app_name: inlcud the app name if True.

    Returns:
        list: list of paths to directories in apps and extensions.
    """
    # Determine the directories of tethys apps directory
    tethysapp_dir = safe_join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')
    tethysapp_contents = next(os.walk(tethysapp_dir))[1]
    potential_dirs = [safe_join(tethysapp_dir, item) for item in tethysapp_contents]

    # Determine the directories of tethys extensions
    harvester = SingletonHarvester()

    for _, extension_module in harvester.extension_modules.items():
        try:
            extension_module = __import__(extension_module, fromlist=[''])
            potential_dirs.append(extension_module.__path__[0])
        except (ImportError, AttributeError, IndexError):
            pass

    # Check each directory combination
    match_dirs = []
    for potential_dir in potential_dirs:
        for directory_name in directory_names:
            # Only check directories
            if os.path.isdir(potential_dir):
                match_dir = safe_join(potential_dir, directory_name)

                if match_dir not in match_dirs and os.path.isdir(match_dir):
                    if not with_app_name:
                        match_dirs.append(match_dir)
                    else:
                        match_dirs.append((os.path.basename(potential_dir), match_dir))

    return match_dirs


def get_active_app(request=None, url=None):
    """
    Get the active TethysApp object based on the request or URL.
    """
    from tethys_apps.models import TethysApp
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
    from tethys_apps.cli.cli_colors import pretty_output, FG_RED, FG_GREEN
    from tethys_apps.models import PersistentStoreDatabaseSetting
    from tethys_apps.models import TethysApp

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
        print(e)
        with pretty_output(FG_RED) as p:
            p.write('The above error was encountered. Aborted.'.format(app_package))
        return False


def remove_ps_database_setting(app_package, name, force=False):
    from tethys_apps.models import TethysApp
    from tethys_apps.cli.cli_colors import pretty_output, FG_RED, FG_GREEN
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
        proceed = input('Are you sure you want to delete the '
                        'PersistentStoreDatabaseSetting named "{}"? [y/n]: '.format(name))
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = input('Please enter either "y" or "n": ')

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
    from tethys_apps.cli.cli_colors import pretty_output, FG_GREEN, FG_RED
    from tethys_sdk.app_settings import (SpatialDatasetServiceSetting, PersistentStoreConnectionSetting,
                                         PersistentStoreDatabaseSetting)
    from tethys_services.models import (SpatialDatasetService, PersistentStoreService)
    from tethys_apps.models import TethysApp

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
