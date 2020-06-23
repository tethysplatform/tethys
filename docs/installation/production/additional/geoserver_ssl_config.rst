.. _production_geoserver_ssl_config:

***************************
GeoServer SSL Configuration
***************************

**Last Updated:** May 2020

A secured server can only communicate with other secured servers. Therefore to allow the secured Tethys Portal to communicate with GeoServer, the latter needs to be secured as well.

1. Add the following location at the end of your server block in your :file:`tethys_nginx.conf`:

.. code-block::

    server {

        ...

        #GeoServer
        location /geoserver {
              proxy_pass http://127.0.0.1:8181/geoserver;
    }

2. Next, go to your GeoServer web interface (e.g.: http://domain-name:8181/geoserver/web/), sign in, and set the **Proxy Base URL** in Global settings to:


.. code-block::

    https://<domain-name>/geoserver

.. image:: images/geoserver_ssl.png
    :width: 600px
    :align: center

3. Finally, restart all supervisor services (NGINX and Daphne) to effect the changes::

    sudo supervisorctl restart all

The portal should now be accessible from https://domain-name and GeoServer should now be accessible from https://domain-name/geoserver.

.. note::

    Notice that the GeoServer port (8181) is not necessary once the proxy is configured
