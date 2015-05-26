import os
import shutil
import subprocess

# from django.conf import settings

# Setup Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_apps.settings")

from tethys_apps.helpers import get_installed_tethys_apps
from tethys_apps import settings

DEFAULT_INSTALLATION_DIRECTORY = '/usr/lib/tethys/src'
DEVELOPMENT_DIRECTORY = '/usr/lib/tethys/tethys'
MANAGE_START = 'start'
MANAGE_SYNCDB = 'syncdb'
MANAGE_COLLECTSTATIC = 'collectstatic'


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
        if settings.STATIC_ROOT:
            installed_apps = get_installed_tethys_apps()
            pre_collectstatic(installed_apps, settings.STATIC_ROOT)
            process = ['python', manage_path, 'collectstatic']
        else:
            print('WARNING: Cannot find the STATIC_ROOT setting in the settings.py file. '
                  'Please provide the path to the static directory using the STATIC_ROOT setting and try again.')
            exit(1)

    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    if process:
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass


def pre_collectstatic(installed_apps, static_root):
    """
    Symbolically link the static directories of each app into the static/public directory specified by the STATIC_ROOT
    parameter of the settings.py. Do this prior to running Django's collectstatic method.
    """
    # Provide feedback to user
    print('INFO: Linking static and public directories of apps to "{0}".'.format(static_root))

    for app, path in installed_apps.iteritems():
        # Check for both variants of the static directory (public and static)
        public_path = os.path.join(path, 'public')
        static_path = os.path.join(path, 'static')
        static_root_path = os.path.join(static_root, app)

        # Clear out old symbolic links/directories if necessary
        try:
            # Remove link
            os.remove(static_root_path)
        except OSError:
            try:
                # Remove directory
                shutil.rmtree(static_root_path)
            except OSError:
                # No file
                pass

        # Create appropriate symbolic link
        if os.path.isdir(public_path):
            os.symlink(public_path, static_root_path)
            print('INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(app))

        elif os.path.isdir(static_path):
            os.symlink(static_path, static_root_path)
            print('INFO: Successfully linked static directory to STATIC_ROOT for app "{0}".'.format(app))