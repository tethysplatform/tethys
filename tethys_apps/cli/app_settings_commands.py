from tethys_apps.utilities import get_app_settings
from tethys_apps.cli.cli_colors import pretty_output, BOLD


def app_settings_list_command(args):
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

    app_settings = get_app_settings(args.app)
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

            if isinstance(setting, PersistentStoreConnectionSetting) or \
                    isinstance(setting, PersistentStoreDatabaseSetting):
                service_name = setting.persistent_store_service.name
            elif isinstance(setting, SpatialDatasetServiceSetting):
                service_name = setting.spatial_dataset_service.name
            elif isinstance(setting, DatasetServiceSetting):
                service_name = setting.dataset_service.name
            elif isinstance(setting, WebProcessingServiceSetting):
                service_name = setting.web_processing_service.name
            else:
                service_name = setting.value

            print('{0: <10}{1: <40}{2: <15}{3: <20}'.format(setting.pk, setting.name,
                                                            setting_type_dict[type(setting)], service_name))


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
