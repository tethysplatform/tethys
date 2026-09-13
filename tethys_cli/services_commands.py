from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
import json

from .cli_colors import BOLD, pretty_output, FG_RED, FG_GREEN
from .cli_helpers import add_geoserver_rest_to_endpoint, setup_django


class FormatError(Exception):
    def __init__(self):
        Exception.__init__(self)


class MissingArgumentError(Exception):
    def __init__(self, error_message):
        Exception.__init__(self, error_message)


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

    # tethys services remove WPS
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

    # tethys services remove secure map
    services_remove_secure_map = services_remove_subparsers.add_parser(
        "secure-map", help="Remove a Secure Map Service."
    )
    services_remove_secure_map.add_argument(
        "service_uid",
        help="The ID or name of the Secure Map Service that you are removing.",
    )
    services_remove_secure_map.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    services_remove_secure_map.set_defaults(func=services_remove_secure_map_command)

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
        required=False,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<host>:<port>"',
    )
    services_create_ps.add_argument(
        "-d",
        "--dir_path",
        required=False,
        type=str,
        help="The directory path for the SQLite database file (only required if type is sqlite).",
    )
    services_create_ps.add_argument(
        "-t",
        "--type",
        required=False,
        type=str,
        choices=["postgres", "sqlite"],
        default="postgres",
        help="Type of persistent store service being created (postgres/sqlite). Default is postgres.",
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
        required=False,
        type=str,
        help="The connection of the Service in the form "
        '"<username>:<password>@<protocol>//<host>:<port>"',
    )
    services_create_sd.add_argument(
        "-e",
        "--endpoint",
        required=False,
        type=str,
        help="The endpoint of the Service of the form, if connection argument is not provided, "
        '"<host>:<port>"',
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

    # tethys services create secure map
    services_create_secure_map = services_create_subparsers.add_parser(
        "secure-map", help="Create a Secure Map Service."
    )
    services_create_secure_map.add_argument(
        "-n", "--name", required=True, help="A unique name for the Service", type=str
    )
    services_create_secure_map.add_argument(
        "-e",
        "--endpoint",
        required=True,
        type=str,
        help="The endpoint URL of the Secure Map Service.",
    )
    services_create_secure_map.add_argument(
        "-l",
        "--legend-title",
        required=True,
        type=str,
        help="The title to use for the legend when this service is added as a layer on a map.",
    )
    services_create_secure_map.add_argument(
        "-a",
        "--auth-method",
        required=True,
        type=str,
        choices=["api_key", "oauth2"],
        help="The authentication method for the service (api_key/oauth2).",
    )
    services_create_secure_map.add_argument(
        "-k",
        "--api-key",
        required=False,
        type=str,
        help="The API key for the service, if authentication method is api_key.",
    )
    services_create_secure_map.add_argument(
        "-o",
        "--oauth2-provider",
        required=False,
        type=str,
        help="The OAuth2 provider name, if authentication method is oauth2 (e.g. 'grid').",
    )
    services_create_secure_map.add_argument(
        "-t",
        "--service-type",
        required=True,
        type=str,
        choices=["image_wms", "gml", "geojson", "rest"],
        help="The type of map service (image_wms/gml/geojson/rest).",
    )
    services_create_secure_map.add_argument(
        "-p",
        "--params",
        required=False,
        type=str,
        help="A JSON string of parameters to include in requests to the service "
        '(e.g. \'{"LAYERS": "my_layer", "VERSION": "1.3.0"}\').',
        default="{}",
    )
    services_create_secure_map.add_argument(
        "--use-proxy",
        action="store_true",
        help="Route requests through a proxy endpoint to keep credentials server-side.",
    )
    services_create_secure_map.add_argument(
        "--connection-timeout",
        required=False,
        type=int,
        default=10,
        help="Timeout in seconds for establishing a connection to the service. Default is 10.",
    )
    services_create_secure_map.add_argument(
        "--read-timeout",
        required=False,
        type=int,
        default=30,
        help="Timeout in seconds to wait for a response from the service. Default is 30.",
    )
    services_create_secure_map.set_defaults(func=services_create_secure_map_command)

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
    group.add_argument(
        "-m",
        "--secure-map",
        action="store_true",
        help="Only list Secure Map Services.",
    )
    services_list_parser.set_defaults(func=services_list_command)


def services_create_persistent_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import (
        PostgresPersistentStoreService,
        SQLitePersistentStoreService,
    )

    name = None

    try:
        name = args.name
        store_type = args.type

        if store_type == "postgres":
            connection = args.connection
            parts = connection.split("@")
            cred_parts = parts[0].split(":")
            store_username = cred_parts[0]
            store_password = cred_parts[1]
            url_parts = parts[1].split(":")
            host = url_parts[0]
            port = url_parts[1]

            new_persistent_service = PostgresPersistentStoreService(
                name=name,
                host=host,
                port=port,
                username=store_username,
                password=store_password,
            )
            new_persistent_service.save()
            with pretty_output(FG_GREEN) as p:
                p.write("Successfully created new PostgreSQL Persistent Store Service!")
        elif store_type == "sqlite":
            dir_path = args.dir_path
            new_persistent_service = SQLitePersistentStoreService(
                name=name,
                dir_path=dir_path,
            )
            new_persistent_service.save()
            with pretty_output(FG_GREEN) as p:
                p.write("Successfully created new SQLite Persistent Store Service!")
        else:
            with pretty_output(FG_RED) as p:
                p.write(f"Unknown persistent store type: {store_type}")

    except AttributeError:
        with pretty_output(FG_RED) as p:
            p.write("Missing Input Parameters. Please check your input.")
    except IndexError:
        with pretty_output(FG_RED) as p:
            p.write(
                'The connection argument (-c) must be of the form "<username>:<password>@<host>:<port>" for postgres or "<file_path>" for sqlite.'
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
        endpoint = args.endpoint

        if connection is None and endpoint is None:
            raise MissingArgumentError(
                "Either connection or endpoint argument must be provided."
            )

        service_username = ""
        service_password = ""

        if connection:
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

    except MissingArgumentError as e:
        with pretty_output(FG_RED) as p:
            p.write(str(e))


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


def services_create_secure_map_command(args):
    """
    Interact with Tethys Services (Secure Map) to create them and/or link them to existing apps.
    """
    setup_django()
    from tethys_services.models import SecureMapService

    SERVICE_TYPE_MAPS = {
        "image_wms": "ImageWMS",
        "gml": "GML",
        "geojson": "GeoJSON",
        "rest": "REST",
    }

    name = None
    try:
        name = args.name
        endpoint = args.endpoint
        legend_title = args.legend_title
        auth_method = args.auth_method
        api_key = args.api_key
        oauth2_provider = args.oauth2_provider
        service_type = SERVICE_TYPE_MAPS[args.service_type]
        params = json.loads(args.params)
        use_proxy = args.use_proxy
        connection_timeout = args.connection_timeout
        read_timeout = args.read_timeout
        if not isinstance(params, dict):
            raise MissingArgumentError("Params must be a valid JSON object.")

        if auth_method == "api_key":
            if oauth2_provider:
                raise MissingArgumentError(
                    "OAuth2 provider should not be provided if the authentication method is 'API key'"
                )
            if not api_key:
                raise MissingArgumentError(
                    "API key is required for api_key authentication."
                )

            new_service = SecureMapService(
                name=name,
                endpoint=endpoint,
                legend_title=legend_title,
                authentication_method=auth_method,
                api_key=api_key,
                service_type=service_type,
                params=params,
                use_proxy=use_proxy,
                connection_timeout=connection_timeout,
                read_timeout=read_timeout,
            )

        elif auth_method == "oauth2":
            if api_key:
                raise MissingArgumentError(
                    "API key should not be provided if the authentication method is 'OAuth2'"
                )
            if not oauth2_provider:
                raise MissingArgumentError(
                    "OAuth2 provider is required for oauth2 authentication."
                )

            new_service = SecureMapService(
                name=name,
                endpoint=endpoint,
                legend_title=legend_title,
                authentication_method=auth_method,
                oauth2_provider=oauth2_provider,
                service_type=service_type,
                params=params,
                use_proxy=use_proxy,
                connection_timeout=connection_timeout,
                read_timeout=read_timeout,
            )
        else:
            raise MissingArgumentError(
                "Authentication method must be either 'api_key' or 'oauth2'."
            )

        new_service.full_clean()
        new_service.save()

        with pretty_output(FG_GREEN) as p:
            p.write("Successfully created new Secure Map Service!")

        return new_service

    except MissingArgumentError as e:
        with pretty_output(FG_RED) as p:
            p.write(str(e))

    except json.JSONDecodeError:
        with pretty_output(FG_RED) as p:
            p.write(
                "Invalid JSON provided for 'params': "
                'Expected a valid JSON object (e.g. \'{"key": "value"}\').'
            )
    except ValidationError as e:
        with pretty_output(FG_RED) as p:
            p.write("Validation errors occurred attempting to create the service:")
            for field, errors in e.message_dict.items():
                p.write(f"- {field}: {', '.join(errors)}")

    except IntegrityError:
        with pretty_output(FG_RED) as p:
            p.write(
                'Secure Map Service with name "{0}" already exists. Command aborted.'.format(
                    name
                )
            )


def remove_service(serviceType, args):
    setup_django()
    from tethys_services.models import (
        SpatialDatasetService,
        DatasetService,
        PostgresPersistentStoreService,
        SQLitePersistentStoreService,
        WebProcessingService,
        SecureMapService,
    )

    services = {
        "spatial": SpatialDatasetService,
        "dataset": DatasetService,
        "wps": WebProcessingService,
        "secure-map": SecureMapService,
    }

    # Determine which persistent store type to use
    if serviceType == "persistent":
        # Try both Postgres and SQLite
        service = None
        service_label = "Persistent Store Service"
        service_id = args.service_uid
        force = args.force
        found = False
        for model in [PostgresPersistentStoreService, SQLitePersistentStoreService]:
            try:
                try:
                    obj = model.objects.get(pk=int(service_id))
                except (ValueError, ObjectDoesNotExist):
                    obj = model.objects.get(name=service_id)
                service = obj
                found = True
                break
            except ObjectDoesNotExist:
                continue

        if not found:
            with pretty_output(FG_RED) as p:
                p.write(
                    'A Persistent Store Service with ID/Name "{0}" does not exist.'.format(
                        service_id
                    )
                )
            exit(0)

        if force:
            service.delete()
            with pretty_output(FG_GREEN) as p:
                p.write(
                    "Successfully removed {0} {1}!".format(service_label, service_id)
                )
            exit(0)
        else:
            proceed = input(
                "Are you sure you want to delete this {0}? [y/n]: ".format(
                    service_label
                )
            )
            while proceed not in ["y", "n", "Y", "N"]:
                proceed = input('Please enter either "y" or "n": ')
            if proceed in ["y", "Y"]:
                service.delete()
                with pretty_output(FG_GREEN) as p:
                    p.write(
                        "Successfully removed {0} {1}!".format(
                            service_label, service_id
                        )
                    )
                exit(0)
            else:
                with pretty_output(FG_RED) as p:
                    p.write("Aborted. {0} not removed.".format(service_label))
                exit(0)

    else:
        service = services.get(serviceType)
        service_label = service._meta.verbose_name
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
                        "Successfully removed {0} {1}!".format(
                            service_label, service_id
                        )
                    )
                exit(0)
            else:
                proceed = input(
                    "Are you sure you want to delete this {0}? [y/n]: ".format(
                        service_label
                    )
                )
                while proceed not in ["y", "n", "Y", "N"]:
                    proceed = input('Please enter either "y" or "n": ')
                if proceed in ["y", "Y"]:
                    service.delete()
                    with pretty_output(FG_GREEN) as p:
                        p.write(
                            "Successfully removed {0} {1}!".format(
                                service_label, service_id
                            )
                        )
                    exit(0)
                else:
                    with pretty_output(FG_RED) as p:
                        p.write("Aborted. {0} not removed.".format(service_label))
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


def services_remove_secure_map_command(args):
    remove_service("secure-map", args)


def services_list_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    setup_django()
    from tethys_services.models import (
        SpatialDatasetService,
        PostgresPersistentStoreService,
        SQLitePersistentStoreService,
        DatasetService,
        WebProcessingService,
        SecureMapService,
    )

    list_persistent = False
    list_spatial = False
    list_dataset = False
    list_wps = False
    list_secure_map = False

    if (
        not args.spatial
        and not args.persistent
        and not args.dataset
        and not args.wps
        and not args.secure_map
    ):
        list_persistent = True
        list_spatial = True
        list_dataset = True
        list_wps = True
        list_secure_map = True
    elif args.spatial:
        list_spatial = True
    elif args.persistent:
        list_persistent = True
    elif args.dataset:
        list_dataset = True
    elif args.wps:
        list_wps = True
    elif args.secure_map:
        list_secure_map = True

    entries = []
    if list_persistent:
        postgres_entries = PostgresPersistentStoreService.objects.order_by("id").all()
        sqlite_entries = SQLitePersistentStoreService.objects.order_by("id").all()
        if len(postgres_entries) > 0:
            entries.append(postgres_entries)
            with pretty_output(BOLD) as p:
                p.write("\nPostgreSQL Persistent Store Services:")
            is_first_entry = True
            for entry in postgres_entries:
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
        if len(sqlite_entries) > 0:
            entries.append(sqlite_entries)
            with pretty_output(BOLD) as p:
                p.write("\nSQLite Persistent Store Services:")
            is_first_entry = True
            for entry in sqlite_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            "{0: <3}{1: <50}{2: <50}".format("ID", "Name", "Dir Path")
                        )
                    is_first_entry = False
                print(
                    "{0: <3}{1: <50}{2: <50}".format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["dir_path"],
                    )
                )

    if list_spatial:
        spatial_entries = SpatialDatasetService.objects.order_by("id").all()
        if len(spatial_entries) > 0:
            entries.append(spatial_entries)
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
        if len(dataset_entries) > 0:
            entries.append(dataset_entries)
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
        if len(service_entries) > 0:
            entries.append(service_entries)
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

    if list_secure_map:
        secure_map_entries = SecureMapService.objects.order_by("id").all()
        if len(secure_map_entries) > 0:
            entries.append(secure_map_entries)
            with pretty_output(BOLD) as p:
                p.write("\nSecure Map Services:")
            is_first_entry = True
            row = "{0: <5}{1: <30}{2: <30}{3: <12}{4: <22}{5: <12}{6: <7}{7}"
            for entry in secure_map_entries:
                model_dict = model_to_dict(entry)
                if is_first_entry:
                    with pretty_output(BOLD) as p:
                        p.write(
                            row.format(
                                "ID",
                                "Name",
                                "Legend",
                                "Auth",
                                "Credential/Provider",
                                "Type",
                                "Proxy",
                                "Endpoint",
                            )
                        )
                    is_first_entry = False

                auth = model_dict["authentication_method"] or "None"
                if auth == "api_key":
                    credential = (
                        "API Key Set" if model_dict["api_key"] else "API Key not set"
                    )
                elif auth == "oauth2":
                    credential = (
                        model_dict["oauth2_provider"]
                        if model_dict["oauth2_provider"]
                        else "Provider not set"
                    )
                else:
                    credential = "None"

                proxy = "Yes" if model_dict["use_proxy"] else "No"

                print(
                    row.format(
                        model_dict["id"],
                        model_dict["name"],
                        model_dict["legend_title"],
                        auth,
                        credential,
                        model_dict["service_type"],
                        proxy,
                        model_dict["endpoint"],
                    )
                )
    return entries
