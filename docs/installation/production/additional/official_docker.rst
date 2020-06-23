.. _production_official_docker:
.. _`Tethys Portal Configuration`: ../../../tethys_portal/configuration.html?highlight=portal%20configuration
.. _`Salt Script`: https://docs.saltstack.com/en/latest/topics/index.html

***************************
Official Docker Image
***************************

**Last Updated:** Jun 2020

Download a Tethys Docker image
##############################

The official Tethys Docker images are located in the tethysplatform/tethys-core Docker Hub repository. Image released are tagged using the following format:

+---------------+------------------------------------------------------------------------------------------------------+
|    Tag        | Description                                                                                          |
+===============+======================================================================================================+
| latest        | latest tagged released                                                                               |
+---------------+------------------------------------------------------------------------------------------------------+
| master        | latest development build (what's in the master branch)                                               |
+---------------+------------------------------------------------------------------------------------------------------+
| version       | Specify the version of Tethys image, for example: v3.0.5                                             |
+---------------+------------------------------------------------------------------------------------------------------+

The following commands will download Tethys image to your machine:
::

    docker pull tethysplatform/tethys-core:latest           # the latest Tethys release
    docker pull tethysplatform/tethys-core:v3.0.5           # Tethys version 3.0.5

How to Run
##########
Make sure that there isn't already a docker container or docker images with the desired name
::

    docker rm tethys-core
    docker rmi tethys-core

Build a new docker with the desired name and tag
::

    docker build -t tethys-core:latest

### Running the docker
To run the docker you can use the following flags

use the following flag with the arguments listed in the environment variable table. (NOTE: args in the build arg table can be used here as well)
::

    -e TETHYS_CONDA_ENV='tethys'


Example of Command:
::

    docker run -p 127.0.0.1:8000:8000 --name tethys-core \
        -e TETHYS_DB_SUPERUSER='tethys_super' -e TETHYS_DB_PASSWORD='3x@m9139@$$' \
        -e TETHYS_DB_PORT='5432' TETHYS_SUPERUSER='admin' \
        -e TETHYS_SUPERUSER_PASS='admin' tethyscore

Docker Compose
##############

A faster way is to use the docker-compose.yml file to build and run the docker image.
::

    version: "3.2"
    services:
      tethys:
        container_name: tethyscore
        image: tethysplatform/tethys-core
        build:
          cache_from:
            - tethysplatform/tethys-core
          context: ../
        ports:
          - "80:80"
        environment:
          TETHYS_DB_SUPERUSER: "tethys_super"
          TETHYS_DB_SUPERUSER_PASS: "pass"
          ASGI_PROCESSES: 4
          CLIENT_MAX_BODY_SIZE: "75M"
        links:
          - db
        depends_on:
          - db
      db:
        image: postgres
        restart: always
        environment:
          POSTGRES_PASSWORD: pass

You can build and run your docker image now with:
::

    docker-compose up

***************************
Environment Variables
***************************

Tethys uses environment variables to build and initialize the app. These are the environment variables in Tethys:

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| TETHYS_HOME               | Path to tethys home directory.  Defaults to "/usr/lib/tethys".                           |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_PERSIST            | Path to tethys persist directory. All the data in this directory are persisted even      |
|                           | after the container stops. Defaults to "/var/lib/tethys_persist"                         |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_APPS_ROOT          | Path to tethys apps root directory. Defaults to "${TETHYS_HOME}/apps".                   |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_PORT               | Tethys' port. Defaults to "8000".                                                        |
+---------------------------+------------------------------------------------------------------------------------------+
| POSTGRES_PASSWORD         | Password of the postgres database. Defaults to "pass".                                   |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_NAME            | Name for Tethys Database. Defaults to "tethys_platform".                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_USERNAME        | Owner's Username for Tethys Database. Defaults to "tethys_default"                       |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_PASSWORD        | Owner's Password for Tethys Database. Defaults to "pass"                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_HOST            | Host of Tethys Database. Defaults to "db"                                                |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_PORT            | Port of Tethys Database. Defaults to "5432"                                              |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_SUPERUSER       | Super User for Tethys Database. Defaults to "tethys_super"                               |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_DB_SUPERUSER_PASS  | Super User's password for Tethys Database. Defaults to "pass"                            |
+---------------------------+------------------------------------------------------------------------------------------+
| PORTAL_SUPERUSER_NAME     | Name for the Tethys portal super user. Empty by default.                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| PORTAL_SUPERUSER_EMAIL    | Email for the Tethys portal super user. Empty by default.                                |
+---------------------------+------------------------------------------------------------------------------------------+
| PORTAL_SUPERUSER_PASSWORD | Password for the Tethys portal super user. Empty by default.                             |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_MANAGE             | Path to manage.py file. Defaults to "${TETHYS_HOME}/tethys/tethys_portal/manage.py"      |
+---------------------------+------------------------------------------------------------------------------------------+
| BASH_PROFILE              | The location of bash profile file. Defaults to ".bashrc"                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| CONDA_HOME                | Path of conda home. Defaults to "/opt/conda"                                             |
+---------------------------+------------------------------------------------------------------------------------------+
| CONDA_ENV_NAME            | Name of conda environment. Defaults to tethys.                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| ASGI_PROCESSES            | The maximum number of asgi worker processes. Defaults to 4.                              |
+---------------------------+------------------------------------------------------------------------------------------+
| CLIENT_MAX_BODY_SIZE      | client_max_body_size parameter for nginx config. Defaults to 75M.                        |
+---------------------------+------------------------------------------------------------------------------------------+
| DEBUG                     | the Django DEBUG setting. Defaults to False. See `Tethys Portal Configuration`_          |
+---------------------------+------------------------------------------------------------------------------------------+
| ALLOWED_HOSTS             | The Django ALLOWED_HOSTS setting. Defaults to "\"[localhost, 127.0.0.1]\"".              |
|                           | See `Tethys Portal Configuration`_                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| BYPASS_TETHYS_HOME_PAGE   | The home page of Tethys Portal redirects to the Apps Library when True.                  |
|                           | Defaults to False. See `Tethys Portal Configuration`_                                    |
+---------------------------+------------------------------------------------------------------------------------------+
| ADD_DJANGO_APPS           | List of the DJANGO APPS in this format "\"[App1, App2]\"". Defaults to "\"[]\"" (Empty)  |
+---------------------------+------------------------------------------------------------------------------------------+
| SESSION_WARN              | Number of seconds in idle until the warning message of session expiration displayed.     | 
|                           | Defaults to "1500" (1500 seconds).                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| SESSION_EXPIRE            | Number of seconds in idle until the session expired. Defaults to "1800" (1800 seconds).  |
+---------------------------+------------------------------------------------------------------------------------------+
| STATIC_ROOT               | Path to the tethys static root folder. Defaults to "${TETHYS_PERSIST}/static"            |
+---------------------------+------------------------------------------------------------------------------------------+
| WORKSPACE_ROOT            | Path to the tethys workspaces root folder. Defaults to "${TETHYS_PERSIST}/workspaces"    |
+---------------------------+------------------------------------------------------------------------------------------+
| QUOTA_HANDLERS            | A list of Tethys ResourceQuotaHandler classes to load in this format "\"[RQ1, RQ22]\"".  |
|                           | Defaults to "\"[]\"" (Empty).                                                            |
|                           | See RESOURCE_QUOTA_HANDLERS in `Tethys Portal Configuration`_                            |
+---------------------------+------------------------------------------------------------------------------------------+
| DJANGO_ANALYTICAL         | the Django Analytical configuration settings for enabling analytics services on the      |
|                           | Tethys Portal in this format "\"{CLICKY_SITE_ID:123}\"". Defaults to "\"{}}\"" (Empty).  |
|                           | Tethys Portal. See ANALYTICS_CONFIGS in `Tethys Portal Configuration`_                   |
+---------------------------+------------------------------------------------------------------------------------------+
| ADD_BACKENDS              | the Django AUTHENTICATION_BACKENDS setting in this format "\"[Setting1, Setting2]\""     |
|                           | Defaults to "\"[]\"" (Empty).                                                            |
|                           | See AUTHENTICATION_BACKENDS in `Tethys Portal Configuration`_                            |
+---------------------------+------------------------------------------------------------------------------------------+
| OAUTH_OPTIONS             | the OAuth options for Tethys Portal in this format "\"{SOCIAL_AUTH_FACEBOOK_KEY:123}\""  |
|                           | Defaults to "\"{}}\"" (Empty).                                                           |
|                           | Tethys Portal. See OATH_CONFIGS in `Tethys Portal Configuration`_                        |
+---------------------------+------------------------------------------------------------------------------------------+
| CHANNEL_LAYER             | the Django Channel Layers Backend. Default to "channels.layers.InMemoryChannelLayer"     |
+---------------------------+------------------------------------------------------------------------------------------+
| RECAPTCHA_PRIVATE_KEY     | Private key for Google ReCaptcha. Required to enable ReCaptcha on the login screen.      |
|                           | See RECAPTCHA_PRIVATE_KEY in `Tethys Portal Configuration`_                              |
+---------------------------+------------------------------------------------------------------------------------------+
| RECAPTCHA_PUBLIC_KEY      | Public key for Google ReCaptcha. Required to enable ReCaptcha on the login screen.       |
|                           | See RECAPTCHA_PUBLIC_KEY in `Tethys Portal Configuration`_                               |
+---------------------------+------------------------------------------------------------------------------------------+
| TAB_TITLE                 | title to display in the web browser tab.                                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| FAVICON                   | icon to display in the web browser tab.                                                  |
+---------------------------+------------------------------------------------------------------------------------------+
| TITLE                     | title of the Tethys Portal.                                                              |
+---------------------------+------------------------------------------------------------------------------------------+
| LOGO                      | the logo/brand image of the Tethys Portal.                                               |
+---------------------------+------------------------------------------------------------------------------------------+
| LOGO_HEIGHT               | height of logo/brand image.                                                              |
+---------------------------+------------------------------------------------------------------------------------------+
| LOGO_WIDTH                | width of logo/brand image.                                                               |
+---------------------------+------------------------------------------------------------------------------------------+
| LOGO_PADDING              | padding around logo/brand image.                                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| LIBRARY_TITLE             | title of the Apps Library page.                                                          |
+---------------------------+------------------------------------------------------------------------------------------+
| PRIMARY_COLOR             | primary color of the Tethys Portal.                                                      |
+---------------------------+------------------------------------------------------------------------------------------+
| SECONDARY_COLOR           | secondary color of the Tethys Portal.                                                    |
+---------------------------+------------------------------------------------------------------------------------------+
| BACKGROUND_COLOR          | background color of the Tethys Portal.                                                   |
+---------------------------+------------------------------------------------------------------------------------------+
| TEXT_COLOR                | primary text color of the Tethys Portal.                                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| TEXT_HOVER_COLOR          | primary text color when hovered over.                                                    |
+---------------------------+------------------------------------------------------------------------------------------+
| SECONDARY_TEXT_COLOR      | secondary text color of the Tethys Portal.                                               |
+---------------------------+------------------------------------------------------------------------------------------+
| SECONDARY_TEXT_HOVER_COLOR| secondary text color when hovered over.                                                  |
+---------------------------+------------------------------------------------------------------------------------------+
| COPYRIGHT                 | the copyright text to display in the footer of the Tethys Portal.                        |
+---------------------------+------------------------------------------------------------------------------------------+
| HERO_TEXT                 | the hero text on the home page.                                                          |
+---------------------------+------------------------------------------------------------------------------------------+
| BLURB_TEXT                | the blurb text on the home page.                                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE1_HEADING          | the home page feature 1 heading.                                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE1_BODY             | the home page feature 1 body text.                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE1_IMAGE            | the home page feature 1 image.                                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE2_HEADING          | the home page feature 2 heading.                                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE2_BODY             | the home page feature 2 body text.                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE2_IMAGE            | the home page feature 2 image.                                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE3_HEADING          | the home page feature 3 heading.                                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE3_BODY             | the home page feature 3 body text.                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| FEATURE3_IMAGE            | the home page feature 3 image.                                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| ACTION_TEXT               | the action text on the home page.                                                        |
+---------------------------+------------------------------------------------------------------------------------------+
| ACTION_BUTTON             | the action button text on the home page.                                                 |
+---------------------------+------------------------------------------------------------------------------------------+

These environment variables can be overwritten in your app docker file.

***************************************
Build your app with Tethys Docker Image
***************************************

You can build your app by extending from the tethys docker image.:
::

    FROM tethysplatform/tethys-core:master

You can overwrite the environment variable of the tethys base image in your app docker file. For example:
::

    ENV ASGI_PROCESSES 1

This line in your docker file will change the environment variable ASGI_PROCESSES from the default value of 4 to 1.

Here is an example of a dockerfile from a tethys app:
::

    # Use our Tethyscore base docker image as a parent image
    FROM tethysplatform/tethys-core:master

    ###############################
    # DEFAULT ENVIRONMENT VARIABLES
    ###############################
    ENV TETHYS_CLUSTER_IP 172.17.0.1
    ENV TETHYS_CLUSTER_USERNAME condor
    ENV TETHYS_CLUSTER_PKEY_FILE ${TETHYS_PERSIST}/keys/condorkey
    ENV TETHYS_CLUSTER_PKEY_PASSWORD please_dont_use_default_passwords
    ENV TETHYS_GS_PROTOCOL http
    ENV TETHYS_GS_HOST 172.17.0.1
    ENV TETHYS_GS_PORT 8181
    ENV TETHYS_GS_PROTOCOL_PUB https
    ENV TETHYS_GS_HOST_PUB 172.17.0.1
    ENV TETHYS_GS_PORT_PUB 443
    ENV TETHYS_GS_USERNAME admin
    ENV TETHYS_GS_PASSWORD geoserver
    ENV APP_DB_HOST ${TETHYS_DB_HOST}
    ENV APP_DB_PORT ${TETHYS_DB_PORT}
    ENV APP_DB_USERNAME ${TETHYS_DB_USERNAME}
    ENV APP_DB_PASSWORD ${TETHYS_DB_PASSWORD}
    ENV CONDORPY_HOME ${TETHYS_HOME}/tethys

    #########
    # SETUP #
    #########
    # Speed up APT installs
    RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
     && echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache \
     && echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/no-check-valid
    # Install APT Package
    RUN apt-get update -qq && apt-get -yqq install gcc libgdal-dev g++ libhdf5-dev > /dev/null
    # Quiet pip installs
    RUN mkdir -p $HOME/.config/pip && echo "[global]\nquiet = True" > $HOME/.config/pip/pip.conf

    ###########
    # INSTALL #
    ###########
    ADD --chown=www:www tethysapp ${TETHYSAPP_DIR}/tethysapp-steem/tethysapp
    ADD --chown=www:www *.py ${TETHYSAPP_DIR}/tethysapp-steem/
    ADD *.ini ${TETHYSAPP_DIR}/tethysapp-steem/
    ADD *.sh ${TETHYSAPP_DIR}/tethysapp-steem/
    ADD install.yml ${TETHYSAPP_DIR}/tethysapp-steem/
    ADD --chown=www:www steem-adapter ${TETHYSAPP_DIR}/steem-adapter

    RUN /bin/bash -c ". ${CONDA_HOME}/bin/activate tethys \
      ; cd ${TETHYSAPP_DIR}/steem-adapter \
      ; python setup.py install \
      ; cd ${TETHYSAPP_DIR}/tethysapp-steem \
      ; python setup.py install"

    #########
    # CHOWN #
    #########
    RUN export NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}') \
      ; find ${TETHYSAPP_DIR} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
      ; find ${WORKSPACE_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
      ; find ${STATIC_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
      ; find ${TETHYS_PERSIST}/keys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
      ; find ${TETHYS_HOME}/tethys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}


    #########################
    # CONFIGURE ENVIRONMENT #
    #########################
    EXPOSE 80


    ################
    # COPY IN SALT #
    ################
    ADD docker/salt/ /srv/salt/


    #######
    # RUN #
    #######
    CMD bash run.sh

The bash script run.sh is executed during run time to finalize the container.

******
Run.sh
******

Run.sh is a bash script used to run `Salt Script`_ and several other tasks when the Tethys docker image is built. Here is what it's trying to accomplish.
* Create Salt Config.
* Set extra ENVs to NGINX.
* Check if Database is ready.
* Run Salt Scripts to establish the necessary set up for the docker image.
* Fix permissions.
* Start supervisor.
* Showing the logs for supervisor, nginx and tethys.

Run.sh also has these following optional arguments:

+---------------------------+------------------------------------------------------------------------------------------+
| Argument                  | Description                                                                              |
+===========================+==========================================================================================+
| --background              | run supervisord in background.                                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| --skip-perm               | skip fixing permissions step.                                                            |
+---------------------------+------------------------------------------------------------------------------------------+
| --db-max-count            | number of attempt to connect to the database. Default is at 24.                          |
+---------------------------+------------------------------------------------------------------------------------------+
| --test                    | only run salt scripts.                                                                   |
+---------------------------+------------------------------------------------------------------------------------------+

***********
Salt Script
***********

Tethys uses `Salt Script`_ to setup the app when the docker container runs. The top file, named top.sls, contains a list of state files to run. These files are pre_tethys.sls, tethyscore.sls and post_app.sls. You can overwrite this file with your own top.sls file for your app. Here is an example of a top.sls file in a tethys app:
::

    base:
      '*':
        - pre_tethys
        - tethyscore
        - tethys_app
        - post_app

In this example, you can put in the salt script to enforce the starting state of your app in the tethys_app.sls file. The rest of the scripts are coming from tethys-core to help finalize the app setup up.
