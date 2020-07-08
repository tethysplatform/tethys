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

from tethys_apps.helpers import get_installed_tethys_apps, get_installed_tethys_extensions


class Command(BaseCommand):
    """
    Command class that handles the syncstores command. Provides persistent store management functionality.
    """

    def add_arguments(self, parser):
        parser.add_argument('-l', '--link', action='store_true', default=False,
                            help='Link static directories of apps into STATIC_ROOT instead of copying them. '
                                 'Not recommended.')

    def handle(self, *args, **options):
        """
        Symbolically link the static directories of each app into the static/public directory specified by the
        STATIC_ROOT parameter of the settings.py. Do this prior to running Django's collectstatic method.
        """  # noqa: E501
        if not settings.STATIC_ROOT:
            print('WARNING: Cannot find the STATIC_ROOT setting. Please provide the path to the static directory using '
                  'the STATIC_ROOT setting in the portal_config.yml file and try again.')
            exit(1)

        # Read settings
        static_root = settings.STATIC_ROOT

        # Get a list of installed apps
        installed_apps_and_extensions = get_installed_tethys_apps()
        installed_apps_and_extensions.update(get_installed_tethys_extensions())

        # Provide feedback to user
        print('INFO: Linking static and public directories of apps and extensions to "{0}".'.format(static_root))

        for item, path in installed_apps_and_extensions.items():
            # Check for both variants of the static directory (public and static)
            public_path = os.path.join(path, 'public')
            static_path = os.path.join(path, 'static')

            if os.path.isdir(public_path):
                app_static_dir = public_path
            elif os.path.isdir(static_path):
                app_static_dir = static_path
            else:
                print(f'WARNING: Cannot find a directory named "static" or "public" for app "{item}". Skipping...')
                continue

            # Path for app in the STATIC_ROOT directory
            static_root_dir = os.path.join(static_root, item)

            # Clear out old symbolic links/directories if necessary
            try:
                # Remove link
                os.remove(static_root_dir)
            except OSError:
                try:
                    # Remove directory
                    shutil.rmtree(static_root_dir)
                except OSError:
                    # No file
                    pass

            # Create appropriate symbolic link
            if options['link']:
                os.symlink(app_static_dir, static_root_dir)
                print('INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(item))

            else:
                shutil.copytree(app_static_dir, static_root_dir)
                print('INFO: Successfully copied public directory to STATIC_ROOT for app "{0}".'.format(item))
