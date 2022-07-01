FROM mambaorg/micromamba
###################
# BUILD ARGUMENTS #
###################
ARG PYTHON_VERSION=3.*

###############
# ENVIRONMENT #
###############
ENV TETHYS_HOME="/usr/lib/tethys"
ENV TETHYS_LOG="/var/log/tethys"
ENV TETHYS_PERSIST="/var/lib/tethys_persist"
ENV TETHYS_APPS_ROOT="/var/www/tethys/apps"
ENV TETHYS_PORT=8000
ENV POSTGRES_PASSWORD="pass"
ENV TETHYS_DB_NAME='tethys_platform'
ENV TETHYS_DB_USERNAME="tethys_default"
ENV TETHYS_DB_PASSWORD="pass"
ENV TETHYS_DB_HOST="db"
ENV TETHYS_DB_PORT=5432
ENV TETHYS_DB_SUPERUSER="tethys_super"
ENV TETHYS_DB_SUPERUSER_PASS="pass"
ENV PORTAL_SUPERUSER_NAME=""
ENV PORTAL_SUPERUSER_EMAIL=""
ENV PORTAL_SUPERUSER_PASSWORD=""
ENV TETHYS_MANAGE="${TETHYS_HOME}/tethys/tethys_portal/manage.py"
ENV TETHYS_PUBLIC_HOST="http://localhost"


# Misc
ENV BASH_PROFILE=".bashrc"
ENV CONDA_HOME="/opt/conda"
ENV CONDA_ENV_NAME=tethys
ENV ENV_NAME=tethys
ENV ASGI_PROCESSES=1
ENV CLIENT_MAX_BODY_SIZE="75M"

# Tethys settings arguments
ENV DEBUG="False"
ENV ALLOWED_HOSTS="\"[localhost, 127.0.0.1]\""
ENV BYPASS_TETHYS_HOME_PAGE="True"
ENV ADD_DJANGO_APPS="\"[]\""
ENV SESSION_WARN=1500
ENV SESSION_EXPIRE=1800
ENV STATIC_ROOT="${TETHYS_PERSIST}/static"
ENV WORKSPACE_ROOT="${TETHYS_PERSIST}/workspaces"
ENV QUOTA_HANDLERS="\"[]\""
ENV DJANGO_ANALYTICAL="\"{}\""
ENV ADD_BACKENDS="\"[]\""
ENV OAUTH_OPTIONS="\"{}\""
ENV CHANNEL_LAYERS_BACKEND="channels.layers.InMemoryChannelLayer"
ENV CHANNEL_LAYERS_CONFIG="\"{}\""
ENV RECAPTCHA_PRIVATE_KEY=""
ENV RECAPTCHA_PUBLIC_KEY=""

# Tethys site arguments
ENV TAB_TITLE=""
ENV FAVICON=""
ENV TITLE=""
ENV LOGO=""
ENV LOGO_HEIGHT=""
ENV LOGO_WIDTH=""
ENV LOGO_PADDING=""
ENV LIBRARY_TITLE=""
ENV PRIMARY_COLOR=""
ENV SECONDARY_COLOR=""
ENV BACKGROUND_COLOR=""
ENV TEXT_COLOR=""
ENV TEXT_HOVER_COLOR=""
ENV SECONDARY_TEXT_COLOR=""
ENV SECONDARY_TEXT_HOVER_COLOR=""
ENV COPYRIGHT=""
ENV HERO_TEXT=""
ENV BLURB_TEXT=""
ENV FEATURE1_HEADING=""
ENV FEATURE1_BODY=""
ENV FEATURE1_IMAGE=""
ENV FEATURE2_HEADING=""
ENV FEATURE2_BODY=""
ENV FEATURE2_IMAGE=""
ENV FEATURE3_HEADING=""
ENV FEATURE3_BODY=""
ENV FEATURE3_IMAGE=""
ENV ACTION_TEXT=""
ENV ACTION_BUTTON=""

#########
# SETUP #
#########
USER root
RUN mkdir -p "${TETHYS_HOME}/tethys"
WORKDIR ${TETHYS_HOME}

# Speed up APT installs
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
  ; echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache

# Install APT packages
RUN rm -rf /var/lib/apt/lists/*\
 && apt-get update \
 && apt-get -y install bzip2 git nginx supervisor gcc salt-minion procps pv \
 && rm -rf /var/lib/apt/lists/*

# Remove default NGINX site
RUN rm -f /etc/nginx/sites-enabled/default

# Setup Conda Environment
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml ${TETHYS_HOME}/tethys/
WORKDIR ${TETHYS_HOME}/tethys
RUN sed -i "s/- python$/- python=${PYTHON_VERSION}/g" environment.yml \
 && micromamba create -n "${CONDA_ENV_NAME}" --yes --file "environment.yml" \
 && micromamba clean --all --yes

###########
# INSTALL #
###########
# Make dirs
RUN mkdir -p ${TETHYS_PERSIST} ${TETHYS_APPS_ROOT} ${WORKSPACE_ROOT} ${STATIC_ROOT} ${TETHYS_LOG}

# Setup www user, run supervisor and nginx processes as www user
RUN groupadd www \
  ; useradd -r -u 1011 -g www www \
  ; sed -i 's/^user.*/user www www;/' /etc/nginx/nginx.conf \
  ; sed -i "/^\[supervisord\]$/a user=www" /etc/supervisor/supervisord.conf \
  ; chown -R www: ${TETHYS_LOG} /run /var/log/supervisor /var/log/nginx /var/lib/nginx

# ADD files from repo
ADD --chown=www:www resources ${TETHYS_HOME}/tethys/resources/
ADD --chown=www:www tethys_apps ${TETHYS_HOME}/tethys/tethys_apps/
ADD --chown=www:www tethys_cli ${TETHYS_HOME}/tethys/tethys_cli/
ADD --chown=www:www tethys_compute ${TETHYS_HOME}/tethys/tethys_compute/
ADD --chown=www:www tethys_config ${TETHYS_HOME}/tethys/tethys_config/
ADD --chown=www:www tethys_layouts ${TETHYS_HOME}/tethys/tethys_layouts/
ADD --chown=www:www tethys_gizmos ${TETHYS_HOME}/tethys/tethys_gizmos/
ADD --chown=www:www tethys_portal ${TETHYS_HOME}/tethys/tethys_portal/
ADD --chown=www:www tethys_quotas ${TETHYS_HOME}/tethys/tethys_quotas/
ADD --chown=www:www tethys_sdk ${TETHYS_HOME}/tethys/tethys_sdk/
ADD --chown=www:www tethys_services ${TETHYS_HOME}/tethys/tethys_services/
ADD --chown=www:www tests ${TETHYS_HOME}/tethys/tests/
ADD --chown=www:www README.rst ${TETHYS_HOME}/tethys/
ADD --chown=www:www LICENSE ${TETHYS_HOME}/tethys/
ADD --chown=www:www *.toml ${TETHYS_HOME}/tethys/
ADD --chown=www:www *.cfg ${TETHYS_HOME}/tethys/
ADD --chown=www:www .git ${TETHYS_HOME}/tethys/.git/

# Run Installer
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN pip install -e .
RUN tethys gen portal_config

# Install channel-redis
RUN pip install channels_redis

############
# CLEAN UP #
############
RUN apt-get -y remove gcc \
  ; apt-get -y autoremove \
  ; apt-get -y clean

#########################
# CONFIGURE  ENVIRONMENT#
#########################
ENV PATH ${CONDA_HOME}/miniconda/envs/tethys/bin:$PATH 
VOLUME ["${TETHYS_HOME}/workspaces", "${TETHYS_HOME}/keys"]
EXPOSE 80

###############*
# COPY IN SALT #
###############*
ADD docker/salt/ /srv/salt/
ADD docker/run.sh ${TETHYS_HOME}/

########
# RUN! #
########
WORKDIR ${TETHYS_HOME}
# Create Salt configuration based on ENVs
CMD bash run.sh
HEALTHCHECK --start-period=240s \
  CMD  ps $(cat $(grep 'pidfile=.*' /etc/supervisor/supervisord.conf | awk -F'=' '{print $2}' | awk '{print $1}')) > /dev/null; && ps $(cat $(grep 'pid .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')) > /dev/null;
