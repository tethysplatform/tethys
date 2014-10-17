"""
Django settings for tethys_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.contrib.messages import constants as message_constants

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8mr7^7i!!=4jpr^z_+mlu7uxrn8yi5_8pq0l4)_gc-89q77-h2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_gravatar',
    'social_auth',
    'bootstrap3',
    'tethys_apps',
    'tethys_gizmos',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'tethys_site.urls'

WSGI_APPLICATION = 'tethys_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tethys_default',
        'USER': 'tethys_default',
        'PASSWORD': 'tethyspass',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'), )

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

# Messaging settings
MESSAGE_TAGS = {message_constants.DEBUG: 'alert-danger',
                message_constants.INFO: 'alert-info',
                message_constants.SUCCESS: 'alert-success',
                message_constants.WARNING: 'alert-warning',
                message_constants.ERROR: 'alert-danger'}

# Gravatar Settings
GRAVATAR_URL = 'http://www.gravatar.com/'
GRAVATAR_SECURE_URL = 'https://secure.gravatar.com/'
GRAVATAR_DEFAULT_SIZE = '80'
GRAVATAR_DEFAULT_IMAGE = 'retro'
GRAVATAR_DEFAULT_RATING = 'g'
GRAVATAR_DFFAULT_SECURE = True

# OAuth Keys
FACEBOOK_APP_ID              = ''
FACEBOOK_API_SECRET          = ''
GOOGLE_CONSUMER_KEY          = ''
GOOGLE_CONSUMER_SECRET       = ''
GOOGLE_OAUTH2_CLIENT_ID      = ''
GOOGLE_OAUTH2_CLIENT_SECRET  = ''

# Email setup
EMAIL_USER_TLS = True
EMAIL_HOST = 'smtp.sendgrid.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'ciwater'
EMAIL_HOST_PASSWORD = '8yu(|w@ter'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Tethys apps settings
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'tethys_apps.utilities.TethysAppsStaticFinder')

TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'tethys_apps.utilities.tethys_apps_template_loader')

TEMPLATE_CONTEXT_PROCESSORS = ('django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.debug',
                               'django.core.context_processors.i18n',
                               'django.core.context_processors.media',
                               'django.core.context_processors.static',
                               'django.core.context_processors.tz',
                               'django.contrib.messages.context_processors.messages',
                               'tethys_apps.context_processors.tethys_apps_context',
                               'tethys_gizmos.context_processors.tethys_gizmos_context')

# Tethys App Persistent Stores
TETHYS_APPS_DATABASE_MANAGER_URL = 'postgresql://tethys_db_manager:tethyspass@localhost:5432/tethys_db_manager'
TETHYS_APPS_SUPERUSER = 'postgresql://tethys_super:tethyspass@localhost:5432/tethys_super'

# Gizmos globals
TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY = 'AIzaSyB-0nvmHhbOaaiYx6UN36145lWjUq5c2tg'

