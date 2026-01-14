.. _docker_run_with_compose:

***********************
Run with Docker Compose
***********************

**Last Updated:** February 2023

With the image built, its now time to run the container. Tethys Portal requires at least a database and a Redis server to run. The custom image that we have built will also require a THREDDS server. Both the database and THREDDS server can be created using a Docker images as well, but that means starting multiple Docker images with one that depends on the others. The easiest way to manage a multi-container deployment like this is with `Docker Compose <https://docs.docker.com/compose/>`_.

Docker Compose Overview
=======================

Docker Compose is best described by their documentation:

    Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration. [#f1]_

A simple Docker Compose YAML (:file:`docker-compose.yml`) for a Django web application looks like this:

.. code-block:: yaml

    services:
      db:
        image: postgres
        volumes:
          - ./data/db:/var/lib/postgresql/data
        environment:
          - POSTGRES_DB=postgres
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
      web:
        build: .
        command: python manage.py runserver 0.0.0.0:8000
        volumes:
          - .:/code
        ports:
          - "8000:8000"
        depends_on:
          - db

Starting all the services in a Docker Compose YAML is done using the following command:

.. code-block:: bash

    docker compose up

.. note::

    In older version of Docker Compose, the command is:

    .. code-block:: bash

        docker-compose up

Here is a list of resources that you can use to learn more about Docker Compose:

* `Docker Compose Features List <https://docs.docker.com/compose/intro/features-uses/>`_
* `Compose File Reference | Docker Documentation <https://docs.docker.com/reference/compose-file/>`_
* `Compose Command Reference | Docker Documentation <https://docs.docker.com/reference/cli/docker/compose/>`_

Create Docker Compose Recipe
============================

Use the following instructions to create a Docker Compose file for the custom Tethys Portal image that you created in the previous tutorial.

1. Create Data Directories
--------------------------

Docker allows directories from the host machine to be mounted into the containers. This is most often used to provide easy access to container data, configuration files, and logs.

a. Create the following directories in :file:`tethys_portal_docker` directory:
    .. code-block:: bash

        mkdir -p data/db
        mkdir -p data/tethys
        mkdir -p data/thredds
        mkdir -p config/thredds
        mkdir -p keys/gee
        mkdir -p logs/tethys
        mkdir -p logs/thredds/thredds
        mkdir -p logs/thredds/tomcat

b. Download the default :file:`tomcat-users.xml` file from the `Unidata/thredds-docker GitHub repository <https://github.com/Unidata/thredds-docker>`_:
    * :download:`tomcat-users.xml <https://raw.githubusercontent.com/Unidata/thredds-docker/master/files/tomcat-users.xml>`

    .. note::

        After clicking on the link above, you may need to right-click and select **Save as...** to download the file. Save the file as :file:`tomcat-users.xml`.

c. Add the :file:`tomcat-users.xml` file to the :file:`config/thredds` directory.

d. Create a service account key as described in Step 1 of the :ref:`tutorial_google_earth_engine_service_account` tutorial.

e. Place the ``JSON`` file containing the service account key in the :file:`keys/gee` directory.

2. Create Docker Compose File
-----------------------------

.. _`image`: https://docs.docker.com/reference/compose-file/services/#image
.. _`build`: https://docs.docker.com/reference/compose-file/services/#build
.. _`restart`: https://docs.docker.com/reference/compose-file/services/#restart
.. _`depends_on`: https://docs.docker.com/reference/compose-file/services/#depends_on
.. _`networks (services)`: https://docs.docker.com/reference/compose-file/services/#networks
.. _`ports`: https://docs.docker.com/reference/compose-file/services/#ports
.. _`env_file`: https://docs.docker.com/reference/compose-file/services/#env_file
.. _`environment`: https://docs.docker.com/reference/compose-file/services/#environment
.. _`volumes`: https://docs.docker.com/reference/compose-file/services/#volumes

Create a new file called :file:`docker-compose.yml` in the :file:`tethys_portal_docker` directory:

.. code-block:: bash

    touch docker-compose.yml

Add the following contents to the :file:`docker-compose.yml`:

.. code-block:: yaml

    services:
      db:
      thredds:
      redis:
      web:
    networks:
      internal:
        internal: true
      external:

**Explanation**

* `services <https://docs.docker.com/reference/compose-file/services/>`_: This section contains a list of services or containers and configuration for each. Three stubs are defined for the four containers that need to be defined for the custom image: ``db``, ``thredds``, ``redis``, and ``web``.
* `networks (top-level) <https://docs.docker.com/reference/compose-file/networks/>`_: Networks that should be created. In this example two networks are defined, one that is internal, meaning only accessible to the containers that are connected to it, and one that is external, to allow access to the web container for example. To learn more about Docker networks, see: `Networking overview | Docker Documentation <https://docs.docker.com/engine/network/>`_.

3. Define Database Service
--------------------------

.. _`postgis/postgis | Docker Hub`: https://hub.docker.com/r/postgis/postgis
.. _`postgres | Docker Hub`: https://hub.docker.com/_/postgres

Tethys Platform works best with a PostgreSQL database and the apps will require one with the PostGIS extension installed. As such, the ``db`` service will be created using the official PostGIS image on Docker Hub: `postgis/postgis | Docker Hub`_. This image extends the official PostgreSQL image on Docker Hub (`postgres | Docker Hub`_), adding the PostGIS extension.

Add the following definition for the ``db`` service in the :file:`docker-compose.yml`:

.. code-block:: yaml

    db:
      image: postgis/postgis:latest
      restart: always
      networks:
        - "internal"
      ports:
        - "5432:5432"
      env_file:
        - ./env/db.env
      volumes:
        - ./data/db:/var/lib/postgresql/data

**Explanation**

* `image`_: The Docker container image used to run the service.
* `restart`_: Set the restart policy for the container in the event of an outage or error.
* `networks (services)`_: Networks for the container to join. The database does not need to be accessible externally, so it is only connected to the ``internal`` network.
* `ports`_: Ports to expose on the container (``<host>:<container>``).
* `env_file`_: A file containing the environment variables to create for the container. Environment variables often contain sensitive information that should not be committed with the :file:`docker-compose.yml`. The :file:`db.env` file will be created in Step 7.
* `volumes`_: Mount directories from the host into the container or create Docker-managed named volumes. Volumes allow you to preserve data that would otherwise be lost when the container is removed. The syntax shown here is: ``<host_dir>:<container_dir>``.
    * ``./data/db:/var/lib/postgresql/data``: The primary data directory for PostgreSQL database. This directory contains the data and configuration files for the database.

4. Define THREDDS Service
-------------------------

.. _`unidata/thredds-docker | Docker Hub`: https://hub.docker.com/r/unidata/thredds-docker

The THREDDS Tutorial application requires a THREDDS service. Although this could be an external THREDDS service, as is used in the tutorial, a local THREDDS service will be created and linked in the Compose file for illustration. The ``thredds`` service will be created using the  THREDDS Docker image developed by Unidata and available on Docker Hub: `unidata/thredds-docker | Docker Hub`_.

Add the following definition for the ``thredds`` service in the :file:`docker-compose.yml`:

.. code-block:: yaml

    thredds:
      image: unidata/thredds-docker:5.6
      restart: always
      networks:
        - "internal"
        - "external"
      ports:
        - "8080:8080"
      env_file:
        - ./env/thredds.env
      volumes:
        - ./data/thredds/:/usr/local/tomcat/content/thredds
        - ./logs/thredds/tomcat/:/usr/local/tomcat/logs/
        - ./logs/thredds/thredds/:/usr/local/tomcat/content/thredds/logs/
        - ./config/thredds/tomcat-users.xml:/usr/local/tomcat/conf/tomcat-users.xml

**Explanation**

* `image`_: The Docker container image used to run the service.
* `restart`_: Set the restart policy for the container in the event of an outage or error.
* `networks (services)`_: Networks for the container to join. The THREDDS server is a map server and needs to be externally accessible, so it is added to both the ``internal`` and ``external`` networks.
* `ports`_: Ports to expose on the container (``<host>:<container>``).
* `env_file`_: A file containing the environment variables to create for the container. Environment variables often contain sensitive information that should not be committed with the :file:`docker-compose.yml`. The :file:`thredds.env` file will be created in Step 7.
* `volumes`_: Mount directories from the host into the container or create Docker-managed named volumes. Volumes allow you to preserve data that would otherwise be lost when the container is removed. The syntax shown here is: ``<host_dir>:<container_dir>``.
    * ``./data/thredds/:/usr/local/tomcat/content/thredds``: Main content directory for THREDDS. This directory will contain the data and XML configuration files for THREDDS.
    * ``./logs/thredds/tomcat/:/usr/local/tomcat/logs/``: Logs for Tomcat, the server running THREDDS.
    * ``./logs/thredds/thredds/:/usr/local/tomcat/content/thredds/logs/``: Logs for THREDDS.
    * ``./config/thredds/tomcat-users.xml:/usr/local/tomcat/conf/tomcat-users.xml``: Tomcat user configuration file. Use this file to create user accounts for the THREDDS Data Manager service that is also run inside the container (see: `THREDDS Data Manager (TDM) <https://docs.unidata.ucar.edu/tds/current/userguide/tdm_ref.html>`_ and `Manager App HOW-TO | Tomcat Documentation <https://tomcat.apache.org/tomcat-8.0-doc/manager-howto.html>`_).

5. Define Redis Service
-----------------------

.. _`redis | Docker Hub`: https://hub.docker.com/_/redis

`Redis <https://redis.io/>`_ is an open source, in-memory key-value store that is used by Tethys Platform in production as a message broker for supporting web sockets and other asynchronous capabilities provided by `Django Channels <https://channels.readthedocs.io/en/stable/>`_. The ``redis`` service will be created using the official Redis Docker container image on Docker Hub: `redis | Docker Hub`_.

Add the following definition for the ``redis`` service in the :file:`docker-compose.yml`:

.. code-block:: yaml

    redis:
      image: redis:latest
      restart: always
      networks:
        - "external"
      ports:
        - "6379:6379"

**Explanation**

* `image`_: The Docker container image used to run the service.
* `restart`_: Set the restart policy for the container in the event of an outage or error.
* `networks (services)`_: Networks for the container to join. The Redis server is does not need to be accessed externally, so it is added to only the ``internal`` network.
* `ports`_: Ports to expose on the container (``<host>:<container>``).

6. Define Tethys Service
------------------------

With the service dependencies for the Tethys container defined, we can now implement the service definition for the Tethys container (``web``).

Add the following definition for the ``web`` service in the :file:`docker-compose.yml`:

.. code-block:: yaml

    web:
      image: tethys-portal-docker:latest
      build: .
      restart: always
      depends_on:
        - "db"
        - "thredds"
        - "redis"
      networks:
        - "internal"
        - "external"
      ports:
          - "80:80"
      env_file:
        - ./env/web.env
      volumes:
        - ./data/tethys:/var/lib/tethys_persist
        - ./keys:/var/lib/tethys/keys
        - ./logs/tethys:/var/log/tethys

**Explanation**

* `image`_: The Docker container image used to run the service.
* `build`_: Specify the path to the build context (directory with the :file:`Dockerfile`).
* `restart`_: Set the restart policy for the container in the event of an outage or error.
* `depends_on`_: Specify the dependency between services. In this case the ``db``, ``thredds``, and ``redis`` containers will be started before the ``web`` container.
* `networks (services)`_: Networks for the container to join. The Tethys server needs to be externally accessible, so it is added to both the ``internal`` and ``external`` networks.
* `ports`_: Ports to expose on the container (``<host>:<container>``).
* `env_file`_: A file containing the environment variables to create for the container. Environment variables often contain sensitive information that should not be committed with the :file:`docker-compose.yml`. The :file:`web.env` file will be created in Step 7.
* `volumes`_: Mount directories from the host into the container or create Docker-managed named volumes. Volumes allow you to preserve data that would otherwise be lost when the container is removed. The syntax shown here is: ``<host_dir>:<container_dir>``.
    * ``./data/tethys:/var/lib/tethys_persist``: Main content directory for Tethys Platform. This directory contains the app workspaces, static files, and configuration files including the :file:`portal_config.yml`.
    * ``./log/tethys:/var/log/tethys``: Logs for Tethys.

7. Create Environment Files
---------------------------

Each of the Docker containers can be configured through the environment variables. While it is possible to specify these variables in the :file:`docker-compose.yml` using the `environment`_ key, it is not recommended. This is because environment variables often contain sensitive information like usernames, passwords, and API keys and the :file:`docker-compose.yml` is a file that is often committed to version control repositories. To prevent leaking sensitive information it is recommended that you use environment or ``.env`` files for storing this information and that you do not commit these files.

With that said, certain environment variables need to be defined for the custom Tethys Portal Compose recipe to work. This is often the case, so another pattern that is used is to provide default ``.env`` files that users can copy and modify. The default ``.env`` files are committed to the repository and the copies with sensitive information are not. In this step you will create the default ``.env`` files referenced in the `env_file`_ sections of the :file:`docker-compose.yml`.

a. Create a new :file:`env` directory in the :file:`tethys_portal_docker` directory for storing the ``.env`` files:
    .. code-block:: bash

        mkdir env

b. Create three new empty files in the :file:`env` directory with the same names as those referenced in the `env_file`_ sections of the :file:`docker-compose.yml`:
    .. code-block:: bash

        touch env/db.env env/thredds.env env/web.env

c. Add the following contents to each ``.env`` file:
    **db.env**

    .. code-block:: docker

        # Password of the db admin account
        POSTGRES_PASSWORD=please_dont_use_default_passwords

    .. tip::

        Review documentation on Docker Hub for the PostgreSQL and PostGIS images for an explanation of the environment variables that are available (see: `postgis/postgis | Docker Hub`_ and `postgres | Docker Hub`_).

    .. important::

        **For Production Deployments:**

        For a production deployment, set ``POSTGRES_PASSWORD`` with a secure password (see: :ref:`production_preparation`).


    **thredds.env**

    .. code-block:: docker

        # Password of the TDM admin user
        TDM_PW=please_dont_use_default_passwords

        # FQDN of the server THREDDS is running on
        TDS_HOST=http://localhost

        # Maximum Memory for THREDDS
        THREDDS_XMX_SIZE=4G

        # Minimum Memory for THREDDS
        THREDDS_XMS_SIZE=4G

        # Maximum Memory for TDM
        TDM_XMX_SIZE=6G

        # Minimum Memory for TDM
        TDM_XMS_SIZE=1G

    .. tip::

        Review documentation on Docker Hub for the THREDDS image for an explanation of the environment variables that are available (see: `unidata/thredds-docker | Docker Hub`_).

    .. important::

        **For Production Deployments:**

        Set ``THREDDS_PASSWORD`` with a secure password and set ``TDS_HOST`` to ``SERVER_DOMAIN_NAME`` (see: :ref:`production_preparation`). Set the memory parameters carefully to fit within the memory constraints of your server.

    **web.env**

    .. code-block:: docker

        TERM=xterm

        # Domain name of server should be first in the list if multiple entries added
        ALLOWED_HOSTS="\"[localhost]\""

        # Don't change these parameters
        ASGI_PROCESSES=1
        CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
        CHANNEL_LAYERS_CONFIG="\"{'hosts':[{'host': 'redis', 'port': 6379}]}\""  # Hostname is the name of the service

        # Database parameters
        TETHYS_DB_HOST=db  # Hostname is the name of the service
        TETHYS_DB_PORT=5432
        TETHYS_DB_ENGINE=django.db.backends.postgresql
        TETHYS_DB_NAME=tethys_platform
        TETHYS_DB_USERNAME=tethys_default
        TETHYS_DB_PASSWORD=please_dont_use_default_passwords
        TETHYS_DB_SUPERUSER=tethys_super
        TETHYS_DB_SUPERUSER_PASS=please_dont_use_default_passwords

        # POSTGRES_PASSWORD should be the same as that in the db.env
        POSTGRES_PASSWORD=please_dont_use_default_passwords

        # Default admin account for Tethys Portal
        PORTAL_SUPERUSER_NAME=admin
        PORTAL_SUPERUSER_PASSWORD=please_dont_use_default_passwords
        PORTAL_SUPERUSER_EMAIL=you@email.com

        # App specific settings
        DAM_INVENTORY_MAX_DAMS=50
        EARTH_ENGINE_PRIVATE_KEY_FILE=/var/lib/tethys/keys/gee/some-key.json
        EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL=you@email.com

        # THREDDS parameters
        THREDDS_TUTORIAL_TDS_USERNAME=admin
        THREDDS_TUTORIAL_TDS_PASSWORD=please_dont_use_default_passwords
        THREDDS_TUTORIAL_TDS_PRIVATE_PROTOCOL=http
        THREDDS_TUTORIAL_TDS_PRIVATE_HOST=thredds  # Endpoint backend (Python) will use, hostname is the name of the service
        THREDDS_TUTORIAL_TDS_PRIVATE_PORT=8080
        THREDDS_TUTORIAL_TDS_PUBLIC_PROTOCOL=http
        THREDDS_TUTORIAL_TDS_PUBLIC_HOST=localhost  # Endpoint the frontend (JavaScript) will use
        THREDDS_TUTORIAL_TDS_PUBLIC_PORT=8080

    .. tip::

        For an explanation of all the environment variables provided by the Tethys Platform image see: :ref:`docker_official_image_env`.

    .. important::

        **For Production Deployments:**

        Replace ``localhost`` in the ``ALLOWED_HOSTS`` setting with ``<SERVER_DOMAIN_NAME>`` and set ``TETHYS_DB_USERNAME``, ``TETHYS_DB_PASSWORD``, ``TETHYS_DB_SUPER_USERNAME``, ``TETHYS_DB_SUPERUSER_PASS``,  ``POSTGRES_PASSWORD``, ``PORTAL_SUPERUSER_NAME``, ``PORTAL_SUPERUSER_PASSWORD``, and ``PORTAL_SUPERUSER_EMAIL`` with appropriate values (see: :ref:`production_preparation`).

        Also set the ``DAM_INVENTORY_MAX_DAMS`` setting to the desired maximum number of dams for the Dam Inventory app and set the ``EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL`` to the email address associated with your Google Earth Engine service account and replace the ``some-key.json`` with the name of your keyfile in the ``EARTH_ENGINE_PRIVATE_KEY_FILE`` setting (see: :ref:`tutorial_google_earth_engine_service_account`). Set the ``THREDDS_PASSWORD`` should be set to match ``TDM_PW`` in the :file:`thredds.env`.

8. Update README
----------------

Update the contents of the README with instructions for using the repository and Docker compose recipe by adding the following lines:

.. code-block:: markdown

    # Checkout

    ```
    git clone --recursive-submodules https://github.com/tethysplatform/tethys_portal_docker.git
    ```

    # Build

    ```
    docker compose build web
    ```

    # Run

    1. Create Data Directories

    ```
    mkdir -p data/db
    mkdir -p data/tethys
    mkdir -p data/thredds
    mkdir -p keys/gee
    mkdir -p logs/tethys
    mkdir -p logs/thredds/thredds
    mkdir -p logs/thredds/tomcat
    ```

    2. Acquire a Earth Engine Service Account and Key file (see Step 1 of [Google Earth Engine Service Account](http://docs.tethysplatform.org/en/stable/tutorials/google_earth_engine/part_3/service_account.html)).

    3. Add the Google Earth Engine service account JSON key file to the `keys/gee` directory.

    4. Create copies of the `.env` files in the `env` directory and modify the settings appropriately.

    5. Update `env_file` sections in the `docker-compose.yml` to point to your copies of the `.env` files.

    6. Start containers:

    ```
    docker compose up -d
    ```

9. Commit Changes
-----------------

The contents of the :file:`data`, :file:`logs`, and :file:`keys` directories should not be committed into the Git repository because they contain large amounts of instance-specific data and sensitive information.

a. Create a :file:`.gitignore` file:
    .. code-block:: bash

        touch .gitignore


b. Add the following contents to the :file:`.gitignore` file to omit the contents of these directories from being tracked:
    .. code-block:: text

        data/
        keys/
        logs/

c. Stage changes and commit the changes as follows:
    .. code-block:: bash

        git add .
        git commit -m "Added Docker Compose recipe"

Run Docker Compose Recipe
=========================

Use the following steps to run the :file:`docker-compose.yml` and verify that it works.

1. Start Containers
-------------------

To start the containers run the following command in the directory with the :file:`docker-compose.yml` file (:file:`tethys_portal_docker`):

.. code-block:: bash

    docker compose up -d

.. note::

    In older version of Docker Compose, use ``docker-compose <command>`` instead of ``docker compose <command>``.

2. Check Status
---------------

Check the status of the containers by running this command:

.. code-block:: bash

    docker compose ps

3. Inspect Logs
---------------

It will take several minutes for the Tethys container to start up the first time as it needs to complete the initialization steps in the Salt State files. Monitor the logs for the Tethys container so that you know when it completes as follows:

.. code-block:: bash

    docker compose logs -f web

When the Salt State files have finished running you will get a report like the one below, but until then, there won't be much output. Be patient.

.. code-block:: bash

    tethys_portal_docker-web-1  | Summary for local
    tethys_portal_docker-web-1  | -------------
    tethys_portal_docker-web-1  | Succeeded: 35 (changed=35)
    tethys_portal_docker-web-1  | Failed:     0
    tethys_portal_docker-web-1  | -------------
    tethys_portal_docker-web-1  | Total states run:     35
    tethys_portal_docker-web-1  | Total run time:  147.540 s

Above this summary will be a summary for each of the Salt State steps executed. For example, here is the output from the ``Create_PostGIS_Database_Service`` step:

.. code-block:: bash

    tethys_portal_docker-web-1  | ----------
    tethys_portal_docker-web-1  |           ID: Create_PostGIS_Database_Service
    tethys_portal_docker-web-1  |     Function: cmd.run
    tethys_portal_docker-web-1  |         Name: . /opt/conda/bin/activate tethys && tethys services create persistent -n tethys_postgis -c tethys_super_user:mysupersecretpassword@db:5432
    tethys_portal_docker-web-1  |       Result: True
    tethys_portal_docker-web-1  |      Comment: Command ". /opt/conda/bin/activate tethys && tethys services create persistent -n tethys_postgis -c tethys_super_user:******@db:5432" run
    tethys_portal_docker-web-1  |      Started: 22:56:45.620825
    tethys_portal_docker-web-1  |     Duration: 3718.461 ms
    tethys_portal_docker-web-1  |      Changes:
    tethys_portal_docker-web-1  |               ----------
    tethys_portal_docker-web-1  |               pid:
    tethys_portal_docker-web-1  |                   173
    tethys_portal_docker-web-1  |               retcode:
    tethys_portal_docker-web-1  |                   0
    tethys_portal_docker-web-1  |               stderr:
    tethys_portal_docker-web-1  |               stdout:
    tethys_portal_docker-web-1  |                   ?[94mLoading Tethys Extensions...?[0m
    tethys_portal_docker-web-1  |                   ?[94mLoading Tethys Apps...?[0m
    tethys_portal_docker-web-1  |                   ?[94mTethys Apps Loaded: ?[0mbokeh_tutorial, dam_inventory, earth_engine, postgis_app, thredds_tutorial
    tethys_portal_docker-web-1  |
    tethys_portal_docker-web-1  |                   ?[32mSuccessfully created new Persistent Store Service!?[0m
    tethys_portal_docker-web-1  | ----------

The Salt State report can be incredibly useful for debugging issues when something goes wrong with the portal deployment. Checking them should be your first action when a Tethys Portal doesn't come up as expected.

Press ``CTRL-C`` to exit the ``tethys logs`` command.

4. View Running Portal
----------------------

In a web browser, navigate to web address of the running portal (Figure 1). If using the default configuration, it will be accessible at http://localhost on the host machine. You may also want to view the THREDDS server catalog, which will be running at http://localhost:8080/thredds with the default config.

.. figure:: images/compose--custom-tethys-portal.png
    :width: 800px
    :alt: Screenshot of the running Tethys Portal.

    **Figure 1**: Screenshot of the running Tethys Portal.

5. Review Mounted Directory Contents
------------------------------------

Inspect the contents of the various directories that were mounted into the containers (i.e.: :file:`data`, :file:`logs`, :file:`config`). Notice how the logs for Tethys and THREDDS are easily accessible. As is the :file:`portal_config.yml` (see :file:`data/tehtys/portal_config.yml`). Data can be easily added to the THREDDS server by adding it to the :file:`data/thredds/public` directory and then modifying the :file:`catalog.xml`.

.. tip::

    Use the contents of these directories to debug and make configuration changes as needed. Be sure to restart the affected container after making changes to configuration (see below).

Solution
========

This concludes this portion of the tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethys_portal_docker>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethys_portal_docker
    cd tethys_portal_docker
    git checkout -b docker-compose-solution docker-compose-solution-|version|

Useful Docker Compose Commands
==============================

Login to a Container
--------------------

Sometimes you may need to log in to one of the running containers to debug or modify a config that isn't exposed through the data directories. Use the ``docker compose exec`` command as follow to do so:

.. code-block:: bash

    docker compose exec web -- /bin/bash

When you are done, run the ``exit`` command.

.. tip::

    You can also use the ``exec`` command to run one-off commands inside a container. Just replace the ``/bin/bash`` with the desired command:

    .. code-block:: bash

        docker compose exec web -- ls

Restart Containers
------------------

The containers can be stopped, started, or restarted with the following commands:

.. code-block:: bash

    docker compose stop

.. code-block:: bash

    docker compose start

.. code-block:: bash

    docker compose restart

An individual container can also be controlled using by providing its service name as an argument to these commands:

.. code-block:: bash

    docker compose stop web

.. code-block:: bash

    docker compose start web

.. code-block:: bash

    docker compose restart web

Build
-----

You can use ``docker compose`` to build the custom Tethys image. It will use the value of ``image`` as the tag:

.. code-block:: bash

    docker compose build web

Remove Containers
-----------------

The ``down`` command stops the containers if they are running and removes them:

.. code-block:: bash

    docker compose down

.. caution::

    Be careful with this command. Everything will be removed except for data contained in the directories that were mounted!

Troubleshooting
===============

Google Earth Engine imagery is not displaying
---------------------------------------------

Check the :file:`tethys.log` (:file:`logs/tethys/tethys.log`). Look for an ``ee.ee_exception.EEException`` and follow the instructions.

THREDDS App is Returning a 500 Error
------------------------------------

This is because the THREDDS server doesn't have the data expected.

.. rubric:: Footnotes

.. [#f1] `Overview of Docker Compose | Docker Documentation <https://docs.docker.com/compose/>`_