"""
********************************************************************************
* Name: collectworkspaces.py
* Author: Nathan Swain
* Created On: August 6, 2015
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
        if not hasattr(settings, 'TETHYS_WORKSPACES_ROOT') or (hasattr(settings, 'TETHYS_WORKSPACES_ROOT') and not settings.TETHYS_WORKSPACES_ROOT):
            print('WARNING: Cannot find the TETHYS_WORKSPACES_ROOT setting in the settings.py file. '
                  'Please provide the path to the static directory using the TETHYS_WORKSPACES_ROOT setting and try again.')
            exit(1)

        # Read settings
        workspaces_root = settings.TETHYS_WORKSPACES_ROOT

        # Get a list of installed apps
        installed_apps = get_installed_tethys_apps()

        # Provide feedback to user
        print('INFO: Moving workspace directories of apps to "{0}" and linking back.'.format(workspaces_root))

        for app, path in installed_apps.iteritems():
            # Check for both variants of the static directory (public and static)
            workspaces_path = os.path.join(path, 'workspaces')
            workspaces_root_path = os.path.join(workspaces_root, app)

            # Only perform if workspaces_path is a directory
            if os.path.isdir(workspaces_path) and not os.path.islink(workspaces_path):
                # Clear out old symbolic links/directories in workspace root if necessary
                try:
                    # Remove link
                    os.remove(workspaces_root_path)
                except OSError:
                    try:
                        # Remove directory
                        shutil.rmtree(workspaces_root_path)
                    except OSError:
                        # No file
                        pass

                # Move the directory to workspace root path
                shutil.move(workspaces_path, workspaces_root_path)

                # Create appropriate symbolic link
                if os.path.isdir(workspaces_root_path):
                    os.symlink(workspaces_root_path, workspaces_path)
                    print('INFO: Successfully linked "workspaces" directory to TETHYS_WORKSPACES_ROOT for app "{0}".'.format(app))

