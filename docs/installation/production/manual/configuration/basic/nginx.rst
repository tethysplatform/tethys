.. _production_nginx_config:

*******************
NGINX Configuration
*******************

**Last Updated:** October 2024

`NGINX <https://docs.nginx.com>`_ is used as the primary HTTP server for a Tethys Portal deployment. It is used to handle all incoming HTTP traffic and directs it to the Daphne/Django server. It also hosts the static files needed by the apps and Tethys Portal. In this section of the production installation guide, you will generate the NGINX configuration files.

.. note::

    Skip this section if you are using Apache as your primary HTTP server. See :ref:`production_apache_config` for Apache configuration.

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
        * The ``/media`` location matches the location of your ``MEDIA_ROOT`` directory.

3. Link the Tethys NGINX Configuration
======================================

Create a symbolic link from the ``tethys_nginx.conf`` file to the NGINX configuration directory (:file:`/etc/nginx`):

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/sites-enabled/tethys_nginx.conf
    
    **Rocky Linux**:
    
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

Most browsers are becoming more restrictive on sites that are not secure. It is highly recommended that you obtain an SSL/TLS certificate and setup HTTPS. For more details see: :ref:`https_config`.
