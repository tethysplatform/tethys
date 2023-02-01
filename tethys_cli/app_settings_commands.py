import yaml
import os
import json
from pathlib import Path
from django.core.signing import Signer
from django.core.exceptions import ValidationError,ObjectDoesNotExist, MultipleObjectsReturned
from tethys_apps.utilities import get_app_settings, get_custom_setting,get_tethys_home_dir
from tethys_cli.cli_colors import pretty_output, BOLD, write_error, write_success, write_warning
from tethys_cli.cli_helpers import load_apps, generate_salt_string

TETHYS_HOME = Path(get_tethys_home_dir())

def add_app_settings_parser(subparsers):
    # APP_SETTINGS COMMANDS
    app_settings_parser = subparsers.add_parser(
        "app_settings", help="Interact with Tethys App Settings."
    )
    app_settings_subparsers = app_settings_parser.add_subparsers(title="Options")

    # tethys app_settings list
    app_settings_list_parser = app_settings_subparsers.add_parser(
        "list", help="List all settings for a specified app"
    )
    app_settings_list_parser.add_argument(
        "app", help='The app ("<app_package>") to list the Settings for.'
    )
    app_settings_list_parser.set_defaults(func=app_settings_list_command)

    # tethys app_settings set
    app_settings_set_parser = app_settings_subparsers.add_parser(
        "set", help="Set the value of a custom setting " "for a specified app."
    )
    app_settings_set_parser.add_argument(
        "app", help='The app ("<app_package>") with the setting to be set.'
    )
    app_settings_set_parser.add_argument(
        "setting", help="The name of the setting to be set."
    )
    app_settings_set_parser.add_argument("value", help="The value to set.")
    app_settings_set_parser.set_defaults(func=app_settings_set_command)

    # tethys app_settings set
    app_settings_reset_parser = app_settings_subparsers.add_parser(
        "reset", help="Reset the value of a custom setting " "to its default value."
    )
    app_settings_reset_parser.add_argument(
        "app", help='The app ("<app_package>") with the setting to be reset.'
    )
    app_settings_reset_parser.add_argument(
        "setting", help="The name of the setting to be reset."
    )
    app_settings_reset_parser.set_defaults(func=app_settings_reset_command)

    # tethys app_settings create
    app_settings_create_cmd = app_settings_subparsers.add_parser(
        "create", help="Create a Setting for an app."
    )

    asc_subparsers = app_settings_create_cmd.add_subparsers(title="Create Options")
    app_settings_create_cmd.add_argument(
        "-a",
        "--app",
        required=True,
        help='The app ("<app_package>") to create the Setting for.',
    )
    app_settings_create_cmd.add_argument(
        "-n", "--name", required=True, help="The name of the Setting to create."
    )
    app_settings_create_cmd.add_argument(
        "-d",
        "--description",
        required=False,
        help="A description for the Setting to create.",
    )
    app_settings_create_cmd.add_argument(
        "-r",
        "--required",
        required=False,
        action="store_true",
        help="Include this flag if the Setting is required for the app.",
    )
    app_settings_create_cmd.add_argument(
        "-i",
        "--initializer",
        required=False,
        help="The function that initializes the PersistentStoreSetting database.",
    )
    app_settings_create_cmd.add_argument(
        "-z",
        "--initialized",
        required=False,
        action="store_true",
        help="Include this flag if the database is already initialized.",
    )

    # tethys app_settings create ps_database
    app_settings_create_psdb_cmd = asc_subparsers.add_parser(
        "ps_database", help="Create a PersistentStoreDatabaseSetting"
    )
    app_settings_create_psdb_cmd.add_argument(
        "-s",
        "--spatial",
        required=False,
        action="store_true",
        help="Include this flag if the database requires spatial capabilities.",
    )
    app_settings_create_psdb_cmd.add_argument(
        "-y",
        "--dynamic",
        action="store_true",
        required=False,
        help="Include this flag if the database should be considered to be "
        "dynamically created.",
    )
    app_settings_create_psdb_cmd.set_defaults(
        func=app_settings_create_ps_database_command
    )

    # tethys app_settings remove
    app_settings_remove_cmd = app_settings_subparsers.add_parser(
        "remove", help="Remove a Setting for an app."
    )
    app_settings_remove_cmd.add_argument(
        "app", help='The app ("<app_package>") to remove the Setting from.'
    )
    app_settings_remove_cmd.add_argument(
        "-n", "--name", help="The name of the Setting to remove.", required=True
    )
    app_settings_remove_cmd.add_argument(
        "-f", "--force", action="store_true", help="Force removal without confirming."
    )
    app_settings_remove_cmd.set_defaults(func=app_settings_remove_command)

    # tethys generate a salt string for a custom secret setting in an app
    app_settings_set_salt_string_custom_setting_secret_parser = app_settings_subparsers.add_parser(
        "gen_salt", help="Set the value of a salt string for a secret custom setting " "for a specified app."
    )
    app_settings_set_salt_string_custom_setting_secret_parser.add_argument(
        "app", help='The app ("<app_package>") with the setting to be set.'
    )
    app_settings_set_salt_string_custom_setting_secret_parser.add_argument(
        "setting", help="The name of the setting to be set."
    )
    app_settings_set_salt_string_custom_setting_secret_parser.add_argument(
        "-s",
        "--salt_string",
        required=False,
        help="The salt string to use, if none is provided one will be generated."
    )
    app_settings_set_salt_string_custom_setting_secret_parser.set_defaults(func=app_settings_create_salt_strings_command)

    # tethys generate a salt string for each custom secret setting in an app
    app_settings_set_salt_string_custom_settings_secrets_parser = app_settings_subparsers.add_parser(
        "gen_salt_all", help="Set the value of a salt string for each secret custom setting " "for a specified app."
    )
    app_settings_set_salt_string_custom_settings_secrets_parser.add_argument(
        "app", help='The app ("<app_package>") with the setting to be set.'
    )
    app_settings_set_salt_string_custom_settings_secrets_parser.set_defaults(func=app_settings_create_all_salt_strings_command)

def app_settings_list_command(args):
    load_apps()
    app_settings = get_app_settings(args.app)
    # breakpoint()
    if app_settings is None:
        return
    unlinked_settings = app_settings["unlinked_settings"]
    linked_settings = app_settings["linked_settings"]

    with pretty_output(BOLD) as p:
        p.write("\nUnlinked Settings:")

    if len(unlinked_settings) == 0:
        with pretty_output() as p:
            p.write("None")
    else:
        is_first_row = True
        for setting in unlinked_settings:
            if is_first_row:
                with pretty_output(BOLD) as p:
                    p.write("{0: <10}{1: <40}{2: <15}".format("ID", "Name", "Type"))
                is_first_row = False
            with pretty_output() as p:
                p.write(
                    "{0: <10}{1: <40}{2: <15}".format(
                        setting.pk, setting.name, get_setting_type(setting)
                    )
                )

    with pretty_output(BOLD) as p:
        p.write("\nLinked Settings:")

    if len(linked_settings) == 0:
        with pretty_output() as p:
            p.write("None")
    else:
        is_first_row = True
        for setting in linked_settings:
            if is_first_row:
                with pretty_output(BOLD) as p:
                    p.write(
                        "{0: <10}{1: <40}{2: <15}{3: <20}".format(
                            "ID", "Name", "Type", "Linked With"
                        )
                    )
                is_first_row = False

            if hasattr(setting, "persistent_store_service"):
                service_name = setting.persistent_store_service.name
            elif hasattr(setting, "spatial_dataset_service"):
                service_name = setting.spatial_dataset_service.name
            elif hasattr(setting, "dataset_service"):
                service_name = setting.dataset_service.name
            elif hasattr(setting, "web_processing_service"):
                service_name = setting.web_processing_service.name
            elif hasattr(setting, "value"):
                service_name = str(setting.value)
            
            with pretty_output() as p:
                p.write(
                    f"{setting.pk: <10}{setting.name: <40}{get_setting_type(setting): <15} {service_name: <20}"
                )


def app_settings_set_command(args):
    load_apps()
    setting = get_custom_setting(args.app, args.setting)

    if not setting:
        write_error(f'No such Custom Setting "{args.setting}" for app "{args.app}".')
        exit(1)

    try:
        value_json = '{}'
        if setting.type_custom_setting == "JSON":
            if os.path.exists(args.value):

                with open(args.value) as json_file:
                    write_warning(
                        f'File found, extracting Json data int o Json String'
                    )
                    value_json = json.load(json_file)
                    # value_json = json.dumps(json_data)
                    # value_json = json.dumps(json_data,sort_keys = True, indent = 4, ensure_ascii = False)
        
                setting.value = value_json
            else:
                setting.value = args.value

        else:
            setting.value = args.value
        
        setting.clean()
        setting.save()
    except ValidationError as e:
        write_error(
            f'Value was not set: {",".join(e.messages)} "{args.value}" was given.'
        )
        exit(1)

    write_success(
        f'Success! Custom Setting "{args.setting}" for app "{args.app}" was set to "{args.value}".'
    )
    exit(0)


def app_settings_reset_command(args):
    load_apps()
    setting = get_custom_setting(args.app, args.setting)

    if not setting:
        write_error(f'No such Custom Setting "{args.setting}" for app "{args.app}".')
        exit(1)

    setting.value = setting.default
    setting.save()

    write_success(
        f'Success! Custom Setting "{args.setting}" for app "{args.app}" '
        f'was reset to the default value of "{setting.value}".'
    )
    exit(0)


def get_setting_type(setting):
    from tethys_apps.models import (
        PersistentStoreConnectionSetting,
        PersistentStoreDatabaseSetting,
        SpatialDatasetServiceSetting,
        DatasetServiceSetting,
        WebProcessingServiceSetting,
        CustomSetting,
        CustomSimpleSetting,
        CustomSecretSetting,
        CustomJSONSetting,
    )

    setting_type_dict = {
        PersistentStoreConnectionSetting: "ps_connection",
        PersistentStoreDatabaseSetting: "ps_database",
        SpatialDatasetServiceSetting: "ds_spatial",
        DatasetServiceSetting: "ds_dataset",
        WebProcessingServiceSetting: "wps",
        CustomSetting: "custom_setting",
        CustomSimpleSetting: "custom_simple_setting",
        CustomSecretSetting: "custom_secret_setting",
        CustomJSONSetting: "custom_json_setting",
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

    success = create_ps_database_setting(
        app_package,
        setting_name,
        setting_description or "",
        required,
        initializer or "",
        initialized,
        spatial,
        dynamic,
    )

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

def app_settings_create_salt_strings_command(args):

    load_apps()

    ## checking if the salt string si provided or not
    if args.salt_string:
        salt_string = args.salt_string
    else:
        salt_string = generate_salt_string().decode()
    app_name = args.app
    setting = args.setting
    breakpoint()
    ## checking the type of setting and the type of custom setting
    if get_custom_setting(app_name,setting) is None:
        write_warning(
            f'No secret custom setting for the app {app_name}'
        )
        exit(1)
    else:
        if get_custom_setting(app_name,setting).type_custom_setting != "SECRET":
            write_warning(
                f'The custom setting {setting} for the app {app_name} is not a a secret custom setting type, but a {get_custom_setting(app_name,setting).type_custom_setting} custom setting type'
            )
            exit(1)
    
    secrets_yaml_file = TETHYS_HOME / "secrets.yml"
    secret_settings = {}
    if secrets_yaml_file.exists():
        with secrets_yaml_file.open("r") as secrets_yaml:
            secret_settings = yaml.safe_load(secrets_yaml) or {}
            if not app_name in secret_settings["secrets"]:
                write_warning(
                    f'No app definition for the app {app_name} in the secrets portion in the portal_config.yml. Generating one...'
                )
                secret_settings["secrets"][app_name] = {}
            if not 'custom_settings_salt_strings' in secret_settings["secrets"][app_name]:
                write_warning(
                    f'No custom_settings_salt_strings in the app definition for the app {app_name} in the secrets portion in the portal_config.yml. Generating one...'
                )
                secret_settings["secrets"][app_name]["custom_settings_salt_strings"] = {}
            
            ## get the last salt string
            last_salt_string = ""
            signer = Signer()
            if setting in secret_settings["secrets"][app_name]["custom_settings_salt_strings"]:
                last_salt_string = secret_settings["secrets"][app_name]["custom_settings_salt_strings"][setting]
                signer = Signer(salt=last_salt_string)
            secret_unsigned= signer.unsign_object(f'{get_custom_setting(app_name,setting).value}')
            secret_settings["secrets"][app_name]["custom_settings_salt_strings"][setting] = salt_string            
            with secrets_yaml_file.open("w") as secrets_yaml:
                yaml.dump(secret_settings, secrets_yaml)
                write_success(
                    f'custom_settings_salt_strings created for setting: {setting} in app {app_name}'
                )
            setting_obj = get_custom_setting(app_name,setting)
            setting_obj.value = secret_unsigned
            setting_obj.clean()
            setting_obj.save()
            exit(0)
    

def app_settings_create_all_salt_strings_command(args):
    load_apps()
    app_name = args.app
    from tethys_apps.models import (
        TethysApp,
        CustomSetting,
        TethysExtension
    )

    try:
        app = TethysApp.objects.get(package=app_name)
        # breakpoint()
        for setting in CustomSetting.objects.filter(tethys_app=app).filter(type_custom_setting="SECRET").select_subclasses():
            breakpoint()
            # if setting.type_custom_setting == "SECRET": 
            salt_string = generate_salt_string().decode()
            secret_yaml_file = TETHYS_HOME / "secrets.yml"
            secret_settings = {}
            if secret_yaml_file.exists():
                with secret_yaml_file.open("r") as secret_yaml:
                    secret_settings = yaml.safe_load(secret_yaml) or {}
                    if not app_name in secret_settings["secrets"]:
                        write_warning(
                            f'No app definition for the app {app_name} in the secrets portion in the portal_config.yml. Generating one...'
                        )
                        secret_settings["secrets"][app_name] = {}
                    if not 'custom_settings_salt_strings' in secret_settings["secrets"][app_name]:
                        write_warning(
                            f'No custom_settings_salt_strings in the app definition for the app {app_name} in the secrets portion in the portal_config.yml. Generating one...'
                        )
                        secret_settings["secrets"][app_name]["custom_settings_salt_strings"] = {}

                    last_salt_string = ""
                    signer = Signer()
                    if setting.name in secret_settings["secrets"][app_name]["custom_settings_salt_strings"]:
                        last_salt_string = secret_settings["secrets"][app_name]["custom_settings_salt_strings"][setting.name]
                        signer = Signer(salt=last_salt_string)
                    secret_unsigned= signer.unsign_object(f'{setting.value}')
                    secret_settings["secrets"][app_name]["custom_settings_salt_strings"][setting.name] = salt_string
                    with secret_yaml_file.open("w") as secret_yaml:
                        yaml.dump(secret_settings, secret_yaml)
                        write_success(
                            f'custom_settings_salt_strings created for setting: {setting.name} in app {app_name}'
                        )
                    setting.value = secret_unsigned
                    setting.clean()
                    setting.save()
        exit(0)
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
    exit(0)
    