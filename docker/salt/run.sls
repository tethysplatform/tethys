{% set TETHYS_HOME = salt['environ.get']('TETHYS_HOME') %}
{% set NGINX_USER = salt['environ.get']('NGINX_USER') %}

uwsgi:
  cmd.run:
    - name: {{ TETHYS_HOME }}/miniconda/envs/tethys/bin/uwsgi --yaml {{ TETHYS_HOME}}/src/tethys_portal/tethys_uwsgi.yml --uid {{ NGINX_USER }} --gid {{ NGINX_USER }}
    - bg: True
    - ignore_timeout: True

nginx:
  cmd.run:
    - name: nginx -g 'daemon off;'
    - bg: True
    - ignore_timeout: True