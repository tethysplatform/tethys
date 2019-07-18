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
{% set TETHYS_SUPER_USER = salt['environ.get']('TETHYS_SUPER_USER') %}
{% set TETHYS_SUPER_USER_PASS = salt['environ.get']('TETHYS_SUPER_USER_PASS') %}
{% set BYPASS_TETHYS_HOME_PAGE = salt['environ.get']('BYPASS_TETHYS_HOME_PAGE') %}
{% set ADD_DJANGO_APPS = salt['environ.get']('ADD_DJANGO_APPS') %}
{% set SESSION_EXPIRE_AT_BROWSER_CLOSE = salt['environ.get']('SESSION_EXPIRE_AT_BROWSER_CLOSE') %}
{% set SESSION_WARN = salt['environ.get']('SESSION_WARN') %}
{% set SESSION_EXPIRE = salt['environ.get']('SESSION_EXPIRE') %}
{% set OPEN_PORTAL = salt['environ.get']('OPEN_PORTAL') %}
{% set OPEN_SIGNUP = salt['environ.get']('OPEN_SIGNUP') %}
{% set STATIC_ROOT = salt['environ.get']('STATIC_ROOT') %}
{% set WORKSPACE_ROOT = salt['environ.get']('WORKSPACE_ROOT') %}
{% set QUOTA_HANDLERS = salt['environ.get']('QUOTA_HANDLERS') %}
{% set DJANGO_ANALYTICAL = salt['environ.get']('DJANGO_ANALYTICAL') %}
{% set ADD_BACKENDS = salt['environ.get']('ADD_BACKENDS') %}
{% set OAUTH_OPTIONS = salt['environ.get']('OAUTH_OPTIONS') %}
{% set CHANNEL_LAYER = salt['environ.get']('CHANNEL_LAYER') %}

~/.bashrc:
  file.append:
    - text: "alias t='. {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }}'"

Generate_Tethys_Settings_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen settings --production --allowed-hosts {{ ALLOWED_HOSTS }} --db-name {{ TETHYS_DB_NAME }} --db-username {{ TETHYS_SUPER_USER }} --db-password {{ TETHYS_SUPER_USER_PASS }} --db-host {{ TETHYS_DB_HOST }} --db-port {{ TETHYS_DB_PORT }} --bypass-portal-home {{ BYPASS_TETHYS_HOME_PAGE }} --add-apps {{ ADD_DJANGO_APPS }} --session-expire-browser {{ SESSION_EXPIRE_AT_BROWSER_CLOSE }} --open-portal {{ OPEN_PORTAL }} --open-signup {{ OPEN_SIGNUP }} --session-warning {{ SESSION_WARN }} --session-expire {{ SESSION_EXPIRE }} --static-root {{ STATIC_ROOT }} --workspaces-root {{ WORKSPACE_ROOT }} --add-quota-handlers {{ QUOTA_HANDLERS }} --django-analytical {{ DJANGO_ANALYTICAL }} --add-backends {{ ADD_BACKENDS }} --oauth-options {{ OAUTH_OPTIONS }} --channel-layer {{ CHANNEL_LAYER }} --overwrite
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Generate_NGINX_Settings_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen nginx --client-max-body-size {{ CLIENT_MAX_BODY_SIZE }} --overwrite
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Generate_NGINX_Service_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen nginx_service --overwrite
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Generate_ASGI_Service_TethysCore:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen asgi_service --asgi-processes {{ ASGI_PROCESSES }} --overwrite
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Link_NGINX_Config_TethysCore:
  file.symlink:
    - name: /etc/nginx/sites-enabled/tethys_nginx.conf
    - target: {{ TETHYS_HOME }}/tethys/tethys_portal/tethys_nginx.conf
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Link_NGINX_Service_TethysCore:
  file.symlink:
    - name: /etc/supervisor/conf.d/nginx_supervisord.conf
    - target: {{ TETHYS_HOME }}/tethys/tethys_portal/nginx_supervisord.conf
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Link_ASGI_Config_TethysCore:
  file.symlink:
    - name: /etc/supervisor/conf.d/asgi_supervisord.conf
    - target: {{ TETHYS_HOME }}/tethys/tethys_portal/asgi_supervisord.conf
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

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

Prepare_Database_TethysCore:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && PGPASSWORD="{{ POSTGRES_PASSWORD }}" {{ TETHYS_BIN_DIR }}/tethys db configure -N {{ TETHYS_SUPER_USER }} -P {{ TETHYS_SUPER_USER_PASS }}
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Collect_Static_Files:
  cmd.run:
    - name: . {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }} && {{ TETHYS_BIN_DIR }}/tethys manage collectstatic
    - shell: /bin/bash
    - unless: /bin/bash -c "[ -f "/usr/lib/tethys/setup_complete" ];"

Flag_Complete_Setup_TethysCore:
  cmd.run:
    - name: touch /usr/lib/tethys/setup_complete
    - shell: /bin/bash
