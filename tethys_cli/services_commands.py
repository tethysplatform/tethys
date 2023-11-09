from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict

from .cli_colors import BOLD, pretty_output, FG_RED, FG_GREEN
from .cli_helpers import add_geoserver_rest_to_endpoint, setup_django

SERVICES_CREATE = "create"
SERVICES_CREATE_PERSISTENT = "persistent"
SERVICES_CREATE_SPATIAL = "spatial"
SERVICES_LINK = "link"
SERVICES_LIST = "list"


class FormatError(Exception):
    def __init__(self):
        Exception.__init__(self)


def add_services_parser(subparsers):
    # SERVICES COMMANDS
    services_parser = subparsers.add_parser(
        "services", help="Services commands for Tethys Platform."
    )
    services_subparsers = services_parser.add_subparsers(title="Commands")

    # tethys services remove
    services_remove_parser = services_subparsers.add_parser(
        "remove", help="Remove a Tethys Service."
    )
    services_remove_subparsers = services_remove_parser.add_subparsers(
        title="Service Type"
    )

    # tethys services remove persistent
    services_remove_persistent = services_remove_subparsers.add_parser(
        "persistent", help="Remove a Persistent Store Service."
    )
    services_remove_persistent.add_argument(
        "service_uid",
        help="The ID or name of the Persistent Store Service that you are removing.",
    )
    services_remove_persistent.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    services_remove_persistent.set_defaults(func=services_remove_persistent_command)

    # tethys services remove spatial
    services_remove_spatial = services_remove_subparsers.add_parser(
        "spatial", help="Remove a Spatial Dataset Service."
    )
    services_remove_spatial.add_argument(
        "service_uid",
        help="The ID or name of the Spatial Dataset Service that you are removing.",
    )
    services_remove_spatial.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    services_remove_spatial.set_defaults(func=services_remove_spatial_command)

    # tethys services remove Dataset
    services_remove_dataset = services_remove_subparsers.add_parser(
        "dataset", help="Remove a Dataset Service."
    )
    services_remove_dataset.add_argument(
        "service_uid",
        help="The ID or name of the Dataset Service that you are removing.",
    )
    services_remove_dataset.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    services_remove_dataset.set_defaults(func=services_remove_dataset_command)

    # tethys services remove Dataset
    services_remove_wps = services_remove_subparsers.add_parser(
        "wps", help="Remove a WPS Service."
    )
    services_remove_wps.add_argument(
        "service_uid", help="The ID or name of the WPS Service that you are removing."
    )
    services_remove_wps.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    services_remove_wps.set_defaults(func=services_remove_wps_command)

    # tethys services create
    services_create_parser = services_subparsers.add_parser(
        "create", help="Create a Tethys Service."
    )
    services_create_subparsers = services_create_parser.add_subparsers(
        title="Service Type"
    )

    # tethys services create persistent
    services_create_ps = services_create_subparsers.add_parser(
        "persistent", help="Create a Persistent Store Service."
    )
    services_create_ps.add_argument(
        "-n", "--name", required=True, help="A unique name for the Service", type=str
    )
    services_create_ps.add_argument(
        "-c",
        "--connection",
        required=True,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<host>:<port>"',
    )
    services_create_ps.set_defaults(func=services_create_persistent_command)

    # tethys services create spatial
    services_create_sd = services_create_subparsers.add_parser(
        "spatial", help="Create a Spatial Dataset Service."
    )
    services_create_sd.add_argument(
        "-n", "--name", required=True, help="A unique name for the Service", type=str
    )
    services_create_sd.add_argument(
        "-t",
        "--type",
        required=False,
        type=str,
        choices=["GeoServer", "THREDDS"],
        default="GeoServer",
        help="Type of spatial dataset service being created (GeoServer/THREDDS).",
    )
    services_create_sd.add_argument(
        "-c",
        "--connection",
        required=True,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<protocol>//<host>:<port>"',
    )
    services_create_sd.add_argument(
        "-p",
        "--public-endpoint",
        type=str,
        help="The public-facing endpoint, if different than what was provided with the "
        '--connection argument, of the form "<host>:<port>"',
    )
    services_create_sd.add_argument(
        "-k",
        "--apikey",
        type=str,
        help="The API key, if any, required to establish a connection.",
    )
    services_create_sd.set_defaults(func=services_create_spatial_command)

    # tethys services create dataset
    services_create_dataset = services_create_subparsers.add_parser(
        "dataset", help="Create a CKAN/HydroShare Dataset Service."
    )
    services_create_dataset.add_argument(
        "-n", "--name", required=True, help="A unique name for the Service", type=str
    )
    services_create_dataset.add_argument(
        "-t",
        "--type",
        required=True,
        type=str,
        choices=["CKAN", "HydroShare"],
        help="Type of dataset service being created (CKAN/HydroShare).",
    )
    services_create_dataset.add_argument(
        "-c",
        "--connection",
        required=True,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<protocol>//<host>:<port>"',
    )
    services_create_dataset.add_argument(
        "-p",
        "--public-endpoint",
        required=False,
        type=str,
        help="The public-facing endpoint, \
                                             if different than what was provided with the "
        '--connection argument, of the form "<host>:<port>"',
    )
    services_create_dataset.add_argument(
        "-k",
        "--apikey",
        required=False,
        type=str,
        help="The API key, if any, required to establish a connection.",
    )
    services_create_dataset.set_defaults(func=services_create_dataset_command)

    # tethys services create WPS
    services_create_wps = services_create_subparsers.add_parser(
        "wps", help="Create a Web Processing Service."
    )
    services_create_wps.add_argument(
        "-n", "--name", required=True, help="A unique name for the Service", type=str
    )
    services_create_wps.add_argument(
        "-c",
        "--connection",
        required=True,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<protocol>//<host>:<port>"',
    )
    services_create_wps.set_defaults(func=services_create_wps_command)

    # tethys services list
    services_list_parser = services_subparsers.add_parser(
        "list", help="List all existing Tethys Services."
    )
    group = services_list_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-p",
        "--persistent",
        action="store_true",
        help="Only list Persistent Store Services.",
    )
    group.add_argument(
        "-s",
        "--spatial",
        action="store_true",
        help="Only list Spatial Dataset Services.",
    )
    group.add_argument(
        "-d", "--dataset", action="store_true", help="Only list Dataset Services."
    )
    group.add_argument(
        "-w", "--wps", action="store_true", help="Only list Web Processing Services."
    )
    services_list_parser.set_defaults(func=services_list_command)


def services_create_persistent_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import PersistentStoreService

    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split("@")
        cred_parts = parts[0].split(":")
        store_username = cred_parts[0]
        store_password = cred_parts[1]
        url_parts = parts[1].split(":")
        host = url_parts[0]
        port = url_parts[1]

        new_persistent_service = PersistentStoreService(
            name=name,
            host=host,
            port=port,
            username=store_username,
            password=store_password,
        )
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write("Successfully created new Persistent Store Service!")
    except AttributeError:
        with pretty_output(FG_RED) as p:
            p.write("Missing Input Parameters. Please check your input.")
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write(
                'The connection argument (-c) must be of the form "<username>:<password>@<host>:<port>".'
            )
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write(
                'Persistent Store Service with name "{0}" already exists. Command aborted.'.format(
                    name
                )
            )


def services_create_spatial_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import SpatialDatasetService

    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split("@")
        cred_parts = parts[0].split(":")
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]
        public_endpoint = args.public_endpoint or ""
        apikey = args.apikey or ""
        service_type = args.type

        engines = {
            "GeoServer": SpatialDatasetService.GEOSERVER,
            "THREDDS": SpatialDatasetService.THREDDS,
        }

        if "http" not in endpoint or "://" not in endpoint:
            raise IndexError()
        if (
            public_endpoint
            and "http" not in public_endpoint
            or "://" not in public_endpoint
        ):
            raise FormatError()

        if service_type == "GeoServer":
            endpoint = add_geoserver_rest_to_endpoint(endpoint)
            if public_endpoint:
                public_endpoint = add_geoserver_rest_to_endpoint(public_endpoint)

        new_persistent_service = SpatialDatasetService(
            name=name,
            endpoint=endpoint,
            public_endpoint=public_endpoint,
            apikey=apikey,
            username=service_username,
            password=service_password,
            engine=engines[service_type],
        )
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write("Successfully created new Spatial Dataset Service!")
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write(
                "The connection argument (-c) must be of the form "
                '"<username>:<password>@<protocol>//<host>:<port>".'
            )
    except FormatError:
        with pretty_output(FG_RED) as p:
            p.write(
                'The public_endpoint argument (-p) must be of the form "<protocol>//<host>:<port>".'
            )
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write(
                'Spatial Dataset Service with name "{0}" already exists. Command aborted.'.format(
                    name
                )
            )


def services_create_dataset_command(args):
    """
    Interact with Tethys Services (Datasets) to create them and/or link them to existing apps
    """
    from tethys_services.models import DatasetService

    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split("@")
        cred_parts = parts[0].split(":")
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]
        public_endpoint = args.public_endpoint or ""
        apikey = args.apikey or ""
        service_type = args.type

        engines = {"CKAN": DatasetService.CKAN, "HydroShare": DatasetService.HYDROSHARE}

        if "http" not in endpoint or "://" not in endpoint:
            raise IndexError()

        if public_endpoint != "":
            if "http" not in public_endpoint or "://" not in public_endpoint:
                raise FormatError()

        new_persistent_service = DatasetService(
            name=name,
            endpoint=endpoint,
            public_endpoint=public_endpoint,
            apikey=apikey,
            username=service_username,
            password=service_password,
            engine=engines[service_type],
        )
        new_persistent_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write("Successfully created new Dataset Service!")
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write(
                "The connection argument (-c) must be of the form "
                '"<username>:<password>@<protocol>//<host>:<port>".'
            )
    except FormatError:
        with pretty_output(FG_RED) as p:
            p.write(
                "The public_endpoint argument (-p) must be of the form "
                '"<protocol>//<host>:<port>".'
            )
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write(
                'Dataset Service with name "{0}" already exists. Command aborted.'.format(
                    name
                )
            )


def services_create_wps_command(args):
    """
    Interact with Tethys Services (WPS) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import WebProcessingService as currentService

    name = None

    try:
        name = args.name
        connection = args.connection
        parts = connection.split("@")
        cred_parts = parts[0].split(":")
        service_username = cred_parts[0]
        service_password = cred_parts[1]
        endpoint = parts[1]

        if "http" not in endpoint or "://" not in endpoint:
            raise IndexError()

        new_service = currentService(
            name=name,
            endpoint=endpoint,
            username=service_username,
            password=service_password,
        )
        new_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write("Successfully created new Web Processing Service!")

        return new_service
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write(
                "The connection argument (-c) must be of the form "
                '"<username>:<password>@<protocol>//<host>:<port>".'
            )
    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write(
                'Web Processing Service with name "{0}" already exists. Command aborted.'.format(
                    name
                )
            )


def remove_service(serviceType, args):
    setup_django()
    from tethys_services.models import (
        SpatialDatasetService,
        DatasetService,
        PersistentStoreService,
        WebProcessingService,
    )

    services = {
        "spatial": SpatialDatasetService,
        "dataset": DatasetService,
        "persistent": PersistentStoreService,
        "wps": WebProcessingService,
    }

    service = services.get(serviceType)
    service_label = str(service)
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
                p.write(
                    "Successfully removed {0} Service {1}!".format(
                        service_label, service_id
                    )
                )
            exit(0)
        else:
            proceed = input(
                "Are you sure you want to delete this {0} Service? [y/n]: ".format(
                    service_label
                )
            )
            while proceed not in ["y", "n", "Y", "N"]:
                proceed = input('Please enter either "y" or "n": ')

            if proceed in ["y", "Y"]:
                service.delete()
                with pretty_output(FG_GREEN) as p:
                    p.write(
                        "Successfully removed {0} Service {1}!".format(
                            service_label, service_id
                        )
                    )
                exit(0)
            else:
                with pretty_output(FG_RED) as p:
                    p.write("Aborted. {0} Service not removed.".format(service_label))
                exit(0)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                'A {0} Service with ID/Name "{1}" does not exist.'.format(
                    service_label, service_id
                )
            )
        exit(0)


def services_remove_spatial_command(args):
    remove_service("spatial", args)


def services_remove_dataset_command(args):
    remove_service("dataset", args)


def services_remove_persistent_command(args):
    remove_service("persistent", args)


def services_remove_wps_command(args):
    remove_service("wps", args)


def services_list_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import (
        SpatialDatasetService,
        PersistentStoreService,
        DatasetService,
        WebProcessingService,
    )

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
        persistent_entries = PersistentStoreService.objects.order_by("id").all()
        entries.append(persistent_entries)
        if len(persistent_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write("\nPersistent Store Services:")
            is_first_entry = True
            for entry in persistent_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            "{0: <3}{1: <50}{2: <25}{3: <6}".format(
                                "ID", "Name", "Host", "Port"
                            )
                        )
                    is_first_entry = False
                print(
                    "{0: <3}{1: <50}{2: <25}{3: <6}".format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["host"],
                        model_dict["port"],
                    )
                )

    if list_spatial:
        spatial_entries = SpatialDatasetService.objects.order_by("id").all()
        entries.append(spatial_entries)
        if len(spatial_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write("\nSpatial Dataset Services:")
            is_first_entry = True
            for entry in spatial_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            "{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}".format(
                                "ID", "Name", "Endpoint", "Public Endpoint", "API Key"
                            )
                        )
                    is_first_entry = False
                print(
                    "{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}".format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["endpoint"],
                        model_dict["public_endpoint"],
                        model_dict["apikey"] if model_dict["apikey"] else "None",
                    )
                )
    if list_dataset:
        dataset_entries = DatasetService.objects.order_by("id").all()
        entries.append(dataset_entries)
        if len(dataset_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write("\nDataset Services:")
            is_first_entry = True
            for entry in dataset_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            "{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}".format(
                                "ID", "Name", "Endpoint", "Public Endpoint", "API Key"
                            )
                        )
                    is_first_entry = False
                print(
                    "{0: <3}{1: <50}{2: <50}{3: <50}{4: <30}".format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["endpoint"],
                        model_dict["public_endpoint"],
                        model_dict["apikey"] if model_dict["apikey"] else "None",
                    )
                )
    if list_wps:
        service_entries = WebProcessingService.objects.order_by("id").all()
        entries.append(service_entries)
        if len(service_entries) > 0:
            with pretty_output(BOLD) as p:
                p.write("\nWeb Processing Services:")
            is_first_entry = True
            for entry in service_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            "{0: <3}{1: <50}{2: <50}{3: <50}".format(
                                "ID", "Name", "Endpoint", "Public Endpoint"
                            )
                        )
                    is_first_entry = False
                print(
                    "{0: <3}{1: <50}{2: <50}{3: <50}".format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["endpoint"],
                        model_dict["public_endpoint"],
                    )
                )

    return entries
