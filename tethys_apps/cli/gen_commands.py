"""
********************************************************************************
* Name: gen_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from builtins import input
import os
import string
import random
from .manage_commands import TETHYS_HOME
from platform import linux_distribution

from django.template import Template, Context
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")
from django.conf import settings


# Initialize settings
try:
    __import__(os.environ['DJANGO_SETTINGS_MODULE'])
except:
    settings.configure()
import django
django.setup()


__all__ = ['VALID_GEN_OBJECTS', 'generate_command']


GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'
GEN_UWSGI_SERVICE_OPTION = 'uwsgi_service'
GEN_UWSGI_SETTINGS_OPTION = 'uwsgi_settings'
GEN_NGINX_OPTION = 'nginx'

FILE_NAMES = {GEN_SETTINGS_OPTION: 'settings.py',
              GEN_APACHE_OPTION: 'tethys-default.conf',
              GEN_UWSGI_SERVICE_OPTION: 'tethys.uwsgi.service',
              GEN_UWSGI_SETTINGS_OPTION: 'tethys_uwsgi.yml',
              GEN_NGINX_OPTION: 'tethys_nginx.conf',
              }

VALID_GEN_OBJECTS = (GEN_SETTINGS_OPTION,
                     GEN_APACHE_OPTION,
                     GEN_UWSGI_SERVICE_OPTION,
                     GEN_UWSGI_SETTINGS_OPTION,
                     GEN_NGINX_OPTION,
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
    destination_dir = os.path.join(TETHYS_HOME, 'src', 'tethys_portal')

    nginx_user = ''
    nginx_home = ''
    nginx_conf_path = '/etc/nginx/nginx.conf'
    if os.path.exists(nginx_conf_path):
        with open(nginx_conf_path, 'r') as nginx_conf:
            for line in nginx_conf.readlines():
                tokens = line.split()
                if len(tokens) > 0 and tokens[0] == 'user':
                    nginx_user = tokens[1].strip(';')
                    break

        with open('/etc/passwd', 'r') as passwd:
            for line in passwd.readlines():
                tokens = line.split(':')
                if tokens[0] == nginx_user:
                    nginx_home = tokens[5]
                    nginx_home = os.path.join(nginx_home, 'tethys')
                    break

    # Settings file setup
    if args.type == GEN_SETTINGS_OPTION:
        # Generate context variables
        secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(50)])
        context.update({'secret_key': secret_key,
                        'allowed_host': args.allowed_host,
                        'db_username': args.db_username,
                        'db_password': args.db_password,
                        'db_port': args.db_port,
                        'server_user_home': nginx_home,
                        'production': args.production,
                        })

    if args.type == GEN_NGINX_OPTION:
        hostname = ''. join(settings.ALLOWED_HOSTS)
        workspaces_root = get_settings_value('TETHYS_WORKSPACES_ROOT')
        static_root = get_settings_value('STATIC_ROOT')

        context.update({'hostname': hostname,
                        'workspaces_root': workspaces_root,
                        'static_root': static_root,
                        })

    if args.type == GEN_UWSGI_SERVICE_OPTION:
        conda_home = get_environment_value('CONDA_HOME')
        conda_env_name = get_environment_value('CONDA_ENV_NAME')

        linux_distro = linux_distribution(full_distribution_name=0)[0]
        user_option_prefix = ''
        if linux_distro in ['redhat', 'centos']:
            user_option_prefix = 'http-'

        context.update({'nginx_user': nginx_user,
                        'conda_home': conda_home,
                        'conda_env_name': conda_env_name,
                        'tethys_home': TETHYS_HOME,
                        'linux_distribution': linux_distro,
                        'user_option_prefix': user_option_prefix
                        })

    if args.type == GEN_UWSGI_SETTINGS_OPTION:
        conda_home = get_environment_value('CONDA_HOME')
        conda_env_name = get_environment_value('CONDA_ENV_NAME')

        context.update({'conda_home': conda_home,
                        'conda_env_name': conda_env_name})

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
