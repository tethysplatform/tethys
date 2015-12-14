"""
********************************************************************************
* Name: pre_collectstatic.py
* Author: Nathan Swain
* Created On: February 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import os
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from tethys_apps.helpers import get_installed_tethys_apps


class Command(BaseCommand):
    """
    Command class that handles the syncstores command. Provides persistent store management functionality.
    """

    def handle(self, *args, **options):
        """
        Symbolically link the static directories of each app into the static/public directory specified by the STATIC_ROOT
        parameter of the settings.py. Do this prior to running Django's collectstatic method.
        """
        if not settings.STATIC_ROOT:
            print('WARNING: Cannot find the STATIC_ROOT setting in the settings.py file. '
                  'Please provide the path to the static directory using the STATIC_ROOT setting and try again.')
            exit(1)

        # Read settings
        static_root = settings.STATIC_ROOT

        # Get a list of installed apps
        installed_apps = get_installed_tethys_apps()

        # Provide feedback to user
        print('INFO: Linking static and public directories of apps to "{0}".'.format(static_root))

        for app, path in installed_apps.iteritems():
            # Check for both variants of the static directory (public and static)
            public_path = os.path.join(path, 'public')
            static_path = os.path.join(path, 'static')
            static_root_path = os.path.join(static_root, app)

            # Clear out old symbolic links/directories if necessary
            try:
                # Remove link
                os.remove(static_root_path)
            except OSError:
                try:
                    # Remove directory
                    shutil.rmtree(static_root_path)
                except OSError:
                    # No file
                    pass

            # Create appropriate symbolic link
            if os.path.isdir(public_path):
                os.symlink(public_path, static_root_path)
                print('INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(app))

            elif os.path.isdir(static_path):
                os.symlink(static_path, static_root_path)
                print('INFO: Successfully linked static directory to STATIC_ROOT for app "{0}".'.format(app))

