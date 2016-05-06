"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import os
import sys
import traceback
import logging

from django.conf.urls import url
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from collections import OrderedDict as SortedDict

from tethys_apps.app_harvester import SingletonAppHarvester

# Other dependency imports DO NOT ERASE
from tethys_apps.models import TethysApp
from tethys_services.utilities import get_dataset_engine

log = logging.getLogger('tethys.tethys_apps.utilities')


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
                    except AttributeError, e:
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
            db_apps = TethysApp.objects.\
                filter(package__exact=installed_app.package).\
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
                    color=installed_app.color
                )
                app.save()

            # If the app is in the database, update developer-first attributes
            elif len(db_apps) == 1:
                db_app = db_apps[0]
                db_app.index = installed_app.index
                db_app.icon = installed_app.icon
                db_app.root_url = installed_app.root_url
                db_app.color = installed_app.color
                db_app.save()

            # More than one instance of the app in db... (what to do here?)
            elif len(db_apps) >= 2:
                continue
    except Exception as e:
        log.error(e)

