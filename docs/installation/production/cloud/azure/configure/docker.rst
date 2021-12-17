.. _azure_vm_config_docker:

************************
Enable Docker (Optional)
************************

**Last Updated:** November 2021

If you would like to use Docker to start supporting services such as THREDDS or GeoServer, you'll need to start the Docker service and enable it so that it will start automatically in the future. The following tutorial demonstrates how to enable Docker and install THREDDS and GeoServer using the ``tethys docker`` command.

Enable Docker
=============

Enabling Docker to start automatically can be done as follows:

.. code-block::

    sudo systemctl enable --now docker

THREDDS
=======

The recommended pattern for installing THREDDS on the Azure virtual machine is as follows:

Create New Docker Container
---------------------------

1. Create a new THREDDS Docker container using the ``tethys docker`` command:

    .. code-block::

        tethys docker init -c thredds

2. Provide appropriate values to the prompts with the following considerations:

    * Use a secure password for the ``TDM Password`` field.
    * Specify the hostname of the VM for ``TDS Host``.
    * Do no specify values greater than the amount of memory available to the VM for the ``Heap Size`` variables.

3. Bind the THREDDS data directory to the host when prompted and specify :file:`/opt/tethys/data/thredds` as the location.

4. Start the THREDDS server:

    .. code-block::

        tethys docker start -c thredds

5. Open the :file:`$TETHYS_HOME/config/tethys_nginx.conf` and add an entrypoint for the THREDDS server to the ``server`` section as follows:

    .. code-block::
        :emphasize-lines: 15-21

        # tethys_nginx.conf

        # the upstream component nginx needs to connect to
        upstream channels-backend {
            server 127.0.0.1:8000;
        }

        # configuration of the server
        server {
            # the port your site will be served on
            listen      80;

            ...

            # Thredds Location
            location ~/thredds(.*)$ {
                proxy_set_header X-Real-IP  $remote_addr;
                proxy_set_header X-Forwarded-For $remote_addr;
                proxy_set_header Host $host;
                proxy_pass http://127.0.0.1:8383/thredds$1$is_args$args;
            }

            location @proxy_to_app {
                proxy_pass http://channels-backend;

                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                proxy_redirect off;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Host $server_name;
            }
        }

6. Restart the NGINX server:

    .. code-block::

        sudo systemctl restart nginx

7. Access the THREDDS server at the following URL: http://<domain_name>/thredds

Create Tethys Service
---------------------

Now that you have a working THREDDS server, create a Tethys Service for apps to use:

1. Log in to the Tethys Portal with an admin account.

2. Select **Site Admin** from the dropdown menu at the top-right.

3. Click on the **Spatial Dataset Services** link under the **TETHYS SERVICES** section.

4. Click on the **ADD SPATIAL DATASET SERVICE** button.

5. Fill the form out as follows:

    * **Name**: A descriptive name for the service (e.g.: <domain_name>_thredds)
    * **Engine**: THREDDS
    * **Endpoint**: http://<domain_name>/thredds
    * **Public Endpoint**: http://<domain_name>/thredds
    * **Apikey**: <leave blank>
    * **Username**: <leave blank>
    * **Password**: <leave blank>

6. Press the **SAVE** button to save the service.

Add Data
--------

Add datasets to the THREDDS server by adding it to the :file:`$TETHYS_HOME/data/thredds` directory. Then edit/add catalog configuration files in the same location. Refer to the :ref:`tutorial_thredds_primer` tutorial for an overview of working with THREDDS.

Start/Stop/Restart
------------------

Start, stop, and restart the THREDDS container using either the ``tethys docker`` commands:

.. code-block::

    tethys docker [start|stop|restart] -c thredds

or the native ``docker`` commmands:

.. code-block::

    docker [start|stop|restart] tethys_thredds

GeoServer
=========

The recommended pattern for installing GeoServer on the Azure virtual machine is as follows:

Create New Docker Container
---------------------------

1. Create a new GeoServer Docker container using the ``tethys docker`` command:

    .. code-block::

        tethys docker init -c geoserver

2. Provide appropriate values to the prompts with the following considerations:

    * Number of GeoServer Instances: no more than number of processors on VM
    * Number of GeoServer Instances with REST API Enabled: 1 is recommended
    * Specify number of processors and set to number of processors VM has
    * Default timeout value is ok
    * Max memory is for each GeoServer instance (e.g. specifying 500 MB for 2 GeoServer instances would be 1 GB total).
    * Min memory is for each GeoServer instance (e.g. specifying 500 MB for 2 GeoServer instances would be 1 GB total).

3. Bind the GeoServer data directory to the host when prompted and specify :file:`/opt/tethys/data/geoserver` as the location.

4. Start the GeoServer server:

    .. code-block::

        tethys docker start -c geoserver

5. Open the :file:`$TETHYS_HOME/config/tethys_nginx.conf` and add an entrypoint for the GeoServer server to the ``server`` section as follows:

    .. code-block::
        :emphasize-lines: 15-21

        # tethys_nginx.conf

        # the upstream component nginx needs to connect to
        upstream channels-backend {
            server 127.0.0.1:8000;
        }

        # configuration of the server
        server {
            # the port your site will be served on
            listen      80;

            ...

            # GeoServer Location
            location ~/geoserver(.*)$ {
                proxy_set_header X-Real-IP  $remote_addr;
                proxy_set_header X-Forwarded-For $remote_addr;
                proxy_set_header Host $host;
                proxy_pass http://127.0.0.1:8181/geoserver$1$is_args$args;
            }

            location @proxy_to_app {
                proxy_pass http://channels-backend;

                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                proxy_redirect off;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Host $server_name;
            }
        }

6. Restart the NGINX server:

    .. code-block::

        sudo systemctl restart nginx

7. Access the GeoServer server at the following URL: http://<domain_name>/geoserver

Open Port 8181
--------------

Open port 8181 for the Azure VM as follows:

a. Navigate to the Overview page for the VM Resource.
b. Click on **Networking** in left navigation panel.
c. Click on the **Add inbound port rule** button.
d. Fill out the **Add inbound security rule** form as follows:

    * **Source**: Any
    * **Source port ranges**: *
    * **Destination**: Any
    * **Service**: Custom
    * **Destination port ranges**: 8181
    * **Protocol**: TCP
    * **Action**: Allow
    * **Priority**: <use_default>
    * **Name**: GeoServer
    * **Description**: <leave_blank>

e. Press the **Add** button.

Create Tethys Service
---------------------

Now that you have a working GeoServer server, create a Tethys Service for apps to use:

1. Log in to the Tethys Portal with an admin account.

2. Select **Site Admin** from the dropdown menu at the top-right.

3. Click on the **Spatial Dataset Services** link under the **TETHYS SERVICES** section.

4. Click on the **ADD SPATIAL DATASET SERVICE** button.

5. Fill the form out as follows:

    * **Name**: A descriptive name for the service (e.g.: <domain_name>_geoserver)
    * **Engine**: GeoServer
    * **Endpoint**: http://<domain_name>/geoserver
    * **Public Endpoint**: http://<domain_name>/geoserver
    * **Apikey**: <leave blank>
    * **Username**: admin
    * **Password**: geoserver

6. Press the **SAVE** button to save the service.

Start/Stop/Restart
------------------

Start, stop, and restart the GeoServer container using either the ``tethys docker`` commands:

.. code-block::

    tethys docker [start|stop|restart] -c geoserver

or the native ``docker`` commmands:

.. code-block::

    docker [start|stop|restart] tethys_geoserver

What about the PostGIS Docker?
==============================

You may be wondering why there aren't instructions for the PostGIS Docker container? The PostGIS docker container is a PostgreSQL server with the PostGIS extension installed. In the Azure Tethys Platform VM image, the system packages of PostgreSQL and the PostGIS extension are both installed. It should not be necessary to use the PostGIS Docker.
