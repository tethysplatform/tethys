"""
********************************************************************************
* Name: syncstores.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.core.management.base import BaseCommand
from tethys_cli.cli_colors import TC_BLUE, TC_WARNING, TC_ENDC

ALL_APPS = 'all'

# TODO: remove syncstores interface and update documentation once able to initialize/create persistent stores from app
# admin interface


class Command(BaseCommand):
    """
    Command class that handles the syncstores command. Provides persistent store management functionality.
    """
    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='+', type=str)
        parser.add_argument('-r', '--refresh',
                            action='store_true',
                            dest='refresh',
                            default=False,
                            help='When called with this option, the database will be dropped prior to syncing '
                                 'resulting in a refreshed database.'),
        parser.add_argument('-f', '--firsttime',
                            action='store_true',
                            dest='first_time',
                            default=False,
                            help='Call with this option to force the initializer functions to be executed with '
                                 '"first_time" parameter True.'),
        parser.add_argument('-d', '--database',
                            help='Name of database to sync.')

    def handle(self, *args, **options):
        """
        Handle the command
        """
        self.provision_persistent_stores(options['app_name'], options)

    def provision_persistent_stores(self, app_names, options):
        """
        Provision all persistent stores for all apps or for only the app name given.
        """
        from tethys_apps.models import TethysApp

        # Execute on all apps loaded
        if ALL_APPS in app_names:
            target_apps = TethysApp.objects.all()

        # Execute only on apps given
        else:
            target_apps = TethysApp.objects.filter(package__in=app_names)

            # Verify all apps included in target apps
            target_app_names = [a.package for a in target_apps]
            for app_name in app_names:
                if app_name not in target_app_names:
                    self.stdout.write('{0}WARNING:{1} The app named "{2}" cannot be found. '
                                      'Please make sure it is installed '
                                      'and try again.'.format(TC_WARNING, TC_ENDC, app_name))

        # Notify user of database provisioning
        self.stdout.write(TC_BLUE + '\nProvisioning Persistent Stores...' + TC_ENDC)

        # Get apps and provision persistent stores if not already created
        for app in target_apps:
            ps_db_settings = app.persistent_store_database_settings

            # Assemble list of target persistent stores
            target_ps_db_settings = []

            # Target the persistent store provided
            if options['database']:
                for ps_db_setting in ps_db_settings:
                    if options['database'] == ps_db_setting.name:
                        target_ps_db_settings.append(ps_db_setting)

            # Target all persistent stores
            else:
                target_ps_db_settings = ps_db_settings

            for target_ps_db_setting in target_ps_db_settings:
                target_ps_db_setting.create_persistent_store_database(
                    refresh=options['refresh'],
                    force_first_time=options['first_time']
                )
