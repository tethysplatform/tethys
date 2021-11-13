.. _azure_vm_config:

******************
Configure Azure VM
******************

**Last Updated:** Nov 2021

This tutorial will guide you through the configuration you **must** do after first creating the Azure virtual machine (VM) to ensure your Tethys server secure. It also contains suggestions for additional configuration you may want to do such as set up SSL, link with a domain name, and customize the look and feel of your Tethys Portal.

Change Secret Key
=================

The :file:`portal_config.yml` has been configured with a default ``SECRET_KEY`` that should be changed. Use a tool like `RandomKeygen <https://randomkeygen.com/>`_ to generate a new key (e.g.: CodeIgniter Encryption Key or 256-bit WEP Key). Update the ``SECRET_KEY`` value as follows:

.. code-block::

    tethys settings --set SECRET_KEY <new_key>

Restart the Tethys service afterward:

.. code-block::

    sudo systemctl restart tethys

Change Passwords
================

All user accounts have default passwords that should be changed to secure passwords soon after creating the VM. Use a password generator like `xkpasswd <https://xkpasswd.net/s/>`_ or similar to create strong and unique passwords for the following accounts:

* Tethys User Account
* Tethys Portal Admin User
* Database Users (postgres, tethys_default, tethys_super)

.. warning::

    Failure to change the passwords on your Tethys Portal server will make it vulnerable to attack! Do not keep the default passwords!

Tethys User
-----------

If you did not change the password of the ``tethys`` user in the :ref:`azure_vm_orientation` tutorial, do so now:

.. code-block::

    sudo passwd tethys

Database Users
--------------

Change the passwords for the database users as follows:

1. Start ``psql`` as the ``postgres`` user:

    .. code-block::

        sudo su - postgres -c psql

2. Use ``ALTER USER`` queries to change the passwords:

    .. code-block::

        ALTER USER <user_name> WITH PASSWORD '<new_password>';

3. Quit ``psql``:

    .. code-block::

        \q

4. Update Tethys ``portal_config.yml``:

    .. code-block::

        tethys settings --set DATABASES.default.PASSWORD <tethys_default_password>

5. Restart the `tethys` service to apply the changes to ``portal_config.yml``:

    .. code-block::

        sudo systemctl restart tethys.service

Tethys Portal Admin
-------------------

Create a new portal admin account and delete the default account as follows:

1. Run the ``createsuperuser`` command:

    .. code-block::

        tethys db createsuperuser --pn <username> --pe <email> --pp <password>

2. Log in to the Tethys Portal with the new admin account.

3. Select **Site Admin** from the dropdown menu at the top-right.

4. Click on the **Users** link under the **AUTHENTICATION AND AUTHORIZATION** section.

5. Check the box next to the **admin** user and

6. Select **Delete selected users** from the **Actions** dropdown and press the **Go** button.

.. figure:: ../../../../images/production/azure/configure--delete-admin.png
    :width: 800px
    :alt: Delete the default admin user account

    **Figure 1.** Delete the default admin user account.

Customize Tethys Portal
=======================

Customize the theme and content of the Tethys Portal to reflect your organization brand and theme guidelines. Follow the :ref:`Customize Portal Theme <production_customize_theme>` configuration guide to learn how to do this.

Custom images, CSS, and JavaScript should be added to a new directory in the :file:`$TETHYS_HOME/static` directory (e.g.: :file:`$TETHYS_HOME/static/custom_theme`. These can then be referenced in the settings via the name of the new directory (e.g.: :file:`custom_theme/images/custom_logo.png`.

.. figure:: ../../../../images/production/azure/configure--custom-theme.png
    :width: 800px
    :alt: Tethys Portal with a custom theme.

    **Figure 2.** Tethys Portal with a custom theme.

Assign Domain Name
==================

A domain name is the text that users enter in a web browser to visit a website (e.g. google.com). Behind the scenes, this text is mapped to the IP address of the server, which is the unique numeric address that can be used to locate your website (e.g ``20.109.16.186``). VMs on Azure can be assigned a generic, Azure supplied, domain name (e.g.: ``my-first-tethys.westus2.cloudapp.azure.com``) or a custom domain (e.g. ``myfirsttethys.org``). With either option there are a few configuration steps that need to be performed in Tethys assigning the domain name.

Generic Domain Name
-------------------

Create a generic, Azure supplied, domain name as follows:

1. Navigate to the Overview page for the VM Resource.
2. Locate the **DNS name** field in the **Essentials** section.
3. Follow the link next to **DNS name**. It will either be "Not configured" or the domain name if previously configured.
4. Enter a **DNS name label**. This is labeled as optional, but it is actually required to enable the generic domain.
5. Press the **Save** button to enable the domain name.

.. figure:: ../../../../images/production/azure/configure--generic-domain-name.png
    :width: 800px
    :alt: Screenshot of the domain name configuration page for an Azure VM

    **Figure 3.** Screenshot of the domain name configuration page for an Azure VM.

Custom Domain Name
------------------

Assigning a custom domain name is a little more involved and depends on how you obtain the domain name.

1. Acquire a domain name if you don't have one to use already: `Google: Domain Name <https://www.google.com/search?q=domain+name>`_
2. Make sure the Public IP address assigned to the Azure VM is static:

    a. Navigate to the Overview page for the VM Resource.
    b. Locate the **Public IP address** field in the **Essentials** section.
    c. Click on the IP address link.
    d. Under **IP address assignment** select the **Static** radio option (see Figure 3).
    e. Click **Save** to save the changes.

3. Create an A-name record that associates the domain name with the public IP address of the Azure VM. The company you bought the domain name from will usually provide a way to do this. If your domain name belongs to your organization, you will need to contact your IT department to find out how this is to be done.

For more information about creating a custom domain name for Azure VMs read the following article: `Add Custom Domain to Azure VM or resource <https://docs.microsoft.com/en-us/azure/virtual-machines/custom-domain>`_.

Tethys Configuration
--------------------

After assigning a domain name to the Azure VM, generic or custom, add it to the configuration of Tethys Platform in two places:

NGINX Configuration
+++++++++++++++++++

1. Open ``$TETHYS_HOME/config/tethys_nginx.conf`` in your favorite command line text editor (e.g. vim or nano).

2. Set the ``server_name`` parameter to the domain name:

    .. code-block::
        :emphasize-lines: 13

        # tethys_nginx.conf

        # the upstream component nginx needs to connect to
        upstream channels-backend {
            server 127.0.0.1:8000;
        }

        # configuration of the server
        server {
            # the port your site will be served on
            listen      80;
            # the domain name it will serve for
            server_name <domain_name>; # substitute your machine's IP address or FQDN
            ...

3. Restart the NGINX service

    .. code-block::

        sudo systemctl restart nginx.service


Tethys Portal Configuration
+++++++++++++++++++++++++++

1. Open ``$TETHYS_HOME\portal_config.yml`` using your favorite command line text editor (e.g. vim or nano).

2. Add the domain name as another item under the ``ALLOWED_HOSTS`` setting.

3. Remove the ``'*'`` entry if it is still listed in ``ALLOWED_HOSTS`` setting.

4. Restart the Tethys service

    .. code-block::

        sudo systemctl restart tethys.service

Configure HTTPS
===============

HTTPS is the secure way of serving websites that won't compromise the data of the website or your users. Most web browsers will warn users when they are using a site that is not secured with HTTPS, which can be a deterrent for some users. Follow the :ref:`Configure HTTPS <https_config>` tutorial to learn how to configure your Azure portal for HTTPS.

Setup Forgotten Password Recovery
=================================

To use forgotten password recovery feature of Tethys Portal, it needs to be configured with an email service. Follow the :ref:`Forgotten Password Recovery <setup_email_capabilities>` tutorial to enable this feature.


Enable Docker (optional)
========================

If you would like to use Docker to start supporting services such as THREDDS or GeoServer, you'll need to start the Docker service and enable it so that it will start automatically in the future:

.. code-block::

    sudo systemctl enable --now docker

THREDDS
-------

The recommended pattern for installing THREDDS on the Azure virtual machine is as follows:

Create New Docker Container
+++++++++++++++++++++++++++

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
+++++++++++++++++++++

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
++++++++

Add datasets to the THREDDS server by adding it to the :file:`$TETHYS_HOME/data/thredds` directory. Then edit/add catalog configuration files in the same location. Refer to the :ref:`tutorial_thredds_primer` tutorial for an overview of working with THREDDS.

Start/Stop/Restart
++++++++++++++++++

Start, stop, and restart the THREDDS container using either the ``tethys docker`` commands:

.. code-block::

    tethys docker [start|stop|restart] -c thredds

or the native ``docker`` commmands:

.. code-block::

    docker [start|stop|restart] tethys_thredds

GeoServer
---------

The recommended pattern for installing GeoServer on the Azure virtual machine is as follows:

Create New Docker Container
+++++++++++++++++++++++++++

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

Create Tethys Service
+++++++++++++++++++++

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
++++++++++++++++++

Start, stop, and restart the GeoServer container using either the ``tethys docker`` commands:

.. code-block::

    tethys docker [start|stop|restart] -c geoserver

or the native ``docker`` commmands:

.. code-block::

    docker [start|stop|restart] tethys_geoserver