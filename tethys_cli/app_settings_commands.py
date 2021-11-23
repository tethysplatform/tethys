from django.core.exceptions import ValidationError
from tethys_apps.utilities import get_app_settings, get_custom_setting
from tethys_cli.cli_colors import pretty_output, BOLD, write_error, write_success
from tethys_cli.cli_helpers import load_apps


def add_app_settings_parser(subparsers):
    # APP_SETTINGS COMMANDS
    app_settings_parser = subparsers.add_parser('app_settings', help='Interact with Tethys App Settings.')
    app_settings_subparsers = app_settings_parser.add_subparsers(title='Options')

    # tethys app_settings list
    app_settings_list_parser = app_settings_subparsers.add_parser('list', help='List all settings for a specified app')
    app_settings_list_parser.add_argument('app', help='The app ("<app_package>") to list the Settings for.')
    app_settings_list_parser.set_defaults(func=app_settings_list_command)

    # tethys app_settings set
    app_settings_set_parser = app_settings_subparsers.add_parser('set', help='Set the value of a custom setting '
                                                                             'for a specified app.')
    app_settings_set_parser.add_argument('app', help='The app ("<app_package>") with the setting to be set.')
    app_settings_set_parser.add_argument('setting', help='The name of the setting to be set.')
    app_settings_set_parser.add_argument('value', help='The value to set.')
    app_settings_set_parser.set_defaults(func=app_settings_set_command)

    # tethys app_settings set
    app_settings_reset_parser = app_settings_subparsers.add_parser('reset', help='Reset the value of a custom setting '
                                                                                 'to its default value.')
    app_settings_reset_parser.add_argument('app', help='The app ("<app_package>") with the setting to be reset.')
    app_settings_reset_parser.add_argument('setting', help='The name of the setting to be reset.')
    app_settings_reset_parser.set_defaults(func=app_settings_reset_command)

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
    load_apps()
    app_settings = get_app_settings(args.app)
    if app_settings is None:
        return
    unlinked_settings = app_settings['unlinked_settings']
    linked_settings = app_settings['linked_settings']

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
                                                          get_setting_type(setting)))

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

            if hasattr(setting, 'persistent_store_service'):
                service_name = setting.persistent_store_service.name
            elif hasattr(setting, 'spatial_dataset_service'):
                service_name = setting.spatial_dataset_service.name
            elif hasattr(setting, 'dataset_service'):
                service_name = setting.dataset_service.name
            elif hasattr(setting, 'web_processing_service'):
                service_name = setting.web_processing_service.name
            elif hasattr(setting, 'value'):
                service_name = setting.value

            with pretty_output() as p:
                p.write(f'{setting.pk: <10}{setting.name: <40}{get_setting_type(setting): <15}{service_name: <20}')


def app_settings_set_command(args):
    load_apps()
    setting = get_custom_setting(args.app, args.setting)

    if not setting:
        write_error(f'No such Custom Setting "{args.setting}" for app "{args.app}".')
        exit(1)

    try:
        setting.value = args.value
        setting.clean()
        setting.save()
    except ValidationError as e:
        write_error(f'Value was not set: {",".join(e.messages)} "{args.value}" was given.')
        exit(1)

    write_success(f'Success! Custom Setting "{args.setting}" for app "{args.app}" was set to "{args.value}".')
    exit(0)


def app_settings_reset_command(args):
    load_apps()
    setting = get_custom_setting(args.app, args.setting)

    if not setting:
        write_error(f'No such Custom Setting "{args.setting}" for app "{args.app}".')
        exit(1)

    setting.value = setting.default
    setting.save()

    write_success(f'Success! Custom Setting "{args.setting}" for app "{args.app}" '
                  f'was reset to the default value of "{setting.value}".')
    exit(0)


def get_setting_type(setting):
    from tethys_apps.models import (PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting,
                                    SpatialDatasetServiceSetting, DatasetServiceSetting, WebProcessingServiceSetting,
                                    CustomSetting)

    setting_type_dict = {
        PersistentStoreConnectionSetting: 'ps_connection',
        PersistentStoreDatabaseSetting: 'ps_database',
        SpatialDatasetServiceSetting: 'ds_spatial',
        DatasetServiceSetting: 'ds_dataset',
        WebProcessingServiceSetting: 'wps',
        CustomSetting: 'custom_setting'
    }

    return setting_type_dict[type(setting)]


def app_settings_create_ps_database_command(args):
    load_apps()
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
    load_apps()
    from tethys_apps.utilities import remove_ps_database_setting
    app_package = args.app
    setting_name = args.name
    force = args.force
    success = remove_ps_database_setting(app_package, setting_name, force)

    if not success:
        exit(1)

    exit(0)
