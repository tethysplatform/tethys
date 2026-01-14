FROM mambaorg/micromamba:debian13-slim
###################
# BUILD ARGUMENTS #
###################
ARG PYTHON_VERSION=3.*
ARG MICRO_TETHYS=false
ARG DJANGO_VERSION=4.2.*
ARG DJANGO_CHANNELS_VERSION
ARG DAPHNE_VERSION

RUN echo "Build Options: Python ${PYTHON_VERSION}, Django ${DJANGO_VERSION}, Daphne ${DAPHNE_VERSION}, Django Channels ${DJANGO_CHANNELS_VERSION}, Micro Tethys ${MICRO_TETHYS}"

###############
# ENVIRONMENT #
###############
ENV TETHYS_HOME="/usr/lib/tethys"
ENV TETHYS_LOG="/var/log/tethys"
ENV TETHYS_PERSIST="/var/lib/tethys_persist"
ENV TETHYS_APPS_ROOT="/var/www/tethys/apps"
ENV TETHYS_PORT=8000
ENV NGINX_PORT=80
ENV POSTGRES_PASSWORD="pass"
ENV SKIP_DB_SETUP=false
ENV TETHYS_DB_ENGINE='django.db.backends.postgresql'
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
ENV CSRF_TRUSTED_ORIGINS="\"[http://localhost, http://127.0.0.1]\""
ENV BYPASS_TETHYS_HOME_PAGE="True"
ENV ADD_DJANGO_APPS="\"[]\""
ENV SESSION_WARN=1500
ENV SESSION_EXPIRE=1800
ENV STATIC_ROOT="${TETHYS_PERSIST}/static"
ENV STATIC_ROOT_CLEAR="True"
ENV WORKSPACE_ROOT="${TETHYS_PERSIST}/workspaces"
ENV MEDIA_ROOT="${TETHYS_PERSIST}/media"
ENV MEDIA_URL="/media/"
ENV QUOTA_HANDLERS="\"[]\""
ENV DJANGO_ANALYTICAL="\"{}\""
ENV ADD_BACKENDS="\"[]\""
ENV OAUTH_OPTIONS="\"{}\""
ENV CHANNEL_LAYERS_BACKEND="channels.layers.InMemoryChannelLayer"
ENV CHANNEL_LAYERS_CONFIG="\"{}\""
ENV RECAPTCHA_PRIVATE_KEY=""
ENV RECAPTCHA_PUBLIC_KEY=""
ENV OTHER_SETTINGS=""

# Tethys site arguments
ENV SITE_TITLE=""
ENV FAVICON=""
ENV BRAND_TEXT=""
ENV BRAND_IMAGE=""
ENV BRAND_IMAGE_HEIGHT=""
ENV BRAND_IMAGE_WIDTH=""
ENV BRAND_IMAGE_PADDING=""
ENV APPS_LIBRARY_TITLE=""
ENV PRIMARY_COLOR=""
ENV SECONDARY_COLOR=""
ENV PRIMARY_TEXT_COLOR=""
ENV PRIMARY_TEXT_HOVER_COLOR=""
ENV SECONDARY_TEXT_COLOR=""
ENV SECONDARY_TEXT_HOVER_COLOR=""
ENV BACKGROUND_COLOR=""
ENV COPYRIGHT=""
ENV HERO_TEXT=""
ENV BLURB_TEXT=""
ENV FEATURE_1_HEADING=""
ENV FEATURE_1_BODY=""
ENV FEATURE_1_IMAGE=""
ENV FEATURE_2_HEADING=""
ENV FEATURE_2_BODY=""
ENV FEATURE_2_IMAGE=""
ENV FEATURE_3_HEADING=""
ENV FEATURE_3_BODY=""
ENV FEATURE_3_IMAGE=""
ENV CALL_TO_ACTION=""
ENV CALL_TO_ACTION_BUTTON=""
ENV PORTAL_BASE_CSS=""
ENV HOME_PAGE_CSS=""
ENV APPS_LIBRARY_CSS=""
ENV ACCOUNTS_BASE_CSS=""
ENV LOGIN_CSS=""
ENV REGISTER_CSS=""
ENV USER_BASE_CSS=""
ENV HOME_PAGE_TEMPLATE=""
ENV APPS_LIBRARY_TEMPLATE=""
ENV LOGIN_PAGE_TEMPLATE=""
ENV REGISTER_PAGE_TEMPLATE=""
ENV USER_PAGE_TEMPLATE=""
ENV USER_SETTINGS_PAGE_TEMPLATE=""

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
  && apt-get clean \
  && apt-get update \
  && apt-get -y install curl gnupg2 ca-certificates lsb-release debian-archive-keyring \
  && apt-get -y install --only-upgrade libpcre2-8-0 \
  && mkdir -p /etc/apt/keyrings \
  && curl -fsSL https://packages.broadcom.com/artifactory/api/security/keypair/SaltProjectKey/public | tee /etc/apt/keyrings/salt-archive-keyring.pgp \
  && curl -fsSL https://github.com/saltstack/salt-install-guide/releases/latest/download/salt.sources | tee /etc/apt/sources.list.d/salt.sources \
  && apt-get update \
  && apt-get -y install bzip2 git nginx supervisor gcc salt-minion procps pv \
  && rm -rf /var/lib/apt/lists/*

# Remove default NGINX site
RUN rm -f /etc/nginx/sites-enabled/default

# Setup conda symlink for the micromamba command
RUN mkdir -p ${CONDA_HOME}/bin
RUN ln -s /bin/micromamba ${CONDA_HOME}/bin/conda

# Setup Conda Environment
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml ${TETHYS_HOME}/tethys/
COPY --chown=$MAMBA_USER:$MAMBA_USER micro_environment.yml ${TETHYS_HOME}/tethys/
COPY --chown=$MAMBA_USER:$MAMBA_USER pyproject.toml ${TETHYS_HOME}/tethys/

WORKDIR ${TETHYS_HOME}/tethys

# Set the versions of Django, Channels, and Daphne if provided in environment.yml and micro_environment.yml
RUN if [ -n "$DJANGO_VERSION" ]; then \
      sed -i "s/\s*- django[^-].*/  - django=${DJANGO_VERSION}/" environment.yml micro_environment.yml; \
    fi && \
    if [ -n "$DJANGO_CHANNELS_VERSION" ]; then \
      sed -i "s/\s*- channels.*/  - channels=${DJANGO_CHANNELS_VERSION}/" environment.yml micro_environment.yml; \
    fi && \
    if [ -n "$DAPHNE_VERSION" ]; then \
      sed -i "s/\s*- daphne.*/  - daphne=${DAPHNE_VERSION}/" environment.yml micro_environment.yml; \
    fi

# Create the conda environment based on the environment.yml or micro_environment.yml file
RUN if [ "${MICRO_TETHYS}" = "true" ]; then \
      sed -i "s/- python[^-].*/- python=${PYTHON_VERSION}/g" micro_environment.yml && \
      micromamba create -n "${CONDA_ENV_NAME}" --yes --file "micro_environment.yml" && \
      micromamba clean --all --yes && \
      rm -rf environment.yml; \
    else \
      sed -i "s/- python[^-].*/- python=${PYTHON_VERSION}/g" environment.yml && \
      micromamba create -n "${CONDA_ENV_NAME}" --yes --file "environment.yml" && \
      micromamba clean --all --yes && \
      rm -rf micro_environment.yml; \
    fi

###########
# INSTALL #
###########
# Make dirs
RUN mkdir -p ${TETHYS_PERSIST} ${TETHYS_APPS_ROOT} ${WORKSPACE_ROOT} ${MEDIA_ROOT} ${STATIC_ROOT} ${TETHYS_LOG}

# Setup www user, run supervisor and nginx processes as www user
RUN groupadd www \
  ; useradd -r -u 1011 -g www www \
  ; sed -i 's/^user.*/user www www;/' /etc/nginx/nginx.conf \
  ; sed -i "/^\[supervisord\]$/a user=www" /etc/supervisor/supervisord.conf \
  ; chown -R www: ${TETHYS_LOG} /run /var/log/supervisor /var/log/nginx /var/lib/nginx

# ADD files from repo
COPY --chown=www:www resources ${TETHYS_HOME}/tethys/resources/
COPY --chown=www:www tethys_apps ${TETHYS_HOME}/tethys/tethys_apps/
COPY --chown=www:www tethys_cli ${TETHYS_HOME}/tethys/tethys_cli/
COPY --chown=www:www tethys_components ${TETHYS_HOME}/tethys/tethys_components/
COPY --chown=www:www tethys_compute ${TETHYS_HOME}/tethys/tethys_compute/
COPY --chown=www:www tethys_config ${TETHYS_HOME}/tethys/tethys_config/
COPY --chown=www:www tethys_layouts ${TETHYS_HOME}/tethys/tethys_layouts/
COPY --chown=www:www tethys_gizmos ${TETHYS_HOME}/tethys/tethys_gizmos/
COPY --chown=www:www tethys_portal ${TETHYS_HOME}/tethys/tethys_portal/
COPY --chown=www:www tethys_quotas ${TETHYS_HOME}/tethys/tethys_quotas/
COPY --chown=www:www tethys_sdk ${TETHYS_HOME}/tethys/tethys_sdk/
COPY --chown=www:www tethys_services ${TETHYS_HOME}/tethys/tethys_services/
COPY --chown=www:www tethys_utils ${TETHYS_HOME}/tethys/tethys_utils/
COPY --chown=www:www tests ${TETHYS_HOME}/tethys/tests/
COPY --chown=www:www README.md ${TETHYS_HOME}/tethys/
COPY --chown=www:www LICENSE ${TETHYS_HOME}/tethys/
COPY --chown=www:www *.cfg ${TETHYS_HOME}/tethys/
COPY --chown=www:www .git ${TETHYS_HOME}/tethys/.git/

# Run Installer
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN pip install --no-deps -e .
RUN tethys gen portal_config

# Install channel-redis
RUN micromamba install -c conda-forge --yes channels_redis

############
# CLEAN UP #
############
RUN apt-get -y remove gcc \
  ; apt-get -y autoremove \
  ; apt-get -y clean

#########################
# CONFIGURE  ENVIRONMENT#
#########################
ENV PATH=${CONDA_HOME}/miniconda/envs/tethys/bin:$PATH 
VOLUME ["${TETHYS_PERSIST}", "${TETHYS_HOME}/keys"]
EXPOSE 80

###############*
# COPY IN SALT #
###############*
COPY docker/salt/ /srv/salt/
COPY docker/run.sh ${TETHYS_HOME}/
COPY docker/liveness-probe.sh ${TETHYS_HOME}/
COPY docker/build-checks.sh ${TETHYS_HOME}/

# Run build.sh to verify Django and Python versions
RUN bash ${TETHYS_HOME}/build-checks.sh

########
# RUN! #
########
WORKDIR ${TETHYS_HOME}
# Create Salt configuration based on ENVs
CMD bash run.sh
HEALTHCHECK --start-period=240s \
  CMD ./liveness-probe.sh
