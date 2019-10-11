"""
Settings for Tethys Platform

***************************************************************************
*
*   WARNING!!!!
*
*   The settings.py file should no longer be edited to customize your local
*   settings. All portal configuration should now happen in the portal_config.yml
*   file (See docs/tethys_portal/configuration.rst).
*
***************************************************************************

This file contains default Django and other settings for the Tethys Platform.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import yaml
import logging

from django.contrib.messages import constants as message_constants
from tethys_apps.utilities import get_tethys_home_dir
from tethys_cli.gen_commands import generate_secret_key

log = logging.getLogger(__name__)
this_module = sys.modules[__name__]

BASE_DIR = os.path.dirname(__file__)
TETHYS_HOME = get_tethys_home_dir()

local_settings = {}
try:
    with open(os.path.join(TETHYS_HOME, 'portal_config.yml')) as portal_yaml:
        local_settings = yaml.safe_load(portal_yaml).get('settings', {}) or {}
except FileNotFoundError:
    log.info('Could not find the portal_config.yml file. To generate a new portal_config.yml run the command '
             '"tethys gen portal_config"')
except Exception:
    log.exception('There was an error while attempting to read the settings from the portal_config.yml file.')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.pop('SECRET_KEY', generate_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.pop('DEBUG', True)

ALLOWED_HOSTS = local_settings.pop('ALLOWED_HOSTS', [])

# List those who should be notified of an error when DEBUG = False as a tuple of (name, email address).
# i.e.: ADMINS = (('John', 'john@example.com'), ('Mary', 'mary@example.com'))
ADMINS = local_settings.pop('ADMINS', ())

# Use this setting to bypass the home page
BYPASS_TETHYS_HOME_PAGE = local_settings.pop('BYPASS_TETHYS_HOME_PAGE', False)

# Use this setting to disable open account signup
ENABLE_OPEN_SIGNUP = local_settings.pop('ENABLE_OPEN_SIGNUP', False)

# Set to True to allow Open Portal mode.
ENABLE_OPEN_PORTAL = local_settings.pop('ENABLE_OPEN_PORTAL', False)

SESSION_CONFIG = local_settings.pop('SESSION_CONFIG', {})
# Force user logout once the browser has been closed.
# If changed, delete all django_session table entries from the tethys_default database to ensure updated behavior
SESSION_EXPIRE_AT_BROWSER_CLOSE = SESSION_CONFIG.pop('SESSION_EXPIRE_AT_BROWSER_CLOSE', True)

# Warn user of forced logout after indicated number of seconds
SESSION_SECURITY_WARN_AFTER = SESSION_CONFIG.pop('SESSION_SECURITY_WARN_AFTER', 840)

# Force user logout after a certain number of seconds
SESSION_SECURITY_EXPIRE_AFTER = SESSION_CONFIG.pop('SESSION_SECURITY_EXPIRE_AFTER', 900)

DATABASES = local_settings.pop('DATABASES', {})
DATABASES.setdefault('default', {})
DEFAULT_DB = DATABASES['default']
DEFAULT_DB.setdefault('ENGINE', 'django.db.backends.postgresql_psycopg2')
DEFAULT_DB.setdefault('NAME', 'tethys_platform')
DEFAULT_DB.setdefault('USER', 'tethys_default')
DEFAULT_DB.setdefault('PASSWORD', 'pass')
DEFAULT_DB.setdefault('HOST', 'localhost')
DEFAULT_DB.setdefault('PORT', 5436)
DEFAULT_DB.setdefault('DIR', 'psql')


LOGGING_CONFIG = local_settings.pop('LOGGING_CONFIG', {})
# See https://docs.djangoproject.com/en/1.8/topics/logging/#configuring-logging for more logging configuration options.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s:%(name)s:%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console_simple': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console_verbose': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console_simple'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
        'tethys': LOGGING_CONFIG.pop('TETHYS_LOGGING', {
            'handlers': ['console_verbose'],
            'level': 'INFO',
        }),
        'tethys.apps': LOGGING_CONFIG.pop('TETHYS_APPS_LOGGING', {
            'handlers': ['console_verbose'],
            'level': 'INFO',
        }),
    },
}

LOGGING['formatters'].update(LOGGING_CONFIG.pop('LOGGING_FORMATTERS', {}))
LOGGING['handlers'].update(LOGGING_CONFIG.pop('LOGGING_HANDLERS', {}))
LOGGING['loggers'].update(LOGGING_CONFIG.pop('LOGGERS', {}))

INSTALLED_APPS = local_settings.pop('INSTALLED_APPS_OVERRIDE', [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_gravatar',
    'bootstrap3',
    'termsandconditions',
    'tethys_config',
    'tethys_apps',
    'tethys_gizmos',
    'tethys_services',
    'tethys_compute',
    'tethys_quotas',
    'social_django',
    'guardian',
    'session_security',
    'captcha',
    'snowpenguin.django.recaptcha2',
    'rest_framework',
    'rest_framework.authtoken',
    'analytical',
    'channels',
])
INSTALLED_APPS = tuple(INSTALLED_APPS + local_settings.pop('INSTALLED_APPS', []))

MIDDLEWARE = local_settings.pop('MIDDLEWARE_OVERRIDE', [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tethys_portal.middleware.TethysSocialAuthExceptionMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',

])
MIDDLEWARE = tuple(MIDDLEWARE + local_settings.pop('MIDDLEWARE', []))

AUTHENTICATION_BACKENDS = local_settings.pop('AUTHENTICATION_BACKENDS_OVERRIDE', [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
])
AUTHENTICATION_BACKENDS = tuple(local_settings.pop('AUTHENTICATION_BACKENDS', []) + AUTHENTICATION_BACKENDS)

RESOURCE_QUOTA_HANDLERS = local_settings.pop('RESOURCE_QUOTA_HANDLERS_OVERRIDE', [
    "tethys_quotas.handlers.workspace.WorkspaceQuotaHandler",
])
RESOURCE_QUOTA_HANDLERS = tuple(RESOURCE_QUOTA_HANDLERS + local_settings.pop('RESOURCE_QUOTA_HANDLERS', []))

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Terms and conditions settings
ACCEPT_TERMS_PATH = '/terms/accept/'
TERMS_EXCLUDE_URL_PREFIX_LIST = {'/admin/', '/oauth2/', '/handoff/', '/accounts/', '/terms/'}
TERMS_EXCLUDE_URL_LIST = {'/'}
TERMS_BASE_TEMPLATE = 'page.html'

ROOT_URLCONF = 'tethys_portal.urls'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'tethys_config.context_processors.tethys_global_settings_context',
                'tethys_apps.context_processors.tethys_apps_context',
                'tethys_gizmos.context_processors.tethys_gizmos_context'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'tethys_apps.template_loaders.TethysTemplateLoader'
            ],
            'debug': DEBUG
        }
    }
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'tethys_apps.static_finders.TethysStaticFinder'
)

STATIC_ROOT = local_settings.pop('STATIC_ROOT', os.path.join(TETHYS_HOME, 'static'))

TETHYS_WORKSPACES_ROOT = local_settings.pop('TETHYS_WORKSPACES_ROOT', os.path.join(TETHYS_HOME, 'workspaces'))

# Messaging settings
MESSAGE_TAGS = {
    message_constants.DEBUG: 'alert-danger',
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger'
}

# Gravatar Settings
GRAVATAR_URL = 'http://www.gravatar.com/'
GRAVATAR_SECURE_URL = 'https://secure.gravatar.com/'
GRAVATAR_DEFAULT_SIZE = '80'
GRAVATAR_DEFAULT_IMAGE = 'retro'
GRAVATAR_DEFAULT_RATING = 'g'
GRAVATAR_DFFAULT_SECURE = True

# OAuth Settings
# http://psa.matiasaguirre.net/docs/configuration/index.html
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/apps/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'

# OAuth Providers
OAUTH_CONFIGS = local_settings.pop('OAUTH_CONFIGS', {})
for setting, value in OAUTH_CONFIGS.items():
    setattr(this_module, setting, value)

# Django Guardian Settings
ANONYMOUS_USER_ID = -1

CAPTCHA_CONFIG = local_settings.pop('CAPTCHA_CONFIG', {})
for setting, value in CAPTCHA_CONFIG.items():
    setattr(this_module, setting, value)
# If you require reCaptcha to be loaded from somewhere other than https://google.com
# (e.g. to bypass firewall restrictions), you can specify what proxy to use.
# RECAPTCHA_PROXY_HOST: https://recaptcha.net

# Placeholders for the ID's required by various web-analytics services supported by Django-Analytical.
# Replace False with the tracking ID as a string e.g. SERVICE_ID = 'abcd1234'
ANALYTICS_CONFIGS = local_settings.pop('ANALYTICS_CONFIGS', {})
for setting, value in ANALYTICS_CONFIGS.items():
    setattr(this_module, setting, value)

ASGI_APPLICATION = "tethys_portal.routing.application"

# Add any additional specified settings to module
for setting, value in local_settings.items():
    setattr(this_module, setting, value)
