.. _docker_official_image:

**************************************
Tethys Platform Docker Image Reference
**************************************

**Last Updated:** February 2023

Versions and Tags
=================

The official Tethys Docker images are located in the `tethysplatform/tethys-core Docker Hub repository <https://hub.docker.com/r/tethysplatform/tethys-core>`_. Images released are tagged using the following format:

+---------------+------------------------------------------------------------------------------------------------------+
|    Tag        | Description                                                                                          |
+===============+======================================================================================================+
| latest        | latest tagged released                                                                               |
+---------------+------------------------------------------------------------------------------------------------------+
| dev           | latest development build (what's in the main branch)                                                 |
+---------------+------------------------------------------------------------------------------------------------------+
| version       | Specify the version of Tethys image, for example: 4.0.0                                              |
+---------------+------------------------------------------------------------------------------------------------------+

Pull a Pre-Built Image
======================

Use the following commands to download the Tethys image to your machine:

**Latest Release**

.. code-block:: bash

    docker pull tethysplatform/tethys-core:latest

**Latest Development Build**

.. code-block:: bash

    docker pull tethysplatform/tethys-core:dev

**Specific Version**

.. code-block:: bash

    docker pull tethysplatform/tethys-core:4.0.0


Build From Source
=================

Make sure that there isn't already a Docker container or Docker images with the desired name:

.. code-block:: bash

    docker build -t my-tethys-core:latest .

Alternatively, specify the Python version to build Tethys with using the ``PYTHON_VERSION`` build arg:

.. code-block:: bash

    docker build --build-arg PYTHON_VERSION=3.6 -t my-tethys-core:latest .

Run Image
=========

When running the docker you can use the ``-e`` flag to set environment variables. A list of available environment variables is given in a table below.

.. code-block::

    -e TETHYS_CONDA_ENV='tethys'

Example of Run Command:

.. code-block:: bash

    docker run -d -p 80:80 --name tethys-core \
        -e TETHYS_DB_SUPERUSER='tethys_super' \
        -e TETHYS_DB_PASSWORD='please_dont_use_default_passwords' \
        -e TETHYS_DB_PORT='5432' \
        -e TETHYS_SUPERUSER='admin' \
        -e TETHYS_SUPERUSER_PASS='please_dont_use_default_passwords' \
        tethysplatform/tethys-core

.. _docker_official_image_env:

Environment Variables
=====================

Tethys uses environment variables to build and initialize the app. These are the environment variables in Tethys:

Build Arguments
---------------

Use these build arguments with the ``build`` command to customize how the image is built.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| PYTHON_VERSION            | The version of Python to build the Tethys environment with. Defaults to "3.*".           |
+---------------------------+------------------------------------------------------------------------------------------+
| MICRO_TETHYS              | Set to True to use `micro-tethys` environment. Defaults to False.                        |
+---------------------------+------------------------------------------------------------------------------------------+

Important Paths
---------------

These environment variables point to important paths in the container. Changing these will probably break the container.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| TETHYS_HOME               | Path to tethys home directory. Defaults to "/usr/lib/tethys".                            |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_LOG                | Path to directory containing the tethys.log. Defaults to "/var/log/tethys".              |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_PERSIST            | Path to tethys_persist directory. Mount a drive from the host machine to this location to|
|                           | persist runtime data. Defaults to "/var/lib/tethys_persist".                             |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_APPS_ROOT          | Path to directory where app source code should be placed.                                |
|                           | Defaults to "${TETHYS_HOME}/apps".                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| CONDA_HOME                | Path to the conda installation. Defaults to "/opt/conda".                                |
+---------------------------+------------------------------------------------------------------------------------------+
| CONDA_ENV_NAME            | Name of conda environment. Defaults to "tethys".                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| STATIC_ROOT               | Path to the tethys static root folder. This also sets the associated setting in the      |
|                           | :file:`portal_config.yml`. Defaults to "${TETHYS_PERSIST}/static"                        |
+---------------------------+------------------------------------------------------------------------------------------+
| WORKSPACE_ROOT            | Path to the tethys workspaces root folder. This also sets the associated setting in the  |
|                           | :file:`portal_config.yml`. Defaults to "${TETHYS_PERSIST}/workspaces"                    |
+---------------------------+------------------------------------------------------------------------------------------+
| MEDIA_URL                 | URL to be used for tethys media. This also sets the associated setting in the            |
|                           | :file:`portal_config.yml`. Defaults to "/media/"                                         |
+---------------------------+------------------------------------------------------------------------------------------+
| MEDIA_ROOT                | Path to the tethys media root folder. This also sets the associated setting in the       |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_MANAGE             | Path to manage.py file. Defaults to "${TETHYS_HOME}/tethys/tethys_portal/manage.py"      |
+---------------------------+------------------------------------------------------------------------------------------+
| BASH_PROFILE              | The location of bash profile file. Defaults to ".bashrc"                                 |
+---------------------------+------------------------------------------------------------------------------------------+

Database Parameters
-------------------

These environment variables are used to configure the database and database users Tethys Portal will use. If the database doesn't exist, then it will be created using the ``postgres`` user.

+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| Environment Variable     | Description                                                                                                                         |
+==========================+=====================================================================================================================================+
|| POSTGRES_PASSWORD       || Password of the postgres user. Used to initialize the Tethys Portal database.                                                      |
||                         || Defaults to "pass".                                                                                                                |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
|| TETHYS_DB_HOST          || Host of the database server where the primary Tethys Portal database resides.                                                      |
||                         || Defaults to "db".                                                                                                                  |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
|| TETHYS_DB_PORT          || Port of the database server where the primary Tethys Portal database resides.                                                      |
||                         || Defaults to "5432".                                                                                                                |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
|| TETHYS_DB_ENGINE        || Type of database backend to use for the primary Tethys Portal database.                                                            |
||                         || Defaults to "django.db.backends.postgresql".                                                                                       |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TETHYS_DB_NAME           | Name of the primary Tethys Portal database. Defaults to "tethys_platform".                                                          |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
|| TETHYS_DB_USERNAME      || Username of the owner of the primary Tethys Portal database.                                                                       |
||                         || Defaults to "tethys_default".                                                                                                      |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TETHYS_DB_PASSWORD       | Password of the owner of the primary Tethys Portal database. Defaults to "pass".                                                    |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TETHYS_DB_SUPERUSER      | Name of the database superuser used by Tethys Portal. Defaults to "tethys_super".                                                   |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TETHYS_DB_SUPERUSER_PASS | Password of the database superuser used by Tethys Portal. Defaults to "pass".                                                       |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SKIP_DB_SETUP            | Set to True to skip database creation, useful for existing databases configured for Tethys. Defaults to False.                      |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+

Tethys Portal Admin User
------------------------

Use these environment variables to set the username, password, and email of the Tethys Portal admin user that is created by the container.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| PORTAL_SUPERUSER_NAME     | Name for the Tethys portal super user. Empty by default.                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| PORTAL_SUPERUSER_EMAIL    | Email for the Tethys portal super user. Empty by default.                                |
+---------------------------+------------------------------------------------------------------------------------------+
| PORTAL_SUPERUSER_PASSWORD | Password for the Tethys portal super user. Empty by default.                             |
+---------------------------+------------------------------------------------------------------------------------------+

Tethys Settings
---------------

The following environment variables can be used to set some of the Tethys Settings found in the :file:`portal_config.yml`.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| DEBUG                     | The Django DEBUG setting. Defaults to False. See :ref:`tethys_configuration`             |
+---------------------------+------------------------------------------------------------------------------------------+
| ALLOWED_HOSTS             | The Django ALLOWED_HOSTS setting. Defaults to "\"[localhost, 127.0.0.1]\"".              |
|                           | See :ref:`tethys_configuration`                                                          |
+---------------------------+------------------------------------------------------------------------------------------+
| CSRF_TRUSTED_ORIGINS      | The Django CSRF_TRUSTED_ORIGINS setting. Defaults to                                     |
|                           | "\"[http://localhost, http://127.0.0.1]\"".                                              |
|                           | See :ref:`tethys_configuration`                                                          |
+---------------------------+------------------------------------------------------------------------------------------+
| BYPASS_TETHYS_HOME_PAGE   | The home page of Tethys Portal redirects to the Apps Library when True.                  |
|                           | Defaults to False. See :ref:`tethys_configuration`                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| ADD_DJANGO_APPS           | List of the DJANGO APPS in this format "\"[App1, App2]\"". Defaults to "\"[]\"" (Empty)  |
+---------------------------+------------------------------------------------------------------------------------------+
| SESSION_WARN              | Number of seconds in idle until the warning message of session expiration displayed.     | 
|                           | Defaults to "1500" (1500 seconds).                                                       |
+---------------------------+------------------------------------------------------------------------------------------+
| SESSION_EXPIRE            | Number of seconds in idle until the session expired. Defaults to "1800" (1800 seconds).  |
+---------------------------+------------------------------------------------------------------------------------------+
| QUOTA_HANDLERS            | A list of Tethys ResourceQuotaHandler classes to load in this format "\"[RQ1, RQ2]\"".   |
|                           | Defaults to "\"[]\"" (Empty).                                                            |
|                           | See RESOURCE_QUOTA_HANDLERS in :ref:`tethys_configuration`                               |
+---------------------------+------------------------------------------------------------------------------------------+
| DJANGO_ANALYTICAL         | The Django Analytical configuration settings for enabling analytics services on the      |
|                           | Tethys Portal in this format "\"{CLICKY_SITE_ID:123}\"". Defaults to "\"{}}\"" (Empty).  |
|                           | Tethys Portal. See ANALYTICS_CONFIGS in :ref:`tethys_configuration`                      |
+---------------------------+------------------------------------------------------------------------------------------+
| ADD_BACKENDS              | The Django AUTHENTICATION_BACKENDS setting in this format "\"[Backend1, Backend2]\""     |
|                           | Defaults to "\"[]\"" (Empty).                                                            |
|                           | See AUTHENTICATION_BACKENDS in :ref:`tethys_configuration`                               |
+---------------------------+------------------------------------------------------------------------------------------+
| OAUTH_OPTIONS             | The OAuth options for Tethys Portal in this format "\"{SOCIAL_AUTH_FACEBOOK_KEY:123}\""  |
|                           | Defaults to "\"{}}\"" (Empty).                                                           |
|                           | Tethys Portal. See OATH_CONFIGS in :ref:`tethys_configuration`                           |
+---------------------------+------------------------------------------------------------------------------------------+
| CHANNEL_LAYERS_BACKEND    | The Django Channel Layers backend. Default to "channels.layers.InMemoryChannelLayer"     |
+---------------------------+------------------------------------------------------------------------------------------+
| CHANNEL_LAYERS_CONFIG     | The Django Channel Layers configuration if a layer other than the default is being used. |
|                           | Defaults to "\"{}}\"" (Empty).                                                           |
|                           | For example: "\"{'hosts':[{'host':\ 'localhost',\ 'port':\ 6379}]}\""                    |
+---------------------------+------------------------------------------------------------------------------------------+
| RECAPTCHA_PRIVATE_KEY     | Private key for Google ReCaptcha. Required to enable ReCaptcha on the login screen.      |
|                           | See RECAPTCHA_PRIVATE_KEY in :ref:`tethys_configuration`                                 |
+---------------------------+------------------------------------------------------------------------------------------+
| RECAPTCHA_PUBLIC_KEY      | Public key for Google ReCaptcha. Required to enable ReCaptcha on the login screen.       |
|                           | See RECAPTCHA_PUBLIC_KEY in :ref:`tethys_configuration`                                  |
+---------------------------+------------------------------------------------------------------------------------------+
| OTHER_SETTINGS            | A catch all for adding other Tethys or Django settings. Should be set as if passing      |
|                           | arguments to the :ref:`tethys_settings_cmd`, (e.g. "--set BOKEH_RESOURCES inline").      |
+---------------------------+------------------------------------------------------------------------------------------+

NGINX Settings
--------------

These settings are used to configure the NGINX process that is running inside the container.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| CLIENT_MAX_BODY_SIZE      | client_max_body_size parameter for nginx config. Defaults to 75M.                        |
+---------------------------+------------------------------------------------------------------------------------------+
| NGINX_PORT                | Port that NGINX binds to. Defaults to "80".                                              |
|                           | Note: This is the port you should expose on your container.                              |
+---------------------------+------------------------------------------------------------------------------------------+
| TETHYS_PORT               | Internal port Tethys is hosted on. Defaults to "8000".                                   |
|                           | Note: This port is only used inside the container by NGINX.                              |
+---------------------------+------------------------------------------------------------------------------------------+

Daphne Settings
---------------

These settings are used to configure the Daphne processes that are running inside the container.

+---------------------------+------------------------------------------------------------------------------------------+
| Environment Variable      | Description                                                                              |
+===========================+==========================================================================================+
| ASGI_PROCESSES            | The maximum number of asgi worker processes. Defaults to 1.                              |
+---------------------------+------------------------------------------------------------------------------------------+

Tethys Portal Site Settings
---------------------------

Environment variables can be set to customize the theme and content of the Tethys Portal. The environment variables are the same as the Portal Config Yaml Key for site settings (see :ref:`Tethys Portal Configuration: Site Settings <tethys_configuration_site_settings>`).



.. _docker_official_run_script:

Run.sh
======

The primary entrypoint for the Tethys Platform container is the `run.sh <https://github.com/tethysplatform/tethys/blob/main/docker/run.sh>`_ bash script. It performs the following tasks:

* Checks and waits for the database to be ready
* Applies Salt State files to initialize Tethys Portal and the apps
* Sets file permissions
* Starts supervisor
* Shows the logs for supervisor, nginx and tethys

Run.sh also has these following optional arguments:

+---------------------------+------------------------------------------------------------------------------------------+
| Argument                  | Description                                                                              |
+===========================+==========================================================================================+
| --background              | Run supervisord in background.                                                           |
+---------------------------+------------------------------------------------------------------------------------------+
| --skip-perm               | Skip fixing permissions step.                                                            |
+---------------------------+------------------------------------------------------------------------------------------+
| --db-max-count            | Number of attempt to connect to the database. Default is at 24.                          |
+---------------------------+------------------------------------------------------------------------------------------+
| --test                    | Only run salt scripts and exit.                                                          |
+---------------------------+------------------------------------------------------------------------------------------+

For example, to run the :file:`run.sh` script with one of the options, override the default command as follows:

.. code-block::

    sudo docker run -it tethysplatform/tethys-core /bin/bash -c ". run.sh --test"


.. _docker_official_salt:

Salt Scripts
============

.. _`Salt State files`: https://docs.saltproject.io/salt/user-guide/en/latest/topics/states.html
.. _`top.sls`: https://github.com/tethysplatform/tethys/blob/main/docker/salt/top.sls

Tethys uses `Salt State files`_ to perform runtime initialization of the container. The file, named `top.sls`_, contains a list of state files to run and the order in which to run them. These files are ``pre_tethys.sls``, ``tethyscore.sls`` and ``post_app.sls``. You can override this file with your own ``top.sls`` file to insert additional salt state files for your app (see: :ref:`docker_salt_state`).

Salt Script Description
-----------------------

.. _`pre_tethys.sls`: https://github.com/tethysplatform/tethys/blob/main/docker/salt/pre_tethys.sls
.. _`tethyscore.sls`: https://github.com/tethysplatform/tethys/blob/main/docker/salt/tethyscore.sls
.. _`post_app.sls`: https://github.com/tethysplatform/tethys/blob/main/docker/salt/post_app.sls

`pre_tethys.sls`_:

* Create static workspace and root for tethys.

`tethyscore.sls`_:

* Generate tethys settings.
* Generate NGINX service.
* Generate ASGI service.
* Prepare database for tethys.

`post_app.sls`_:

* Persist portal_config.yaml.
* Persist workspace and static data of the app.
* Persist and link NGINX and ASGI for the app.

Source Code
===========

* `Dockerfile <https://github.com/tethysplatform/tethys/blob/main/Dockerfile>`_
* `run.sh`_
* `pre_tethys.sls`_
* `tethyscore.sls`_
* `post_app.sls`_
* `top.sls`_
