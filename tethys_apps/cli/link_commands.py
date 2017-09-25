from django.core.exceptions import ObjectDoesNotExist

from .cli_colors import *


def link_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    from tethys_apps.models import TethysApp
    from tethys_sdk.app_settings import (SpatialDatasetServiceSetting, PersistentStoreConnectionSetting,
                                         PersistentStoreDatabaseSetting)
    from tethys_services.models import (SpatialDatasetService, PersistentStoreService)

    service_type_to_model_dict = {
        'spatial': SpatialDatasetService,
        'persistent': PersistentStoreService
    }

    setting_type_to_link_model_dict = {
        'ps_database': {
            'setting_model': PersistentStoreDatabaseSetting,
            'service_field': 'persistent_store_service'
        },
        'ps_connection': {
            'setting_model': PersistentStoreConnectionSetting,
            'service_field': 'persistent_store_service'
        },
        'ds_spatial': {
            'setting_model': SpatialDatasetServiceSetting,
            'service_field': 'spatial_dataset_service'
        }
    }

    try:
        service = args.service
        setting = args.setting

        service_parts = service.split(':')
        setting_parts = setting.split(':')
        service_type = None
        service_uid = None
        setting_app_package = None
        setting_type = None
        setting_uid = None

        try:
            service_type = service_parts[0]
            service_uid = service_parts[1]

            setting_app_package = setting_parts[0]
            setting_type = setting_parts[1]
            setting_uid = setting_parts[2]
        except IndexError:
            with pretty_output(FG_RED) as p:
                p.write(
                    'Incorrect argument format. \nUsage: "tethys link <spatial|persistent>:<service_id|service_name> '
                    '<app_package>:<setting_type (ps_database|ps_connection|ds_spatial)><setting_id|setting_name>"'
                    '\nCommand aborted.')
            exit(1)

        service_model = service_type_to_model_dict[service_type]

        try:
            try:
                service_uid = int(service_uid)
                service = service_model.objects.get(pk=service_uid)
            except ValueError:
                service = service_model.objects.get(name=service_uid)
        except ObjectDoesNotExist:
            with pretty_output(FG_RED) as p:
                p.write('A {0} with ID/Name "{1}" does not exist.'.format(str(service_model), service_uid))
            exit(1)

        app = None
        try:
            app = TethysApp.objects.get(package=setting_app_package)
        except ObjectDoesNotExist:
            with pretty_output(FG_RED) as p:
                p.write('The app you specified ("{0}") does not exist.'.format(setting_app_package))
            exit(1)

        linked_setting_model_dict = None
        try:
            linked_setting_model_dict = setting_type_to_link_model_dict[setting_type]
        except KeyError:
            with pretty_output(FG_RED) as p:
                p.write('The setting_type you specified ("{0}") does not exist.'
                        '\nChoose from: "ps_database|ps_connection|ds_spatial"'.format(setting_type))
            exit(1)

        linked_setting_model = linked_setting_model_dict['setting_model']
        linked_service_field = linked_setting_model_dict['service_field']

        try:
            try:
                setting_uid = int(setting_uid)
                setting = linked_setting_model.objects.get(tethys_app=app, pk=setting_uid)
            except ValueError:
                setting = linked_setting_model.objects.get(tethys_app=app, name=setting_uid)
        except ObjectDoesNotExist:
            with pretty_output(FG_RED) as p:
                p.write('A {0} with ID/Name "{1}" does not exist.'.format(str(linked_setting_model), setting_uid))
            exit(1)

        setattr(setting, linked_service_field, service)

        setting.save()

    except Exception as e:
        print e
        with pretty_output(FG_RED) as p:
            p.write('An unexpected error occurred. Please try again.')
