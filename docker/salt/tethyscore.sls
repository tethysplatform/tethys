{% set DEBUG = salt['environ.get']('DEBUG') %}
{% set ALLOWED_HOSTS = salt['environ.get']('ALLOWED_HOSTS') %}
{% set CONDA_ENV_NAME = salt['environ.get']('CONDA_ENV_NAME') %}
{% set CONDA_HOME = salt['environ.get']('CONDA_HOME') %}
{% set NGINX_USER = salt['environ.get']('NGINX_USER') %}
{% set CLIENT_MAX_BODY_SIZE = salt['environ.get']('CLIENT_MAX_BODY_SIZE') %}
{% set ASGI_PROCESSES = salt['environ.get']('ASGI_PROCESSES') %}
{% set TETHYS_BIN_DIR = [CONDA_HOME, "/envs/", CONDA_ENV_NAME, "/bin"]|join %}
{% set TETHYS_DB_NAME = salt['environ.get']('TETHYS_DB_NAME') %}
{% set TETHYS_DB_HOST = salt['environ.get']('TETHYS_DB_HOST') %}
{% set TETHYS_DB_PASSWORD = salt['environ.get']('TETHYS_DB_PASSWORD') %}
{% set POSTGRES_PASSWORD = salt['environ.get']('POSTGRES_PASSWORD') %}
{% set TETHYS_DB_PORT = salt['environ.get']('TETHYS_DB_PORT') %}
{% set TETHYS_DB_USERNAME = salt['environ.get']('TETHYS_DB_USERNAME') %}
{% set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') %}
{% set TETHYS_PORT = salt['environ.get']('TETHYS_PORT') %}
{% set TETHYS_PUBLIC_HOST = salt['environ.get']('TETHYS_PUBLIC_HOST') %}
{% set TETHYS_DB_SUPERUSER = salt['environ.get']('TETHYS_DB_SUPERUSER') %}
{% set TETHYS_DB_SUPERUSER_PASS = salt['environ.get']('TETHYS_DB_SUPERUSER_PASS') %}
{% set PORTAL_SUPERUSER_NAME = salt['environ.get']('PORTAL_SUPERUSER_NAME') %}
{% set PORTAL_SUPERUSER_EMAIL = salt['environ.get']('PORTAL_SUPERUSER_EMAIL') %}
{% set PORTAL_SUPERUSER_PASSWORD = salt['environ.get']('PORTAL_SUPERUSER_PASSWORD') %}
{% set ADD_DJANGO_APPS = salt['environ.get']('ADD_DJANGO_APPS') %}
{% set SESSION_WARN = salt['environ.get']('SESSION_WARN') %}
{% set SESSION_EXPIRE = salt['environ.get']('SESSION_EXPIRE') %}
{% set TETHYS_PERSIST = salt['environ.get']('TETHYS_PERSIST') %}
{% set STATIC_ROOT = salt['environ.get']('STATIC_ROOT') %}
{% set WORKSPACE_ROOT = salt['environ.get']('WORKSPACE_ROOT') %}
{% set QUOTA_HANDLERS = salt['environ.get']('QUOTA_HANDLERS') %}
{% set DJANGO_ANALYTICAL = salt['environ.get']('DJANGO_ANALYTICAL') %}
{% set ADD_BACKENDS = salt['environ.get']('ADD_BACKENDS') %}
{% set OAUTH_OPTIONS = salt['environ.get']('OAUTH_OPTIONS') %}
{% if salt['environ.get']('CHANNEL_LAYER') %}
{% set CHANNEL_LAYER = salt['environ.get']('CHANNEL_LAYER') %}
{% else %}
{% set CHANNEL_LAYER = "''" %}
{% endif %}
{% if salt['environ.get']('RECAPTCHA_PRIVATE_KEY') %}
{% set RECAPTCHA_PRIVATE_KEY = salt['environ.get']('RECAPTCHA_PRIVATE_KEY') %}
{% else %}
{% set RECAPTCHA_PRIVATE_KEY = "''" %}
{% endif %}
{% if salt['environ.get']('RECAPTCHA_PUBLIC_KEY') %}
{% set RECAPTCHA_PUBLIC_KEY = salt['environ.get']('RECAPTCHA_PUBLIC_KEY') %}
{% else %}
{% set RECAPTCHA_PUBLIC_KEY = "''" %}
{% endif %}

{% set TETHYS_SITE_VAR_LIST = ['TAB_TITLE', 'FAVICON', 'TITLE', 'LOGO', 'LOGO_HEIGHT', 'LOGO_WIDTH', 'LOGO_PADDING',
                               'LIBRARY_TITLE', 'PRIMARY_COLOR', 'SECONDARY_COLOR', 'BACKGROUND_COLOR',
                               'TEXT_COLOR', 'TEXT_HOVER_COLOR', 'SECONDARY_TEXT_COLOR', 'SECONDARY_TEXT_HOVER_COLOR',
                               'COPYRIGHT', 'HERO_TEXT', 'BLURB_TEXT', 'FEATURE1_HEADING', 'FEATURE1_BODY',
                               'FEATURE1_IMAGE', 'FEATURE2_HEADING', 'FEATURE2_BODY', 'FEATURE2_IMAGE',
                               'FEATURE3_HEADING', 'FEATURE3_BODY', 'FEATURE3_IMAGE', 'ACTION_TEXT', 'ACTION_BUTTON'] %}

{% set TETHYS_SITE_CONTENT_LIST = [] %}

{% for ARG in TETHYS_SITE_VAR_LIST %}
  {% if salt['environ.get'](ARG) %}
    {% set ARG_KEY = ['--', ARG.replace('_', '-')|lower]|join %}
    {% set CONTENT = [ARG_KEY, salt['environ.get'](ARG)|quote]|join(' ') %}
    {% do TETHYS_SITE_CONTENT_LIST.append(CONTENT) %}
  {% endif %}
{% endfor %}

{% set TETHYS_SITE_CONTENT = TETHYS_SITE_CONTENT_LIST|join(' ') %}

~/.bashrc:
  file.append:
    - text: "alias t='. {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }}'"

Generate_Tethys_Settings_TethysCore:
  cmd.run:
    - name: >
        {{ TETHYS_BIN_DIR }}/tethys settings
        --set DEBUG {{ DEBUG }}
        --set ALLOWED_HOSTS {{ ALLOWED_HOSTS }}
        --set DATABASES.default.NAME {{ TETHYS_DB_NAME }}
        --set DATABASES.default.USER {{ TETHYS_DB_USERNAME }}
        --set DATABASES.default.PASSWORD {{ TETHYS_DB_PASSWORD }}
        --set DATABASES.default.HOST {{ TETHYS_DB_HOST }}
        --set DATABASES.default.PORT {{ TETHYS_DB_PORT }}
        --set INSTALLED_APPS {{ ADD_DJANGO_APPS }}
        --set SESSION_CONFIG.SECURITY_WARN_AFTER {{ SESSION_WARN }}
        --set SESSION_CONFIG.SECURITY_EXPIRE_AFTER {{ SESSION_EXPIRE }}
        --set TETHYS_PORTAL_CONFIG.STATIC_ROOT {{ STATIC_ROOT }}
        --set TETHYS_PORTAL_CONFIG.TETHYS_WORKSPACES_ROOT {{ WORKSPACE_ROOT }}
        --set RESOURCE_QUOTA_HANDLERS {{ QUOTA_HANDLERS }}
        --set ANALYTICS_CONFIGS {{ DJANGO_ANALYTICAL }}
        --set AUTHENTICATION_BACKENDS {{ ADD_BACKENDS }}
        --set OAUTH_CONFIGS {{ OAUTH_OPTIONS }}
        --set CHANNEL_LAYERS.default.BACKEND {{ CHANNEL_LAYER }}
        --set CAPTCHA_CONFIG.RECAPTCHA_PRIVATE_KEY {{ RECAPTCHA_PRIVATE_KEY }}
        --set CAPTCHA_CONFIG.RECAPTCHA_PUBLIC_KEY {{ RECAPTCHA_PUBLIC_KEY }}
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

Generate_NGINX_Settings_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen nginx --client-max-body-size {{ CLIENT_MAX_BODY_SIZE }} --overwrite
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

Generate_NGINX_Service_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen nginx_service --overwrite
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

Generate_ASGI_Service_TethysCore:
  cmd.run:
    - name: >
        {{ TETHYS_BIN_DIR }}/tethys gen asgi_service
        --asgi-processes {{ ASGI_PROCESSES }}
        --conda-prefix {{ CONDA_HOME }}/envs/{{ CONDA_ENV_NAME }}
        --overwrite
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

/run/asgi:
  file.directory:
    - user: {{ NGINX_USER }}
    - group: {{ NGINX_USER }}
    - mode: 755
    - makedirs: True

/var/log/tethys/tethys.log:
  file.managed:
    - user: {{ NGINX_USER }}
    - replace: False
    - makedirs: True

Create_Database_User_and_SuperUser_TethysCore:
  cmd.run:
    - name: >
        . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} &&
        PGPASSWORD="{{ POSTGRES_PASSWORD }}" {{ TETHYS_BIN_DIR }}/tethys db create
        -n {{ TETHYS_DB_USERNAME }}
        -p {{ TETHYS_DB_PASSWORD }}
        -N {{ TETHYS_DB_SUPERUSER }}
        -P {{ TETHYS_DB_SUPERUSER_PASS }}
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

Migrate_Database_TethysCore:
  cmd.run:
    - name: >
        . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && {{ TETHYS_BIN_DIR }}/tethys db migrate
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

Create_Database_Portal_SuperUser_TethysCore:
  cmd.run:
    - name: >
        . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && {{ TETHYS_BIN_DIR }}/tethys db createsuperuser
        {%- if PORTAL_SUPERUSER_NAME and PORTAL_SUPERUSER_PASSWORD %}
        --pn {{ PORTAL_SUPERUSER_NAME }} --pp {{ PORTAL_SUPERUSER_PASSWORD }}
        {% endif %}
        {%- if PORTAL_SUPERUSER_EMAIL %}--pe {{ PORTAL_SUPERUSER_EMAIL }}{% endif %}
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"

{% if TETHYS_SITE_CONTENT %}
Modify_Tethys_Site_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys site {{ TETHYS_SITE_CONTENT }}
    - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/setup_complete" ];"
{% endif %}

Flag_Complete_Setup_TethysCore:
  cmd.run:
    - name: touch {{ TETHYS_PERSIST }}/setup_complete
    - shell: /bin/bash
