"""
********************************************************************************
* Name: manage_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import os
import subprocess

from tethys_apps.base.testing.environment import set_testing_environment

#/usr/lib/tethys/src/tethys_apps/cli
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#/usr/lib/tethys
TETHYS_MAIN_DIR = os.sep.join(CURRENT_SCRIPT_DIR.split(os.sep)[:-3])
#/usr/lib/tethys/src
DEFAULT_INSTALLATION_DIRECTORY = os.path.join(TETHYS_MAIN_DIR,'src')
#/usr/lib/tethys/tethys
DEVELOPMENT_DIRECTORY = os.path.join(TETHYS_MAIN_DIR,'tethys')
MANAGE_START = 'start'
MANAGE_SYNCDB = 'syncdb'
MANAGE_COLLECTSTATIC = 'collectstatic'
MANAGE_COLLECTWORKSPACES = 'collectworkspaces'
MANAGE_COLLECT = 'collectall'
MANAGE_CREATESUPERUSER = 'createsuperuser'


def get_manage_path(args):
    """
    Validate user defined manage path, use default, or throw error
    """
    # Determine path to manage.py file
    manage_path = os.path.join(DEFAULT_INSTALLATION_DIRECTORY, 'manage.py')

    # Check for path option
    if args.manage:
        manage_path = args.manage

        # Throw error if path is not valid
        if not os.path.isfile(manage_path):
            print('ERROR: Can\'t open file "{0}", no such file.'.format(manage_path))
            exit(1)

    elif not os.path.isfile(manage_path):
        # Try the development path version
        manage_path = os.path.join(DEVELOPMENT_DIRECTORY, 'manage.py')

        # Throw error if default path is not valid
        if not os.path.isfile(manage_path):
            print('ERROR: Cannot find the "manage.py" file at the default location. Try using the "--manage"'
                  'option to provide the path to the location of the "manage.py" file.')
            exit(1)

    return manage_path


def manage_command(args):
    """
    Management commands.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # Define the process to be run
    primary_process = None


    if args.command == MANAGE_START:
        if args.port:
            primary_process = ['python', manage_path, 'runserver', args.port]
        else:
            primary_process = ['python', manage_path, 'runserver']
    elif args.command == MANAGE_SYNCDB:
        intermediate_process = ['python', manage_path, 'makemigrations']
        run_process(intermediate_process)

        primary_process = ['python', manage_path, 'migrate']

    elif args.command == MANAGE_COLLECTSTATIC:
        # Run pre_collectstatic
        intermediate_process = ['python', manage_path, 'pre_collectstatic']
        run_process(intermediate_process)

        # Setup for main collectstatic
        primary_process = ['python', manage_path, 'collectstatic']

    elif args.command == MANAGE_COLLECTWORKSPACES:
        # Run collectworkspaces command
        primary_process = ['python', manage_path, 'collectworkspaces']

    elif args.command == MANAGE_COLLECT:
        # Convenience command to run collectstatic and collectworkspaces
        ## Run pre_collectstatic
        intermediate_process = ['python', manage_path, 'pre_collectstatic']
        run_process(intermediate_process)

        ## Setup for main collectstatic
        intermediate_process = ['python', manage_path, 'collectstatic']
        run_process(intermediate_process)

        ## Run collectworkspaces command
        primary_process = ['python', manage_path, 'collectworkspaces']

    elif args.command == MANAGE_CREATESUPERUSER:
        primary_process = ['python', manage_path, 'createsuperuser']

    if primary_process:
        run_process(primary_process)


def run_process(process):
    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    try:
        if 'test' in process:
            set_testing_environment(True)
        subprocess.call(process)
    except KeyboardInterrupt:
        pass
    finally:
        set_testing_environment(False)
