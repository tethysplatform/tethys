FROM continuumio/miniconda3

###############
# ENVIRONMENT #
###############
ENV  TETHYS_HOME="/usr/lib/tethys" \
     TETHYS_PERSIST="/var/lib/tethys_persist" \
     TETHYS_APPS_ROOT="${TETHYS_HOME}/apps" \
     TETHYS_PORT=8000 \
     POSTGRES_PASSWORD="pass" \
     TETHYS_DB_NAME='tethys_platform' \
     TETHYS_DB_USERNAME="tethys_default" \
     TETHYS_DB_PASSWORD="pass" \
     TETHYS_DB_HOST="db" \
     TETHYS_DB_PORT=5432 \
     TETHYS_DB_SUPERUSER="tethys_super" \
     TETHYS_DB_SUPERUSER_PASS="pass" \
     PORTAL_SUPERUSER_NAME="" \
     PORTAL_SUPERUSER_EMAIL="" \
     PORTAL_SUPERUSER_PASSWORD="" \
     TETHYS_MANAGE="${TETHYS_HOME}/tethys/tethys_portal/manage.py"


# Misc
ENV  BASH_PROFILE=".bashrc" \
     CONDA_HOME="/opt/conda" \
     CONDA_ENV_NAME=tethys \
     ASGI_PROCESSES=4 \
     CLIENT_MAX_BODY_SIZE="75M"

# Tethys settings arguments
ENV  ALLOWED_HOSTS="localhost 127.0.0.1" \
     BYPASS_TETHYS_HOME_PAGE="True" \
     ADD_DJANGO_APPS=None \
     SESSION_WARN=1500 \
     SESSION_EXPIRE=1800 \
     STATIC_ROOT="${TETHYS_PERSIST}/static" \
     WORKSPACE_ROOT="${TETHYS_PERSIST}/workspaces" \
     QUOTA_HANDLERS=None \
     DJANGO_ANALYTICAL=None \
     ADD_BACKENDS=None \
     OAUTH_OPTIONS=None \
     CHANNEL_LAYER="" \
     RECAPTCHA_PRIVATE_KEY="" \
     RECAPTCHA_PUBLIC_KEY=""


# Tethys settings flags
# Flags do not take arguments. They evaluate to "True" when included. Available flags:
#   --production, --overwrite, --open-portal, --open-signup, --bypass-portal-home, --session-persist, --captcha
ENV TETHYS_SETTINGS_FLAGS="--production, --overwrite"

# Tethys site arguments
ENV  TAB_TITLE="" \
     FAVICON="" \
     TITLE="" \
     LOGO="" \
     LOGO_HEIGHT="" \
     LOGO_WIDTH="" \
     LOGO_PADDING="" \
     LIBRARY_TITLE="" \
     PRIMARY_COLOR="" \
     SECONDARY_COLOR="" \
     BACKGROUND_COLOR="" \
     TEXT_COLOR="" \
     TEXT_HOVER_COLOR="" \
     SECONDARY_TEXT_COLOR="" \
     SECONDARY_TEXT_HOVER_COLOR="" \
     COPYRIGHT="" \
     HERO_TEXT="" \
     BLURB_TEXT="" \
     FEATURE1_HEADING="" \
     FEATURE1_BODY="" \
     FEATURE1_IMAGE="" \
     FEATURE2_HEADING="" \
     FEATURE2_BODY="" \
     FEATURE2_IMAGE="" \
     FEATURE3_HEADING="" \
     FEATURE3_BODY="" \
     FEATURE3_IMAGE="" \
     ACTION_TEXT="" \
     ACTION_BUTTON=""

#########
# SETUP #
#########
RUN mkdir -p "${TETHYS_HOME}/tethys"
WORKDIR ${TETHYS_HOME}

# Speed up APT installs
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
  ; echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache

# Install APT packages
RUN rm -rf /var/lib/apt/lists/*\
 && apt-get update \
 && apt-get -y install wget gnupg2 \
 && rm -rf /var/lib/apt/lists/*\
 && wget -O - https://repo.saltstack.com/apt/debian/9/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add - \
 && echo "deb http://repo.saltstack.com/apt/debian/9/amd64/latest stretch main" > /etc/apt/sources.list.d/saltstack.list
RUN rm -rf /var/lib/apt/lists/*\
 && apt-get update \
 && apt-get -y install bzip2 git nginx supervisor gcc salt-minion procps pv
 && rm -rf /var/lib/apt/lists/*\
RUN rm -f /etc/nginx/sites-enabled/default

# Setup Conda Environment
ADD environment.yml ${TETHYS_HOME}/tethys/
WORKDIR ${TETHYS_HOME}/tethys
RUN ${CONDA_HOME}/bin/conda env create -n "${CONDA_ENV_NAME}" -f "environment.yml"

###########
# INSTALL #
###########

#Setup Nginx User:
RUN groupadd www;useradd -r -u 1011 -g www www;sed -i 's/^user.*/user www www;/' /etc/nginx/nginx.conf;

# ADD files from repo
ADD --chown=www:www resources ${TETHYS_HOME}/tethys/resources/
ADD --chown=www:www tethys_apps ${TETHYS_HOME}/tethys/tethys_apps/
ADD --chown=www:www tethys_cli ${TETHYS_HOME}/tethys/tethys_cli/
ADD --chown=www:www tethys_compute ${TETHYS_HOME}/tethys/tethys_compute/
ADD --chown=www:www tethys_config ${TETHYS_HOME}/tethys/tethys_config/
ADD --chown=www:www tethys_gizmos ${TETHYS_HOME}/tethys/tethys_gizmos/
ADD --chown=www:www tethys_portal ${TETHYS_HOME}/tethys/tethys_portal/
ADD --chown=www:www tethys_quotas ${TETHYS_HOME}/tethys/tethys_quotas/
ADD --chown=www:www tethys_sdk ${TETHYS_HOME}/tethys/tethys_sdk/
ADD --chown=www:www tethys_services ${TETHYS_HOME}/tethys/tethys_services/
ADD --chown=www:www tests ${TETHYS_HOME}/tethys/tests/
ADD --chown=www:www README.rst ${TETHYS_HOME}/tethys/
ADD --chown=www:www *.py ${TETHYS_HOME}/tethys/
ADD --chown=www:www *.cfg ${TETHYS_HOME}/tethys/
ADD --chown=www:www .git ${TETHYS_HOME}/tethys/.git/

# Run Installer
# we need to have a settings.py file for some commands to work in the Dockerfile (like tethys install)
RUN /bin/bash -c '. ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME} \
  ; python setup.py develop'
RUN /bin/bash -c '. ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME} \
  ; tethys gen settings'
RUN mkdir -p ${TETHYS_PERSIST} ${APPS_ROOT} ${WORKSPACE_ROOT} ${STATIC_ROOT}

############
# CLEAN UP #
############
RUN apt-get -y remove wget gcc gnupg2 \
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

