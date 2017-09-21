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
    Command class that handles the collectworkspaces command.
    """

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', action='store_true', default=False,
                            help='Force the overwrite the app directory into its collected-to location.')

    def handle(self, *args, **options):
        """
        Symbolically link the static directories of each app into the static/public directory specified by the
        STATIC_ROOT parameter of the settings.py. Do this prior to running Django's collectstatic method.
        """
        if not hasattr(settings, 'TETHYS_WORKSPACES_ROOT') or (hasattr(settings, 'TETHYS_WORKSPACES_ROOT')
                                                               and not settings.TETHYS_WORKSPACES_ROOT):
            print('WARNING: Cannot find the TETHYS_WORKSPACES_ROOT setting in the settings.py file. '
                  'Please provide the path to the static directory using the TETHYS_WORKSPACES_ROOT '
                  'setting and try again.')
            exit(1)
        # Get optional force arg
        force = options['force']

        # Read settings
        workspaces_root = settings.TETHYS_WORKSPACES_ROOT

        # Get a list of installed apps
        installed_apps = get_installed_tethys_apps()

        # Provide feedback to user
        print('INFO: Moving workspace directories of apps to "{0}" and linking back.'.format(workspaces_root))

        for app, path in installed_apps.items():
            # Check for both variants of the static directory (public and static)
            app_ws_path = os.path.join(path, 'workspaces')
            tethys_ws_root_path = os.path.join(workspaces_root, app)

            # Only perform if workspaces_path is a directory
            if not os.path.isdir(app_ws_path):
                print 'WARNING: The workspace_path for app "{}" is not a directory. Skipping...'.format(app)
                continue

            if not os.path.islink(app_ws_path):
                if not os.path.exists(tethys_ws_root_path):
                    # Move the directory to workspace root path
                    shutil.move(app_ws_path, tethys_ws_root_path)
                else:
                    if force:
                        # Clear out old symbolic links/directories in workspace root if necessary
                        try:
                            # Remove link
                            os.remove(tethys_ws_root_path)
                        except OSError:
                            shutil.rmtree(tethys_ws_root_path, ignore_errors=True)

                        # Move the directory to workspace root path
                        shutil.move(app_ws_path, tethys_ws_root_path)
                    else:
                        print('WARNING: Workspace directory for app "{}" already exists in the TETHYS_WORKSPACES_ROOT '
                              'directory. A symbolic link is being created to the existing directory. To force overwrite '
                              'the existing directory, re-run the command with the "-f" argument.'.format(app))
                        shutil.rmtree(app_ws_path, ignore_errors=True)

                # Create appropriate symbolic link
                if os.path.isdir(tethys_ws_root_path):
                    os.symlink(tethys_ws_root_path, app_ws_path)
                    print('INFO: Successfully linked "workspaces" directory to TETHYS_WORKSPACES_ROOT for app '
                          '"{0}".'.format(app))
            else:
                print('WARNING: Workspace directory for app "{}" is already symbolically linked to another directory '
                      'within the TETHYS_WORKSPACES_ROOT directory. Skipping... '.format(app))
