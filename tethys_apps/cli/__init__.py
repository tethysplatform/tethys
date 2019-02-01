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

from tethys_apps.cli.docker_commands import docker_command, docker_container_inputs
from tethys_apps.cli.list_command import list_command as lc
from tethys_apps.cli.scaffold_commands import scaffold_command
from tethys_apps.cli.syncstores_command import syncstores_command as syc
from tethys_apps.cli.test_command import test_command as tstc
from tethys_apps.cli.uninstall_command import uninstall_command as uc
from tethys_apps.cli.manage_commands import (manage_command, MANAGE_START, MANAGE_SYNCDB,
                                             MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES, MANAGE_SYNC,
                                             MANAGE_COLLECT, MANAGE_CREATESUPERUSER)
from tethys_apps.cli.services_commands import (services_create_persistent_command, services_create_spatial_command,
                                               services_list_command, services_remove_persistent_command,
                                               services_remove_spatial_command)
from tethys_apps.cli.link_commands import link_command
from tethys_apps.cli.app_settings_commands import (app_settings_list_command, app_settings_create_ps_database_command,
                                                   app_settings_remove_command)
from tethys_apps.cli.scheduler_commands import (schedulers_list_command, schedulers_remove_command,
                                                condor_scheduler_create_command, dask_scheduler_create_command)
from tethys_apps.cli.gen_commands import VALID_GEN_OBJECTS, generate_command

# Module level variables
PREFIX = 'tethysapp'


def tethys_command():
    """
    Tethys commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands', dest='require at least one argument')
    subparsers.required = True

    # Setup scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Create a new Tethys app project from a scaffold.')
    scaffold_parser.add_argument('name', help='The name of the new Tethys app project to create. Only lowercase '
                                              'letters, numbers, and underscores allowed.')
    scaffold_parser.add_argument('-t', '--template', dest='template', help="Name of template to use.")
    scaffold_parser.add_argument('-e', '--extension', dest='extension', action="store_true")
    scaffold_parser.add_argument('-d', '--defaults', dest='use_defaults', action='store_true',
                                 help="Run command, accepting default values automatically.")
    scaffold_parser.add_argument('-o', '--overwrite', dest='overwrite', action="store_true",
                                 help="Attempt to overwrite project automatically if it already exists.")
    scaffold_parser.set_defaults(func=scaffold_command, template='default', extension=False)

    # Setup generate command
    gen_parser = subparsers.add_parser('gen', help='Aids the installation of Tethys by automating the '
                                                   'creation of supporting files.')
    gen_parser.add_argument('type', help='The type of object to generate.', choices=VALID_GEN_OBJECTS)
    gen_parser.add_argument('-d', '--directory', help='Destination directory for the generated object.')
    gen_parser.add_argument('--allowed-host', dest='allowed_host',
                            help='Single hostname or IP address to add to allowed hosts in the settings file. '
                                 'e.g.: 127.0.0.1')
    gen_parser.add_argument('--allowed-hosts', dest='allowed_hosts',
                            help='A list of hostnames or IP addresses to add to allowed hosts in the settings file. '
                                 'e.g.: "[\'127.0.0.1\', \'localhost\']"')
    gen_parser.add_argument('--client-max-body-size', dest='client_max_body_size',
                            help='Populates the client_max_body_size parameter for nginx config. Defaults to "75M".')
    gen_parser.add_argument('--uwsgi-processes', dest='uwsgi_processes',
                            help='The maximum number of uwsgi worker processes. Defaults to 10.')
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
    gen_parser.set_defaults(func=generate_command, allowed_host=None, allowed_hosts=None, client_max_body_size='75M',
                            uwsgi_processes=10, db_username='tethys_default', db_password='pass', db_port=5436,
                            production=False, overwrite=False)

    # Setup start server command
    manage_parser = subparsers.add_parser('manage', help='Management commands for Tethys Platform.')
    manage_parser.add_argument('command', help='Management command to run.',
                               choices=[MANAGE_START, MANAGE_SYNCDB, MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES,
                                        MANAGE_COLLECT, MANAGE_CREATESUPERUSER, MANAGE_SYNC])
    manage_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    manage_parser.add_argument('-p', '--port', type=str,
                               help='Host and/or port on which to bind the development server.')
    manage_parser.add_argument('--noinput', action='store_true',
                               help='Pass the --noinput argument to the manage.py command.')
    manage_parser.add_argument('-f', '--force', required=False, action='store_true',
                               help='Used only with {} to force the overwrite the app directory into its collect-to '
                                    'location.')
    manage_parser.set_defaults(func=manage_command)

    # SCHEDULERS COMMANDS
    scheduler_parser = subparsers.add_parser('schedulers', help='Scheduler commands for Tethys Platform.')
    scheduler_subparsers = scheduler_parser.add_subparsers(title='Commands')

    # tethys condor schedulers create
    condor_schedulers_create = scheduler_subparsers.add_parser('create-condor',
                                                               help='Create a Condor Scheduler that can be '
                                                               'accessed by Tethys Apps.')
    condor_schedulers_create.add_argument('-n', '--name', required=True,
                                          help='A unique name for the Condor Scheduler', type=str)
    condor_schedulers_create.add_argument('-e', '--endpoint', required=True, type=str,
                                          help='The endpoint of the service in the form <protocol>//<host>"')
    condor_schedulers_create.add_argument('-u', '--username', required=True,
                                          help='The username to connect to the host with', type=str)
    group = condor_schedulers_create.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--password', required=False, type=str,
                       help='The password associated with the provided username')
    group.add_argument('-f', '--private-key-path', required=False, help='The path to the private ssh key file',
                       type=str)
    condor_schedulers_create.add_argument('-k', '--private-key-pass', required=False, type=str,
                                          help='The password to the private ssh key file')
    condor_schedulers_create.set_defaults(func=condor_scheduler_create_command)

    # tethys dask schedulers create
    dask_schedulers_create = scheduler_subparsers.add_parser('create-dask', help='Create a Dask Scheduler that can be '
                                                             'accessed by Tethys Apps.')
    dask_schedulers_create.add_argument('-n', '--name', required=True,
                                        help='A unique name for the Condor Scheduler', type=str)
    dask_schedulers_create.add_argument('-e', '--endpoint', required=True, type=str,
                                        help='The endpoint of the service in the form <protocol>//<host>"')
    dask_schedulers_create.add_argument('-t', '--timeout', required=False, type=int,
                                        help='The timeout value of the Dask Job')
    dask_schedulers_create.add_argument('-b', '--heartbeat-interval', required=False,
                                        help='The heartbeat interval value of the Dask Job', type=int)
    dask_schedulers_create.add_argument('-d', '--dashboard', required=False, type=str,
                                        help='The dashboard type of a DaskJob')
    dask_schedulers_create.set_defaults(func=dask_scheduler_create_command)

    # tethys condor/dask schedulers list

    schedulers_list = scheduler_subparsers.add_parser('list', help='List the existing Schedulers.')
    schedulers_list.add_argument('-t', '--type', required=True,
                                 help='input: Condor or Dask (List Condor or Dask type)', type=str)
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
                                             'Of the form "<app_package>:'
                                             '<setting_type (ps_database|ps_connection|ds_spatial)>:'
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
    test_parser.set_defaults(func=tstc)

    # Setup uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall an app.')
    uninstall_parser.add_argument('app_or_extension', help='Name of the app or extension to uninstall.')
    uninstall_parser.add_argument('-e', '--extension', dest='is_extension', default=False, action='store_true',
                                  help='Flag to denote an extension is being uninstalled')
    uninstall_parser.set_defaults(func=uc)

    # Setup list command
    list_parser = subparsers.add_parser('list', help='List installed apps and extensions.')
    list_parser.set_defaults(func=lc)

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
    syncstores_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for '
                                                          'Tethys Platform installation.')
    syncstores_parser.set_defaults(func=syc, refresh=False, firstime=False)

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
                               choices=docker_container_inputs)
    docker_parser.add_argument('-b', '--boot2docker',
                               action='store_true',
                               dest='boot2docker',
                               help="Stop boot2docker on container stop. Only applicable to stop command.")
    docker_parser.set_defaults(func=docker_command)

    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)
