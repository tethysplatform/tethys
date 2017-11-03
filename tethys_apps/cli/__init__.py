"""
********************************************************************************
* Name: cli/__init__.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
# Commandline interface for Tethys
import argparse
import os
import subprocess
import webbrowser

from builtins import input

from tethys_apps.cli.scaffold_commands import scaffold_command
from tethys_apps.terminal_colors import TerminalColors
from .docker_commands import *
from .gen_commands import GEN_SETTINGS_OPTION, GEN_APACHE_OPTION, generate_command
from .manage_commands import (manage_command, get_manage_path, run_process,
                              MANAGE_START, MANAGE_SYNCDB,
                              MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES, MANAGE_SYNCAPPS,
                              MANAGE_COLLECT, MANAGE_CREATESUPERUSER, TETHYS_SRC_DIRECTORY)
from .services_commands import (SERVICES_CREATE, SERVICES_CREATE_PERSISTENT, SERVICES_CREATE_SPATIAL, SERVICES_LINK,
                                services_create_persistent_command, services_create_spatial_command,
                                services_list_command, services_remove_persistent_command,
                                services_remove_spatial_command)
from .link_commands import link_command
from .app_settings_commands import (app_settings_list_command, app_settings_create_ps_database_command,
                                    app_settings_remove_command)
from .scheduler_commands import scheduler_create_command, schedulers_list_command, schedulers_remove_command
from .gen_commands import VALID_GEN_OBJECTS, generate_command
from tethys_apps.helpers import get_installed_tethys_apps

# Module level variables
PREFIX = 'tethysapp'


def uninstall_command(args):
    """
    Uninstall an app command.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)
    app_name = args.app
    process = ['python', manage_path, 'tethys_app_uninstall', app_name]
    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass


def list_apps_command(args):
    """
    List installed apps.
    """
    installed_apps = get_installed_tethys_apps()

    for app in installed_apps:
        print(app)


def docker_command(args):
    """
    Docker management commands.
    """
    if args.command == 'init':
        docker_init(containers=args.containers, defaults=args.defaults)

    elif args.command == 'start':
        docker_start(containers=args.containers)

    elif args.command == 'stop':
        docker_stop(containers=args.containers, boot2docker=args.boot2docker)

    elif args.command == 'status':
        docker_status()

    elif args.command == 'update':
        docker_update(containers=args.containers, defaults=args.defaults)

    elif args.command == 'remove':
        docker_remove(containers=args.containers)

    elif args.command == 'ip':
        docker_ip()

    elif args.command == 'restart':
        docker_restart(containers=args.containers)


def syncstores_command(args):
    """
    Sync persistent stores.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # This command is a wrapper for a custom Django manage.py method called syncstores.
    # See tethys_apps.mangement.commands.syncstores
    process = ['python', manage_path, 'syncstores']

    if args.refresh:
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')
        proceed = input('{1}WARNING:{2} You have specified the database refresh option. This will drop all of the '
                        'databases for the following apps: {0}. This could result in significant data loss and '
                        'cannot be undone. Do you wish to continue? (y/n): '.format(', '.join(args.app),
                                                                                    TerminalColors.WARNING,
                                                                                    TerminalColors.ENDC)).lower()

        while proceed not in valid_inputs:
            proceed = input('Invalid option. Do you wish to continue? (y/n): ').lower()

        if proceed not in no_inputs:
            process.extend(['-r'])
        else:
            print('Operation cancelled by user.')
            exit(0)

    if args.firsttime:
        process.extend(['-f'])

    if args.database:
        process.extend(['-d', args.database])

    if args.app:
        process.extend(args.app)

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass


def test_command(args):
    args.manage = False
    # Get the path to manage.py
    manage_path = get_manage_path(args)
    tests_path = os.path.join(TETHYS_SRC_DIRECTORY, 'tests')

    # Define the process to be run
    primary_process = ['python', manage_path, 'test']

    # Tag to later check if tests are being run on a specific app
    app_package_tag = 'tethys_apps.tethysapp.'

    if args.coverage or args.coverage_html:
        os.environ['TETHYS_TEST_DIR'] = tests_path
        if args.file and app_package_tag in args.file:
            app_package_parts = args.file.split(app_package_tag)
            app_name = app_package_parts[1].split('.')[0]
            core_app_package = '{}{}'.format(app_package_tag, app_name)
            app_package = 'tethysapp.{}'.format(app_name)
            config_opt = '--source={},{}'.format(core_app_package, app_package)
        else:
            config_opt = '--rcfile={0}'.format(os.path.join(tests_path, 'coverage.cfg'))
        primary_process = ['coverage', 'run', config_opt, manage_path, 'test']

    if args.file:
        primary_process.append(args.file)
    elif args.unit:
        primary_process.append(os.path.join(tests_path, 'unit_tests'))
    elif args.gui:
        primary_process.append(os.path.join(tests_path, 'gui_tests'))

    # print(primary_process)
    run_process(primary_process)
    if args.coverage:
        if args.file and app_package_tag in args.file:
            run_process(['coverage', 'report'])
        else:
            run_process(['coverage', 'report', config_opt])
    if args.coverage_html:
        report_dirname = 'coverage_html_report'
        index_fname = 'index.html'

        if args.file and app_package_tag in args.file:
            run_process(['coverage', 'html', '--directory={0}'.format(os.path.join(tests_path, report_dirname))])
        else:
            run_process(['coverage', 'html', config_opt])

        try:
            status = run_process(['open', os.path.join(tests_path, report_dirname, index_fname)])
            if status != 0:
                raise Exception
        except:
            webbrowser.open_new_tab(os.path.join(tests_path, report_dirname, index_fname))


def tethys_command():
    """
    Tethys commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands')

    # Setup scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Create a new Tethys app project from a scaffold.')
    scaffold_parser.add_argument('name', help='The name of the new Tethys app project to create. Only lowercase '
                                              'letters, numbers, and underscores allowed.')
    scaffold_parser.add_argument('-t', '--template', dest='template', help="Name of app template to use.")
    scaffold_parser.add_argument('-e', '--extension', dest='extension', help="Name of extension template to use.")
    scaffold_parser.add_argument('-d', '--defaults', dest='use_defaults', action='store_true',
                                 help="Run command, accepting default values automatically.")
    scaffold_parser.add_argument('-o', '--overwrite', dest='overwrite', action="store_true",
                                 help="Attempt to overwrite project automatically if it already exists.")
    scaffold_parser.set_defaults(func=scaffold_command, template='default', extension=None)

    # Setup generate command
    gen_parser = subparsers.add_parser('gen', help='Aids the installation of Tethys by automating the '
                                                   'creation of supporting files.')
    gen_parser.add_argument('type', help='The type of object to generate.', choices=VALID_GEN_OBJECTS)
    gen_parser.add_argument('-d', '--directory', help='Destination directory for the generated object.')
    gen_parser.add_argument('--allowed-host', dest='allowed_host',
                            help='Hostname or IP address to add to allowed hosts in the settings file.')
    gen_parser.add_argument('--db-username', dest='db_username',
                            help='Username for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-password', dest='db_password',
                            help='Password for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-port', dest='db_port',
                            help='Port for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--production', dest='production', action='store_true',
                            help='Generate a new settings file for a production server.')
    gen_parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                            help='Overwrite existing file without prompting.')
    gen_parser.set_defaults(func=generate_command, allowed_host=None, db_username='tethys_default',
                            db_password='pass', db_port=5436, production=False, overwrite=False)

    # Setup start server command
    manage_parser = subparsers.add_parser('manage', help='Management commands for Tethys Platform.')
    manage_parser.add_argument('command', help='Management command to run.',
                               choices=[MANAGE_START, MANAGE_SYNCDB, MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES,
                                        MANAGE_COLLECT, MANAGE_CREATESUPERUSER, MANAGE_SYNCAPPS])
    manage_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    manage_parser.add_argument('-p', '--port', type=str, help='Host and/or port on which to bind the development server.')
    manage_parser.add_argument('--noinput', action='store_true', help='Pass the --noinput argument to the manage.py command.')
    manage_parser.add_argument('-f', '--force', required=False, action='store_true',
                               help='Used only with {} to force the overwrite the app directory into its collect-to '
                                    'location.')
    manage_parser.set_defaults(func=manage_command)

    # SCHEDULERS COMMANDS
    scheduler_parser = subparsers.add_parser('schedulers', help='Scheduler commands for Tethys Platform.')
    scheduler_subparsers = scheduler_parser.add_subparsers(title='Commands')

    # tethys schedulers create
    schedulers_create = scheduler_subparsers.add_parser('create', help='Create a Scheduler that can be '
                                                                       'accessed by Tethys Apps.')
    schedulers_create.add_argument('-n', '--name', required=True, help='A unique name for the Scheduler', type=str)
    schedulers_create.add_argument('-e', '--endpoint', required=True, type=str,
                                   help='The endpoint of the service in the form <protocol>//<host>"')
    schedulers_create.add_argument('-u', '--username', required=True, help='The username to connect to the host with',
                                   type=str)
    group = schedulers_create.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--password', required=False, type=str,
                       help='The password associated with the provided username')
    group.add_argument('-f', '--private-key-path', required=False, help='The path to the private ssh key file',
                       type=str)
    schedulers_create.add_argument('-k', '--private-key-pass', required=False, type=str,
                                   help='The password to the private ssh key file')
    schedulers_create.set_defaults(func=scheduler_create_command)

    # tethys schedulers list
    schedulers_list = scheduler_subparsers.add_parser('list', help='List the existing Schedulers.')
    schedulers_list.set_defaults(func=schedulers_list_command)

    # tethys schedulers remove
    schedulers_remove = scheduler_subparsers.add_parser('remove', help='Remove a Scheduler.')
    schedulers_remove.add_argument('scheduler_name', help='The unique name of the Scheduler that you are removing.')
    schedulers_remove.add_argument('-f', '--force', action='store_true', help='Force removal without confirming.')
    schedulers_remove.set_defaults(func=schedulers_remove_command)

    # SERVICES COMMANDS
    services_parser = subparsers.add_parser('services', help='Services commands for Tethys Platform.')
    services_subparsers = services_parser.add_subparsers(title='Commands')

    # tethys services remove
    services_remove_parser = services_subparsers.add_parser('remove', help='Remove a Tethys Service.')
    services_remove_subparsers = services_remove_parser.add_subparsers(title='Service Type')

    # tethys services remove persistent
    services_remove_persistent = services_remove_subparsers.add_parser('persistent',
                                                                       help='Remove a Persistent Store Service.')
    services_remove_persistent.add_argument('service_uid', help='The ID or name of the Persistent Store Service '
                                                                'that you are removing.')
    services_remove_persistent.add_argument('-f', '--force', action='store_true',
                                            help='Force removal without confirming.')
    services_remove_persistent.set_defaults(func=services_remove_persistent_command)

    # tethys services remove spatial
    services_remove_spatial = services_remove_subparsers.add_parser('spatial',
                                                                    help='Remove a Spatial Dataset Service.')
    services_remove_spatial.add_argument('service_uid', help='The ID or name of the Spatial Dataset Service '
                                                             'that you are removing.')
    services_remove_spatial.add_argument('-f', '--force', action='store_true', help='Force removal without confirming.')
    services_remove_spatial.set_defaults(func=services_remove_spatial_command)

    # tethys services create
    services_create_parser = services_subparsers.add_parser('create', help='Create a Tethys Service.')
    services_create_subparsers = services_create_parser.add_subparsers(title='Service Type')

    # tethys services create persistent
    services_create_ps = services_create_subparsers.add_parser('persistent',
                                                               help='Create a Persistent Store Service.')
    services_create_ps.add_argument('-n', '--name', required=True, help='A unique name for the Service', type=str)
    services_create_ps.add_argument('-c', '--connection', required=True, type=str,
                                    help='The connection of the Service in the form '
                                         '"<username>:<password>@<host>:<port>"')
    services_create_ps.set_defaults(func=services_create_persistent_command)

    # tethys services create spatial
    services_create_sd = services_create_subparsers.add_parser('spatial',
                                                               help='Create a Spatial Dataset Service.')
    services_create_sd.add_argument('-n', '--name', required=True, help='A unique name for the Service', type=str)
    services_create_sd.add_argument('-c', '--connection', required=True, type=str,
                                    help='The connection of the Service in the form '
                                         '"<username>:<password>@<protocol>//<host>:<port>"')
    services_create_sd.add_argument('-p', '--public-endpoint', required=False, type=str,
                                    help='The public-facing endpoint, if different than what was provided with the '
                                         '--connection argument, of the form "<host>:<port>"')
    services_create_sd.add_argument('-k', '--apikey', required=False, type=str,
                                    help='The API key, if any, required to establish a connection.')
    services_create_sd.set_defaults(func=services_create_spatial_command)

    # tethys services list
    services_list_parser = services_subparsers.add_parser('list', help='List all existing Tethys Services.')
    group = services_list_parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--persistent', action='store_true', help='Only list Persistent Store Services.')
    group.add_argument('-s', '--spatial', action='store_true', help='Only list Spatial Dataset Services.')
    services_list_parser.set_defaults(func=services_list_command)

    # APP_SETTINGS COMMANDS
    app_settings_parser = subparsers.add_parser('app_settings', help='Interact with Tethys App Settings.')
    app_settings_subparsers = app_settings_parser.add_subparsers(title='Options')

    # tethys app_settings list
    app_settings_list_parser = app_settings_subparsers.add_parser('list', help='List all settings for a specified app')
    app_settings_list_parser.add_argument('app', help='The app ("<app_package>") to list the Settings for.')
    app_settings_list_parser.set_defaults(func=app_settings_list_command)

    # tethys app_settings create
    app_settings_create_cmd = app_settings_subparsers.add_parser('create', help='Create a Setting for an app.')

    asc_subparsers = app_settings_create_cmd.add_subparsers(title='Create Options')
    app_settings_create_cmd.add_argument('-a', '--app', required=True,
                                         help='The app ("<app_package>") to create the Setting for.')
    app_settings_create_cmd.add_argument('-n', '--name', required=True, help='The name of the Setting to create.')
    app_settings_create_cmd.add_argument('-d', '--description', required=False,
                                         help='A description for the Setting to create.')
    app_settings_create_cmd.add_argument('-r', '--required', required=False, action='store_true',
                                         help='Include this flag if the Setting is required for the app.')
    app_settings_create_cmd.add_argument('-i', '--initializer', required=False,
                                         help='The function that initializes the PersistentStoreSetting database.')
    app_settings_create_cmd.add_argument('-z', '--initialized', required=False, action='store_true',
                                         help='Include this flag if the database is already initialized.')

    # tethys app_settings create ps_database
    app_settings_create_psdb_cmd = asc_subparsers.add_parser('ps_database',
                                                             help='Create a PersistentStoreDatabaseSetting')
    app_settings_create_psdb_cmd.add_argument('-s', '--spatial', required=False, action='store_true',
                                              help='Include this flag if the database requires spatial capabilities.')
    app_settings_create_psdb_cmd.add_argument('-y', '--dynamic', action='store_true', required=False,
                                              help='Include this flag if the database should be considered to be '
                                                   'dynamically created.')
    app_settings_create_psdb_cmd.set_defaults(func=app_settings_create_ps_database_command)

    # tethys app_settings remove
    app_settings_remove_cmd = app_settings_subparsers.add_parser('remove', help='Remove a Setting for an app.')
    app_settings_remove_cmd.add_argument('app', help='The app ("<app_package>") to remove the Setting from.')
    app_settings_remove_cmd.add_argument('-n', '--name', help='The name of the Setting to remove.', required=True)
    app_settings_remove_cmd.add_argument('-f', '--force', action='store_true', help='Force removal without confirming.')
    app_settings_remove_cmd.set_defaults(func=app_settings_remove_command)

    # LINK COMMANDS
    link_parser = subparsers.add_parser('link', help='Link a Service to a Tethys app Setting.')

    # tethys link
    link_parser.add_argument('service', help='Service to link to a target app. Of the form '
                                             '"<spatial|persistent>:<service_id|service_name>" '
                                             '(i.e. "persistent_connection:super_conn")')
    link_parser.add_argument('setting', help='Setting of an app with which to link the specified service.'
                                             'Of the form "<app_package>:<setting_type (ps_database|ps_connection|ds_spatial)>:'
                                             '<setting_id|setting_name>" (i.e. "epanet:database:epanet_2")')
    link_parser.set_defaults(func=link_command)

    # Setup test command
    test_parser = subparsers.add_parser('test', help='Testing commands for Tethys Platform.')
    test_parser.add_argument('-c', '--coverage', help='Run coverage with tests and output report to console.',
                             action='store_true')
    test_parser.add_argument('-C', '--coverage-html', help='Run coverage with tests and output html formatted report.',
                             action='store_true')
    test_parser.add_argument('-u', '--unit', help='Run only unit tests.', action='store_true')
    test_parser.add_argument('-g', '--gui', help='Run only gui tests. Mutually exclusive with -u. '
                                                 'If both flags are set then -u takes precedence.',
                             action='store_true')
    test_parser.add_argument('-f', '--file', type=str, help='File to run tests in. Overrides -g and -u.')
    test_parser.set_defaults(func=test_command)

    # Setup uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall an app.')
    uninstall_parser.add_argument('app', help='Name of the app to uninstall.')
    uninstall_parser.set_defaults(func=uninstall_command)

    # Setup list command
    list_parser = subparsers.add_parser('list', help='List installed apps.')
    list_parser.set_defaults(func=list_apps_command)

    # Sync stores command
    syncstores_parser = subparsers.add_parser('syncstores', help='Management command for App Persistent Stores.')
    syncstores_parser.add_argument('app', help='Name of the target on which to perform persistent store sync OR "all" '
                                               'to sync all of them.',
                                   nargs='+')
    syncstores_parser.add_argument('-r', '--refresh',
                                   help='When called with this option, the tables will be dropped prior to syncing'
                                        ' resulting in a refreshed database.',
                                   action='store_true',
                                   dest='refresh')
    syncstores_parser.add_argument('-f', '--firsttime',
                                   help='Call with this option to force the initializer functions to be executed with '
                                        '"first_time" parameter True.',
                                   action='store_true',
                                   dest='firsttime')
    syncstores_parser.add_argument('-d', '--database', help='Name of database to sync.')
    syncstores_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    syncstores_parser.set_defaults(func=syncstores_command, refresh=False, firstime=False)

    # Setup the docker commands
    docker_parser = subparsers.add_parser('docker', help="Management commands for the Tethys Docker containers.")
    docker_parser.add_argument('command',
                               help='Docker command to run.',
                               choices=['init', 'start', 'stop', 'status', 'update', 'remove', 'ip', 'restart'])
    docker_parser.add_argument('-d', '--defaults',
                               action='store_true',
                               dest='defaults',
                               help="Run command without prompting without interactive input, using defaults instead.")
    docker_parser.add_argument('-c', '--containers',
                               nargs='+',
                               help="Execute the command only on the given container(s).",
                               choices=[POSTGIS_INPUT, GEOSERVER_INPUT, N52WPS_INPUT])
    docker_parser.add_argument('-b', '--boot2docker',
                               action='store_true',
                               dest='boot2docker',
                               help="Stop boot2docker on container stop. Only applicable to stop command.")
    docker_parser.set_defaults(func=docker_command)

    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)