{%- set ALLOWED_HOST = salt['environ.get']('ALLOWED_HOST') -%}
{%- set CONDA_ENV_NAME = salt['environ.get']('CONDA_ENV_NAME') -%}
{%- set CONDA_HOME = salt['environ.get']('CONDA_HOME') -%}
{%- set TETHYS_BIN_DIR = [CONDA_HOME, "/envs/", CONDA_ENV_NAME, "/bin"]|join -%}
{%- set TETHYS_DB_HOST = salt['environ.get']('TETHYS_DB_HOST') -%}
{%- set TETHYS_DB_PASSWORD = salt['environ.get']('TETHYS_DB_PASSWORD') -%}
{%- set TETHYS_DB_PORT = salt['environ.get']('TETHYS_DB_PORT') -%}
{%- set TETHYS_DB_USERNAME = salt['environ.get']('TETHYS_DB_USERNAME') -%}
{%- set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') -%}
{%- set TETHYS_PUBLIC_HOST = salt['environ.get']('TETHYS_PUBLIC_HOST') -%}
{%- set TETHYS_SUPER_USER = salt['environ.get']('TETHYS_SUPER_USER') -%}
{%- set TETHYS_SUPER_USER_EMAIL = salt['environ.get']('TETHYS_SUPER_USER_EMAIL') -%}
{%- set TETHYS_SUPER_USER_PASS = salt['environ.get']('TETHYS_SUPER_USER_PASS') -%}

~/.bashrc:
  file.append:
    - text: alias t=. {{ CONDA_HOME }}/bin/activate {{ CONDA_ENV_NAME }}

Generate_Tethys_Settings:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen settings --production --allowed-host={{ ALLOWED_HOST }} --db-username {{ TETHYS_DB_USERNAME }} --db-password {{ TETHYS_DB_PASSWORD }} --db-port {{ TETHYS_DB_PORT }} --overwrite

Edit_Tethys_Settings_File_(HOST):
  file.replace:
    - name: {{ TETHYS_HOME }}/src/tethys_portal/settings.py
    - pattern: "'HOST': '127.0.0.1'"
    - repl: "'HOST': '{{ TETHYS_DB_HOST }}'"

Edit_Tethys_Settings_File_(HOME_PAGE):
  file.replace:
    - name: {{ TETHYS_HOME }}/src/tethys_portal/settings.py
    - pattern: "BYPASS_TETHYS_HOME_PAGE = False"
    - repl: "BYPASS_TETHYS_HOME_PAGE = True"

Edit_Tethys_Settings_File_(SESSION_WARN):
  file.replace:
    - name: {{ TETHYS_HOME }}/src/tethys_portal/settings.py
    - pattern: "SESSION_SECURITY_WARN_AFTER = 840"
    - repl: "SESSION_SECURITY_WARN_AFTER = 25 * 60"

Edit_Tethys_Settings_File_(SESSION_EXPIRE):
  file.replace:
    - name: {{ TETHYS_HOME }}/src/tethys_portal/settings.py
    - pattern: "SESSION_SECURITY_EXPIRE_AFTER = 900"
    - repl: "SESSION_SECURITY_EXPIRE_AFTER = 30 * 60"

Edit_Tethys_Settings_File_(PUBLIC_HOST):
  file.append:
    - name: {{ TETHYS_HOME }}/src/tethys_portal/settings.py
    - text: "PUBLIC_HOST = \"{{ TETHYS_PUBLIC_HOST }}\""

Generate_NGINX_Settings:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen nginx --overwrite

Generate_uwsgi_Settings:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen uwsgi_settings --overwrite

Generate_uwsgi_service:
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys gen uwsgi_service --overwrite
  file.managed:
    - name: /var/log/uwsgi/tethys.log
    - makedirs: True

Prepare_Database:
  postgres_user.present:
    - name: {{ TETHYS_DB_USERNAME }}
    - password: {{ TETHYS_DB_PASSWORD }}
    - login: True
  postgres_database.present:
    - name: {{ TETHYS_DB_USERNAME }}
  cmd.run:
    - name: {{ TETHYS_BIN_DIR }}/tethys manage syncdb

Create_Super_User:
  cmd.run:
    - name: echo "from django.contrib.auth.models import User; User.objects.create_superuser('{{ TETHYS_SUPER_USER }}', '{{ TETHYS_SUPER_USER_EMAIL }}', '{{ TETHYS_SUPER_USER_PASS }}') if (len(User.objects.filter(username='{{ TETHYS_SUPER_USER }}')) == 0)" | {{TETHYS_BIN_DIR }}/python manage.py shell
    - cwd: {{ TETHYS_HOME }}/src

Link_NGINX_Config:
  file.symlink:
    - name: /etc/nginx/sites-enabled/tethys_nginx.conf
    - target: ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf


uwsgi:
  cmd.run:
    - name: {{ TETHYS_HOME }}/miniconda/envs/tethys/bin/uwsgi --yaml /usr/lib/tethys/src/tethys_portal/tethys_uwsgi.yml --uid www-data --gid www-data
    - bg: True
    - ignore_timeout: True

nginx:
  cmd.run:
    - name: nginx -g 'daemon off'
    - bg: True
    - ignore_timeout: True

