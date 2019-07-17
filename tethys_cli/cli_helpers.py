import os
import subprocess

import django

from tethys_apps.base.testing.environment import set_testing_environment
from tethys_apps.utilities import get_tethys_src_dir
from tethys_cli.cli_colors import pretty_output, FG_RED


def add_geoserver_rest_to_endpoint(endpoint):
    parts = endpoint.split('//')
    protocol = parts[0]
    parts2 = parts[1].split(':')
    host = parts2[0]
    port_and_path = parts2[1]
    port = port_and_path.split('/')[0]

    return '{0}//{1}:{2}/geoserver/rest/'.format(protocol, host, port)


def get_manage_path(args):
    """
    Validate user defined manage path, use default, or throw error
    """
    # Determine path to manage.py file
    manage_path = os.path.join(get_tethys_src_dir(), 'tethys_portal', 'manage.py')

    # Check for path option
    if hasattr(args, 'manage'):
        manage_path = args.manage or manage_path

    # Throw error if path is not valid
    if not os.path.isfile(manage_path):
        with pretty_output(FG_RED) as p:
            p.write('ERROR: Can\'t open file "{0}", no such file.'.format(manage_path))
        exit(1)

    return manage_path


def run_process(process):
    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    try:
        if 'test' in process:
            set_testing_environment(True)
        return subprocess.call(process)
    except KeyboardInterrupt:
        pass
    finally:
        set_testing_environment(False)


def load_apps():
    django.setup()
