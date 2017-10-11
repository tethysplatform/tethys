# Use an official Python runtime as a parent image
FROM python:2

WORKDIR /usr/lib/tethys

# Add files to docker image
ADD docker/install_tethys.sh /usr/lib/tethys/install_tethys.sh
ADD . /usr/lib/tethys/src

# Arguments
# ARG TETHYSBUILD_BRANCH=release
# ARG TETHYSBUILD_PY_VERSION=2
# ARG TETHYSBUILD_TETHYS_HOME=/usr/lib/tethys
# ARG TETHYSBUILD_CONDA_HOME=/usr/lib/tethys/miniconda
# ARG TETHYSBUILD_CONDA_ENV_NAME=tethys

# Run Scripts to Get Files
RUN pwd \
    && apt-get update \
    && apt-get --assume-yes install wget bzip2 git nginx \
    && bash install_tethys.sh \
         --python-version 2 \
         --tethys-home /usr/lib/tethys \
         --conda-env-name tethys \
    && mkdir /usr/lib/tethys/workspaces

VOLUME ["/usr/lib/tethys/workspaces"]
VOLUME ["/usr/lib/tethys/keys"]

ADD docker/setup_tethys.sh /usr/lib/tethys/setup_tethys.sh
ADD aquaveo_static/images/aquaveo_favicon.ico /usr/lib/tethys/src/static/tethys_portal/images/default_favicon.png
ADD aquaveo_static/images/aquaveo_logo.png /usr/lib/tethys/src/static/tethys_portal/images/tethys-logo-75.png
ADD aquaveo_static/tethys_main.css /usr/lib/tethys/src/static/tethys_portal/css/tethys_main.css

# Make port 8000 available to the outside world
EXPOSE 80

# Configure Tethys
ENV PATH ${TETHYSBUILD_CONDA_HOME:-/usr/lib/tethys/miniconda}/envs/tethys/bin:$PATH

# Install Tethys
CMD echo Error: Not a Standalone Docker
