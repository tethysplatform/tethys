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
from platform import linux_distribution

from django.template import Template, Context
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")


# Initialize settings
try:
    __import__(os.environ['DJANGO_SETTINGS_MODULE'])
except Exception:
    # Initialize settings with templates variable to allow gen to work properly
    settings.configure(TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
        }
    ])
import django  # noqa: E402
django.setup()


__all__ = ['VALID_GEN_OBJECTS', 'generate_command']


GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'
GEN_ASGI_SERVICE_OPTION = 'asgi_service'
GEN_NGINX_OPTION = 'nginx'
GEN_NGINX_SERVICE_OPTION = 'nginx_service'

FILE_NAMES = {GEN_SETTINGS_OPTION: 'settings.py',
              GEN_APACHE_OPTION: 'tethys-default.conf',
              GEN_ASGI_SERVICE_OPTION: 'asgi_supervisord.conf',
              GEN_NGINX_OPTION: 'tethys_nginx.conf',
              GEN_NGINX_SERVICE_OPTION: 'nginx_supervisord.conf',
              }

VALID_GEN_OBJECTS = (GEN_SETTINGS_OPTION,
                     GEN_APACHE_OPTION,
                     GEN_ASGI_SERVICE_OPTION,
                     GEN_NGINX_OPTION,
                     GEN_NGINX_SERVICE_OPTION,
                     )


def get_environment_value(value_name):
    value = os.environ.get(value_name)
    if value is not None:
        return value
    else:
        raise EnvironmentError('Environment value "%s" must be set before generating this file.', value_name)


def get_settings_value(value_name):
    value = getattr(settings, value_name, None)
    if value is not None:
        return value
    else:
        raise ValueError('Settings value "%s" must be set before generating this file.', value_name)


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Consts
    TETHYS_HOME = get_tethys_home_dir()
    TETHYS_SRC = get_tethys_src_dir()

    # Setup variables
    context = Context()

    # Determine template path

    gen_templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gen_templates')
    template_path = os.path.join(gen_templates_dir, args.type)

    # Parse template
    template = Template(open(template_path).read())

    # Determine destination file name (defaults to type)
    destination_file = FILE_NAMES[args.type]

    # Default destination path is the current working directory
    destination_dir = os.path.join(TETHYS_SRC, 'tethys_portal')

    nginx_user = ''
    nginx_conf_path = '/etc/nginx/nginx.conf'
    if os.path.exists(nginx_conf_path):
        with open(nginx_conf_path, 'r') as nginx_conf:
            for line in nginx_conf.readlines():
                tokens = line.split()
                if len(tokens) > 0 and tokens[0] == 'user':
                    nginx_user = tokens[1].strip(';')
                    break

    # Settings file setup
    if args.type == GEN_SETTINGS_OPTION:
        # Generate context variables
        secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])
        context.update({'secret_key': secret_key,
                        'allowed_host': args.allowed_host,
                        'allowed_hosts': args.allowed_hosts,
                        'db_username': args.db_username,
                        'db_password': args.db_password,
                        'db_port': args.db_port,
                        'tethys_home': TETHYS_HOME,
                        'production': args.production,
                        'open_portal': args.open_portal
                        })

    if args.type == GEN_NGINX_OPTION:
        hostname = str(settings.ALLOWED_HOSTS[0]) if len(settings.ALLOWED_HOSTS) > 0 else '127.0.0.1'
        workspaces_root = get_settings_value('TETHYS_WORKSPACES_ROOT')
        static_root = get_settings_value('STATIC_ROOT')

        context.update({'hostname': hostname,
                        'port': args.tethys_port,
                        'workspaces_root': workspaces_root,
                        'static_root': static_root,
                        'client_max_body_size': args.client_max_body_size
                        })

    if args.type == GEN_ASGI_SERVICE_OPTION:
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

        context.update({'nginx_user': nginx_user,
                        'hostname': hostname,
                        'port': args.tethys_port,
                        'asgi_processes': args.asgi_processes,
                        'conda_home': conda_home,
                        'conda_env_name': conda_env_name,
                        'tethys_src': TETHYS_SRC,
                        'user_option_prefix': user_option_prefix
                        })

    if args.directory:
        if os.path.isdir(args.directory):
            destination_dir = args.directory
        else:
            print('ERROR: "{0}" is not a valid directory.'.format(destination_dir))
            exit(1)

    destination_path = os.path.join(destination_dir, destination_file)

    # Check for pre-existing file
    if os.path.isfile(destination_path):
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')

        if args.overwrite:
            overwrite_input = 'yes'
        else:
            overwrite_input = input('WARNING: "{0}" already exists. '
                                    'Overwrite? (y/n): '.format(destination_file)).lower()

            while overwrite_input not in valid_inputs:
                overwrite_input = input('Invalid option. Overwrite? (y/n): ').lower()

        if overwrite_input in no_inputs:
            print('Generation of "{0}" cancelled.'.format(destination_file))
            exit(0)

    # Render template and write to file
    if template:
        with open(destination_path, 'w') as f:
            f.write(template.render(context))
