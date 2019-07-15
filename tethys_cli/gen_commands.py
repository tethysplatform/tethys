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
    gen_parser.add_argument('--allowed-hosts', dest='allowed_hosts', nargs='+',
                            help='Add multiple hostnames or IP addresses to allowed hosts in the settings file. '
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
    gen_parser.add_argument('--open-portal', dest='open_portal', help='Allow Open Portal Mode. Defaults to False')
    gen_parser.add_argument('--open-signup', dest='open_signup', help='Enable open account signup. Defaults to False')
    gen_parser.add_argument('--tethys-port', dest='tethys_port',
                            help='Port for the Tethys Server to run on in production. This is used when generating the '
                                 'Daphne and nginx configuration files. Defaults to 8000.')
    gen_parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                            help='Overwrite existing file without prompting.')
    gen_parser.add_argument('--add-apps', dest='add_apps', nargs='+',
                            help='Enable applications by adding them to the INSTALLED_APPS in settings.py. '
                                 'e.g.: grappelli django_registration')
    gen_parser.add_argument('--remove-apps', dest='remove_apps', nargs='+',
                            help='Remove applications from the INSTALLED_APPS in settings.py. '
                                 'e.g.: grappelli django_registration')
    gen_parser.add_argument('--session-expire-browser', dest='session_expire_browser',
                            help='Force user logout once the browser has been closed. Defaults to True')
    gen_parser.add_argument('--session-warning', dest='session_warning',
                            help='Warn user of forced logout after indicated number of seconds. Defaults to 840')
    gen_parser.add_argument('--session-expire', dest='session_expire',
                            help='Force user logout after a specified number of seconds. Defaults to 900')
    gen_parser.add_argument('--static-root', dest='static_root',
                            help='For production. Path to static files diretory. Defaults to ${TETHYS_HOME}/static. '
                                 'Applies default if directory does not exist.')
    gen_parser.add_argument('--workspaces-root', dest='workspaces_root',
                            help='For production. Path to workspaces diretory. Defaults to ${TETHYS_HOME}/workspaces. '
                                 'Applies default if directory does not exist.')
    gen_parser.add_argument('--bypass-portal-home', dest='bypass_portal_home',
                            help='Bypasses the Tethys home page. Defaults to False')
    gen_parser.add_argument('--add-quota-handlers', dest='add_quota_handlers', nargs='+',
                            help='Append one or more dot-formatted handlers to the resource quota handlers list in '
                                 'settings.py. Defaults to tethys_quotas.handlers.workspace.WorkspaceQuotaHandler. '
                                 'e.g.: tethysapp.dam_inventory.dam_quota_handler.DamQuotaHandler')
    gen_parser.add_argument('--remove-quota-handlers', dest='remove_quota_handlers', nargs='+',
                            help='Remove one or more dot-formatted handlers from the resource quota handlers list in '
                                 'settings.py. e.g.: tethysapp.dam_inventory.dam_quota_handler.DamQuotaHandler')
    gen_parser.add_argument('--django-analytical', dest='django_analytical', nargs='+',
                            help='Provide one or more ID:SERVICE_ID pair for django analytical options in settings.py. '
                                 'All IDs default to False. Available IDs are: CLICKMAP_TRACKER_ID, CLICKY_SITE_ID, '
                                 'CRAZY_EGG_ACCOUNT_NUMBER, GAUGES_SITE_ID, GOOGLE_ANALYTICS_JS_PROPERTY_ID, '
                                 'GOSQUARED_SITE_TOKEN, HOTJAR_SITE_ID, HUBSPOT_PORTAL_ID, INTERCOM_APP_ID, '
                                 'KISSINSIGHTS_ACCOUNT_NUMBER, KISSINSIGHTS_SITE_CODE, KISS_METRICS_API_KEY, '
                                 'MIXPANEL_API_TOKEN, OLARK_SITE_ID, OPTIMIZELY_ACCOUNT_NUMBER, PERFORMABLE_API_KEY, '
                                 'PIWIK_DOMAIN_PATH, PIWIK_SITE_ID, RATING_MAILRU_COUNTER_ID, SNAPENGAGE_WIDGET_ID, '
                                 'SPRING_METRICS_TRACKING_ID, USERVOICE_WIDGET_KEY, WOOPRA_DOMAIN, '
                                 'YANDEX_METRICA_COUNTER_ID. '
                                 'e.g.: CLICKMAP_TRACKER_ID:123456 CLICKY_SITE_ID:789123')
    gen_parser.add_argument('--add-backends', dest='add_backends', nargs='+',
                            help='Add one or more authentication backends to settings.py. Django try these backends in '
                                 'the same order they are listed. Provide the dot-formatted python path to a custom '
                                 'backend or one of the following keys: hydroshare, linkedin, google, facebook. '
                                 'The default backends are django.contrib.auth.backends.ModelBackend and '
                                 'guardian.backends.ObjectPermissionBackend. '
                                 'e.g.: project.backend.CustomBackend hydroshare')
    gen_parser.add_argument('--remove-backends', dest='remove_backends', nargs='+',
                            help='Remove one or more authentication backends to settings.py. Django try these backends '
                                 'in the same order they are listed. Provide the dot-formatted python path to a custom '
                                 'backend or one of the following keys: hydroshare, linkedin, google, facebook. '
                                 'The default backends are django.contrib.auth.backends.ModelBackend and '
                                 'guardian.backends.ObjectPermissionBackend. Defaults cannot be removed. '
                                 'e.g.: project.backend.CustomBackend hydroshare')
    gen_parser.add_argument('--oauth-options', dest='oauth_options', nargs='+',
                            help='Add options for oauth providers in the settings.py. '
                                 'Available options are: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, '
                                 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, SOCIAL_AUTH_FACEBOOK_KEY, '
                                 'SOCIAL_AUTH_FACEBOOK_SECRET, SOCIAL_AUTH_FACEBOOK_SCOPE, '
                                 'SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY, SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET, '
                                 'SOCIAL_AUTH_HYDROSHARE_KEY, SOCIAL_AUTH_HYDROSHARE_SECRET. '
                                 'e.g.: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:123456 SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET:789123')
    'channels.layers.InMemoryChannelLayer'
    gen_parser.add_argument('--channel-layer', dest='channel_layer',
                            help='Backend to enable communication between apps via websockets. The Default available '
                                 'values is channels.layers.InMemoryChannelLayer. For production, it is recommended to '
                                 'install channel_redis and use channels_redis.core.RedisChannelLayer instead. '
                                 'A custom backend can be added using dot-formatted path.')
    gen_parser.set_defaults(func=generate_command, allowed_host=None, allowed_hosts=None, client_max_body_size='75M',
                            asgi_processes=4, db_name='tethys_platform', db_username='tethys_default',
                            db_password='pass', db_host='127.0.0.1', db_port=5436, db_dir='psql', production=False,
                            open_portal=False, open_signup=False, tethys_port=8000, overwrite=False, add_apps=None,
                            remove_apps=None, session_expire_browser=True, session_warning=840, session_expire=900,
                            bypass_portal_home=False, channel_layer='')


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
                      'guardian', 'session_security', 'captcha', 'rest_framework', 'rest_framework.authtoken',
                      'analytical', 'channels']

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

    if args.add_apps:
        installed_apps += [i for i in args.add_apps if i not in installed_apps]

    if args.remove_apps:
        installed_apps = [i for i in installed_apps if i not in args.remove_apps]

    if args.add_quota_handlers:
        resource_quota_handlers += [i for i in args.add_quota_handlers if i not in resource_quota_handlers]

    if args.remove_quota_handlers:
        resource_quota_handlers = [i for i in resource_quota_handlers if i not in args.remove_quota_handlers]

    if args.session_expire_browser and args.session_expire_browser not in ['0', 'f', 'F', 'false', 'False']:
        session_expire_browser = True
    else:
        session_expire_browser = False

    try:
        session_warning = int(args.session_warning)
    except:
        session_warning = 840

    try:
        session_expire = int(args.session_expire)
    except:
        session_expire = 900

    if args.static_root and os.path.exists(args.static_root):
        static_root = args.static_root
    else:
        static_root = os.path.join(TETHYS_HOME, 'static')

    if args.workspaces_root and os.path.exists(args.workspaces_root):
        workspaces_root = args.workspaces_root
    else:
        workspaces_root = os.path.join(TETHYS_HOME, 'workspaces')

    if args.bypass_portal_home and args.bypass_portal_home not in ['0', 'f', 'F', 'false', 'False']:
        bypass_portal_home = True
    else:
        bypass_portal_home = False

    if args.open_signup and args.open_signup not in ['0', 'f', 'F', 'false', 'False']:
        open_signup = True
    else:
        open_signup = False

    if args.open_portal and args.open_portal not in ['0', 'f', 'F', 'false', 'False']:
        open_portal = True
    else:
        open_portal = False

    if args.django_analytical:
        for pair in args.django_analytical:
            key, value = pair.split(':')
            django_analytical[key.upper()] = value

    if args.add_backends:
        c = 0
        for item in args.add_backends:
            if item in custom_backends:
                backends.insert(c, custom_backends[item])
            else:
                backends.insert(c, item)
            c += 1

    if args.oauth_options:
        for pair in args.oauth_options:
            key, value = pair.split(':')
            oauth_options[key.upper()] = value

    context = {
        'secret_key': secret_key,
        'allowed_host': args.allowed_host,
        'allowed_hosts': args.allowed_hosts,
        'db_name': args.db_name,
        'db_username': args.db_username,
        'db_password': args.db_password,
        'db_host': args.db_host,
        'db_port': args.db_port,
        'db_dir': args.db_dir,
        'tethys_home': TETHYS_HOME,
        'production': args.production,
        'open_portal': open_portal,
        'open_signup': open_signup,
        'installed_apps': installed_apps,
        'session_expire_browser': session_expire_browser,
        'session_warning': session_warning,
        'session_expire': session_expire,
        'static_root': static_root,
        'workspaces_root': workspaces_root,
        'bypass_portal_home': bypass_portal_home,
        'resource_quota_handlers': resource_quota_handlers,
        'django_analytical': django_analytical,
        'backends': backends,
        'oauth_options': oauth_options,
        'channel_layer': args.channel_layer
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
