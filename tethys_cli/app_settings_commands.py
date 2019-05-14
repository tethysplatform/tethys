from django.core.exceptions import ObjectDoesNotExist

from tethys_cli.cli_colors import pretty_output, BOLD, FG_RED


def add_app_settings_parser(subparsers):
    # APP_SETTINGS COMMANDS
    app_settings_parser = subparsers.add_parser('app_settings', help='Interact with Tethys App Settings.')
    app_settings_subparsers = app_settings_parser.add_subparsers(title='Options')

    # tethys app_settings list
    app_settings_list_parser = app_settings_subparsers.add_parser('list', help='List all settings for a specified app')
    app_settings_list_parser.add_argument('app', help='The app ("<app_package>") to list the Settings for.')
    app_settings_list_parser.set_defaults(func=app_settings_list_command)

    # tethys app_settings create
    app_settings_create_cmd = app_settings_subparsers.add_parser('create', help='Create a Setting for an app.')

    asc_subparsers = app_settings_create_cmd.add_subparsers(title='Create Options')
    app_settings_create_cmd.add_argument('-a', '--app', required=True,
                                         help='The app ("<app_package>") to create the Setting for.')
    app_settings_create_cmd.add_argument('-n', '--name', required=True, help='The name of the Setting to create.')
    app_settings_create_cmd.add_argument('-d', '--description', required=False,
                                         help='A description for the Setting to create.')
    app_settings_create_cmd.add_argument('-r', '--required', required=False, action='store_true',
                                         help='Include this flag if the Setting is required for the app.')
    app_settings_create_cmd.add_argument('-i', '--initializer', required=False,
                                         help='The function that initializes the PersistentStoreSetting database.')
    app_settings_create_cmd.add_argument('-z', '--initialized', required=False, action='store_true',
                                         help='Include this flag if the database is already initialized.')

    # tethys app_settings create ps_database
    app_settings_create_psdb_cmd = asc_subparsers.add_parser('ps_database',
                                                             help='Create a PersistentStoreDatabaseSetting')
    app_settings_create_psdb_cmd.add_argument('-s', '--spatial', required=False, action='store_true',
                                              help='Include this flag if the database requires spatial capabilities.')
    app_settings_create_psdb_cmd.add_argument('-y', '--dynamic', action='store_true', required=False,
                                              help='Include this flag if the database should be considered to be '
                                                   'dynamically created.')
    app_settings_create_psdb_cmd.set_defaults(func=app_settings_create_ps_database_command)

    # tethys app_settings remove
    app_settings_remove_cmd = app_settings_subparsers.add_parser('remove', help='Remove a Setting for an app.')
    app_settings_remove_cmd.add_argument('app', help='The app ("<app_package>") to remove the Setting from.')
    app_settings_remove_cmd.add_argument('-n', '--name', help='The name of the Setting to remove.', required=True)
    app_settings_remove_cmd.add_argument('-f', '--force', action='store_true', help='Force removal without confirming.')
    app_settings_remove_cmd.set_defaults(func=app_settings_remove_command)


def app_settings_list_command(args):
    from tethys_apps.models import (TethysApp, PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting,
                                    SpatialDatasetServiceSetting)

    setting_type_dict = {
        PersistentStoreConnectionSetting: 'ps_connection',
        PersistentStoreDatabaseSetting: 'ps_database',
        SpatialDatasetServiceSetting: 'ds_spatial'
    }

    app_package = args.app
    try:
        app = TethysApp.objects.get(package=app_package)

        app_settings = []
        for setting in PersistentStoreConnectionSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in PersistentStoreDatabaseSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in SpatialDatasetServiceSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)

        unlinked_settings = []
        linked_settings = []

        for setting in app_settings:
            if hasattr(setting, 'spatial_dataset_service') and setting.spatial_dataset_service \
                    or hasattr(setting, 'persistent_store_service') and setting.persistent_store_service:
                linked_settings.append(setting)
            else:
                unlinked_settings.append(setting)

        with pretty_output(BOLD) as p:
            p.write("\nUnlinked Settings:")

        if len(unlinked_settings) == 0:
            with pretty_output() as p:
                p.write('None')
        else:
            is_first_row = True
            for setting in unlinked_settings:
                if is_first_row:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <10}{1: <40}{2: <15}'.format('ID', 'Name', 'Type'))
                    is_first_row = False
                with pretty_output() as p:
                    p.write('{0: <10}{1: <40}{2: <15}'.format(setting.pk, setting.name,
                                                              setting_type_dict[type(setting)]))

        with pretty_output(BOLD) as p:
            p.write("\nLinked Settings:")

        if len(linked_settings) == 0:
            with pretty_output() as p:
                p.write('None')
        else:
            is_first_row = True
            for setting in linked_settings:
                if is_first_row:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <10}{1: <40}{2: <15}{3: <20}'.format('ID', 'Name', 'Type', 'Linked With'))
                    is_first_row = False
                service_name = setting.spatial_dataset_service.name if hasattr(setting, 'spatial_dataset_service') \
                    else setting.persistent_store_service.name
                print('{0: <10}{1: <40}{2: <15}{3: <20}'.format(setting.pk, setting.name,
                                                                setting_type_dict[type(setting)], service_name))
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('The app you specified ("{0}") does not exist. Command aborted.'.format(app_package))
    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write('Something went wrong. Please try again.')


def app_settings_create_ps_database_command(args):
    from tethys_apps.utilities import create_ps_database_setting
    app_package = args.app
    setting_name = args.name
    setting_description = args.description
    required = args.required
    initializer = args.initializer
    initialized = args.initialized
    spatial = args.spatial
    dynamic = args.dynamic

    success = create_ps_database_setting(app_package, setting_name, setting_description or '',
                                         required, initializer or '', initialized, spatial, dynamic)

    if not success:
        exit(1)

    exit(0)


def app_settings_remove_command(args):
    from tethys_apps.utilities import remove_ps_database_setting
    app_package = args.app
    setting_name = args.name
    force = args.force
    success = remove_ps_database_setting(app_package, setting_name, force)

    if not success:
        exit(1)

    exit(0)
