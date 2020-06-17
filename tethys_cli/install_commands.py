import yaml
import os
from pathlib import Path

from subprocess import (call, Popen, PIPE, STDOUT)
from argparse import Namespace
from conda.cli.python_api import run_command as conda_run, Commands
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from tethys_cli.cli_colors import write_msg, write_error, write_warning, write_success
from tethys_cli.services_commands import services_list_command
from tethys_cli.cli_helpers import load_apps
from tethys_apps.utilities import (
    link_service_to_app_setting,
    get_app_settings,
    get_service_model_from_type,
    get_tethys_home_dir,
)

FNULL = open(os.devnull, 'w')


def add_install_parser(subparsers):
    # Install Commands

    application_install_parser = subparsers.add_parser('install', help='Install and Initialize Applications')
    application_install_parser.add_argument('-d', '--develop',
                                            help='Will run setup.py develop instead of setup.py install',
                                            action='store_true')
    application_install_parser.add_argument('-f', '--file', type=str, help='The path to the Install file. ')
    application_install_parser.add_argument('-s', '--services-file', type=str,
                                            help='The path to the Services.yml config file')
    application_install_parser.add_argument('--force-services',
                                            help='Force Services.yml file over portal_config.yml file',
                                            action='store_true')
    application_install_parser.add_argument('-q', '--quiet',
                                            help='Skips interactive mode.',
                                            action='store_true')
    application_install_parser.add_argument('-n', '--no-sync-stores',
                                            help='Skips syncstores when linked persistent stores are found.',
                                            action='store_true')
    application_install_parser.add_argument('-N', '--no-db-sync',
                                            help='Skips any database related commands.',
                                            action='store_true')
    application_install_parser.add_argument('-v', '--verbose',
                                            help='Will show all pip install output when enabled.',
                                            action='store_true')
    application_install_parser.add_argument('-u', '--update-installed',
                                            help='Will attempt to update already installed dependencies to versions '
                                                 'listed in the install.yml. WARNING: This may break your Tethys '
                                                 'installation and is not recommended.',
                                            action='store_true')
    application_install_parser.add_argument('-o', '--only-dependencies',
                                            help='Install only the dependencies of an app or extension.',
                                            action='store_true')

    application_install_parser.add_argument('-w', '--without-dependencies',
                                            help='Install the app or extension without installing its dependencies.',
                                            action='store_true')

    application_install_parser.set_defaults(func=install_command)


def open_file(file_path):
    try:
        with file_path.open() as f:
            return yaml.safe_load(f)

    except Exception as e:
        write_error(str(e))
        write_error('An unexpected error occurred reading the file. Please try again.')
        exit(1)


def validate_service_id(service_type, service_id):
    service_model = get_service_model_from_type(service_type)
    try:
        service_model.objects.get(id=service_id)  # noqa: F841
        return True
    except (ObjectDoesNotExist, ValueError):
        try:
            service_model.objects.get(name=service_id)  # noqa: F841
            return True
        except ObjectDoesNotExist:
            pass

    return False


def get_setting_type_from_setting(setting):
    from tethys_apps.models import PersistentStoreDatabaseSetting, PersistentStoreConnectionSetting, \
        SpatialDatasetServiceSetting, DatasetServiceSetting, WebProcessingServiceSetting

    if setting.__class__ == PersistentStoreDatabaseSetting or isinstance(setting, PersistentStoreDatabaseSetting):
        return 'ps_database'

    elif setting.__class__ == PersistentStoreConnectionSetting or isinstance(setting, PersistentStoreConnectionSetting):
        return 'ps_connection'

    elif setting.__class__ == SpatialDatasetServiceSetting or isinstance(setting, SpatialDatasetServiceSetting):
        return 'ds_spatial'

    elif setting.__class__ == DatasetServiceSetting or isinstance(setting, DatasetServiceSetting):
        return 'ds_dataset'

    elif setting.__class__ == WebProcessingServiceSetting or isinstance(setting, WebProcessingServiceSetting):
        return 'wps'

    raise RuntimeError(f'Could not determine setting type for setting: {setting}')


def get_service_type_from_setting(setting):
    from tethys_apps.models import PersistentStoreDatabaseSetting, PersistentStoreConnectionSetting, \
        SpatialDatasetServiceSetting, DatasetServiceSetting, WebProcessingServiceSetting

    if setting.__class__ == PersistentStoreDatabaseSetting or isinstance(setting, PersistentStoreDatabaseSetting):
        return 'persistent'

    elif setting.__class__ == PersistentStoreConnectionSetting or isinstance(setting, PersistentStoreConnectionSetting):
        return 'persistent'

    elif setting.__class__ == SpatialDatasetServiceSetting or isinstance(setting, SpatialDatasetServiceSetting):
        return 'spatial'

    elif setting.__class__ == DatasetServiceSetting or isinstance(setting, DatasetServiceSetting):
        return 'dataset'

    elif setting.__class__ == WebProcessingServiceSetting or isinstance(setting, WebProcessingServiceSetting):
        return 'wps'

    raise RuntimeError(f'Could not determine service type for setting: {setting}')


# Pulling this function out so I can mock this for inputs to the interactive mode
def get_interactive_input():
    return input("")


def get_service_name_input():
    return input("")


def print_unconfigured_settings(app_name, unlinked_settings):
    if len(unlinked_settings) > 0:
        write_msg(f'\nThe following settings were not configured for app: {app_name}:\n')
        write_msg('{0: <50}{1: <50}{2: <15}'.format('Name', 'Type', 'Required'))

        for unlinked_setting in unlinked_settings:
            write_msg('{0: <50}{1: <50}{2: <15}'.format(unlinked_setting.name, unlinked_setting.__class__.__name__,
                                                        str(unlinked_setting.required)))


def run_sync_stores(app_name, linked_settings):
    from tethys_apps.models import PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting

    linked_persistent = False
    for setting in linked_settings:
        if isinstance(setting, PersistentStoreDatabaseSetting) or isinstance(setting, PersistentStoreConnectionSetting):
            linked_persistent = True

    if linked_persistent:
        write_msg('Running syncstores for app {}'.format(app_name))
        call(['tethys', 'syncstores', app_name])


def get_setting_type(setting):
    from tethys_apps.models import (PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting,
                                    SpatialDatasetServiceSetting, DatasetServiceSetting, WebProcessingServiceSetting,
                                    CustomSetting)

    setting_type_dict = {
        PersistentStoreConnectionSetting: 'persistent',
        PersistentStoreDatabaseSetting: 'persistent',
        SpatialDatasetServiceSetting: 'spatial',
        DatasetServiceSetting: 'dataset',
        WebProcessingServiceSetting: 'wps',
        CustomSetting: 'custom_setting'
    }

    return setting_type_dict[type(setting)]


def run_interactive_services(app_name):
    write_msg('Running Interactive Service Mode. '
              'Any configuration options in services.yml or portal_config.yml will be ignored...')
    write_msg('Hit return at any time to skip a step.')

    app_settings = get_app_settings(app_name)

    # In the case the app isn't installed, has no settings, or it is an extension,
    # skip configuring services/settings
    if not app_settings:
        write_msg(f'No settings found for app "{app_name}". Skipping interactive configuration...')
        return

    unlinked_settings = app_settings['unlinked_settings']

    for setting in unlinked_settings:
        valid = False
        configure_text = "Configuring {}".format(setting.name)
        star_out = '*' * len(configure_text)
        write_msg(f"\n{star_out}\n{configure_text}\n{star_out}")
        write_msg(f"Type: {setting.__class__.__name__}\n"
                  f"Description: {setting.description}\n"
                  f"Required: {setting.required}")
        if hasattr(setting, 'value'):
            while not valid:
                write_msg('\nEnter the desired value for the current custom setting: {}'.format(setting.name))
                try:
                    value = get_interactive_input()
                    if value != "":
                        try:
                            setting.value = value
                            setting.clean()
                            setting.save()
                            valid = True
                            write_success("{} successfully set with value: {}.".format(setting.name, value))
                        except ValidationError:
                            write_error("Incorrect value type given for custom setting '{}'. Please try again"
                                        .format(setting.name))

                    else:
                        write_msg("Skipping setup of {}".format(setting.name))
                        valid = True

                except (KeyboardInterrupt, SystemExit):
                    write_msg('\nInstall Command cancelled.')
                    exit(0)
        else:
            # List existing services
            args = Namespace()

            for conf in ['spatial', 'persistent', 'wps', 'dataset']:
                setattr(args, conf, False)

            setattr(args, get_setting_type(setting), True)
            services = services_list_command(args)[0]

            if len(services) <= 0:
                write_warning('No compatible services found. See:\n\n  tethys services create {} -h\n'
                              .format(get_setting_type(setting)))
                continue

            while not valid:
                write_msg('\nEnter the service ID/Name to link to the current service setting: {}.'
                          .format(setting.name))
                try:
                    service_id = get_interactive_input()
                    if service_id != "":
                        try:
                            setting_type = get_setting_type_from_setting(setting)
                            service_type = get_service_type_from_setting(setting)
                        except RuntimeError as e:
                            write_error(str(e) + ' Skipping...')
                            break

                        # Validate the given service id
                        valid_service = validate_service_id(service_type, service_id)

                        if valid_service:
                            link_service_to_app_setting(service_type,
                                                        service_id,
                                                        app_name,
                                                        setting_type,
                                                        setting.name)

                            valid = True
                        else:
                            write_error('Incorrect service ID/Name. Please try again.')

                    else:
                        write_msg("Skipping setup of {}".format(setting.name))
                        valid = True

                except (KeyboardInterrupt, SystemExit):
                    write_msg('\nInstall Command cancelled.')
                    exit(0)


def find_and_link(service_type, setting_name, service_id, app_name, setting):
    valid_service = validate_service_id(service_type, service_id)
    setting_type = get_setting_type_from_setting(setting)
    if valid_service:
        link_service_to_app_setting(service_type, service_id, app_name, setting_type, setting_name)
    else:
        write_error(f'Warning: Could not find service of type: "{service_type}" with the Name/ID: "{service_id}"')


def configure_services_from_file(services, app_name):
    from tethys_apps.models import CustomSetting

    if services['version']:
        del services['version']
    for service_type in services:
        if services[service_type] is not None:
            current_services = services[service_type]
            for setting_name in current_services:
                if service_type == 'custom_setting':
                    try:
                        custom_setting = CustomSetting.objects.get(name=setting_name)
                    except ObjectDoesNotExist:
                        write_warning(f'Custom setting named "{setting_name}" could not be found in app "{app_name}". '
                                      f'Skipping...')
                        continue

                    try:
                        custom_setting.value = current_services[setting_name]
                        custom_setting.clean()
                        custom_setting.save()
                        write_success(f'CustomSetting: "{setting_name}" was assigned the value: '
                                      f'"{current_services[setting_name]}"')
                    except ValidationError:
                        write_error("Incorrect value type given for custom setting '{}'. Please adjust "
                                    "services.yml or set the value in the app's settings page."
                                    .format(setting_name))
                else:
                    app_settings = get_app_settings(app_name)

                    # In the case the app isn't installed, has no settings, or it is an extension,
                    # skip configuring services/settings
                    if not app_settings:
                        write_msg(f'No settings found for app "{app_name}". Skipping automated configuration...')
                        return

                    unlinked_settings = app_settings['unlinked_settings']

                    setting_found = False

                    for setting in unlinked_settings:

                        if setting.name != setting_name:
                            continue

                        setting_found = True

                        service_id = current_services[setting_name]
                        if not service_id:
                            write_warning(f'No service given for setting "{setting_name}". Skipping...')
                            continue

                        find_and_link(service_type, setting_name, service_id, app_name, setting)

                    if not setting_found:
                        write_warning(f'Service setting "{setting_name}" already configured or does not exist in app '
                                      f'"{app_name}". Skipping...')


def run_portal_install(app_name):

    file_path = Path(get_tethys_home_dir()) / 'portal_config.yml'

    if not file_path.exists():
        write_msg("No Portal Services file found. Searching for local app level services.yml...")
        return False

    write_msg("Portal install file found...Processing...")
    portal_options = open_file(file_path)
    app_check = portal_options and 'apps' in portal_options and portal_options['apps']
    if app_check and app_name in portal_options['apps'] and 'services' in portal_options['apps'][app_name]:
        services = portal_options['apps'][app_name]['services']
        if services and len(services) > 0:
            configure_services_from_file(services, app_name)
        else:
            write_msg("No app configuration found for app: {} in portal config file. "
                      "Searching for local app level services.yml... ".format(app_name))
            return False

    else:
        write_msg("No apps configuration found in portal config file. "
                  "Searching for local app level services.yml... ")
        return False

    return True


def run_services(app_name, args):
    file_path = Path('./services.yml') if args.services_file is None else Path(args.services_file)

    if not file_path.exists():
        write_msg("No Services file found.")
        return

    services = open_file(file_path)

    if services and len(services) > 0:
        configure_services_from_file(services, app_name)
    else:
        write_msg("No Services listed in Services file.")


def install_packages(conda_config, update_installed=False):
    # Compile channels arguments
    install_args = []
    if validate_schema('channels', conda_config):
        channels = conda_config['channels']
        for channel in channels:
            install_args.extend(['-c', channel])

    # Install all Packages
    if validate_schema('packages', conda_config):
        if not update_installed:
            install_args.extend(['--freeze-installed'])
        else:
            write_warning('Warning: Updating previously installed packages. This could break your Tethys environment.')
        install_args.extend(conda_config['packages'])
        write_msg("Running conda installation tasks...")
        [resp, err, code] = conda_run(
            Commands.INSTALL, *install_args, use_exception_handler=False, stdout=None, stderr=None)
        if code != 0:
            write_error('Warning: Packages installation ran into an error. Please try again or a manual install')


def install_command(args):
    """
    install Command
    """
    app_name = None
    skip_config = False
    file_path = Path('./install.yml') if args.file is None else Path(args.file)

    # Check for install.yml file
    if not file_path.exists():
        write_warning('WARNING: No install file found.')
        if not args.quiet:
            valid_inputs = ('y', 'n', 'yes', 'no')
            no_inputs = ('n', 'no')

            generate_input = input('Would you like to generate a template install.yml file in your current directory '
                                   'now? (y/n): ')

            while generate_input not in valid_inputs:
                generate_input = input('Invalid option. Try again. (y/n): ').lower()

            if generate_input in no_inputs:
                skip_config = True
                write_msg('Generation of Install File cancelled.')
            else:
                call(['tethys', 'gen', 'install'])
                write_msg('Install file generated. Fill out necessary information and re-install.')
                exit(0)

        write_warning('Continuing install without configuration.')

    # Install Dependencies
    if not skip_config:
        write_msg("Installing dependencies...")
        install_options = open_file(file_path)

        if "name" in install_options:
            app_name = install_options['name']

        if validate_schema('requirements', install_options):
            requirements_config = install_options['requirements']
            skip = False
            if "skip" in requirements_config:
                skip = requirements_config['skip']

            if skip:
                write_warning("Skipping package installation, Skip option found.")
            elif args.without_dependencies:
                write_warning("Skipping package installation.")
            else:
                if validate_schema('conda', requirements_config):  # noqa: E501
                    conda_config = requirements_config['conda']
                    install_packages(conda_config, update_installed=args.update_installed)
                if validate_schema('pip', requirements_config):
                    write_msg("Running pip installation tasks...")
                    call(['pip', 'install', *requirements_config["pip"]])

    # Skip the rest if we are installing dependencies only
    if args.only_dependencies:
        successful_exit(app_name, "installed dependencies for")

    # Run Setup.py
    write_msg("Running application install....")
    if args.verbose:
        call(['python', 'setup.py', 'clean', '--all'], stderr=STDOUT)
        if args.develop:
            call(['python', 'setup.py', 'develop'], stderr=STDOUT)
        else:
            call(['python', 'setup.py', 'install'], stderr=STDOUT)
    else:
        call(['python', 'setup.py', 'clean', '--all'], stdout=FNULL, stderr=STDOUT)
        if args.develop:
            call(['python', 'setup.py', 'develop'], stdout=FNULL, stderr=STDOUT)
        else:
            call(['python', 'setup.py', 'install'], stdout=FNULL, stderr=STDOUT)

    if args.no_db_sync:
        successful_exit(app_name)

    call(['tethys', 'db', 'sync'])

    # Run Portal Level Config if present
    if not skip_config:
        load_apps()
        if args.force_services:
            run_services(app_name, args)
        else:
            portal_result = run_portal_install(app_name)
            if not portal_result:
                run_services(app_name, args)

        if args.quiet:
            write_msg("Quiet mode: No additional service setting validation will be performed.")
        else:
            run_interactive_services(app_name)

        write_success("Services Configuration Completed.")

        app_settings = get_app_settings(app_name)

        if app_settings is not None:
            linked_settings = app_settings['linked_settings']
            unlinked_settings = app_settings['unlinked_settings']
            if args.no_sync_stores:
                write_msg('Skipping syncstores.')
            else:
                run_sync_stores(app_name, linked_settings)

            print_unconfigured_settings(app_name, unlinked_settings)

        # Check to see if any extra scripts need to be run
        if validate_schema('post', install_options):
            write_msg("Running post installation tasks...")
            for post in install_options["post"]:
                path_to_post = file_path.resolve().parent / post
                # Attempting to run processes.
                process = Popen(str(path_to_post), shell=True, stdout=PIPE)
                stdout = process.communicate()[0]
                write_msg("Post Script Result: {}".format(stdout))
    successful_exit(app_name)


def validate_schema(check_str, check_list):
    return check_str in check_list and check_list[check_str] and len(check_list[check_str]) > 0


def successful_exit(app_name, action="installed"):
    write_success(f"Successfully {action} {app_name}.")
    exit(0)
