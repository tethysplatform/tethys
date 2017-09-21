from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from tethys_services.models import SpatialDatasetService, PersistentStoreService

from .cli_colors import *
from .cli_helpers import console_superuser_required, add_geoserver_rest_to_endpoint

SERVICES_CREATE = 'create'
SERVICES_CREATE_PERSISTENT = 'persistent'
SERVICES_CREATE_SPATIAL = 'spatial'
SERVICES_LINK = 'link'
SERVICES_LIST = 'list'


class FormatError(Exception):
    def __init__(self):
        Exception.__init__(self)


@console_superuser_required
def services_create_persistent_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
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
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write('The connection argument (-c) must be of the form "<username>:<password>@<host>:<port>".')
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write('Persistent Store Service with name "{0}" already exists. Command aborted.'.format(name))


@console_superuser_required
def services_remove_persistent_command(args):
    persistent_service_id = None

    try:
        persistent_service_id = args.service_id

        try:
            persistent_service_id = int(persistent_service_id)
            service = PersistentStoreService.objects.get(pk=persistent_service_id)
        except ValueError:
            service = PersistentStoreService.objects.get(name=persistent_service_id)

        proceed = raw_input('Are you sure you want to delete this Persistent Store Service? [y/n]: ')
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = raw_input('Please enter either "y" or "n": ')

        if proceed in ['y', 'Y']:
            service.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed Persistent Store Service {0}!'.format(persistent_service_id))
        else:
            with pretty_output(FG_RED) as p:
                p.write('Aborted. Persistent Store Service not removed.')
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A Persistent Store Service with ID/Name "{0}" does not exist.'.format(persistent_service_id))


@console_superuser_required
def services_create_spatial_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
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
            p.write('Successfully created new Persistent Store Service!')
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
            p.write('Spatial Dataset Service with name "{0}" already exists. Command aborted.'.format(name))


@console_superuser_required
def services_remove_spatial_command(args):
    spatial_service_id = None

    try:
        spatial_service_id = args.service_id

        try:
            spatial_service_id = int(spatial_service_id)
            service = SpatialDatasetService.objects.get(pk=spatial_service_id)
        except ValueError:
            service = SpatialDatasetService.objects.get(name=spatial_service_id)

        proceed = raw_input('Are you sure you want to delete this Persistent Store Service? [y/n]: ')
        while proceed not in ['y', 'n', 'Y', 'N']:
            proceed = raw_input('Please enter either "y" or "n": ')

        if proceed in ['y', 'Y']:
            service.delete()
            with pretty_output(FG_GREEN) as p:
                p.write('Successfully removed Persistent Store Service {0}!'.format(spatial_service_id))
        else:
            with pretty_output(FG_RED) as p:
                p.write('Aborted. Persistent Store Service not removed.')
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write('A Persistent Store Service with ID/Name "{0}" does not exist.'.format(spatial_service_id))


@console_superuser_required
def services_list_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    list_persistent = False
    list_spatial = False

    if not args.spatial and not args.persistent:
        list_persistent = True
        list_spatial = True
    elif args.spatial:
        list_spatial = True
    elif args.persistent:
        list_persistent = True

    if list_persistent:
        persistent_entries = PersistentStoreService.objects.order_by('id').all()
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
                print '{0: <3}{1: <50}{2: <25}{3: <6}'.format(model_dict['id'], model_dict['name'],
                                                              model_dict['host'], model_dict['port'])

    if list_spatial:
        spatial_entries = SpatialDatasetService.objects.order_by('id').all()
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
                print '{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}'.format(model_dict['id'], model_dict['name'],
                                                                       model_dict['endpoint'],
                                                                       model_dict['public_endpoint'],
                                                                       model_dict['apikey'] if model_dict['apikey']
                                                                       else "None")
