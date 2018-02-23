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
from termcolor import colored
import importlib

from builtins import input

from tethys_apps.cli.scaffold_commands import scaffold_command
from tethys_apps.terminal_colors import TerminalColors
from .docker_commands import *
from .gen_commands import GEN_SETTINGS_OPTION, GEN_APACHE_OPTION, generate_command
from .manage_commands import (manage_command, get_manage_path, run_process,
                              MANAGE_START, MANAGE_SYNCDB,
                              MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES,
                              MANAGE_COLLECT, MANAGE_CREATESUPERUSER, TETHYS_SRC_DIRECTORY)
from .gen_commands import VALID_GEN_OBJECTS, generate_command
from tethys_apps.helpers import get_installed_tethys_apps

# Module level variables
PREFIX = 'tethysapp'

def get_tethys_processes_directory():
    """
    Return the absolute path to the tethys_wps directory.
    """
    return os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'tethys_wps/processes')


def CheckIdentifierExist(name):
    """
    Check if the service identifier already be used
    """
    identifiers = []
    import tethys_wps.processes
    import inspect
    for m in inspect.getmembers(tethys_wps.processes, inspect.isclass):
        identifiers.append(m[0])

    if name in identifiers:
        return True
    else:
        return False


def wps_command(args):

    """
    Public WPS service from a Tethys app
    """
    # Get tethys pywps processes folder
    tethys_wps_processes_dir = get_tethys_processes_directory()
    # Get __init__ file path in tethys pywps processes folder
    pywps_init_file_path = os.path.join(tethys_wps_processes_dir, '__init__.py')

    if args.command == 'list':

        from os import listdir
        from os.path import isfile, join
        from pywps import Process

        all_processes = []
        publish_processes = []

        print(colored("Published WPS services: ", color='green'))
        import tethys_wps.processes
        import inspect
        for m in inspect.getmembers(tethys_wps.processes, inspect.isclass):
            print(m[0])
            publish_processes.append(m[0])

        print(colored("Unpublished WPS services: ", color='yellow'))
        for f in listdir(tethys_wps_processes_dir):
            if isfile(join(tethys_wps_processes_dir, f)):
                if f.endswith(".py"):
                    if not f.startswith("_"):
                        module = importlib.import_module("tethys_wps.processes." + f.split('.')[0])
                        for m in inspect.getmembers(module, inspect.isclass):
                            if issubclass(m[1], Process) and m[0] != 'Process':
                                all_processes.append(m[0])
        for item in all_processes:
            if item not in publish_processes:
                print(item)


    if args.command == 'publish':
        appname_input = raw_input('Please provide your Tethys App name: ')

        if "tethysapp" not in appname_input:
            process_appname = appname_input
        else:
            process_appname = appname_input.replace("tethysapp-", "")
        print(process_appname)

        # Get tethys app wps process file path
        app_process_name = process_appname.replace('-', '').replace('_', '').lower()
        process_file_name = app_process_name + '_process.py'
        process_symbol_file_path = os.path.join(tethys_wps_processes_dir, process_file_name)

        if os.path.exists(process_symbol_file_path):

            identifier_inputs = raw_input('Please provide your process identifier (separate with comma if multiple): ')
            identifier_array = identifier_inputs.split(',')

            for name in identifier_array:
                try:
                    # Check if the identifier conflicts with any servive on the server
                    exit = CheckIdentifierExist(name)
                    if exit:
                        print(colored(
                            "Error: Identifier " + name + " already exists on Tethys WPS Server. Please rename it.",
                            color='red'))
                    else:
                        # Check if the identifier valid
                        f = open(pywps_init_file_path, 'ab')
                        good = True
                        try:
                            module = importlib.import_module("tethys_wps.processes." + app_process_name + "_process")
                            my_class = getattr(module, name)
                            instance = my_class()
                        except Exception as ex:
                            good = False
                            print(colored("Error: Invalid indentifier: " + name + ". Please check your inputs.",
                                          color='red'))
                            print(ex)
                        if good:
                            f.write("from " + app_process_name + "_process import " + name + '\n')
                            print(colored("Process " + name + " has been successfully published.", color='green'))
                        f.close()
                except Exception as ex:
                    print(ex)
        else:
            print(colored("Notice: no WPS process file found.", color='red'))


    if args.command == 'remove':

        identifier_input = raw_input('Please provide your process identifier to remove: ')

        try:
            # Check if the identifier conflicts with any servive on the server
            exit = CheckIdentifierExist(identifier_input)
            if not exit:
                print(colored(
                    "Error: Identifier " + identifier_input + " not exist on Tethys WPS Server.", color='red'))
            else:
                f = open(pywps_init_file_path, 'rb')
                output = []
                for line in f:
                    if line.split(' ')[-1].strip() != identifier_input:
                       output.append(line)
                f.close()
                f = open(pywps_init_file_path, 'w')
                f.writelines(output)
                f.close()
                print(colored(
                    "Process " + identifier_input + " has been successfully removed.", color='green'))
        except Exception as ex:
            print(ex)


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
        # Remove WPS process
        tethys_pywps_processes_dir = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'tethys_wps/processes/')

        if "tethysapp-" in app_name:
             app_name_noprefix = app_name.replace("tethysapp-", "")
        else:
            app_name_noprefix = app_name

        app_process_file_path = os.path.join(tethys_pywps_processes_dir, app_name_noprefix.replace('_', '').lower() + '_process.py')
        pywps_init_file_path = os.path.join(tethys_pywps_processes_dir, '__init__.py')

        # remove process file
        if os.path.exists(app_process_file_path):
            os.remove(app_process_file_path)
            # modify init file
            app_process_name = app_name_noprefix.replace('_', '').lower() + '_process'
            f = open(pywps_init_file_path, 'rb')
            output = []
            for line in f:
                if not app_process_name in line:
                    output.append(line)
            f.close()
            f = open(pywps_init_file_path, 'w')
            f.writelines(output)
            f.close()
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
            app_package = app_package_tag + app_package_parts[1].split('.')[0]
            config_opt = '--source={0}'.format(app_package)
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
                               choices=[MANAGE_START, MANAGE_SYNCDB, MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES, MANAGE_COLLECT, MANAGE_CREATESUPERUSER])
    manage_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    manage_parser.add_argument('-p', '--port', type=str, help='Host and/or port on which to bind the development server.')
    manage_parser.add_argument('--noinput', action='store_true', help='Pass the --noinput argument to the manage.py command.')
    manage_parser.set_defaults(func=manage_command)

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

    # Setup wps command
    wps_parser = subparsers.add_parser('wps', help='Publish WPS service from Tethys app.')
    wps_parser.add_argument('command',
                            help='"publish": publish WPS service(s). "list": list published and unpublished processes. "remove": remove a WPS service.',
                            choices=['publish', 'list', 'remove'])
    wps_parser.set_defaults(func=wps_command)

    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)