# Use an official Python runtime as a parent image
FROM python:2-slim-stretch

#####################
# Default Variables #
#####################

# Tethys
ENV  TETHYS_HOME="/usr/lib/tethys" \
     TETHYS_PORT=80 \
     TETHYS_DB_USERNAME='tethys_default' \
     TETHYS_DB_PASSWORD='pass' \
     TETHYS_DB_HOST='172.17.0.1' \
     TETHYS_DB_PORT=5432 \
     TETHYS_SUPER_USER='admin' \
     TETHYS_SUPER_USER_EMAIL='' \
     TETHYS_SUPER_USER_PASS='pass' \
     TETHYS_CONDA_HOME=${CONDA_HOME} \
     TETHYS_CONDA_ENV_NAME=${CONDA_ENV_NAME} \

# Misc
     ALLOWED_HOST=127.0.0.1 \
     BASH_PROFILE=".bashrc" \
     CONDA_HOME="${TETHYS_HOME}/miniconda" \
     CONDA_ENV_NAME=tethys \
     MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh" \
     PYTHON_VERSION=2 \
     ACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/activate.d" \
     DEACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/deactivate.d" \
     ACTIVATE_SCRIPT="${ACTIVATE_DIR}/tethys-activate.sh" \
     DEACTIVATE_SCRIPT="${DEACTIVATE_DIR}/tethys-deactivate.sh" 


#########
# SETUP #
#########
RUN mkdir -p "${TETHYS_HOME}/src"

# Speed up APT installs
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup
RUN echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache

# Install APT packages
RUN apt-get update && apt-get -y install wget \
 && wget -O - https://repo.saltstack.com/apt/debian/9/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add - \
 && echo "deb http://repo.saltstack.com/apt/debian/9/amd64/latest stretch main" > /etc/apt/sources.list.d/saltstack.list
RUN apt-get update && apt-get -y install bzip2 git nginx gcc salt-minion
RUN rm -f /etc/nginx/sites-enabled/default

# Install Miniconda
RUN wget ${MINICONDA_URL} -O "${TETHYS_HOME}/miniconda.sh" 
RUN bash ${TETHYS_HOME}/miniconda.sh -b -p "${CONDA_HOME}" 

# Setup Conda Environment
ADD environment_py2.yml ${TETHYS_HOME}/src/
WORKDIR ${TETHYS_HOME}/src
RUN ${CONDA_HOME}/bin/conda env create -n "${CONDA_ENV_NAME}" -f "environment_py${PYTHON_VERSION}.yml"

###########
# INSTALL #
###########
# ADD files from repo
ADD resources ${TETHYS_HOME}/src/
ADD templates ${TETHYS_HOME}/src/
ADD tethys_apps ${TETHYS_HOME}/src/
ADD tethys_compute ${TETHYS_HOME}/src/
ADD tethys_config ${TETHYS_HOME}/src/
ADD tethys_gizmos ${TETHYS_HOME}/src/
ADD tethys_portal ${TETHYS_HOME}/src/
ADD tethys_sdk ${TETHYS_HOME}/src/
ADD tethys_services ${TETHYS_HOME}/src/
ADD *.py ${TETHYS_HOME}/src/

# Run Installer
RUN . ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME} \
  ; python setup.py develop \
  ; conda install -c conda-forge uwsgi -y \
  ; mkdir ${TETHYS_HOME}/workspaces

# Add static files
ADD static ${TETHYS_HOME}/src/
ADD aquaveo_static/images/aquaveo_favicon.ico ${TETHYS_HOME}/src/static/tethys_portal/images/default_favicon.png
ADD aquaveo_static/images/aquaveo_logo.png ${TETHYS_HOME}/src/static/tethys_portal/images/tethys-logo-75.png
ADD aquaveo_static/tethys_main.css ${TETHYS_HOME}/src/static/tethys_portal/css/tethys_main.css

# Generate Inital Settings Files
RUN . ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME} \
  ; tethys gen settings --production --allowed-host ${ALLOWED_HOST} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT} --overwrite \
  ; sed -i -e "s/#TETHYS_WORKSPACES_ROOT = '\/var\/www\/tethys\/static\/workspaces'/TETHYS_WORKSPACES_ROOT = '\/usr\/lib\/tethys\/workspaces'/g" ${TETHYS_HOME}/src/tethys_portal/settings.py \
  ; tethys gen nginx --overwrite \
  ; tethys gen uwsgi_settings --overwrite \
  ; tethys gen uwsgi_service --overwrite


# Give NGINX Permission
RUN NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}') \
    find ${TETHYS_HOME} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}

############
# CLEAN UP #
############
RUN apt-get -y remove wget gcc \
  ; apt-get -y autoremove \
  ; apt-get -y clean

#########################
# CONFIGURE  ENVIRONMENT#
#########################
ENV PATH ${CONDA_HOME}/miniconda/envs/tethys/bin:$PATH 
VOLUME ["${TETHYS_HOME}/workspaces", "${TETHYS_HOME}/keys"]
EXPOSE 80

########
# RUN! #
########
CMD echo "Sleeping Forever"
CMD while [ 1 ]; do sleep 1; done
