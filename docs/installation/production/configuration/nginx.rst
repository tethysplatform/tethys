.. _production_nginx_config:

*******************
NGINX Configuration
*******************

**Last Updated:** May 2020

`NGINX <https://www.nginx.com/resources/wiki/>`_ is used as the primary HTTP server for a Tethys Platform deployment. It is used to handle all incoming HTTP traffic and directs it to the Daphne/Django server. It also hosts the static files needed by the apps and Tethys Portal. In this section of the production installation guide, you will generate the NGINX configuration files.

1. Generate the NGINX Configuration
===================================

Generate the NGINX configuration file using the ``tethys gen`` command:

    .. code-block:: bash

        tethys gen nginx --overwrite


2. Review NGINX Configuration
=============================

Review the contents of the NGINX configuration file:

    .. code-block:: bash

        vim <TETHYS_HOME>/tethys_nginx.conf

    .. tip::

        Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

    In particular, verify the following:

        * The ``server_name`` parameter is set to your server's public domain name (e.g. my.example.com).
        * The ``/static`` location matches the location of your ``STATIC_ROOT`` directory.
        * The ``/workspace`` location matches the location of your ``TETHYS_WORKSPACES_ROOT`` directory.

3. Link the Tethys NGINX Configuration
======================================

Create a symbolic link from the ``tethys_nginx.conf`` file to the NGINX configuration directory (:file:`/etc/nginx`):

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/sites-enabled/tethys_nginx.conf
    
    **CentOS**:
    
        .. code-block:: bash
        
            sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/conf.d/tethys_nginx.conf

    .. tip::

        Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

4. Remove the Default NGINX Configuration (Ubuntu Only)
=======================================================

For Ubuntu systems, remove the default NGINX configuration file so NGINX will use the Tethys configuration:

    **Ubuntu**:

        .. code-block:: bash

            sudo rm /etc/nginx/sites-enabled/default

5. Note ``nginx`` User
======================

Get the name of the ``nginx`` user for use in later parts of the installation guide:

    .. code-block:: bash

        grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}'

    Note this user and use it in the following steps where you see ``<NGINX_USER>``.

6. Configure SSL (Recommended)
==============================

SSL is the standard  technology for establishing a secured connection between a web server and a browser. In order to create a secured connection, an SSL certificate and key are needed.

1. Obtain an SSL Certificate

    An SSL certificate can be `self-signed <https://linuxize.com/post/creating-a-self-signed-ssl-certificate/>`_ for testing but should be purchased from a Certificate Authority for a production installation. Some of the top certificate authorities include: Digicert, VertiSign, GeoTrust, Comodo, Thawte, GoDaddy, and Nework Solutions. If your instance of Tethys Platform is part of a larger organization, contact your IT department to determine if an agreement with one of these authorities already exists.

2. Modify NGINX Configuration

    Once a certificate is obtained, it needs to be referenced in the NGINX configuration. The configuration file can be found at :file:`<TETHYS_HOME>/tethys_nginx.conf`.

    Change the ``listen`` port to 443 and enable SSL with the following options:

    .. code-block::

        server {
            listen   443;

            ssl    on;
            ssl_certificate    /<path_to_your_ssl_certs>/your_domain_name.pem; (or bundle.crt)
            ssl_certificate_key    /<path_to_your_ssl_certs>/your_domain_name.key;
            ...
        }

    .. tip::

        If you need your site to be accessible through both secured (https) and non-secured (http) connections, you will need a server block for each type of connection. Simply copy the the server block and paste it below the original server block. Then modify one as show above.

    .. important::

        HTTPS traffic is expected to go through port 443 instead of port 80. hence the server block above listens on 443 instead of 80. Be sure to update your firewall accordingly if applicable (see: :ref:`production_firewall_config`).
