from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict

from .cli_colors import BOLD, pretty_output, FG_RED, FG_GREEN
from .cli_helpers import add_geoserver_rest_to_endpoint

SERVICES_CREATE = 'create'
SERVICES_CREATE_PERSISTENT = 'persistent'
SERVICES_CREATE_SPATIAL = 'spatial'
SERVICES_LINK = 'link'
SERVICES_LIST = 'list'


class FormatError(Exception):
    def __init__(self):
        Exception.__init__(self)


def services_create_persistent_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    from tethys_services.models import PersistentStoreService
    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split('@')
        cred_parts = parts[0].split(':')
        store_username = cred_parts[0]
        store_password = cred_parts[1]
        url_parts = parts[1].split(':')
        host = url_parts[0]
        port = url_parts[1]

        new_persistent_service = PersistentStoreService(name=name, host=host, port=port,
                                                        username=store_username, password=store_password)
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write('Successfully created new Persistent Store Service!')
    except AttributeError:
        with pretty_output(FG_RED) as p:
            p.write('Missing Input Parameters. Please check your input.')
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write('The connection argument (-c) must be of the form "<username>:<password>@<host>:<port>".')
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write('Persistent Store Service with name "{0}" already exists. Command aborted.'.format(name))


def services_create_spatial_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    from tethys_services.models import SpatialDatasetService
    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split('@')
        cred_parts = parts[0].split(':')
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]
        public_endpoint = args.public_endpoint or ''
        apikey = args.apikey or ''

        if 'http' not in endpoint or '://' not in endpoint:
            raise IndexError()
        if public_endpoint and 'http' not in public_endpoint or '://' not in public_endpoint:
            raise FormatError()

        endpoint = add_geoserver_rest_to_endpoint(endpoint)
        if public_endpoint:
            public_endpoint = add_geoserver_rest_to_endpoint(public_endpoint)

        new_persistent_service = SpatialDatasetService(name=name, endpoint=endpoint, public_endpoint=public_endpoint,
                                                       apikey=apikey, username=service_username,
                                                       password=service_password)
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write('Successfully created new Spatial Dataset Service!')
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write('The connection argument (-c) must be of the form '
                    '"<username>:<password>@<protocol>//<host>:<port>".')
    except FormatError:
        with pretty_output(FG_RED) as p:
            p.write('The public_endpoint argument (-p) must be of the form "<protocol>//<host>:<port>".')
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write('Spatial Dataset Service with name "{0}" already exists. Command aborted.'.format(name))


def services_create_dataset_command(args):
    """
    Interact with Tethys Services (Datasets) to create them and/or link them to existing apps
    """
    from tethys_services.models import DatasetService
    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split('@')
        cred_parts = parts[0].split(':')
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]
        public_endpoint = args.public_endpoint or ''
        apikey = args.apikey or ''
        serviceType = args.type

        if 'http' not in endpoint or '://' not in endpoint:
            raise IndexError()

        if (public_endpoint != ""):
            if ('http' not in public_endpoint or '://' not in public_endpoint):
                raise FormatError()

        new_persistent_service = DatasetService(name=name, endpoint=endpoint, public_endpoint=public_endpoint,
                                                apikey=apikey, username=service_username,
                                                password=service_password, engine=serviceType)
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write('Successfully created new Dataset Service!')
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write('The connection argument (-c) must be of the form '
                    '"<username>:<password>@<protocol>//<host>:<port>".')
    except FormatError:
        with pretty_output(FG_RED) as p:
            p.write('The public_endpoint argument (-p) must be of the form '
                    '"<protocol>//<host>:<port>".')
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write('Dataset Service with name "{0}" already exists. Command aborted.'.format(name))


def services_create_wps_command(args):
    """
    Interact with Tethys Services (WPS) to create them and/or link them to existing apps
    """
    from tethys_services.models import WebProcessingService as currentService
    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split('@')
        cred_parts = parts[0].split(':')
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]

        if 'http' not in endpoint or '://' not in endpoint:
            raise IndexError()

        new_service = currentService(
            name=name, endpoint=endpoint, username=service_username, password=service_password)
        new_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write('Successfully created new Web Processing Service!')

        return new_service
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write('The connection argument (-c) must be of the form '
                    '"<username>:<password>@<protocol>//<host>:<port>".')
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write('Web Processing Service with name "{0}" already exists. Command aborted.'.format(name))


def remove_service(serviceType, args):

    from tethys_services.models import (SpatialDatasetService, DatasetService,
                                        PersistentStoreService, WebProcessingService)

    services = {
        "spatial": SpatialDatasetService,
        "dataset": DatasetService,
        "persistent": PersistentStoreService,
        'wps': WebProcessingService
    }

    service = services.get(serviceType)
    serviceLabel = str(service)
    service_id = None

    try:
        service_id = args.service_uid
        force = args.force

        try:
            service_id = int(service_id)
            service = service.objects.get(pk=service_id)
        except ValueError:
            service = service.objects.get(name=service_id)

        if force:
            service.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed {0} Service {1}!'.format(serviceLabel, service_id))
            exit(0)
        else:
            proceed = input(
                'Are you sure you want to delete this {0} Service? [y/n]: '.format(serviceLabel))
            while proceed not in ['y', 'n', 'Y', 'N']:
                proceed = input('Please enter either "y" or "n": ')

            if proceed in ['y', 'Y']:
                service.delete()
                with pretty_output(FG_GREEN) as p:
                    p.write('Successfully removed {0} Service {1}!'.format(serviceLabel, service_id))
                exit(0)
            else:
                with pretty_output(FG_RED) as p:
                    p.write('Aborted. {0} Service not removed.'.format(serviceLabel))
                exit(0)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A {0} Service with ID/Name "{1}" does not exist.'.format(serviceLabel, service_id))
        exit(0)


def services_remove_spatial_command(args):
    remove_service('spatial', args)


def services_remove_dataset_command(args):
    remove_service('dataset', args)


def services_remove_persistent_command(args):
    remove_service('persistent', args)


def services_remove_wps_command(args):
    remove_service('wps', args)


def services_list_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    from tethys_services.models import (SpatialDatasetService, PersistentStoreService,
                                        DatasetService, WebProcessingService)
    list_persistent = False
    list_spatial = False
    list_dataset = False
    list_wps = False

    if not args.spatial and not args.persistent and not args.dataset and not args.wps:
        list_persistent = True
        list_spatial = True
        list_dataset = True
        list_wps = True
    elif args.spatial:
        list_spatial = True
    elif args.persistent:
        list_persistent = True
    elif args.dataset:
        list_dataset = True
    elif args.wps:
        list_wps = True

    entries = []
    if list_persistent:
        persistent_entries = PersistentStoreService.objects.order_by('id').all()
        entries.append(persistent_entries)
        if len(persistent_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write('\nPersistent Store Services:')
            is_first_entry = True
            for entry in persistent_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <3}{1: <50}{2: <25}{3: <6}'.format('ID', 'Name', 'Host', 'Port'))
                    is_first_entry = False
                print('{0: <3}{1: <50}{2: <25}{3: <6}'.format(model_dict['id'], model_dict['name'],
                                                              model_dict['host'], model_dict['port']))

    if list_spatial:
        spatial_entries = SpatialDatasetService.objects.order_by('id').all()
        entries.append(spatial_entries)
        if len(spatial_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write('\nSpatial Dataset Services:')
            is_first_entry = True
            for entry in spatial_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}'.format('ID', 'Name', 'Endpoint',
                                                                                 'Public Endpoint', 'API Key'))
                    is_first_entry = False
                print('{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}'.format(model_dict['id'], model_dict['name'],
                                                                       model_dict['endpoint'],
                                                                       model_dict['public_endpoint'],
                                                                       model_dict['apikey'] if model_dict['apikey']
                                                                       else "None"))
    if list_dataset:
        dataset_entries = DatasetService.objects.order_by('id').all()
        entries.append(dataset_entries)
        if len(dataset_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write('\nDataset Services:')
            is_first_entry = True
            for entry in dataset_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}'.format('ID', 'Name', 'Endpoint',
                                                                                 'Public Endpoint', 'API Key'))
                    is_first_entry = False
                print('{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}'.format(model_dict['id'], model_dict['name'],
                                                                       model_dict['endpoint'],
                                                                       model_dict['public_endpoint'],
                                                                       model_dict['apikey'] if model_dict['apikey']
                                                                       else "None"))
    if list_wps:
        service_entries = WebProcessingService.objects.order_by('id').all()
        entries.append(service_entries)
        if len(service_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write('\nWeb Processing Services:')
            is_first_entry = True
            for entry in service_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write('{0: <3}{1: <50}{2: <50}{3: <50}'.format('ID', 'Name', 'Endpoint',
                                                                         'Public Endpoint'))
                    is_first_entry = False
                print('{0: <3}{1: <50}{2: <50}{3: <50}'.format(model_dict['id'], model_dict['name'],
                                                               model_dict['endpoint'],
                                                               model_dict['public_endpoint']))

    return entries
