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
    Command class that handles the collectstatic command for apps an extensions.
    """

    def add_arguments(self, parser):
        parser.add_argument('-l', '--link', action='store_true', default=False,
                            help='Link static directories of apps into STATIC_ROOT instead of copying them. '
                                 'Not recommended.')

    def handle(self, *args, **kwargs):
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

        # Get a list of installed apps and extensions
        installed_apps_and_extensions = get_installed_tethys_apps()
        installed_apps_and_extensions.update(get_installed_tethys_extensions())

        # Provide feedback to user
        print('INFO: Collecting static and public directories of apps and extensions to "{0}".'.format(static_root))

        # Get the link option
        link_opt = kwargs.get('link')

        for item, path in installed_apps_and_extensions.items():
            # Check for both variants of the static directory (named either public or static)
            public_path = os.path.join(path, 'public')
            static_path = os.path.join(path, 'static')

            if os.path.isdir(public_path):
                item_static_source_dir = public_path
            elif os.path.isdir(static_path):
                item_static_source_dir = static_path
            else:
                print(f'WARNING: Cannot find a directory named "static" or "public" for app "{item}". Skipping...')
                continue

            # Path for app in the STATIC_ROOT directory
            item_static_root_dir = os.path.join(static_root, item)

            # Clear out old symbolic links/directories if necessary
            try:
                # Remove link
                os.remove(item_static_root_dir)
            except OSError:
                try:
                    # Remove directory
                    shutil.rmtree(item_static_root_dir)
                except OSError:
                    pass
                    # No file to remove

            # Create appropriate symbolic link
            if link_opt:
                os.symlink(item_static_source_dir, item_static_root_dir)
                print('INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(item))

            else:
                shutil.copytree(item_static_source_dir, item_static_root_dir)
                print('INFO: Successfully copied public directory to STATIC_ROOT for app "{0}".'.format(item))
