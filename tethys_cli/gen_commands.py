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
from pathlib import Path
import string
import random

from conda.cli.python_api import run_command, Commands
from yaml import safe_load
from distro import linux_distribution
from jinja2 import Template

from django.conf import settings

from tethys_apps.utilities import get_tethys_home_dir, get_tethys_src_dir
from tethys_cli.cli_colors import write_error, write_info, write_warning

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")

GEN_APACHE_OPTION = 'apache'
GEN_ASGI_SERVICE_OPTION = 'asgi_service'
GEN_NGINX_OPTION = 'nginx'
GEN_NGINX_SERVICE_OPTION = 'nginx_service'
GEN_PORTAL_OPTION = 'portal_config'
GEN_SERVICES_OPTION = 'services'
GEN_INSTALL_OPTION = 'install'
GEN_META_YAML_OPTION = 'metayaml'

FILE_NAMES = {
    GEN_APACHE_OPTION: 'tethys-default.conf',
    GEN_ASGI_SERVICE_OPTION: 'asgi_supervisord.conf',
    GEN_NGINX_OPTION: 'tethys_nginx.conf',
    GEN_NGINX_SERVICE_OPTION: 'nginx_supervisord.conf',
    GEN_PORTAL_OPTION: 'portal_config.yml',
    GEN_SERVICES_OPTION: 'services.yml',
    GEN_INSTALL_OPTION: 'install.yml',
    GEN_META_YAML_OPTION: 'meta.yaml'
}

VALID_GEN_OBJECTS = (
    # GEN_APACHE_OPTION,
    GEN_ASGI_SERVICE_OPTION,
    GEN_NGINX_OPTION,
    GEN_NGINX_SERVICE_OPTION,
    GEN_PORTAL_OPTION,
    GEN_SERVICES_OPTION,
    GEN_INSTALL_OPTION,
    GEN_META_YAML_OPTION
)

TETHYS_SRC = get_tethys_src_dir()
TETHYS_HOME = get_tethys_home_dir()


def add_gen_parser(subparsers):

    # Setup generate command
    gen_parser = subparsers.add_parser('gen', help='Aids the installation of Tethys by automating the '
                                                   'creation of supporting files.')
    gen_parser.add_argument('type', help='The type of object to generate.', choices=VALID_GEN_OBJECTS)
    gen_parser.add_argument('-d', '--directory', help='Destination directory for the generated object.')
    gen_parser.add_argument('-p', '--pin-level', choices=['major', 'minor', 'patch', 'none'],
                            help='Level to pin dependencies when generating the meta.yaml. One of "major", "minor", '
                                 '"patch", or "none". Defaults to "none".')
    gen_parser.add_argument('--client-max-body-size', dest='client_max_body_size',
                            help='Populate the client_max_body_size parameter for nginx config. Defaults to "75M".')
    gen_parser.add_argument('--asgi-processes', dest='asgi_processes',
                            help='The maximum number of asgi worker processes. Defaults to 1.')
    gen_parser.add_argument('--conda-prefix', dest='conda_prefix',
                            help='The path to the Tethys conda environment. Required if $CONDA_PREFIX is not defined.')
    gen_parser.add_argument('--tethys-port', dest='tethys_port',
                            help='Port for the Tethys Server to run on in production. This is used when generating the '
                                 'Daphne and nginx configuration files. Defaults to 8000.')
    gen_parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                            help='Overwrite existing file without prompting.')
    gen_parser.set_defaults(func=generate_command, client_max_body_size='75M', asgi_processes=1, conda_prefix=False,
                            tethys_port=8000, overwrite=False, pin_level='none')


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


def generate_secret_key():
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])


def gen_nginx(args):
    hostname = str(settings.ALLOWED_HOSTS[0]) if len(settings.ALLOWED_HOSTS) > 0 else '127.0.0.1'
    workspaces_root = get_settings_value('TETHYS_WORKSPACES_ROOT')
    static_root = get_settings_value('STATIC_ROOT')

    context = {
        'hostname': hostname,
        'workspaces_root': workspaces_root,
        'static_root': static_root,
        'client_max_body_size': args.client_max_body_size,
        'port': args.tethys_port
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

    conda_prefix = args.conda_prefix if args.conda_prefix else get_environment_value('CONDA_PREFIX')
    conda_home = Path(conda_prefix).parents[1]

    user_option_prefix = ''

    try:
        linux_distro = linux_distribution(full_distribution_name=0)[0]
        if linux_distro in ['redhat', 'centos']:
            user_option_prefix = 'http-'
    except Exception:
        pass

    context = {
        'nginx_user': nginx_user,
        'port': args.tethys_port,
        'asgi_processes': args.asgi_processes,
        'conda_prefix': conda_prefix,
        'conda_home': conda_home,
        'tethys_src': TETHYS_SRC,
        'tethys_home': TETHYS_HOME,
        'user_option_prefix': user_option_prefix
    }
    return context


def gen_nginx_service(args):
    context = {}
    return context


def gen_portal_yaml(args):
    write_info(f'A Tethys Portal configuration file is being generated at '
               f'{get_tethys_home_dir() + "/" + FILE_NAMES[GEN_PORTAL_OPTION]}. '
               f'Please review the file and fill in the appropriate settings.')

    context = {'SECRET_KEY': generate_secret_key()}
    return context


def gen_services_yaml(args):
    context = {}
    return context


def derive_version_from_conda_environment(dep_str, level='none'):
    """
    Determine dependency string based on the current tethys environment.

    Args:
        dep_str(str): The dep string from the environment.yml (e.g. 'python>=3.6').
        level(str): Level to lock dependencies to. One of 'major', 'minor', 'patch', or None. Defaults to 'minor'.

    Returns:
        str: the dependency string.
    """
    stdout, stderr, ret = run_command(Commands.LIST, dep_str)

    if ret != 0:
        print(f'ERROR: Something went wrong looking up dependency "{dep_str}" in environment')
        print(stderr)
        return dep_str

    lines = stdout.split('\n')

    for line in lines:
        if line.startswith('#'):
            continue

        try:
            package, version, build, channel = line.split()
        except ValueError:
            continue

        if package != dep_str:
            continue

        version_numbers = version.split('.')

        if level == 'major':
            if len(version_numbers) >= 2:
                dep_str = f'{package}={version_numbers[0]}.*'
            if len(version_numbers) == 1:
                dep_str = f'{package}={version_numbers[0]}'
        elif level == 'minor':
            if len(version_numbers) >= 3:
                dep_str = f'{package}={version_numbers[0]}.{version_numbers[1]}.*'
            elif len(version_numbers) == 2:
                dep_str = f'{package}={version_numbers[0]}.{version_numbers[1]}'
        elif level == 'patch':
            if len(version_numbers) > 3:
                dep_str = f'{package}={version_numbers[0]}.{version_numbers[1]}.{version_numbers[2]}.*'
            elif len(version_numbers) >= 1:
                dep_str = f'{package}={".".join(version_numbers)}'

    return dep_str


def gen_meta_yaml(args):
    environment_file_path = os.path.join(TETHYS_SRC, 'environment.yml')
    with open(environment_file_path, 'r') as env_file:
        environment = safe_load(env_file)

    dependencies = environment.get('dependencies', [])
    run_requirements = []

    for dependency in dependencies:
        if not any([operator in dependency for operator in ['=', '<', '>']]):
            conda_env_version = derive_version_from_conda_environment(dependency, level=args.pin_level)
            run_requirements.append(conda_env_version)
        else:
            run_requirements.append(dependency)

    context = dict(run_requirements=run_requirements)
    return context


def gen_install(args):
    write_info('Please review the generated install.yml file and fill in the appropriate information '
               '(app name is required).')

    context = {}
    return context


def get_destination_path(args):
    # Determine destination file name (defaults to type)
    destination_file = FILE_NAMES[args.type]

    # Default destination path is the tethys_portal source dir
    destination_dir = TETHYS_HOME

    # Make the Tethys Home directory if it doesn't exist yet.
    if not os.path.isdir(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)

    if args.type in [GEN_SERVICES_OPTION, GEN_INSTALL_OPTION]:
        destination_dir = os.getcwd()

    elif args.type == GEN_META_YAML_OPTION:
        destination_dir = os.path.join(TETHYS_SRC, 'conda.recipe')

    if args.directory:
        destination_dir = os.path.abspath(args.directory)

    if not os.path.isdir(destination_dir):
        write_error('ERROR: "{0}" is not a valid directory.'.format(destination_dir))
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
            write_warning('Generation of "{0}" cancelled.'.format(destination_file))
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


def write_path_to_console(file_path):
    write_info(f'File generated at "{file_path}".')


GEN_COMMANDS = {
    GEN_ASGI_SERVICE_OPTION: gen_asgi_service,
    GEN_NGINX_OPTION: gen_nginx,
    GEN_NGINX_SERVICE_OPTION: gen_nginx_service,
    GEN_PORTAL_OPTION: gen_portal_yaml,
    GEN_SERVICES_OPTION: gen_services_yaml,
    GEN_INSTALL_OPTION: gen_install,
    GEN_META_YAML_OPTION: gen_meta_yaml
}


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Setup variables
    context = GEN_COMMANDS[args.type](args)

    destination_path = get_destination_path(args)

    render_template(args.type, context, destination_path)

    write_path_to_console(destination_path)
