import os
import shutil
import subprocess

from tethys_apps.helpers import get_installed_tethys_apps

DEFAULT_INSTALLATION_DIRECTORY = '/usr/lib/tethys/src'
DEVELOPMENT_DIRECTORY = '/usr/lib/tethys/tethys'
MANAGE_START = 'start'
MANAGE_SYNCDB = 'syncdb'
MANAGE_COLLECTSTATIC = 'collectstatic'
MANAGE_COLLECTWORKSPACES = 'collectworkspaces'
MANAGE_COLLECT = 'collectall'


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
    process = None

    if args.command == MANAGE_START:
        if args.port:
            process = ['python', manage_path, 'runserver', str(args.port)]
        else:
            process = ['python', manage_path, 'runserver']
    elif args.command == MANAGE_SYNCDB:
        process = ['python', manage_path, 'syncdb']

    elif args.command == MANAGE_COLLECTSTATIC:
        # Run pre_collectstatic
        process = ['python', manage_path, 'pre_collectstatic']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

        # Setup for main collectstatic
        process = ['python', manage_path, 'collectstatic']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

    elif args.command == MANAGE_COLLECTWORKSPACES:
        # Run collectworkspaces command
        process = ['python', manage_path, 'collectworkspaces']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

    elif args.command == MANAGE_COLLECT:
        # Convenience command to run collectstatic and collectworkspaces
        ## Run pre_collectstatic
        process = ['python', manage_path, 'pre_collectstatic']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

        ## Setup for main collectstatic
        process = ['python', manage_path, 'collectstatic']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

        ## Run collectworkspaces command
        process = ['python', manage_path, 'collectworkspaces']
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass

    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    if process:
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass