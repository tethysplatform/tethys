.. _production_installation_ssl:

*******************************
SSL Configuration (recommended)
*******************************

**Last Updated:** January 2020

3. Setup GeoServer SSL
======================

A secured server can only communicate with other secured servers. Therefore to allow the secured Tethys Portal to communicate with GeoServer, the latter needs to be secured as well. To do this, add the following location at the end of your server block.

::

    server {

        ...

        #GeoServer
        location /geoserver {
              proxy_pass http://127.0.0.1:8181/geoserver;
    }

Next, go to your GeoServer web interface (http://domain-name:8181/geoserver/web), sign in, and set the **Proxy Base URL** in Global settings to:
::

    https://<domain-name>/geoserver

.. image:: images/geoserver_ssl.png
    :width: 600px
    :align: center

4. Restart Tethys
=================

Finally, restart the supervisor services to effect the changes::

    sudo supervisorctl restart all


The portal should now be accessible from: https://domain-name and GeoServer should now be accessible from: https://domain-name/geoserver

.. Note::

    Notice that the GeoServer port (8181) is not necessary once the proxy is configured
