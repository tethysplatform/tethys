from cli_helpers import console_superuser_required
from django.core.exceptions import ObjectDoesNotExist
from tethys_apps.models import (TethysApp, PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting,
                                SpatialDatasetServiceSetting)

from .cli_colors import *

setting_type_dict = {
    PersistentStoreConnectionSetting: 'ps_connection',
    PersistentStoreDatabaseSetting: 'ps_database',
    SpatialDatasetServiceSetting: 'ds_spatial'
}


@console_superuser_required
def app_settings_list_command(args):
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
            if hasattr(setting, 'spatial_dataset_service') and setting.dataset_service \
                    or hasattr(setting, 'persistent_store_service') and setting.persistent_store_service:
                linked_settings.append(setting)
            else:
                unlinked_settings.append(setting)

        with pretty_output(BOLD) as p:
            p.write("\nUnlinked Settings:")

        if len(unlinked_settings) == 0:
            print 'None'
        else:
            is_first_row = True
            for setting in unlinked_settings:
                if is_first_row:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <10}{1: <40}{2: <15}'.format('ID', 'Name', 'Type'))
                    is_first_row = False
                print '{0: <10}{1: <40}{2: <15}'.format(setting.pk, setting.name, setting_type_dict[type(setting)])

        with pretty_output(BOLD) as p:
            p.write("\nLinked Settings:")

        if len(linked_settings) == 0:
            print 'None'
        else:
            is_first_row = True
            for setting in linked_settings:
                if is_first_row:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <10}{1: <40}{2: <15}{3: <20}'.format('ID', 'Name', 'Type', 'Linked With'))
                    is_first_row = False
                service_name = setting.spatial_dataset_service.name if hasattr(setting, 'spatial_dataset_service') \
                    else setting.persistent_store_service.name
                print '{0: <10}{1: <40}{2: <15}{3: <20}'.format(setting.pk, setting.name,
                                                                setting_type_dict[type(setting)], service_name)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('The app you specified ("{0}") does not exist. Command aborted.'.format(app_package))
    except Exception as e:
        print e
        with pretty_output(FG_RED) as p:
            p.write('Something went wrong. Please try again.')
