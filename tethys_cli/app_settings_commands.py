import os
import json
from pathlib import Path
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from tethys_apps.utilities import (
    get_app_settings,
    get_custom_setting,
    get_tethys_home_dir,
)
from tethys_cli.cli_colors import (
    pretty_output,
    BOLD,
    write_error,
    write_success,
    write_warning,
    write_msg,
)
from tethys_cli.cli_helpers import setup_django, gen_salt_string_for_setting
from subprocess import call

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

    # tethys generate a salt string for each custom secret setting for each app
    app_settings_set_salt_string_custom_settings_secrets_parser = (
        app_settings_subparsers.add_parser(
            "gen_salt",
            help="Set the value of a salt string for each secret custom setting "
            "for a specified app.",
        )
    )
    app_settings_set_salt_string_custom_settings_secrets_parser.add_argument(
        "-a",
        "--app",
        required=False,
        help='The app ("<app_package>") with the setting to be set.',
    )
    app_settings_set_salt_string_custom_settings_secrets_parser.add_argument(
        "-s",
        "--setting",
        required=False,
        help="The name of the setting to be set, if none is provided salt strings will be generated for all the settings.",
    )

    app_settings_set_salt_string_custom_settings_secrets_parser.set_defaults(
        func=app_settings_gen_salt_strings_command
    )


def app_settings_list_command(args):
    setup_django()
    app_settings = get_app_settings(args.app)
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
    setup_django()
    setting = get_custom_setting(args.app, args.setting)
    actual_value = args.value

    if not setting:
        write_error(f'No such Custom Setting "{args.setting}" for app "{args.app}".')
        exit(1)

    try:
        value_json = "{}"
        if setting.type_custom_setting == "JSON":
            if os.path.exists(actual_value):
                with open(actual_value) as json_file:
                    write_warning("File found, extracting JSON data")
                    value_json = json.load(json_file)

                setting.value = value_json
            else:
                try:
                    setting.value = json.loads(actual_value)
                except json.decoder.JSONDecodeError:
                    write_error("Please enclose the JSON in single quotes")
                    exit(1)

        else:
            setting.value = actual_value

        setting.clean()
        setting.save()
    except ValidationError as e:
        write_error(
            f'Value was not set: {",".join(e.messages)} "{args.value}" was given.'
        )
        exit(1)
    except TypeError as e:
        write_error(f'Value was not set: {e} "')
        exit(1)

    write_success(
        f'Success! Custom Setting "{args.setting}" for app "{args.app}" was set to "{args.value}".'
    )
    exit(0)


def app_settings_reset_command(args):
    setup_django()
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
        SecretCustomSetting,
        JSONCustomSetting,
    )

    setting_type_dict = {
        PersistentStoreConnectionSetting: "ps_connection",
        PersistentStoreDatabaseSetting: "ps_database",
        SpatialDatasetServiceSetting: "ds_spatial",
        DatasetServiceSetting: "ds_dataset",
        WebProcessingServiceSetting: "wps",
        CustomSetting: "custom_setting",
        SecretCustomSetting: "secret_custom_setting",
        JSONCustomSetting: "json_custom_setting",
    }

    return setting_type_dict[type(setting)]


def app_settings_create_ps_database_command(args):
    setup_django()
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
    setup_django()
    from tethys_apps.utilities import remove_ps_database_setting

    app_package = args.app
    setting_name = args.name
    force = args.force
    success = remove_ps_database_setting(app_package, setting_name, force)

    if not success:
        exit(1)

    exit(0)


def app_settings_gen_salt_strings_command(args):
    setup_django()
    # create a list for apps, settings, and salt strings

    from tethys_apps.models import TethysApp, CustomSettingBase, TethysExtension

    list_apps = []
    list_settings = []
    if not args.app and args.setting:
        write_error(
            "Please use the -a or --app flag to specify an application, and then use the -s / --setting flag to specify a setting. Command aborted."
        )
        exit(1)

    if args.app:
        try:
            list_apps.append(TethysApp.objects.get(package=args.app))
        except ObjectDoesNotExist:
            try:
                # Fail silently if the object is an Extension
                TethysExtension.objects.get(package=args.app)
            except ObjectDoesNotExist:
                # Write an error if the object is not a TethysApp or Extension
                write_error(
                    'The app or extension you specified ("{0}") does not exist. Command aborted.'.format(
                        args.app
                    )
                )
                exit(1)
    else:
        list_apps = TethysApp.objects.all()

    for app in list_apps:
        app_name = app.package
        write_success(f"{app_name} application: ")
        if args.setting:
            list_settings.append(get_custom_setting(app.package, args.setting))
            if not list_settings[0]:
                write_error(
                    f"No custom settings with the name {args.setting} for the {app_name} exits."
                )

                exit(1)
        else:
            list_settings = (
                CustomSettingBase.objects.filter(tethys_app=app)
                .filter(type_custom_setting="SECRET")
                .select_subclasses()
            )

        for setting in list_settings:
            secret_yaml_file = TETHYS_HOME / "secrets.yml"
            if not secret_yaml_file.exists():
                write_warning("No secrets.yml found. Generating one...")
                call(["tethys", "gen", "secrets"])
                write_msg("secrets file generated.")

            gen_salt_string_for_setting(app_name, setting)

    exit(0)
