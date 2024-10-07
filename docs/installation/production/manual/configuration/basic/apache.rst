.. _production_apache_config:

********************
Apache Configuration
********************

**Last Updated:** October 2024

`Apache <https://httpd.apache.org/docs/2.4/>`_ can be used as the primary HTTP server for a Tethys Portal deployment. It is used to handle all incoming HTTP traffic and directs it to the Daphne/Django server. It also hosts the static files needed by the apps and Tethys Portal. In this section of the production installation guide, you will generate the Apache configuration files.

.. note::

    Skip this section if you are using NGINX as your primary HTTP server. See :ref:`production_nginx_config` for NGINX configuration.


1. Generate the Apache Configuration
====================================

Generate the Apache configuration file using the ``tethys gen`` command:

    .. code-block:: bash

        tethys gen apache --overwrite


2. Review Apache Configuration
==============================

Review the contents of the Apache configuration file:

    .. code-block:: bash

        vim <TETHYS_HOME>/tethys_apache.conf

    .. tip::

        Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

    In particular, verify the following:

        * The ``ServerName`` parameter is set to your server's public domain name (e.g. my.example.com).
        * The ``/static`` location matches the location of your ``STATIC_ROOT`` directory.
        * The ``/media`` location matches the location of your ``MEDIA_ROOT`` directory.

3. Link the Tethys Apache Configuration
=======================================

Create a symbolic link from the ``tethys_apache.conf`` file to the Apache configuration directory (:file:`/etc/apache` or :file:`etc/httpd`):

    **Ubuntu**:
    
        .. code-block:: bash
        
            sudo ln -s <TETHYS_HOME>/tethys_apache.conf /etc/apache/sites-enabled/tethys_apache.conf
    
    **Rocky Linux**:
    
        .. code-block:: bash
        
            sudo ln -s <TETHYS_HOME>/tethys_apache.conf /etc/httpd/conf.d/tethys_apache.conf

    .. tip::

        Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

4. Remove the Default Apache Configuration (Ubuntu Only)
========================================================

For Ubuntu systems, remove the default Apache configuration file so Apache will use the Tethys configuration:

    **Ubuntu**:

        .. code-block:: bash

            sudo rm /etc/apache/sites-enabled/default

5. Note ``apache`` User
=======================

Get the name of the ``apache`` user for use in later parts of the installation guide:

    **Ubuntu**:

        .. code-block:: bash

            grep 'User .*' /etc/apache/apache.conf | awk '{print $2}' | awk -F';' '{print $1}'

    **Rocky Linux**:

        .. code-block:: bash

            grep 'User .*' /etc/httpd/conf/httpd.conf | awk '{print $2}' | awk -F';' '{print $1}'

    Note this user and use it in the following steps where you see ``<APACHE_USER>``.

6. Configure SSL (Recommended)
==============================

Most browsers are becoming more restrictive on sites that are not secure. It is highly recommended that you obtain an SSL/TLS certificate and setup HTTPS. For more details see: :ref:`https_config`.
