"""
********************************************************************************
* Name: gen_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import os
import string
import random
from tethys_apps.utilities import get_tethys_home_dir, get_tethys_src_dir
from distro import linux_distribution

from django.conf import settings
from jinja2 import Template


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")


GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'
GEN_ASGI_SERVICE_OPTION = 'asgi_service'
GEN_NGINX_OPTION = 'nginx'
GEN_NGINX_SERVICE_OPTION = 'nginx_service'
GEN_PORTAL_OPTION = 'portal'
GEN_SERVICES_OPTION = 'services'
GEN_INSTALL_OPTION = 'install'

FILE_NAMES = {
    GEN_SETTINGS_OPTION: 'settings.py',
    GEN_APACHE_OPTION: 'tethys-default.conf',
    GEN_ASGI_SERVICE_OPTION: 'asgi_supervisord.conf',
    GEN_NGINX_OPTION: 'tethys_nginx.conf',
    GEN_NGINX_SERVICE_OPTION: 'nginx_supervisord.conf',
    GEN_PORTAL_OPTION: 'portal.yml',
    GEN_SERVICES_OPTION: 'services.yml',
    GEN_INSTALL_OPTION: 'install.yml',
}

VALID_GEN_OBJECTS = (
    GEN_SETTINGS_OPTION,
    # GEN_APACHE_OPTION,
    GEN_ASGI_SERVICE_OPTION,
    GEN_NGINX_OPTION,
    GEN_NGINX_SERVICE_OPTION,
    GEN_PORTAL_OPTION,
    GEN_SERVICES_OPTION,
    GEN_INSTALL_OPTION,
)

TETHYS_SRC = get_tethys_src_dir()


def add_gen_parser(subparsers):

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
    gen_parser.add_argument('--asgi-processes', dest='asgi_processes',
                            help='The maximum number of asgi worker processes. Defaults to 4.')
    gen_parser.add_argument('--db-name', dest='db_name',
                            help='Name for the Tethys database to be set in the settings file.')
    gen_parser.add_argument('--db-username', dest='db_username',
                            help='Username for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-password', dest='db_password',
                            help='Password for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-port', dest='db_port',
                            help='Port for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-dir', dest='db_dir',
                            help='Directory where the local Tethys Database server is created.')
    gen_parser.add_argument('--production', dest='production', action='store_true',
                            help='Generate a new settings file for a production server.')
    gen_parser.add_argument('--open-portal', dest='open_portal',
                            help='Allow Open Portal Mode.')
    gen_parser.add_argument('--tethys-port', dest='tethys_port',
                            help='Port for the Tethys Server to run on in production. This is used when generating the '
                                 'Daphne and nginx configuration files. Defaults to 8000.')
    gen_parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                            help='Overwrite existing file without prompting.')
    gen_parser.set_defaults(func=generate_command, allowed_host=None, allowed_hosts=None, client_max_body_size='75M',
                            asgi_processes=4, db_name='tethys_platform', db_username='tethys_default',
                            db_password='pass', db_port=5436, db_dir='psql', production=False, open_portal=False,
                            tethys_port=8000, overwrite=False)


def get_environment_value(value_name):
    value = os.environ.get(value_name)
    if value is not None:
        return value
    else:
        raise EnvironmentError(f'Environment value "{value_name}" must be set before generating this file.')


def get_settings_value(value_name):
    value = getattr(settings, value_name, None)
    if value is not None:
        return value
    else:
        raise ValueError(f'Settings value "{value_name}" must be set before generating this file.')


def gen_settings(args):
    TETHYS_HOME = get_tethys_home_dir()

    # Generate context variables
    secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])
    context = {
        'secret_key': secret_key,
        'allowed_host': args.allowed_host,
        'allowed_hosts': args.allowed_hosts,
        'db_name': args.db_name,
        'db_username': args.db_username,
        'db_password': args.db_password,
        'db_port': args.db_port,
        'db_dir': args.db_dir,
        'tethys_home': TETHYS_HOME,
        'production': args.production,
        'open_portal': args.open_portal
    }
    return context


def gen_nginx(args):
    hostname = str(settings.ALLOWED_HOSTS[0]) if len(settings.ALLOWED_HOSTS) > 0 else '127.0.0.1'
    workspaces_root = get_settings_value('TETHYS_WORKSPACES_ROOT')
    static_root = get_settings_value('STATIC_ROOT')

    context = {
        'hostname': hostname,
        'workspaces_root': workspaces_root,
        'static_root': static_root,
        'client_max_body_size': args.client_max_body_size
    }
    return context


def gen_asgi_service(args):
    nginx_user = ''
    nginx_conf_path = '/etc/nginx/nginx.conf'
    if os.path.exists(nginx_conf_path):
        with open(nginx_conf_path, 'r') as nginx_conf:
            for line in nginx_conf.readlines():
                tokens = line.split()
                if len(tokens) > 0 and tokens[0] == 'user':
                    nginx_user = tokens[1].strip(';')
                    break

    hostname = str(settings.ALLOWED_HOSTS[0]) if len(settings.ALLOWED_HOSTS) > 0 else '127.0.0.1'
    conda_home = get_environment_value('CONDA_HOME')
    conda_env_name = get_environment_value('CONDA_ENV_NAME')

    user_option_prefix = ''

    try:
        linux_distro = linux_distribution(full_distribution_name=0)[0]
        if linux_distro in ['redhat', 'centos']:
            user_option_prefix = 'http-'
    except Exception:
        pass

    context = {
        'nginx_user': nginx_user,
        'hostname': hostname,
        'port': args.tethys_port,
        'asgi_processes': args.asgi_processes,
        'conda_home': conda_home,
        'conda_env_name': conda_env_name,
        'tethys_src': TETHYS_SRC,
        'user_option_prefix': user_option_prefix
    }
    return context


def gen_nginx_service(args):
    context = {}
    return context


def gen_portal_yaml(args):
    context = {}
    return context


def gen_services_yaml(args):
    context = {}
    return context


def gen_install(args):
    print('Please review the generated install.yml file and fill in the appropriate information '
          '(app name is requited).')

    context = {}
    return context


def get_destination_path(args):
    # Determine destination file name (defaults to type)
    destination_file = FILE_NAMES[args.type]

    # Default destination path is the tethys_portal source dir
    destination_dir = os.path.join(TETHYS_SRC, 'tethys_portal')

    if args.type in [GEN_SERVICES_OPTION, GEN_INSTALL_OPTION]:
        destination_dir = os.getcwd()

    if args.directory:
        directory = os.path.abspath(args.directory)
        if os.path.isdir(directory):
            destination_dir = directory
        else:
            print('ERROR: "{0}" is not a valid directory.'.format(destination_dir))
            exit(1)
    destination_path = os.path.join(destination_dir, destination_file)

    check_for_existing_file(destination_path, destination_file, args.overwrite)

    return destination_path


def check_for_existing_file(destination_path, destination_file, overwrite):
    # Check for pre-existing file
    if os.path.isfile(destination_path):
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')

        if overwrite:
            overwrite_input = 'yes'
        else:
            overwrite_input = input('WARNING: "{0}" already exists. '
                                    'Overwrite? (y/n): '.format(destination_file)).lower()

            while overwrite_input not in valid_inputs:
                overwrite_input = input('Invalid option. Overwrite? (y/n): ').lower()

        if overwrite_input in no_inputs:
            print('Generation of "{0}" cancelled.'.format(destination_file))
            exit(0)


def render_template(file_type, context, destination_path):
    # Determine template path
    gen_templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gen_templates')
    template_path = os.path.join(gen_templates_dir, file_type)

    # Parse template
    template = Template(open(template_path).read())
    # Render template and write to file
    if template:
        with open(destination_path, 'w') as f:
            f.write(template.render(context))


gen_commands = {
    GEN_SETTINGS_OPTION: gen_settings,
    GEN_ASGI_SERVICE_OPTION: gen_asgi_service,
    GEN_NGINX_OPTION: gen_nginx,
    GEN_NGINX_SERVICE_OPTION: gen_nginx_service,
    GEN_PORTAL_OPTION: gen_portal_yaml,
    GEN_SERVICES_OPTION: gen_services_yaml,
    GEN_INSTALL_OPTION: gen_install,
}


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Setup variables
    context = gen_commands[args.type](args)

    destination_path = get_destination_path(args)

    render_template(args.type, context, destination_path)
