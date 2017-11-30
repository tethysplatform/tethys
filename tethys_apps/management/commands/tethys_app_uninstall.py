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
import subprocess
import warnings

from django.core.management.base import BaseCommand
from tethys_apps.helpers import get_installed_tethys_apps


class Command(BaseCommand):
    """
    Command class that handles the uninstall command for uninstall Tethys apps.
    """
    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Remove the app from disk and in the database
        """
        PREFIX = 'tethysapp'
        app_name = options['app_name'][0]
        installed_apps = get_installed_tethys_apps()

        if PREFIX in app_name:
            prefix_length = len(PREFIX) + 1
            app_name = app_name[prefix_length:]

        if app_name not in installed_apps:
            warnings.warn('WARNING: App with name "{0}" cannot be uninstalled, because it is not installed.'.format(app_name))
            exit(0)

        app_with_prefix = '{0}-{1}'.format(PREFIX, app_name)

        # Confirm
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')

        overwrite_input = raw_input('Are you sure you want to uninstall "{0}"? (y/n): '.format(app_with_prefix)).lower()

        while overwrite_input not in valid_inputs:
            overwrite_input = raw_input('Invalid option. Are you sure you want to '
                                        'uninstall "{0}"? (y/n): '.format(app_with_prefix)).lower()

        if overwrite_input in no_inputs:
            self.stdout.write('Uninstall cancelled by user.')
            exit(0)

        # Remove app from database
        from tethys_apps.models import TethysApp
        try:
            db_app = TethysApp.objects.get(package=app_name)
            db_app.delete()
        except TethysApp.DoesNotExist:
            warnings.warn('WARNING: The app was not found in the database.')

        try:
            # Remove directory
            shutil.rmtree(installed_apps[app_name])
        except OSError:
            # Remove symbolic link
            os.remove(installed_apps[app_name])

        # Uninstall using pip
        process = ['pip', 'uninstall', '-y', '{0}-{1}'.format(PREFIX, app_name)]

        try:
            subprocess.Popen(process, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
        except KeyboardInterrupt:
            pass

        self.stdout.write('App "{0}" successfully uninstalled.'.format(app_with_prefix))
