"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import importlib
import logging
from os import environ
from pathlib import Path

import pkgutil
import yaml

from django.core.signing import Signer
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils._os import safe_join
from django.http import HttpRequest
from django.conf import settings
from channels.consumer import SyncConsumer

from tethys_apps.base.mixins import (
    TethysAsyncWebsocketConsumerMixin,
    TethysWebsocketConsumerMixin,
)
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from .harvester import SingletonHarvester
from django.db.utils import ProgrammingError

tethys_log = logging.getLogger("tethys." + __name__)


def get_tethys_src_dir():
    """
    Get/derive the TETHYS_SRC variable.

    Returns:
        str: path to TETHYS_SRC.
    """
    default = Path(__file__).parents[1]
    return environ.get("TETHYS_SRC", str(default))


def get_tethys_home_dir():
    """
    Get/derive the TETHYS_HOME variable.

    Returns:
        str: path to TETHYS_HOME.
    """
    env_tethys_home = environ.get("TETHYS_HOME")

    # Return environment value if set
    if env_tethys_home:
        return env_tethys_home

    # Initialize to default TETHYS_HOME
    tethys_home = Path.home() / ".tethys"
    active_conda_env = environ.get("CONDA_DEFAULT_ENV")
    active_venv = environ.get("VIRTUAL_ENV_PROMPT", "")
    if active_venv.strip().startswith("(") and active_venv.strip().endswith(")"):
        active_venv = active_venv.strip()[1:-1]
    active_env = active_conda_env or active_venv
    if active_env != "tethys":
        try:
            tethys_home = tethys_home / active_env
        except Exception:
            tethys_log.warning(
                f"Running Tethys outside of active virtual environment detected. Using default "
                f'TETHYS_HOME "{tethys_home}". Set TETHYS_HOME environment to override.'
            )

    return str(tethys_home)


def relative_to_tethys_home(path, as_str=False):
    if not Path(path).is_absolute():
        path = Path(get_tethys_home_dir()) / path
    if as_str:
        path = str(path)
    return path


def get_directories_in_tethys(directory_names, with_app_name=False):
    """
    # Locate given directories in tethys apps and extensions.
    Args:
        directory_names: directory to get path to.
        with_app_name: include the app name if True.

    Returns:
        list: list of paths to directories in apps and extensions.
    """
    potential_dirs = []
    # Determine the directories of tethys extensions
    harvester = SingletonHarvester()

    for _, app_module in harvester.app_modules.items():
        try:
            app_module = __import__(app_module, fromlist=[""])
            potential_dirs.append(app_module.__path__[0])
        except (ImportError, AttributeError, IndexError):
            pass

    for _, extension_module in harvester.extension_modules.items():
        try:
            extension_module = __import__(extension_module, fromlist=[""])
            potential_dirs.append(extension_module.__path__[0])
        except (ImportError, AttributeError, IndexError):
            pass

    # Check each directory combination
    match_dirs = []
    for potential_dir in potential_dirs:
        for directory_name in directory_names:
            # Only check directories
            if Path(potential_dir).is_dir():
                match_dir = safe_join(potential_dir, directory_name)

                if match_dir not in match_dirs and Path(match_dir).is_dir():
                    if not with_app_name:
                        match_dirs.append(match_dir)
                    else:
                        match_dirs.append((Path(potential_dir).name, match_dir))

    return match_dirs


def get_app_model(app_or_request):
    """
    Get the TethysApp model instance for the given app or request.
    """
    from tethys_apps.models import TethysApp
    from tethys_apps.base.app_base import TethysAppBase

    if isinstance(app_or_request, HttpRequest):
        app = get_active_app(app_or_request)
    elif isinstance(app_or_request, TethysAppBase) or (
        isinstance(app_or_request, type) and issubclass(app_or_request, TethysAppBase)
    ):
        app = TethysApp.objects.get(root_url=app_or_request.root_url)
    elif isinstance(app_or_request, TethysApp):
        app = app_or_request
    else:
        raise ValueError(
            f'Argument "app_or_request" must be of type HttpRequest, TethysAppBase, or TethysApp: '
            f'"{type(app_or_request)}" given.'
        )

    return app


def get_active_app(request=None, url=None, get_class=False):
    """
    Get the active TethysApp object based on the request or URL.
    """
    from tethys_apps.models import TethysApp

    # Find the app key
    if settings.MULTIPLE_APP_MODE:
        if request is not None:
            the_url = request.path
        elif url is not None:
            the_url = url
        else:
            return None

        apps_root = "apps"
        if the_url.endswith(f"/{apps_root}"):
            the_url += "/"

        url_parts = the_url.split("/")
        app = None

        if apps_root in url_parts:
            # The app root_url is the path item following (+1) the apps_root item
            app_root_url_index = url_parts.index(apps_root) + 1
            app_root_url = url_parts[app_root_url_index]

            if app_root_url:
                try:
                    # Get the app from the database
                    app = TethysApp.objects.get(root_url=app_root_url)
                except ObjectDoesNotExist:
                    tethys_log.warning(
                        'Could not locate app with root url "{0}".'.format(app_root_url)
                    )
                except MultipleObjectsReturned:
                    tethys_log.warning(
                        'Multiple apps found with root url "{0}".'.format(app_root_url)
                    )
    else:
        app = get_configured_standalone_app()

    if get_class:
        app = get_app_class(app)

    return app


def get_app_class(app):
    for app_s in SingletonHarvester().apps:
        if app_s.package == app.package:
            return app_s


def get_app_settings(app):
    """
    Get settings related to app

    Args:
        app(str): name of app

    Returns:
        dict (linked_settings, unlinked_settings): Dictionary with two keys: linked_settings(list) - list of linked settings, unlinked_settings(list) - list of unlinked settings  # noqa: E501
    """
    from tethys_cli.cli_colors import write_error
    from tethys_apps.models import (
        TethysApp,
        TethysExtension,
        PersistentStoreConnectionSetting,
        PersistentStoreDatabaseSetting,
        SpatialDatasetServiceSetting,
        DatasetServiceSetting,
        WebProcessingServiceSetting,
        CustomSettingBase,
    )

    try:
        app = TethysApp.objects.get(package=app)

        app_settings = []
        for setting in PersistentStoreConnectionSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in PersistentStoreDatabaseSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in SpatialDatasetServiceSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in DatasetServiceSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in WebProcessingServiceSetting.objects.filter(tethys_app=app):
            app_settings.append(setting)
        for setting in CustomSettingBase.objects.filter(
            tethys_app=app
        ).select_subclasses():
            app_settings.append(setting)
        unlinked_settings = []
        linked_settings = []
        for setting in app_settings:
            if (
                (
                    hasattr(setting, "spatial_dataset_service")
                    and setting.spatial_dataset_service
                )
                or (
                    hasattr(setting, "persistent_store_service")
                    and setting.persistent_store_service
                )
                or (hasattr(setting, "dataset_service") and setting.dataset_service)
                or (
                    hasattr(setting, "web_processing_service")
                    and setting.web_processing_service
                )
                or (
                    hasattr(setting, "value")
                    and (setting.value != "" and bool(setting.value))
                )
            ):
                linked_settings.append(setting)
            else:
                unlinked_settings.append(setting)

        return {
            "linked_settings": linked_settings,
            "unlinked_settings": unlinked_settings,
        }

    except ObjectDoesNotExist:
        try:
            # Fail silently if the object is an Extension
            TethysExtension.objects.get(package=app)
        except ObjectDoesNotExist:
            # Write an error if the object is not a TethysApp or Extension
            write_error(
                'The app or extension you specified ("{0}") does not exist. Command aborted.'.format(
                    app
                )
            )
    except Exception as e:
        write_error(str(e))
        write_error("Something went wrong. Please try again.")


def get_custom_setting(app_package, setting_name):
    """
    Get a CustomSetting for a specified TethysApp.

    Args:
        app_package (str): The name/package of the TethysApp.
        setting_name (str): The name of the CustomSetting.

    Returns:
        CustomSetting: The Custom Setting or None if the TethysApp or CustomSetting cannot be found.
    """
    from tethys_apps.models import TethysApp, CustomSettingBase

    try:
        app = TethysApp.objects.get(package=app_package)
    except TethysApp.DoesNotExist:
        return None
    try:
        setting = (
            CustomSettingBase.objects.filter(tethys_app=app)
            .select_subclasses()
            .get(name=setting_name)
        )
    except CustomSettingBase.DoesNotExist:
        return None

    return setting


def get_secret_custom_settings(app_package):
    """
    Get the SecretCustomSettings for a specified TethysApp.

    Args:
        app_package (str): The name/package of the TethysApp.

    Returns:
        InheritanceQuerySet: A Inheritance Query Set containing SecretCustomSetting, None if the TethysApp, or an empty Inheritance Query Set if the app does not have any SecretCustomSetting.
    """
    from tethys_apps.models import TethysApp, CustomSettingBase

    try:
        app = TethysApp.objects.get(package=app_package)
    except TethysApp.DoesNotExist:
        return None

    settings = (
        CustomSettingBase.objects.filter(tethys_app=app)
        .select_subclasses()
        .filter(type_custom_setting="SECRET")
    )

    return settings


def create_ps_database_setting(
    app_package,
    name,
    description="",
    required=False,
    initializer="",
    initialized=False,
    spatial=False,
    dynamic=False,
):
    from tethys_cli.cli_colors import pretty_output, FG_RED, FG_GREEN
    from tethys_apps.models import PersistentStoreDatabaseSetting
    from tethys_apps.models import TethysApp

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                'A Tethys App with the name "{}" does not exist. Aborted.'.format(
                    app_package
                )
            )
        return False

    try:
        setting = PersistentStoreDatabaseSetting.objects.get(name=name)
        if setting:
            with pretty_output(FG_RED) as p:
                p.write(
                    'A PersistentStoreDatabaseSetting with name "{}" already exists. Aborted.'.format(
                        name
                    )
                )
            return False
    except ObjectDoesNotExist:
        pass

    try:
        ps_database_setting = PersistentStoreDatabaseSetting(
            tethys_app=app,
            name=name,
            description=description,
            required=required,
            initializer=initializer,
            initialized=initialized,
            spatial=spatial,
            dynamic=dynamic,
        )
        ps_database_setting.save()
        with pretty_output(FG_GREEN) as p:
            p.write(
                'PersistentStoreDatabaseSetting named "{}" for app "{}" created successfully!'.format(
                    name, app_package
                )
            )
        return True
    except Exception as e:
        print(e)
        with pretty_output(FG_RED) as p:
            p.write("The above error was encountered. Aborted.")
        return False


def remove_ps_database_setting(app_package, name, force=False):
    from tethys_apps.models import TethysApp
    from tethys_cli.cli_colors import pretty_output, FG_RED, FG_GREEN
    from tethys_apps.models import PersistentStoreDatabaseSetting

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                'A Tethys App with the name "{}" does not exist. Aborted.'.format(
                    app_package
                )
            )
        return False

    try:
        setting = PersistentStoreDatabaseSetting.objects.get(tethys_app=app, name=name)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                'An PersistentStoreDatabaseSetting with the name "{}" for app "{}" does not exist. Aborted.'.format(
                    name, app_package
                )
            )
        return False

    if not force:
        proceed = input(
            "Are you sure you want to delete the "
            'PersistentStoreDatabaseSetting named "{}"? [y/n]: '.format(name)
        )
        while proceed not in ["y", "n", "Y", "N"]:
            proceed = input('Please enter either "y" or "n": ')

        if proceed in ["y", "Y"]:
            setting.delete()
            with pretty_output(FG_GREEN) as p:
                p.write(
                    'Successfully removed PersistentStoreDatabaseSetting with name "{0}"!'.format(
                        name
                    )
                )
            return True
        else:
            with pretty_output(FG_RED) as p:
                p.write("Aborted. PersistentStoreDatabaseSetting not removed.")
    else:
        setting.delete()
        with pretty_output(FG_GREEN) as p:
            p.write(
                'Successfully removed PersistentStoreDatabaseSetting with name "{0}"!'.format(
                    name
                )
            )
        return True


def link_service_to_app_setting(
    service_type, service_uid, app_package, setting_type, setting_uid
):
    """
    Links a Tethys Service to a TethysAppSetting.
    :param service_type: The type of service being linked to an app.
        Must be either 'condor', 'dask', 'dataset', 'persistent', 'spatial', or 'wps'.
    :param service_uid: The name or id of the service being linked to an app.
    :param app_package: The package name of the app whose setting is being linked to a service.
    :param setting_type: The type of setting being linked to a service. Must be one of the following: 'ps_database',
    'ds_dataset', 'ds_spatial', 'ps_connection', 'ps_database', 'ss_scheduler', or 'wps'.
    :param setting_uid: The name or id of the setting being linked to a service.
    :return: True if successful, False otherwise.
    """
    import django

    django.setup()
    from tethys_cli.cli_colors import pretty_output, FG_GREEN, FG_RED
    from tethys_apps.models import (
        TethysApp,
        SpatialDatasetServiceSetting,
        PersistentStoreConnectionSetting,
        PersistentStoreDatabaseSetting,
        DatasetServiceSetting,
        SchedulerSetting,
        WebProcessingServiceSetting,
    )

    setting_type_to_link_model_dict = {
        "ps_database": {
            "setting_model": PersistentStoreDatabaseSetting,
            "service_field": "persistent_store_service",
        },
        "ps_connection": {
            "setting_model": PersistentStoreConnectionSetting,
            "service_field": "persistent_store_service",
        },
        "ds_spatial": {
            "setting_model": SpatialDatasetServiceSetting,
            "service_field": "spatial_dataset_service",
        },
        "ds_dataset": {
            "setting_model": DatasetServiceSetting,
            "service_field": "dataset_service",
        },
        "ss_scheduler": {
            "setting_model": SchedulerSetting,
            "service_field": "scheduler_service",
        },
        "wps": {
            "setting_model": WebProcessingServiceSetting,
            "service_field": "web_processing_service",
        },
    }

    service_model = get_service_model_from_type(service_type)

    try:
        try:
            service_uid = int(service_uid)
            service = service_model.objects.get(pk=service_uid)
        except ValueError:
            service = service_model.objects.get(name=service_uid)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                f'A {service_model.__class__.__name__} with ID/Name "{service_uid}" does not exist.'
            )
        return False

    try:
        app = TethysApp.objects.get(package=app_package)
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                f'A Tethys App with the name "{app_package}" does not exist. Aborted.'
            )
        return False

    try:
        linked_setting_model_dict = setting_type_to_link_model_dict[setting_type]
    except KeyError:
        with pretty_output(FG_RED) as p:
            p.write(
                f'The setting_type you specified ("{setting_type}") does not exist.'
                '\nChoose from: "ps_database|ps_connection|ds_spatial"'
            )
        return False

    linked_setting_model = linked_setting_model_dict["setting_model"]
    linked_service_field = linked_setting_model_dict["service_field"]
    try:
        try:
            setting_uid = int(setting_uid)
            setting = linked_setting_model.objects.get(tethys_app=app, pk=setting_uid)
        except ValueError:
            setting = linked_setting_model.objects.get(tethys_app=app, name=setting_uid)

        setattr(setting, linked_service_field, service)
        setting.save()
        with pretty_output(FG_GREEN) as p:
            p.write(
                f'{service.__class__.__name__}:"{service.name}" was successfully linked '
                f'to {setting.__class__.__name__}:"{setting.name}" of the "{app_package}" Tethys App'
            )
        return True
    except ObjectDoesNotExist:
        with pretty_output(FG_RED) as p:
            p.write(
                f'A {linked_setting_model.__name__} with ID/Name "{setting_uid}" does not exist.'
            )
        return False


def get_service_model_from_type(service_type):
    from tethys_services.models import (
        SpatialDatasetService,
        DatasetService,
        PersistentStoreService,
        WebProcessingService,
    )
    from tethys_compute.models import (
        CondorScheduler,
        DaskScheduler,
    )

    service_type_to_model_dict = {
        "condor": CondorScheduler,
        "dask": DaskScheduler,
        "dataset": DatasetService,
        "persistent": PersistentStoreService,
        "spatial": SpatialDatasetService,
        "wps": WebProcessingService,
    }

    return service_type_to_model_dict[service_type]


def user_can_access_app(user, app):
    from django.conf import settings

    RESTRICTED_APP_ACCESS = getattr(settings, "ENABLE_RESTRICTED_APP_ACCESS", False)

    if getattr(settings, "ENABLE_OPEN_PORTAL", False):
        return True
    elif RESTRICTED_APP_ACCESS:
        if isinstance(RESTRICTED_APP_ACCESS, bool):
            return user.has_perm(f"{app.package}:access_app", app)
        elif app.package in RESTRICTED_APP_ACCESS:
            return user.has_perm(f"{app.package}:access_app", app)
        else:
            return True
    else:
        return True


def get_installed_tethys_items(apps=False, extensions=False):
    harvester = SingletonHarvester()
    installed_apps = harvester.app_modules
    install_extensions = harvester.extension_modules

    items = {}
    if apps:
        items.update(installed_apps)
    if extensions:
        items.update(install_extensions)

    paths = {}

    for name, module in items.items():
        try:
            item = __import__(module, fromlist=[""])
            value = item.__path__[0]
            paths[name] = value
        except (IndexError, ImportError):
            """DO NOTHING"""

    return paths


def get_configured_standalone_app():
    """
    Returns a list apps installed in the tethysapp directory.
    """
    from tethys_apps.models import TethysApp

    standalone_app = settings.STANDALONE_APP
    app = None
    try:
        if standalone_app:
            app = TethysApp.objects.get(package=standalone_app)
        else:
            app = TethysApp.objects.first()
    except (ProgrammingError, TethysApp.DoesNotExist):
        # If a tethys application is not actually installed or DB is not setup yet, continue and the UI will notify the user
        pass

    return app


def get_installed_tethys_apps():
    """
    Returns a list apps installed in the tethysapp directory.
    """
    return get_installed_tethys_items(apps=True)


def get_installed_tethys_extensions():
    """
    Get a list of installed extensions
    """
    return get_installed_tethys_items(extensions=True)


def get_all_submodules(m):
    """
    Gets all submodules of `m` including submodules that are not directly imported under m.
    """
    modules = [m]
    try:
        for sm in pkgutil.iter_modules(m.__path__):
            nm = importlib.import_module(f".{sm.name}", m.__name__)
            modules.append(nm)
            if sm.ispkg:
                modules.extend(get_all_submodules(nm))
    except AttributeError:
        pass
    return modules


def delete_secrets(app_name):
    TETHYS_HOME = Path(get_tethys_home_dir())
    secrets_yaml_file = TETHYS_HOME / "secrets.yml"
    portal_secrets = {}
    if secrets_yaml_file.exists():
        with secrets_yaml_file.open("r") as secrets_yaml:
            portal_secrets = yaml.safe_load(secrets_yaml) or {}
            if "secrets" in portal_secrets:
                if app_name not in portal_secrets["secrets"]:
                    # always reset on a new install
                    portal_secrets["secrets"][app_name] = {}
                if (
                    "custom_settings_salt_strings"
                    in portal_secrets["secrets"][app_name]
                ):
                    portal_secrets["secrets"][app_name][
                        "custom_settings_salt_strings"
                    ] = {}

                with secrets_yaml_file.open("w") as secrets_yaml:
                    yaml.dump(portal_secrets, secrets_yaml)


def secrets_signed_unsigned_value(name, value, tethys_app_package_name, is_signing):
    return_string = ""
    TETHYS_HOME = get_tethys_home_dir()
    secrets_path = Path(TETHYS_HOME) / "secrets.yml"
    signer = Signer()
    try:
        if not secrets_path.exists():
            return_string = sign_and_unsign_secret_string(signer, value, is_signing)
        else:
            secret_app_settings = (yaml.safe_load(secrets_path.read_text()) or {}).get(
                "secrets", {}
            )
            if bool(secret_app_settings):
                if tethys_app_package_name in secret_app_settings:
                    if (
                        "custom_settings_salt_strings"
                        in secret_app_settings[tethys_app_package_name]
                    ):
                        app_specific_settings = secret_app_settings[
                            tethys_app_package_name
                        ]["custom_settings_salt_strings"]
                        if name in app_specific_settings:
                            app_custom_setting_salt_string = app_specific_settings[name]
                            if app_custom_setting_salt_string != "":
                                signer = Signer(salt=app_custom_setting_salt_string)
            return_string = sign_and_unsign_secret_string(signer, value, is_signing)
    except signing.BadSignature:
        raise TethysAppSettingNotAssigned(
            f"The salt string for the setting {name} has been changed or lost, please enter the secret custom settings in the application settings again."
        )

    return return_string


def sign_and_unsign_secret_string(signer, value, is_signing):
    if is_signing:
        secret_signed = signer.sign_object(value)
        return secret_signed
    else:
        secret_unsigned = signer.unsign_object(f"{value}")
        return secret_unsigned


def update_decorated_websocket_consumer_class(
    consumer_class, permissions_required, permissions_use_or, login_required, with_paths
):
    """Updates a given consumer class and adds the necessary properties and function for authorizing user access
    depending on the other args given.

    Args:
        consumer_class (class): class of the websocket consumer
        permissions_required (str, list, tuple): the permissions required for user access
        permissions_use_or (bool): Determines if all permissions need to be met or just one of them
        login_required (bool): Determines if the user needs to be logged in to use
        with_paths (bool): Determines if the path attributes on the class should be initialized

    Returns:
        class: updated class with necessary properties and function for authorizing user access
    """
    if issubclass(consumer_class, SyncConsumer):
        consumer_mixin = TethysWebsocketConsumerMixin
    else:
        consumer_mixin = TethysAsyncWebsocketConsumerMixin

    class_bases = list(consumer_class.__bases__)
    class_bases.insert(0, consumer_mixin)
    consumer_class.__bases__ = tuple(class_bases)
    consumer_class.permissions = permissions_required
    consumer_class.permissions_use_or = permissions_use_or
    consumer_class.login_required = login_required

    if with_paths or login_required:
        consumer_class.__call__ = initialize_consumer_app_and_user(
            consumer_class.__call__
        )

    return consumer_class


def initialize_consumer_app_and_user(call_func):
    """Wrapper for Consumer class with Tethys(Async)WebsocketConsumerMixin __call__ function to initialize
    the active app and user properties
    """

    async def wrapper(self, scope, *args, **kwargs):
        self.scope = scope
        await self._initialize_app_and_user()
        result = await call_func(self, scope, *args, **kwargs)

        return result

    return wrapper
