"""
********************************************************************************
* Name: static_finders.py
* Author: nswain
* Created On: February 21, 2018
* Copyright:
* License:
********************************************************************************
"""

from pathlib import Path
from collections import OrderedDict as SortedDict
import django
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from .utilities import get_directories_in_tethys


class TethysStaticFinder(BaseFinder):
    """
    A static files finder that looks in each app in the tethysapp directory for static files.
    This finder search for static files in a directory called 'public' or 'static'.
    """

    def __init__(self, *args, **kwargs):
        # List of locations with static files
        self.locations = get_directories_in_tethys(
            ("static", "public"), with_app_name=True
        )

        # Maps dir paths to an appropriate storage instance
        self.storages = SortedDict()

        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage

        super().__init__(*args, **kwargs)

    # Django changes the argument `all` to `find_all` since the version 5.2
    # Remove the argument `all` when Tethys doesn't support Django<5.2 anymore
    def find(self, path, all=False, find_all=False):
        """
        Looks for files in the Tethys apps static or public directories
        """
        find_all_files = find_all if django.VERSION >= (5, 2) else all
        matches = []
        for prefix, root in self.locations:
            matched_path = self.find_location(root, path, prefix)
            if matched_path:
                if not find_all_files:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path, prefix=None):
        """
        Finds a requested static file in a location, returning the found
        absolute path (or ``None`` if no match).
        """
        path = Path(path)
        if prefix:
            prefix = Path(f"{prefix}/")
            if not path.is_relative_to(prefix):
                return None
            path = path.relative_to(prefix)
        path = Path(safe_join(str(root), str(path)))
        if path.exists():
            return path

    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        for _, root in self.locations:
            storage = self.storages[root]
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage
