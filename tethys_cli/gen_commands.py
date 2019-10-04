"""
********************************************************************************
* Name: gen_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import string
import random
import os
from conda.cli.python_api import run_command, Commands
from yaml import safe_load
from distro import linux_distribution
from django.conf import settings
from jinja2 import Template
from tethys_apps.utilities import get_tethys_home_dir, get_tethys_src_dir


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")


GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'
GEN_ASGI_SERVICE_OPTION = 'asgi_service'
GEN_NGINX_OPTION = 'nginx'
GEN_NGINX_SERVICE_OPTION = 'nginx_service'
GEN_PORTAL_OPTION = 'portal'
GEN_SERVICES_OPTION = 'services'
GEN_INSTALL_OPTION = 'install'
GEN_SITE_YAML_OPTION = 'site_content'
GEN_META_YAML_OPTION = 'metayaml'

FILE_NAMES = {
    GEN_SETTINGS_OPTION: 'settings.py',
    GEN_APACHE_OPTION: 'tethys-default.conf',
    GEN_ASGI_SERVICE_OPTION: 'asgi_supervisord.conf',
    GEN_NGINX_OPTION: 'tethys_nginx.conf',
    GEN_NGINX_SERVICE_OPTION: 'nginx_supervisord.conf',
    GEN_PORTAL_OPTION: 'portal.yml',
    GEN_SERVICES_OPTION: 'services.yml',
    GEN_INSTALL_OPTION: 'install.yml',
    GEN_SITE_YAML_OPTION: 'site_content.yml',
    GEN_META_YAML_OPTION: 'meta.yaml'
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
    GEN_SITE_YAML_OPTION,
    GEN_META_YAML_OPTION
)

TETHYS_SRC = get_tethys_src_dir()


def add_gen_parser(subparsers):

    # Setup generate command
    gen_parser = subparsers.add_parser('gen', help='Aids the installation of Tethys by automating the '
                                                   'creation of supporting files.')
    gen_parser.add_argument('type', help='The type of object to generate.', choices=VALID_GEN_OBJECTS)
    gen_parser.add_argument('-d', '--directory', help='Destination directory for the generated object.')
    gen_parser.add_argument('-p', '--pin-level', choices=['major', 'minor', 'patch', 'none'],
                            help='Level to pin dependencies when generating the meta.yaml. One of "major", "minor", '
                                 '"patch", or "none". Defaults to "none".')
    gen_parser.add_argument('--allowed-hosts', dest='allowed_hosts', nargs='+',
                            help='Add one or more hostnames or IP addresses to ALLOWED_HOSTS in the settings file. '
                                 'e.g.: 127.0.0.1 localhost')
    gen_parser.add_argument('--client-max-body-size', dest='client_max_body_size',
                            help='Populate the client_max_body_size parameter for nginx config. Defaults to "75M".')
    gen_parser.add_argument('--asgi-processes', dest='asgi_processes',
                            help='The maximum number of asgi worker processes. Defaults to 4.')
    gen_parser.add_argument('--db-name', dest='db_name',
                            help='Name for the Tethys database to be set in the settings file.')
    gen_parser.add_argument('--db-username', dest='db_username',
                            help='Username for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-password', dest='db_password',
                            help='Password for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-host', dest='db_host',
                            help='Host for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-port', dest='db_port',
                            help='Port for the Tethys Database server to be set in the settings file.')
    gen_parser.add_argument('--db-dir', dest='db_dir',
                            help='Directory where the local Tethys Database server is created.')
    gen_parser.add_argument('--production', dest='production', action='store_true',
                            help='Generate a new settings file for a production server.')
    gen_parser.add_argument('--open-portal', dest='open_portal', action='store_true',
                            help='Enable open portal mode. Defaults to False')
    gen_parser.add_argument('--open-signup', dest='open_signup', action='store_true',
                            help='Enable open account signup. Defaults to False')
    gen_parser.add_argument('--tethys-port', dest='tethys_port',
                            help='Port for the Tethys Server to run on in production. This is used when generating the '
                                 'Daphne and nginx configuration files. Defaults to 8000.')
    gen_parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                            help='Overwrite existing file without prompting.')
    gen_parser.add_argument('--add-apps', dest='add_apps', nargs='+',
                            help='Enable additional Django apps by adding them to the INSTALLED_APPS in settings.py. '
                                 'e.g.: grappelli django_registration')
    gen_parser.add_argument('--session-persist', dest='session_persist', action='store_true',
                            help='Disable forced user logout once the browser has been closed. Defaults to False')
    gen_parser.add_argument('--session-warning', dest='session_warning',
                            help='Warn user of forced logout after indicated number of seconds. Defaults to 840')
    gen_parser.add_argument('--session-expire', dest='session_expire',
                            help='Force user logout after a specified number of seconds. Defaults to 900')
    gen_parser.add_argument('--static-root', dest='static_root',
                            help='Path to static files directory for production configuration. '
                                 'Defaults to ${TETHYS_HOME}/static. '
                                 'Applies default if directory does not exist.')
    gen_parser.add_argument('--workspaces-root', dest='workspaces_root',
                            help='Path to workspaces directory for production configuration. '
                                 'Defaults to ${TETHYS_HOME}/workspaces. Applies default if directory does not exist.')
    gen_parser.add_argument('--bypass-portal-home', dest='bypass_portal_home', action='store_true',
                            help='Enable bypassing the Tethys Portal home page. When the home page is accessed, '
                                 'users are redirected to the Apps Library page. Defaults to False')
    gen_parser.add_argument('--add-quota-handlers', dest='add_quota_handlers', nargs='+',
                            help='Add one or more dot-formatted paths to custom ResourceQuotaHandler classes. '
                                 'Defaults to tethys_quotas.handlers.workspace.WorkspaceQuotaHandler. '
                                 'e.g.: tethysapp.dam_inventory.dam_quota_handler.DamQuotaHandler')
    gen_parser.add_argument('--django-analytical', dest='django_analytical', nargs='+',
                            help='Provide one or more KEY:VALUE pairs for django analytical options in settings.py. '
                                 'All VALUEs default to False. Available KEYs: CLICKMAP_TRACKER_ID, CLICKY_SITE_ID, '
                                 'CRAZY_EGG_ACCOUNT_NUMBER, GAUGES_SITE_ID, GOOGLE_ANALYTICS_JS_PROPERTY_ID, '
                                 'GOSQUARED_SITE_TOKEN, HOTJAR_SITE_ID, HUBSPOT_PORTAL_ID, INTERCOM_APP_ID, '
                                 'KISSINSIGHTS_ACCOUNT_NUMBER, KISSINSIGHTS_SITE_CODE, KISS_METRICS_API_KEY, '
                                 'MIXPANEL_API_TOKEN, OLARK_SITE_ID, OPTIMIZELY_ACCOUNT_NUMBER, PERFORMABLE_API_KEY, '
                                 'PIWIK_DOMAIN_PATH, PIWIK_SITE_ID, RATING_MAILRU_COUNTER_ID, SNAPENGAGE_WIDGET_ID, '
                                 'SPRING_METRICS_TRACKING_ID, USERVOICE_WIDGET_KEY, WOOPRA_DOMAIN, '
                                 'YANDEX_METRICA_COUNTER_ID. '
                                 'e.g.: CLICKMAP_TRACKER_ID:123456 CLICKY_SITE_ID:789123')
    gen_parser.add_argument('--add-backends', dest='add_backends', nargs='+',
                            help='Add one or more authentication backends to settings.py. Provide the dot-formatted '
                                 'python path to a custom backend or one of the following keys: hydroshare, linkedin, '
                                 'google, facebook. The default backends are django.contrib.auth.backends.ModelBackend '
                                 'and guardian.backends.ObjectPermissionBackend. '
                                 'e.g.: project.backend.CustomBackend hydroshare')
    gen_parser.add_argument('--oauth-options', dest='oauth_options', nargs='+',
                            help='Provide KEY:VALUE pairs of parameters for oauth providers in the settings.py. '
                                 'Available Keys are: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, '
                                 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, SOCIAL_AUTH_FACEBOOK_KEY, '
                                 'SOCIAL_AUTH_FACEBOOK_SECRET, SOCIAL_AUTH_FACEBOOK_SCOPE, '
                                 'SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY, SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET, '
                                 'SOCIAL_AUTH_HYDROSHARE_KEY, SOCIAL_AUTH_HYDROSHARE_SECRET. '
                                 'e.g.: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:123456 SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET:789123')
    gen_parser.add_argument('--channel-layer', dest='channel_layer',
                            help='Specify a backend to handle communication between apps via websockets. '
                                 'The default backend is channels.layers.InMemoryChannelLayer. '
                                 'For production, it is recommended to install channels_redis and use '
                                 'channels_redis.core.RedisChannelLayer instead. '
                                 'A custom backend can be added using a dot-formatted path.')
    gen_parser.add_argument('--captcha', dest='captcha', action='store_true',
                            help='Enable captcha verification. Choices include an image captcha or Google recaptcha. '
                                 'The default is True when the --production flag is used and False when it is omitted. '
                                 'If no recaptcha keys are provided, the image captcha will be used. See '
                                 '--recaptcha-private-key and --recaptcha-public-key arguments.')
    gen_parser.add_argument('--recaptcha-private-key', dest='recaptcha_private_key',
                            help='Provide a private key to enable Google Recaptcha. '
                                 'The Default is None. A private key can be obtained '
                                 'from https://www.google.com/recaptcha/admin')
    gen_parser.add_argument('--recaptcha-public-key', dest='recaptcha_public_key',
                            help='Provide a public key to enable Google Recaptcha. '
                                 'The Default is None. A public key can be obtained '
                                 'from https://www.google.com/recaptcha/admin')
    gen_parser.set_defaults(func=generate_command, allowed_hosts=None, client_max_body_size='75M', asgi_processes=4,
                            db_name='tethys_platform', db_username='tethys_default', db_password='pass',
                            db_host='127.0.0.1', db_port=5436, db_dir='psql', production=False, open_portal=False,
                            open_signup=False, tethys_port=8000, overwrite=False, add_apps=None,
                            session_persist=False, session_warning=840, session_expire=900,
                            bypass_portal_home=False, channel_layer='', recaptcha_private_key=None,
                            recaptcha_public_key=None, pin_level='none')


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
    installed_apps = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
                      'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
                      'django_gravatar', 'bootstrap3', 'termsandconditions', 'tethys_config', 'tethys_apps',
                      'tethys_gizmos', 'tethys_services', 'tethys_compute', 'tethys_quotas', 'social_django',
                      'guardian', 'session_security', 'captcha', 'snowpenguin.django.recaptcha2', 'rest_framework',
                      'rest_framework.authtoken', 'analytical', 'channels']

    resource_quota_handlers = ['tethys_quotas.handlers.workspace.WorkspaceQuotaHandler']

    django_analytical = dict(CLICKMAP_TRACKER_ID=False, CLICKY_SITE_ID=False, CRAZY_EGG_ACCOUNT_NUMBER=False,
                             GAUGES_SITE_ID=False, GOOGLE_ANALYTICS_JS_PROPERTY_ID=False,
                             GOSQUARED_SITE_TOKEN=False, HOTJAR_SITE_ID=False, HUBSPOT_PORTAL_ID=False,
                             INTERCOM_APP_ID=False, KISSINSIGHTS_ACCOUNT_NUMBER=False,
                             KISSINSIGHTS_SITE_CODE=False, KISS_METRICS_API_KEY=False, MIXPANEL_API_TOKEN=False,
                             OLARK_SITE_ID=False, OPTIMIZELY_ACCOUNT_NUMBER=False, PERFORMABLE_API_KEY=False,
                             PIWIK_DOMAIN_PATH=False, PIWIK_SITE_ID=False, RATING_MAILRU_COUNTER_ID=False,
                             SNAPENGAGE_WIDGET_ID=False, SPRING_METRICS_TRACKING_ID=False,
                             USERVOICE_WIDGET_KEY=False, WOOPRA_DOMAIN=False, YANDEX_METRICA_COUNTER_ID=False)

    backends = ['django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend']

    custom_backends = dict(hydroshare='tethys_services.backends.hydroshare.HydroShareOAuth2',
                           linkedin='social_core.backends.linkedin.LinkedinOAuth2',
                           google='social_core.backends.google.GoogleOAuth2',
                           facebook='social_core.backends.facebook.FacebookOAuth2')

    oauth_options = dict(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='', SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='',
                         SOCIAL_AUTH_FACEBOOK_KEY='', SOCIAL_AUTH_FACEBOOK_SECRET='',
                         SOCIAL_AUTH_FACEBOOK_SCOPE='email', SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY='',
                         SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET='', SOCIAL_AUTH_HYDROSHARE_KEY='',
                         SOCIAL_AUTH_HYDROSHARE_SECRET='')

    if args.add_apps and args.add_apps != ['None']:
        installed_apps += [i for i in args.add_apps if i not in installed_apps]

    if args.add_quota_handlers:
        resource_quota_handlers += [i for i in args.add_quota_handlers if i not in resource_quota_handlers and
                                    i != 'None']

    try:
        session_warning = int(args.session_warning)
    except Exception:
        session_warning = 840

    try:
        session_expire = int(args.session_expire)
    except Exception:
        session_expire = 900

    if args.static_root and os.path.exists(args.static_root):
        static_root = args.static_root
    else:
        static_root = os.path.join(TETHYS_HOME, 'static')

    if args.workspaces_root and os.path.exists(args.workspaces_root):
        workspaces_root = args.workspaces_root
    else:
        workspaces_root = os.path.join(TETHYS_HOME, 'workspaces')

    if args.django_analytical:
        for pair in args.django_analytical:
            if pair != 'None':
                try:
                    key, value = pair.split(':')
                    django_analytical[key.upper()] = value
                except ValueError:
                    raise ValueError('Provide key-value pairs in the form of KEY:VALUE')

    if args.add_backends:
        c = 0
        for item in args.add_backends:
            if item != 'None':
                if item in custom_backends:
                    backends.insert(c, custom_backends[item])
                else:
                    backends.insert(c, item)
                c += 1

    if args.oauth_options:
        for pair in args.oauth_options:
            if pair != 'None':
                try:
                    key, value = pair.split(':')
                    oauth_options[key.upper()] = value
                except ValueError:
                    raise ValueError('Provide key-value pairs in the form of KEY:VALUE')

    context = {
        'secret_key': secret_key,
        'allowed_hosts': args.allowed_hosts,
        'db_name': args.db_name,
        'db_username': args.db_username,
        'db_password': args.db_password,
        'db_host': args.db_host,
        'db_port': args.db_port,
        'db_dir': args.db_dir,
        'tethys_home': TETHYS_HOME,
        'production': args.production,
        'open_portal': args.open_portal,
        'open_signup': args.open_signup,
        'installed_apps': installed_apps,
        'session_expire_browser': not args.session_persist,
        'session_warning': session_warning,
        'session_expire': session_expire,
        'static_root': static_root,
        'workspaces_root': workspaces_root,
        'bypass_portal_home': args.bypass_portal_home,
        'resource_quota_handlers': resource_quota_handlers,
        'django_analytical': django_analytical,
        'backends': backends,
        'oauth_options': oauth_options,
        'channel_layer': args.channel_layer,
        'captcha': args.captcha if args.captcha else args.production,
        'recaptcha_private_key': args.recaptcha_private_key,
        'recaptcha_public_key': args.recaptcha_public_key
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
    print('Please review the generated install.yml file and fill in the appropriate information '
          '(app name is requited).')

    context = {}
    return context


def gen_site_content_yaml(args):
    print('Please review the generated site_content.yml file and fill in the appropriate information.')

    context = {}
    return context


def get_destination_path(args):
    # Determine destination file name (defaults to type)
    destination_file = FILE_NAMES[args.type]

    # Default destination path is the tethys_portal source dir
    destination_dir = os.path.join(TETHYS_SRC, 'tethys_portal')

    if args.type in [GEN_SERVICES_OPTION, GEN_INSTALL_OPTION, GEN_SITE_YAML_OPTION]:
        destination_dir = os.getcwd()

    elif args.type == GEN_META_YAML_OPTION:
        destination_dir = os.path.join(TETHYS_SRC, 'conda.recipe')

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


GEN_COMMANDS = {
    GEN_SETTINGS_OPTION: gen_settings,
    GEN_ASGI_SERVICE_OPTION: gen_asgi_service,
    GEN_NGINX_OPTION: gen_nginx,
    GEN_NGINX_SERVICE_OPTION: gen_nginx_service,
    GEN_PORTAL_OPTION: gen_portal_yaml,
    GEN_SERVICES_OPTION: gen_services_yaml,
    GEN_INSTALL_OPTION: gen_install,
    GEN_SITE_YAML_OPTION: gen_site_content_yaml,
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
