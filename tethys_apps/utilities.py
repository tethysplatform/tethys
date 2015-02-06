import os

from django.conf.urls import url
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join
from django.utils.datastructures import SortedDict

from tethys_apps.app_harvester import SingletonAppHarvester

# Other dependency imports DO NOT ERASE
from tethys_datasets.utilities import get_dataset_engine


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
                django_url = url(url_map.url, url_map.controller, name=url_map.name)

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


def tethys_apps_template_loader(template_name, template_dirs=None):
    """
    Custom Django template loader for tethys apps
    """
    # Search for the template in the list of template directories
    tethysapp_template_dirs = get_directories_in_tethys_apps(('templates',))

    template = None

    for template_dir in tethysapp_template_dirs:
        template_path = safe_join(template_dir, template_name)

        try:
            template = open(template_path).read(), template_name
            break
        except IOError:
            pass

    # If the template is still None, raise the exception
    if not template:
        raise TemplateDoesNotExist(template_name)

    return template


# This loader is always usable
tethys_apps_template_loader.is_usable = True


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