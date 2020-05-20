.. _production_installation_ssl:

*******************************
SSL Configuration (recommended)
*******************************

**Last Updated:** January 2020


SSL is the standard  technology for establishing a secured connection between a web server and a browser. In order to create a secured connection, an SSL certificate and key are needed.

1. Obtain an SSL Certificate
============================

An SSL certificate can be self-signed for testing but should be purchased from a Certificate Authority for a production installation. Some of the top certificate authorities include: Digicert, VertiSign, GeoTrust, Comodo, Thawte, GoDaddy, and Nework Solutions. If your instance of Tethys is part of a larger organization, contact your IT to determine if an agreement with one of these authorities already exists.

2. Modify NGINX Configuration
=============================

Once a certificate is obtained, it needs to be referenced in the Nginx configuration, which is the web server that Tethys uses in production. The configuration file can be found at :file:`<TETHYS_HOME>/tethys_nginx.conf`.

If you need your site to be accessible through both secured (https) and non-secured (http) connections, you will need a server block for each type of connection. Otherwise just edit the existing block.

Change the listen port to 443 and enable ssl with the following options:

::

    server {
        listen   443;

        ssl    on;
        ssl_certificate    /<path_to_your_ssl_certs>/your_domain_name.pem; (or bundle.crt)
        ssl_certificate_key    /<path_to_your_ssl_certs>/your_domain_name.key;
        ...
    }

.. important::

    SSL goes through port 443, hence the server block above listens on 443 instead of 80. Be sure to update your firewall accordingly if applicable. If you followed the production installation instructions exactly, this means you'll need to run:

::

    sudo firewall-cmd --permanent --zone=public --add-service=https
    sudo firewall-cmd --reload

.. tip::

    If you need your site to be accessible through both secured (https) and non-secured (http) connections, you will need a server block for each type of connection. Simply copy the the server block and paste it below the original server block. Then modify one as show above.


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
